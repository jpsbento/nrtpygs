import re
from nrtpygs.mqclient.mqconnection import MqConnection
import nrtpygs.customlogger as log

class MqConsume():
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
        self._connection = MqConnection('rmqconsumer')
        self._connection.connect()
        self._consumers = []

    def consume(self, exchange, binding_keys, queue_name,
                callback, durable=False, arguments=None):
        # Set the queuename to hold the service TLA prefix
        new_consumer = MqConsumer(
            self._connection,
            exchange,
            binding_keys,
            queue_name,
            callback,
            durable,
            arguments
        )

        self._consumers.append(new_consumer)

    def get_consumers(self):
        return self._consumers

    def disconnect(self):
        self._connection.close()


class MqConsumer():
    """
    The class for holding information on an individual consumer
    """

    def __init__(self, connection, exchange,
                 binding_keys, queue_name, callback, durable, arguments):
        self._rmqconnection = connection
        self._connection = self._rmqconnection.get_connection()
        self._channel = None
        self._exchange = exchange
        self._binding_keys = binding_keys
        if not re.search(r'^[A-Z]{3}', queue_name):
            self._queue_name = queue_name
        self._callback = callback
        self._durable = durable
        self._arguments = arguments
        self._logger = log.get_logger()
        self._setup_consume()

    def _setup_consume(self):
        self._create_channel()
        self._create_queue()
        self._setup_bindings()
        self._consume()

    def _create_channel(self):
        self._channel = self._rmqconnection.create_channel()

    def _create_queue(self):
        self._logger.debug('Creating queue {}'.format(self._queue_name))
        self._channel.queue_declare(
            queue=self._queue_name,
            durable=self._durable,
            arguments=self._arguments,
        )

    def _setup_bindings(self):
        # First delete any previous bindings. This allows code updates
        # to take effect without getting old messages routed.
        self._logger.debug('Setting up bindings')
        # Then rebind the keys
        for binding_key in self._binding_keys:
            self._channel.queue_bind(
                exchange=self._exchange,
                queue=self._queue_name,
                routing_key=binding_key
            )

    def _consume(self):
        """
        We set the basic consume and set the callback,
        Being asyncronous we don't need a
        pika.Channel.start_consuming() method
        """
        self._logger.debug('Starting consume')
        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._callback,
            auto_ack=True
        )


class ExampleConsume():
    """
    Example usage of RmqConsumer
    """

    def __init__(self):
        self._msgs_received = 0
        consume = MqConsume()
        consume.consume(
            'rmq.telemetry',
            ['#'],
            'priority_queue',
            self.msgcallback,
            durable=True,
            arguments={
                'x-queue-type': 'classic',
                'x-max-priority': 3
            }
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
