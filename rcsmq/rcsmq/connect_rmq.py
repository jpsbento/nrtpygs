import pika
import logging as log
import os
from pika.adapters.asyncio_connection import AsyncioConnection
import time
import threading

# Connection parameters to the RabbitMQ server from ENV_VARS
CREDENTIALS = pika.PlainCredentials(
    os.environ['RMQ_USER'], os.environ['RMQ_PASS']
    )

CON_PARAMS = pika.ConnectionParameters(
    host=os.environ['RMQ_HOST'],
    credentials=CREDENTIALS,
    )

log.getLogger("pika").setLevel(logging.WARNING)

log.basicConfig(
    filename='rcsmq.log',
    level=log.INFO,
    format='%(asctime)s: %(levelname)s: %(message)s')

class RmqConnection():
    """
    Class to provide connection and new channel options to the rmq server
    """

    def __init__(self):
        self._connection = None
        self._stopping = False

    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """
        log.info('Connecting to %s', CON_PARAMS.host)
        self._connection = pika.SelectConnection(
            CON_PARAMS,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

        self.iothread = threading.Thread(
            target=self._connection.ioloop.start,
            args=())
        self.iothread.start()
        return self._connection

    def on_connection_open(self, _unused_connection):
        log.info('Connection opened')
        pass

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        log.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self.connect)

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            log.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self.connect)

    def close(self):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.

        """
        log.info('Closing Connection')
        self._stopping = True
        if self._connection is not None:
            log.info('Closing connection')
            self._connection.close()
            self._connection = None

    def create_channel(self, queue_number=None):
        """
        Create a queue on the connection and return the Queue
        Object
        """

        new_channel = self._connection.channel(on_open_callback=self.on_channel_open)
        new_channel.add_on_close_callback(self.on_channel_closed)
        return new_channel

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        log.info('Channel opened')

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        log.warning('Channel %i was closed: %s', channel, reason)


def main():
    """
    Used for an expample of how connection table palce and how channels communicate
    TODO: Make it as an end to end test
    """

    connection = RmqConnection()
    connection.connect()
    connection.createChannel()


    print ("We never get here until the connect() method returns")

if __name__ == '__main__':
    main()
