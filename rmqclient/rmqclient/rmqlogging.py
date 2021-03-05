import datetime
import pika
from rmqconnection import RmqConnection
import logging as log
from queue import Queue
import json
import time
import threading

import rmqsettings as settings

class RmqLogging():
    def __init__(self):
        self._stopping = False
        log.debug('Initiating class')
        self._rmqconnection = RmqConnection('rmqlogger')
        self._connection = self._rmqconnection.connect()
        self._channel = self._rmqconnection.create_channel()
        self.logq = Queue(maxsize=settings.LOGQ_MAX_SIZE)
        self.logThread = threading.Thread(target=self._publish_message_loop, args=())
        self.logThread.start()


    def log(self, level, message):
        """
        Add logging message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'timestamp': time,
            'level': settings.LOGLEVELS[level],
            'message': message,
        }
        self._publish_message(body)

    def disconnect(self):
        self._stopping = True
        self._connection.close()
        self.logThread.join


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
        Single thread function to read logq and publish
        """
        log.debug('Starting publish message loop')
        while not self._stopping:
            # Block until a message body is available
            body = self.logq.get(block=True, timeout=None)
            if self.logq.qsize()>10000:
                print ("more than 10000 messages in queue")
            elif self.logq.qsize()>1000:
                print ("more than 1000 messages in queue")
            elif self.logq.qsize()>100:
                print ("more than 100 messages in queue")
            elif self.logq.qsize()>50:
                print ("more than 50 messages in queue")
            # Publish the message on the log connection
            self._publish_message(body)

    def _publish_message(self, body):
        """
        Publish message in a loop until mit is sent. If there is an exception
        then recreate the send channel on the autoreconnected connection
        """
        message_sent = False
        while not message_sent:
            try:
                self._channel.basic_publish(
                    exchange=settings.EXCHANGES['log'],
                    routing_key='rcs.'+settings.TLA+'.'+body['level'],
                    properties=pika.BasicProperties(),
                    body=json.dumps(body)
                )
                message_sent = True
            except:
                log.error('Error sending message, attempting reconnection')
                self._recreate_channel()


# Set up telemetry object
rmqlogging = RmqLogging()


def main():
    """
    Used for an example of how logging can be used
    TODO: Make it as an end to end test?
    """

    while True:
        rmqlogging.log(1, 'This is a debug log')
    rmqlogging.disconnect()


if __name__ == '__main__':
    main()
