import datetime
import time
import json
import os
import pika
from queue import Queue
import threading


# Connection parameters to the RabbitMQ server from ENV_VARS
CREDENTIALS = pika.PlainCredentials(
    os.environ['RMQ_USER'], os.environ['RMQ_PASS']
    )

CON_PARAMS = pika.ConnectionParameters(
    host=os.environ['RMQ_HOST'],
    credentials=CREDENTIALS,
    )

LOGLEVELS = {
    0: 'CRT',
    1: 'SYS',
    2: 'ERR',
    3: 'WRN',
    4: 'INF',
    5: 'DBG',
}


# A test blocking loop to wait for Rabbitmq to come up when loading module
# Really don't like the printing here, but better than a logger?
print('Testing Rabbitmq Server is up:')
while True:
    print('\tAttempting Rabbitmq Connection')

    try:
        connection = pika.BlockingConnection(CON_PARAMS)
        break
    except Exception as e:
        print('Received exception ', e)
        print('\tConnection Error! Retrying in 2s')
        time.sleep(2)

print("Connected, Rabbitmq is up!")
print("Disconnecting")
connection.close()


class RCSmq():
    """
    RCS Messaging queue library using pika with RabbitMQ
    """

    def __init__(self, modTLA):
        """
        Initiation takes the service TLA, and sets up the necessary Connections
        Currently;
        - logconnection [OUT] - Logging connection
        - rpcconnection [OUT] - For making RPC calls
        - inconnection  [IN]  - Consuming connection for incomming data and RPC
                                calls
        """
        self.modTLA = modTLA
        self.listenQ = modTLA

        self.rpcconnection = pika.BlockingConnection(CON_PARAMS)
        self.response = None
        self.outconnection = pika.BlockingConnection(CON_PARAMS)
        self.outchannel = self.outconnection.channel()

        self.logconnection = pika.BlockingConnection(CON_PARAMS)
        self.logchannel = self.logconnection.channel()
        self.logq = Queue(maxsize=20)
        logThread = threading.Thread(target=self.logPublish)
        logThread.start()

        self.inconnection = pika.BlockingConnection(CON_PARAMS)
        self.inchannel = self.inconnection.channel()
        self.inchannel.queue_declare(queue=self.listenQ)
        self.inchannel.basic_consume(queue=self.listenQ,
                                     on_message_callback=self.routeMessage,
                                     auto_ack=True)
        inThread = threading.Thread(target=self.inchannel.start_consuming,
                                    args=())
        inThread.start()

    def callback(self, ch, method, props, body):
        """
        Blank callback method, so if service doesn't overwrite,
        then the service wont hang
        """
        pass

    def routeMessage(self, ch, method, props, body):
        """
        Called by the inchannel consume. Message type is assessed.
        If not an RPC call, then passed to the callback() which the
        service can overwrite and handle.

        Else, passed to rpcHandle()
        """

        if props.type != 'rpc':
            self.callback(ch, method, props, body)
        else:
            self.rpcHandle(ch, method, props, body)

    def rpcCall(self, routing_key, body):
        """
        Send and RPC call and wait on responses
        """
        self.log(5, 'Starting RPC Call')
        self.log(5, 'Making response channel and queue')
        channel = self.rpcconnection.channel()
        result = channel.queue_declare(queue='', exclusive=True)
        self.log(5, 'Obtaining response queue name')
        response_queue = result.method.queue
        self.log(5, 'Making callback queue setup for queue ' + response_queue)
        channel.basic_consume(
            queue=response_queue,
            on_message_callback=self.rpcResponse,
            auto_ack=True)

        self.log(5, 'Sending RPC request to ' + routing_key)
        self.outchannel.basic_publish(
            exchange='',
            routing_key=routing_key,
            properties=pika.BasicProperties(
                type='rpc',
                reply_to=response_queue,
            ),
            body=json.dumps(body)
        )
        self.log(5, 'Awaiting RPC response')
        while self.response is None:
            self.rpcconnection.process_data_events()

        self.log(5, 'Received RPC response: ' + str(self.response))
        self.log(5, 'Removing queue ' + response_queue)
        channel.queue_delete(queue=response_queue)
        return self.response.decode()

    def rpcResponse(self, ch, method, props, body):
        self.response = body

    def rpcHandle(self, ch, method, props, body):
        """
        Handle RPC requests sent with a JSON type payload
        """
        message = json.loads(body)
        self.log(5, 'RPC Message Received to call function: ' + message['rpc'])
        RPC = getattr(self, message['rpc'], None)
        if callable(RPC):
            self.log(5, 'Function exists, calling: ' + message['rpc'])
            response = RPC()
        else:
            self.log(5, 'No function called: ' + message['rpc'])
            response = 'No function called: ' + message['rpc']
        self.pub(props.reply_to, response)

    def log(self, level, message):
        """
        Logging call to RCS Logging System (RLS) utilising Zej Piascik
        logging format suggestions in
        http://telescope.livjm.ac.uk/pmwiki/index.php?n=Main.LoggingStandards
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = (
            [
                'log', time + '    ' +
                self.modTLA + '    ' +
                LOGLEVELS[level] + '    ' +
                message
            ]
        )

        self.logq.put(body)

    def tel(self, keyValue):
        """
        Telemetry Feed publish to log queue
        """
        body = ['tel', json.dumps(keyValue)]
        self.logq.put(body)

    def logPublish(self):
        """
        Single thread function to read logq and publish
        """
        while True:
            type, body = self.logq.get(block=True, timeout=None)
            if type == 'log':
                properties = pika.BasicProperties(type='log')
            elif type == 'tel':
                properties = pika.BasicProperties(type='tel')

            self.logchannel.basic_publish(
                exchange='',
                routing_key='RLS',
                properties=properties,
                body=body
            )

    def pub(self, routing_key, body):
        """
        Standard publish
        """
        channel = self.outconnection.channel()
        channel.basic_publish(exchange='', routing_key=routing_key, body=body)
        channel.close()
