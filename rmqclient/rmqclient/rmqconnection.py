import pika

import logging as log
import os
import time
import threading
import rmqsettings as settings
import code

# Connection parameters to the RabbitMQ server from ENV_VARS
CREDENTIALS = pika.PlainCredentials(
    os.environ['RMQ_USER'], os.environ['RMQ_PASS']
    )

RMQ_HOST = os.environ['RMQ_HOST']

# Turn off pika info and Debug Level logging
log.getLogger('pika').setLevel(settings.PIKA_LOGLEVEL)
log.basicConfig(
    filename=settings.RMQ_LOGFILE,
    level=settings.RMQ_LOGLEVEL,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')

#log = log.getLogger(__name__)

class RmqConnection():
    """
    Class to provide connection and new channel options to the rmq server
    """

    def __init__(self, name):
        self._stopping = False
        self.new_channel = None
        self.connection_name = settings.TLA + '.' + name

    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """
        parameters = pika.ConnectionParameters(
            host=RMQ_HOST,
            credentials=CREDENTIALS,
            client_properties={
                'connection_name': self.connection_name,
            },)

        self.connection = pika.SelectConnection(
            parameters=parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

        log.info('Connecting to %s', parameters.host)
        self.iothread = threading.Thread(
            target=self.connection.ioloop.start,
            args=())
        self.iothread.start()
        # Wait to allow connection to open before returning
        while not self.connection.is_open:
            pass
        log.debug('Connection open')
        return self.connection

    def get_connection(self):
        return self.connection

    def on_connection_open(self, _unused_connection):
        log.info('Connection opened')
        return

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        log.error('Connection open failed, reopening in 5 seconds: %s', err)
        self.connection.ioloop.call_later(5, self.connect)
        return

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        if self._stopping:
            self.connection.ioloop.stop()
        else:
            log.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self.connection.ioloop.call_later(5, self.connect)

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
        if self.connection is not None:
            log.info('Closing connection')
            self.connection.close()
            self.connection = None

    def create_channel(self, channel_number=None, on_close_callback=None):
        """
        Create a channel on the connection. Once open return the channel object

        on_close_callback can be specified to handle disconnections of
        the channel in a graceful way with your own function.

        It MUST accept the same arguments as self.on_channel_closed()  e.g.
        def on_close_callback_method(self, channel, reason)

        If a custom function is specified (i.e. for reconnection) it should
        check if the connection class is stopping and if so,
        not attempt reconnection and exit gracfully.
        """

        if on_close_callback:
            log.debug('The channel on_close_callback is has been overloaded')
        else:
            log.debug('The channel on_close_callback is default to RmqConnection')
            on_close_callback = self.on_channel_closed

        self.new_channel = self.connection.channel(on_open_callback=self.on_channel_open)
        self.new_channel.add_on_close_callback(on_close_callback)
        # Wait for channel to open before returning
        while not self.new_channel.is_open:
            pass
        return self.new_channel

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
    Used for an example of how connection takes palce and how to send a message
    TODO: Make it as an end to end test
    """

    connection = RmqConnection()
    connection.connect()
    channel = connection.create_channel()

if __name__ == '__main__':
    main()
