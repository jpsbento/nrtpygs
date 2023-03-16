import datetime
import pika
from mqconnection import MqConnection
import logging as log
from queue import Queue
import json
import time
import threading

import mqclient.mqsettings as settings


class MqTelemetry():

    def __init__(self):
        self._sent = 0
        self._sending_message = False
        self._stopping = False
        self._await_reconnect = False
        log.debug('Initiating class')
        self._rmqconnection = MqConnection('rmqtelemetry')
        self._connection = self._rmqconnection.connect()
        self._channel = self._rmqconnection.get_channel()
        self._telq = Queue(maxsize=settings.LOGQ_MAX_SIZE)

        # Set up publish message thread.
        self._telThread = threading.Thread(
            target=self._publish_message_loop,
            args=())
        self._telThread.start()

    def create_channel(self):
        self._channel = self._rmqconnection.create_channel()

    def tel(self, datum, value):
        """
        Add telemetry message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'type': 'tel',
            'timestamp': time,
            'name': datum,
            'value': value,
        }

        self._telq.put(body)

    def alm(self, name, state):
        """
        Add telemetry message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'type': 'alm',
            'timestamp': time,
            'name': name,
            'value': state,
        }

        self._telq.put(body)

    def evn(self, name):
        """
        Add telemetry message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'type': 'evn',
            'timestamp': time,
            'name': name,
        }

        self._telq.put(body)

    def disconnect(self):
        log.info('Disconnecting Telemetry Connection')
        self._stopping = True
        # Wait for all messages to be sent from queue

        while not self._telq.empty():
            time.sleep(0.01)
            pass
        # Allow extra time for remaining messages to purge
        time.sleep(0.5)
        self._rmqconnection.close()
        self._telThread.join()

    def _await_new_channel(self):
        """
        Recreate the channel if there is a publish error
        """
        log.info('Trying to recreate the channel')
        try:
            self._channel.close()
        except Exception as e:
            log.error('Received Exception on channel close: {}'.format(e))
        # Wait until Connection reopens if it was a channel issue;
        log.debug('Waiting on connection to reopen')

        while not self._connection.is_open:
            time.sleep(0.1)
            self._connection = self._rmqconnection.get_connection()

        log.debug('Connection is open again, recreating channel')
        self._channel = self._rmqconnection.create_channel()

    def _publish_message_loop(self):
        """
        Single thread function to read logq and publish log messages
        """
        log.debug('Starting publish message loop')
        while True:
            # Stop the loop consuming all resource
            # max rate 10kHz
            time.sleep(0.0001)

            if self._await_reconnect:
                self._await_new_channel()

            if not self._telq.empty() and not self._sending_message:
                self._sending_message = True
                self._connection.ioloop.add_callback(self._publish_message)
                self._sent += 1
                if self._sent % 1000 == 0:
                    log.debug(
                        'Published {} telemetry messages. Queuesize is {}'
                        .format(self._sent, self._telq.qsize())
                    )

            if self._telq.empty() and self._stopping:
                break

    def _publish_message(self):
        """
        Publish message in a loop until mit is sent. If there is an exception
        then recreate the send channel on the autoreconnected connection
        """
        body = self._telq.get(block=True, timeout=None)
        routing_key = 'rcs.' + settings.TLA + '.' \
                      + body['type'] + '.' + body['name']
        priority = settings.TEL_PRIORITIES[body['type']]
        properties = settings.TEL_PROPERTIES
        properties.priority = priority

        try:
            self._channel.basic_publish(
                exchange=settings.EXCHANGES['tel'],
                routing_key=routing_key,
                properties=properties,
                body=json.dumps(body)
            )
        except pika.exceptions.ChannelWrongStateError:
            log.error(
                'Error sending message (ChannelWrongState), reconnecting.'
            )
            self._await_reconnect = True
        self._sending_message = False


# Set up telemetry object
rmqtel = MqTelemetry()


def main():
    """
    Used for an example of how telemetry is used and to check throughput
    """
    x = 10000
    delay_ms = 0
    print('Sending {} telemetry mesages with {}ms delay'
          .format(str(x), str(delay_ms)))
    for i in range(1, x+1):
        rmqtel.tel('temp', 122.3)
        time.sleep(delay_ms / 1000)
    print('Sent {} messages'.format(str(x)))
    time.sleep(1)
    rmqtel.disconnect()


if __name__ == '__main__':
    main()
