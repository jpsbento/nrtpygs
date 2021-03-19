from rmqclient.rmqconnection import RmqConnection
from rmqclient.rmqconsume import RmqConsume
from rmqclient.rmqlogging import rmqlog
import logging as log
import pika
import rmqclient.rmqsettings as settings
import json
import os
import time
import shortuuid


class RmqRpcServer():
    """
    Main RPC class for handling RPCs
    """

    def __init__(self):
        """
        Set up the connection and consume callbacks
        """
        self.rmqlog = rmqlog
        self.rmqconnection = RmqConnection('rpcserver')
        self.connection = self.rmqconnection.connect()
        self._inchannel = self.rmqconnection.create_channel()
        self._outchannel = self.rmqconnection.create_channel()
        self._setup_consume()

    def _rpc_handle_callback(self, ch, method, props, body):
        """
        Handle RPC requests sent with a JSON type payload
        TODO: This should be much more rigorous for safety
        i.e. checking user ids and privilidges
        """
        from rmqclient.rmqlogging import rmqlog
        try:
            message = json.loads(body)
        except json.JSONDecodeError:
            rmqlog.log(3, 'Error with JSON decoding of message')
            response = 'JSON decode error'
            return
        rmqlog.log(1, 'RPC Message Received to call function {}'.format(message['rpc']))
        rmqlog.log(1, 'RPC Message Received to call function {}'.format(message['rpc']))
        RPC = getattr(self, message['rpc'], None)
        if callable(RPC):
            rmqlog.log(1, 'Function exists, calling: {}'.format(message['rpc']))
            response = RPC(message['args'])
        else:
            rmqlog.log(1, 'No function called: {}'.format(message['rpc']))
            response = 'No function called: ' + message['rpc']
        rmqlog.log(1, 'Response is: {} and type {}'.format(response, type(response)))

        self._outchannel.basic_publish(
            exchange=settings.EXCHANGES['rpc'],
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                type='rpc'
            ),
            body=str(response)
        )

    def _setup_consume(self):
        """
        Setup the queues for RPC
        """
        rmqlog.log(1, 'Starting RPC consume')

        queue_name = settings.TLA + '.rpcserver'
        self._inchannel.queue_declare(
            queue=queue_name,
            durable=True,)

        rmqlog.log(1, 'Making bindings')
        self._inchannel.queue_bind(
            exchange=settings.EXCHANGES['rpc'],
            queue=queue_name)

        self._inchannel.basic_consume(
            queue=queue_name,
            on_message_callback=self._rpc_handle_callback,
            auto_ack=True)


class RmqRpcClient():
    """
    Client Library for making RPC calls
    """
    def __init__(self):
        """
        Set up the connection
        """
        self.rmqconnection = RmqConnection('rpcclient')
        self.connection = self.rmqconnection.connect()
        self._outchannel = self.rmqconnection.create_channel()

    def call(self, TLA, funcname, args=None):
        """
        Send and RPC call and wait on responses
        """

        body = {
            'rpc': funcname,
            'args': args,
        }

        rmqlog.log(1, 'Starting RPC Call')
        rmqlog.log(1, 'Making response channel and queue')
        channel = self.rmqconnection.create_channel()
        response_queue = settings.TLA + '.' + 'rpcresponse'
        rmqlog.log(1, 'Creating response queue {}'.format(response_queue))
        channel.queue_declare(queue=response_queue, exclusive=True)
        rmqlog.log(1, 'Making bindings')
        try:
            rmqlog.log(1, 'Making callback queue setup for queue ' + response_queue)
            channel.queue_bind(
            exchange=settings.EXCHANGES['rpc'],
            queue=response_queue)
        except Exception as e:
            print('Channel Bind Error', e)
            
        try:
            channel.basic_consume(
                queue=response_queue,
                on_message_callback=self.rpcResponse,
                auto_ack=True)
        except Exception as e:
            print('Basic Consume error', e)

        routing_key = TLA + '.rpcserver'
        rmqlog.log(1, 'Sending RPC request to {}'.format(routing_key))


        self._outchannel.basic_publish(
            exchange=settings.EXCHANGES['rpc'],
            routing_key=routing_key,
            properties=pika.BasicProperties(
                type='rpc',
                reply_to=response_queue,
            ),
            body=json.dumps(body)
        )
        rmqlog.log(1, 'Awaiting RPC response')
        self.response = None
        while self.response is None:
            pass

        rmqlog.log(1, 'Received RPC response: ' + str(self.response))
        rmqlog.log(1, 'Removing queue ' + response_queue)
        channel.queue_delete(queue=response_queue)
        channel.close()
        return self.response.decode()

    def rpcResponse(self, ch, method, props, body):
        rmqlog.log(1, 'Received response')
        self.response = body

# Create class intances
rpcServer = RmqRpcServer()
rpcClient = RmqRpcClient()



class RmqRpcBase():
    """
    Base class for classes wishing to expose RPC functions.
    This at least shows what is required
    """
    def __init__(self, rpc_function_list):
        self.rpcRegister(rpc_function_list)

    def rpcRegister(self, rpc_function_list):
        rmqlog.log(2, 'Registering rpc functions')
        for function in rpc_function_list:
            rmqlog.log(1, 'Registering rpc function {}'.format(function))
            func = getattr(self, function, None)
            setattr(rpcServer, func.__name__, func)
