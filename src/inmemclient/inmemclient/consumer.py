import re
from inmemclient.connection import Connection
import inmemclient.settings as settings
import logging as log


class Consume():
    """
    Class to allow clients to subscribe to messages. On initiation the class
    will create a connection. At that point a client can setup multiple
    consumers using this connection. Each consumer has one queue, but can
    specify multiple binding keys.

    A new RmqConsumer object is created each time consume is called and stored
    This is required for future ability for consumers to detect when a channel
    has closed and to reopen it by suppliying an on channel closed callback.

    The client needs to specify the paramaters in the consume method
    Namely
        - exchange
        - binding keys
        - queue_name
        - callback
    """

    def __init__(self):
        self._connection = Connection()
        self._connection.connect()
        
    def consume(self, key, callback):
        # Set the queuename to hold the service TLA prefix
        new_consumer = Consumer(
            self._connection,
            key,
            callback,
        )

        self._consumers.append(new_consumer)

    def get_consumers(self):
        return self._consumers

    def disconnect(self):
        self._connection.close()


class Consumer():
    """
    The class for holding information on an individual consumer
    """

    def __init__(self, connection, key, callback):
        self._connection = connection.get_connection()
        self._key = key
        self._callback = callback
        self._consume()

    def _consume(self):
        """
        Setting up a basic channel consumption
        """
        log.debug('Starting consume')
        pubsub = self._connection.pubsub()
        pubsub.psubscribe(**{self._key:self._callback})
        


class ExampleConsume():
    """
    Example usage of RmqConsumer
    """

    def __init__(self):
        consume = Consume()
        consume.consume(
            'rmq.telemetry',
            self.msgcallback,
            
        )

    def msgcallback(self, ch, method, props, body):
        print(props.app_id, body)
        self._msgs_received += 1
        if self._msgs_received % 100 == 0:
            print('Messages received', self._msgs_received)


def main():
    """
    This triggers the ExampleConsume class, which shows how the consume
    callback can be used within a Class structure interacting with
    Class members
    """
    ExampleConsume()


if __name__ == '__main__':
    main()
