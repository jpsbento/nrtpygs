import datetime
import pika
import logging as log
from queue import PriorityQueue
import json
import time
import threading

from rmqconnection import RmqConnection
import rmqsettings as settings
from rmqlogging import rmqlog


class RmqTelemetry():

    def __init__(self):
        self._stopping = False
        log.debug('Initiating class')
        rmqlog.log(1, 'Telemetry object created')
        self._rmqconnection = RmqConnection('rmqtemelemtry')
        self._connection = self._rmqconnection.connect()
        self._channel = self._rmqconnection.create_channel()
        self._telq = PriorityQueue(maxsize=settings.LOGQ_MAX_SIZE)

        # Set up publish message thread.
        self._telThread = threading.Thread(
            target=self._publish_message_loop,
            args=())
        self._telThread.start()

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
        self._telq.put((settings.TEL_PRIORITIES[body['type']], body))

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
        self._telq.put((settings.TEL_PRIORITIES[body['type']], body))

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
        self._telq.put((settings.TEL_PRIORITIES[body['type']], body))

    def disconnect(self):
        print('Disconnecting')
        self._stopping = True
        self._rmqconnection.close()
        time.sleep(0.1)
        # self._telThread.join()

    def _recreate_channel(self):
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
            self._connection = self._rmqconnection.get_connection()

        log.debug('Connection is open again, recreating channel')
        self._channel = self._rmqconnection.create_channel()

    def _publish_message_loop(self):
        """
        Single thread function to read logq and publish log messages
        """
        log.debug('Starting publish message loop')
        while not self._stopping:
            # Block until a message body is available
            # TODO: Tidy up the double breaks.
            # Could raise an exception perhaps?
            while self._telq.empty():
                if self._stopping:
                    print("Stopping!")
                    break
                pass

            if self._stopping:
                print("Stopping!")
                break
            body = self._telq.get(block=True, timeout=None)[1]
            self._publish_message(body)

    def _publish_message(self, body):
        """
        Publish message in a loop until mit is sent. If there is an exception
        then recreate the send channel on the autoreconnected connection
        """
        message_sent = False
        routing_key = 'rcs.' + settings.TLA + '.' \
                      + body['type'] + '.' + body['name']
        priority = 4 - settings.TEL_PRIORITIES[body['type']]
        TelProperties = settings.TEL_PROPERTIES
        TelProperties.priority = priority
        while not message_sent:
            try:
                self._channel.basic_publish(
                    exchange=settings.EXCHANGES['tel'],
                    routing_key=routing_key,
                    properties=TelProperties,
                    body=json.dumps(body)
                )
                message_sent = True
            except pika.exceptions.ChannelWrongStateError:
                log.error('Error sending message, attempting reconnection')
                self._recreate_channel()


# Set up telemetry object
rmqtel = RmqTelemetry()


def main():
    """
    Used for an example of how telemetry can be used
    TODO: Make it as an end to end test?
    """
    x = 10
    delay = 0.1
    print('Sending {} telemetry mesages with {}s delay'
          .format(str(x), str(delay)))
    for i in range(1, x+1):
        rmqtel.tel('temp', 122.3)
        time.sleep(delay)
    print('Sent {} messages'.format(str(x)))
    time.sleep(2)
    rmqtel.disconnect()


if __name__ == '__main__':
    main()
