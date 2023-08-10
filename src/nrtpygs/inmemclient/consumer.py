from nrtpygs.inmemclient.connection import Connection
from nrtpygs.logging import get_logger
from operator import itemgetter

class Consumer():
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

    def __init__(self, cluster=True):
        self._connection = Connection()
        self._connection.connect(cluster=cluster)
        self._consumers = []
        self._logger = get_logger()
        
    def subscribe(self, key: str, callback):
        try:
            pubsub = self._connection.connection.pubsub()
            pubsub.psubscribe(**{key:callback})
            thread = pubsub.run_in_thread(sleep_time=0.001)
            self._consumers.append(thread)
            self._logger.info('Consuming %s on redis server' % key)
        except Exception as e:
            self._logger.error('Unable to subscribe to channel %s: %s' % (key, e))
            
    def get_consumers(self):
        return self._consumers

    def disconnect(self):
        for thread in self._consumers:
            thread.stop()
        self._connection.close()

class ExampleConsume():
    """
    Example usage of RmqConsumer
    """

    def __init__(self):
        consume = Consumer()
        consume.subscribe(
            'rmq.telemetry',
            self.msgcallback,
        )

    def msgcallback(self, message: dict):
        type, pattern, channel, data = itemgetter('type', 'pattern', 'channel', 'data')(message)
        print('The data on this event is: %e' % str(data))
        
        

def main():
    """
    This triggers the ExampleConsume class, which shows how the consume
    callback can be used within a Class structure interacting with
    Class members
    """
    ExampleConsume()


if __name__ == '__main__':
    main()
