import datetime
import pika
from rmqconnection import RmqConnection
from queue import Queue
import json
import time
import threading

import logging as log

import code

class RmqConsume():
    """
    Class to allow clients to subscribe to messages. On initiation the class
    will create a connection. At that point a client can setup multiple
    consuming queues.

    The client needs to specify the paramaters in the consume method
    Namely
        - exchange
        - binding keys
        - queue_name
        - callback
    """

    def __init__(self):
        self._connection = RmqConnection('Consume')
        self._connection.connect()

    def consume(self, exchange, binding_keys, queue_name, callback):
        self._create_channel()
        self._create_queue(queue_name)
        self._setup_bindings(exchange, queue_name, binding_keys)
        self._consume(queue_name, callback)

    def _create_channel(self):
        self._channel = self._connection.create_channel()

    def _create_queue(self, queue_name):
        log.debug('Creating queue {}'.format(queue_name))
        self._channel.queue_declare(queue=queue_name, exclusive=True)

    def _setup_bindings(self, exchange, queue_name, binding_keys):
        for binding_key in binding_keys:
            self._channel.queue_bind(
                exchange=exchange,
                queue=queue_name,
                routing_key=binding_key
            )

    def _consume(self, queue, callback):
        # we set the basic consume and set the callback, however as
        self._channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=True
        )



def main():
    """
    Used for an example of how consuming takes palce and how to send a message
    TODO: Make it as an end to end test?
    """

    consume=RmqConsume()

    def msgcallback(ch, method, properties, body):
        print('Message Received:')
        print(body)

    consume.consume('rmq.logging', ['#'], 'test_queue', msgcallback)
    consume.consume('rmq.logging', ['#'], 'test_queue2', msgcallback)

if __name__ == '__main__':
    main()
