from nrtpygs.mqclient.mqconnection import MqConnection
import nrtpygs.customlogger as log
import pika
import json
import time


class MqRpcServer():
    """
    Main RPC class for handling RPCs
    """

    def __init__(self, source = 'rpc'):
        """
        Set up the connection and consume callbacks
        """
        self.rmqlog = log.get_logger()
        self.rmqconnection = MqConnection(source)
        self.connection = self.rmqconnection.connect()
        self.channel = self.rmqconnection.get_channel()
        self._setup_consume()

    def disconnect(self):
        self.rmqconnection.close()

    def _rpc_handle_callback(self, ch, method, props, body):
        """
        Handle RPC requests sent with a JSON type payload
        TODO: This should be much more rigorous for safety
        i.e. checking user ids and privilidges
        """
        self.rmqlog.log(1, 'RPC callback triggered')
        try:
            message = json.loads(body)
        except json.JSONDecodeError:
            self.rmqlog.log(3, 'Error with JSON decoding of message')
            response = 'JSON decode error'
            return
        self.rmqlog.log(1, 'RPC request received: {}'.format(message['rpc']))
        RPC = getattr(self, message['rpc'], None)
        if callable(RPC):
            self.rmqlog.log(1, 'Calling function: {}'.format(message['rpc']))
            response = RPC(message['args'])
        else:
            self.rmqlog.log(1, 'No function called: {}'.format(message['rpc']))
            response = 'No function called: ' + message['rpc']
        self.rmqlog.log(1, 'Response is: {}'.format(response))
        self.rmqlog.log(1, 'Sending response: {}'.format(json.dumps(response)))

        self.connection.ioloop.add_callback(
            lambda: self.channel.basic_publish(
                exchange='rmq.direct',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    type='rpc'
                ),
                body=json.dumps(response)
            )
        )

    def _setup_consume(self):
        """
        Setup the queues for RPC
        """
        self.rmqlog.log(1, 'Starting RPC consume')

        queue_name = '.rpcserver'
        time.sleep(0.2)
        self.connection.ioloop.add_callback(
            lambda: self.channel.queue_declare(
                queue=queue_name,
                durable=True,
            )
        )

        self.rmqlog.log(1, 'Making bindings')
        time.sleep(0.2)
        self.connection.ioloop.add_callback(
            lambda: self.channel.queue_bind(
                exchange='rmq.direct',
                queue=queue_name,
            )
        )
        time.sleep(0.2)
        self.rmqlog.log(1, 'Making bindings')
        self.connection.ioloop.add_callback(
            lambda: self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._rpc_handle_callback,
                auto_ack=True,
            )
        )
        time.sleep(0.2)


class MqRpcClient():
    """
    Client Library for making RPC calls
    """
    def __init__(self):
        """
        Set up the connection
        """
        self.rmqconnection = MqConnection('rpcclient')
        self.connection = self.rmqconnection.connect()
        self.channel = self.rmqconnection.get_channel()

    def disconnect(self):
        self.rmqconnection.close()

    def call(self, TLA, funcname, args=None):
        """
        Send an RPC call and wait on responses
        """

        body = {
            'rpc': funcname,
            'args': args,
        }

        self.rmqlog.log(1, 'Starting RPC Call')
        self.rmqlog.log(1, 'Making response channel and queue')
        response_queue = 'rpcclient' + '.' + 'rpcresponse'

        self.rmqlog.log(1, 'Creating response queue {}'.format(response_queue))
        self.connection.ioloop.add_callback(
            lambda: self.channel.queue_declare(
                queue=response_queue, exclusive=True
            )
        )
        time.sleep(0.2)

        self.rmqlog.log(1, 'Making bindings')
        self.connection.ioloop.add_callback(
            lambda: self.channel.queue_bind(
                exchange='rmq.direct',
                queue=response_queue
            )
        )
        time.sleep(0.2)

        self.rmqlog.log(1, 'Making callback setup for ' + response_queue)
        self.connection.ioloop.add_callback(
            lambda: self.channel.basic_consume(
                queue=response_queue,
                on_message_callback=self.rpcResponse,
                auto_ack=True
            )
        )
        time.sleep(0.2)

        routing_key = TLA + '.rpcserver'
        self.rmqlog.log(1, 'Sending RPC request to {}'.format(routing_key))

        self.connection.ioloop.add_callback(
            lambda: self.channel.basic_publish(
                exchange='rmq.direct',
                routing_key=routing_key,
                properties=pika.BasicProperties(
                    type='rpc',
                    reply_to=response_queue,
                ),
                body=json.dumps(body)
            )
        )
        self.rmqlog.log(1, 'Awaiting RPC response')
        self.response = None
        while self.response is None:
            pass

        self.rmqlog.log(1, 'Received RPC response: ' + str(self.response))
        self.rmqlog.log(1, 'Removing queue ' + response_queue)
        self.connection.ioloop.add_callback(
            lambda: self.channel.queue_delete(queue=response_queue)
        )
        return self.response.decode()

    def rpcResponse(self, ch, method, props, body):
        self.rmqlog.log(1, 'Received response')
        self.response = body


# Create class intances
rpcserver = MqRpcServer()
rpcclient = MqRpcClient()


class MqRpcBase():
    """
    Base class for classes wishing to expose RPC functions.
    This at least shows what is required
    """
    def __init__(self, rpc_function_list):
        self.rpcRegister(rpc_function_list)
        self.rmqlog = log.get_logger()

    def rpcRegister(self, rpc_function_list):
        self.rmqlog.log(2, 'Registering rpc functions')
        for function in rpc_function_list:
            self.rmqlog.log(1, 'Registering rpc function {}'.format(function))
            func = getattr(self, function, None)
            setattr(rpcserver, func.__name__, func)
