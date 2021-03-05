import asyncio
import datetime
import pika
from rmqconnection import RmqConnection
from queue import Queue
import json
import time
import threading
import rmqsettings as settings

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
        self._connection = RmqConnection('rmqconsumer')
        self._connection.connect()
        self._consumers = []

    def consume(self, exchange, binding_keys, queue_name, callback):
        #Set the queuename to hold the service TLA prefix
        new_consumer = RmqConsumer(
            self._connection,
            exchange,
            binding_keys,
            queue_name,
            callback
        )

        self._consumers.append(new_consumer)

    def get_consumers(self):
        return self._consumers


class RmqConsumer():
    """
    The class for holding information on an individual consumer
    """

    def __init__(self, connection, exchange, binding_keys, queue_name, callback):
        self._rmqconnection = connection
        self._connection = self._rmqconnection.get_connection()
        self._channel = None
        self._exchange = exchange
        self._binding_keys = binding_keys
        queue_prefix = settings.TLA + '.'
        self._queue_name = queue_prefix + queue_name
        self._callback = callback
        self._setup_consume()

    def _setup_consume(self):
        self._create_channel()
        self._create_queue()
        self._setup_bindings()
        self._consume()

    def _create_channel(self):
        self._channel = self._rmqconnection.create_channel()

    def _create_queue(self):
        log.debug('Creating queue {}'.format(self._queue_name))
        self._channel.queue_declare(
            queue=self._queue_name,
            durable=True,
        )

    def _setup_bindings(self):
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
        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._callback,
            auto_ack=True
        )


def main():
    """
    Used for an example of how consuming takes place and how to send a message
    TODO: Make it as an end to end test?
    """

    consume=RmqConsume()

    def msgcallback(ch, method, properties, body):
        if not msgs_received:
            msgs_received = 0
        msgs_received += 1
        if msgs_received%100:
            print (msgs_reecieved, 'messages have been received')

    consume.consume('rmq.logging', ['#'], 'all_queue', msgcallback)

if __name__ == '__main__':
    main()
