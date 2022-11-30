import logging as log
import os
import threading
import time
import inmemclient.settings as settings
import redis
import timeout_decorator

# Connection parameters to the RabbitMQ server from ENV_VARS
REDIS_HOST=os.environ['REDIS_HOST']
REDIS_USERNAME=os.environ['REDIS_USERNAME']
REDIS_PASSWORD=os.environ['REDIS_PASSWORD']

POOL = redis.ConnectionPool(host=os.environ['REDIS_HOST'], username=REDIS_USERNAME, password=REDIS_PASSWORD, port=6379)


# Turn off pika info and Debug Level logging
log.getLogger('redis').setLevel(settings.LOGLEVEL)
log.basicConfig(
    filename=settings.LOGFILE,
    level=settings.LOGLEVEL,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')

# TODO: Test what this does!
log = log.getLogger(__name__)


class Connection():
    """
    Class to provide connection and new channel options to the rmq server
    At present a single channel is opened and the object returned.
    """

    def __init__(self):
        self.pool = POOL
        
    @timeout_decorator.timeout(2)
    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """

        self.connection = redis.RedisCluster(connection_pool=self.pool)

        log.debug('Connecting to %s', REDIS_HOST)
        # Wait to allow connection to open before returning
        while not self.connection.ping():
            pass
        log.debug('Connection opened')
        return self.connection

    @timeout_decorator.timeout(2)
    def get_connection(self):
        while not self.connection.ping():
            time.sleep(0.1)
            pass
        return self.connection

    @timeout_decorator.timeout(3)
    def close(self):
        log.debug('Closing Connection')
        if self.connection is not None:
            self.connection.close()
        # Block until connection closes
        while self.connection.is_open:
            pass


def main():
    """
    Used for an example of how connection takes place and how to send a message
    TODO: Make it as an end to end test

    NOTE: A number of OS environment variables need to be set for a successful
    connection to the rmq server. These are;
    - REDIS_USER
    - REDIS_PASS
    - REDIS_HOST

    See rcs-gsi/utils.setenv.sh for a tool to do this outside of the 4mnrt/gsi
    container.
    """
    # Create the RmqConnection class
    redis_connection = Connection()

    # Start connection and get connection handle.
    connection = redis_connection.connect()

    # Send a message usong the channel handle inside the ioloop callback
    connection.publish("key",'hello')
    
    # Check if the connection is still open
    if connection.ping():
        redis_connection.close()


if __name__ == '__main__':
    main()
