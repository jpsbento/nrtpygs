from rmqclient.rmqconnection import RmqConnection
from rmqclient.rmqlogging import rmqlog
import rmqclient.rmqsettings as settings
import json


class RmqProducer():
    """
    Main Class for making calls to RabbitMQ
    """

    def __init__(self):
        """
        Set up the connection
        """
        self.rmqconnection = RmqConnection('rpcclient')
        self.connection = self.rmqconnection.connect()
        self.channel = self.rmqconnection.get_channel()

    def disconnect(self):
        self.rmqconnection.close()

    def call(self, TLA, funcname, args=None):
        """
        Send an RPC call and wait on responses
        """

        body = {
            'producer': funcname,
            'args': args,
        }

        rmqlog.log(1, 'Starting RPC Call')

        routing_key = TLA + '.producer'
        rmqlog.log(1, 'Sending request to {}'.format(routing_key))

        self.connection.ioloop.add_callback(
            lambda: self.channel.basic_publish(
                exchange=settings.EXCHANGES['produce'],
                routing_key=routing_key,
                body=json.dumps(body)
            )
        )
