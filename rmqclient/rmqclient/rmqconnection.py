import pika
import logging as log
import os
import threading
import rmqclient.rmqsettings as settings

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

# TODO: Test what this does!
log = log.getLogger(__name__)


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
        return self.connection

    def get_connection(self):
        return self.connection

    def on_connection_open(self, _unused_connection):
        log.info('Connection opened')
        return

    def on_connection_open_error(self, _unused_connection, err):
        """
        This method is called by pika if the connection to RabbitMQ
        can't be established.
        """
        log.error('Connection open failed, trying again in 3 seconds: %s', err)
        self.connection.ioloop.call_later(3, self.connect)
        return

    def on_connection_closed(self, _unused_connection, reason):
        """
        This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. If it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        """
        if self._stopping:
            log.info('Connection closed by user')
            self.connection.ioloop.stop()
            self.connection = None
        else:
            log.warning(
                'Connection closed, reopening in 5 seconds: %s',
                reason)
            self.connection.ioloop.call_later(1, self.connect)

    def close(self):
        log.info('Closing Connection')
        self._stopping = True
        if self.connection is not None:
            self.connection.close()

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
            log.debug(
                'The channel on_close_callback is has been overloaded')
        else:
            log.debug(
                'The channel on_close_callback is default to RmqConnection')
            on_close_callback = self.on_channel_closed

        self.new_channel = self.connection.channel(
            on_open_callback=self.on_channel_open)
        self.new_channel.add_on_close_callback(on_close_callback)
        # Wait for channel to open before returning
        while not self.new_channel.is_open:
            pass
        return self.new_channel

    def on_channel_open(self, channel):
        log.info('Channel opened')

    def on_channel_closed(self, channel, reason):
        """
        Invoked by pika when RabbitMQ unexpectedly closes the channel.
        """
        if not self._stopping:
            log.warning('Channel %i was closed: %s', channel, reason)
        else:
            log.info('Channel %i was closed: %s', channel, reason)


def main():
    """
    Used for an example of how connection takes place and how to send a message
    TODO: Make it as an end to end test

    NOTE: A numebr of OS environment variables need to be set for a successful
    connection to the rmq server. These are;
    - RMQ_USER
    - RMQ_PASS
    - RMQ_HOST
    - SER_TLA
    """
    # Create the RmqConnection class
    rmqconnection = RmqConnection('ConnectionNameHere')
    # Start connection and get connection handle.
    connection = rmqconnection.connect()
    # Open a channel and get a channel object for local use
    channel = rmqconnection.create_channel()
    # Send a message
    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body='HELLO!')

    # Check if the connection is still open
    if connection.is_open:
        rmqconnection.close()


if __name__ == '__main__':
    main()
