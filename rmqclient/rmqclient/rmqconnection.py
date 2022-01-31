import pika
import logging as log
import os
import threading
import time
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
    At present a single channel is opened and the object returned.
    """

    def __init__(self, name):
        self._stopping = False
        self.channel = None
        self.new_channel = None  # Non functional. See self.create_channel()
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
        while not self.connection.is_open:
            pass
        return self.connection

    def get_channel(self):
        """
        Waits until channel is defined and open before returning the channel
        handle.
        Not elegent, but works
        """
        while not self.channel:
            time.sleep(0.001)
            pass
        while not self.channel.is_open:
            time.sleep(0.001)
            pass
        return self.channel

    def on_connection_open(self, _unused_connection):
        log.info('Connection opened')
        self.channel = self.connection.channel()
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
            self.channel = None
        else:
            log.warning(
                'Connection closed unexpectedly, reopening in 1 second: %s',
                reason)
            self.connection.ioloop.call_later(1, self.connect)

    def close(self):
        log.info('Closing Connection')
        self._stopping = True
        if self.connection is not None:
            self.connection.close()
        # Block until connection closes
        while self.connection.is_open:
            pass

    def create_channel(self, channel_number=None, on_close_callback=None):
        """
        NOTE: THIS IS NOT ACTIVE IN THE rmqconnectionAPI
        Creating and returning channel handles outside of the ioloop structure
        causes multithreading issues which cause frame errors.
        See https://github.com/4mnrt/wp4-pdr-project/issues/23

        Creates a channel on the connection.
        Once open returns the channel object

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

    NOTE: A number of OS environment variables need to be set for a successful
    connection to the rmq server. These are;
    - RMQ_USER
    - RMQ_PASS
    - RMQ_HOST
    - SER_TLA

    See rcs-gsi/utils.setenv.sh for a tool to do this outside of the 4mnrt/gsi
    container.
    """
    # Create the RmqConnection class
    rmqconnection = RmqConnection('ConnectionNameHere')

    # Start connection and get connection handle.
    connection = rmqconnection.connect()

    # Open a channel and get a channel object for local use
    channel = rmqconnection.get_channel()

    # Send a message usong the channel handle inside the ioloop callback
    connection.ioloop.add_callback(
        lambda: channel.basic_publish(
            exchange='',
            routing_key='hello',
            body='HELLO!')
    )

    # Connections should be long lived and the previous call was asynchronous
    # meaning we should allow the ioloop to complete the request
    # Importing inline is horrendous, but needs must!
    import time
    time.sleep(1)

    # Check if the connection is still open
    if connection.is_open:
        rmqconnection.close()


if __name__ == '__main__':
    main()
