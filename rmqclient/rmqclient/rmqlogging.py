import datetime
import pika
from rmqclient.rmqconnection import RmqConnection
import logging as log
from queue import Queue
import json
import time
import threading

import rmqclient.rmqsettings as settings


class RmqLogging():

    def __init__(self):
        self._sent = 0
        self._stopping = False
        log.debug('Initiating class')
        self._rmqconnection = RmqConnection('rmqlogger')
        self._connection = self._rmqconnection.connect()
        self._channel = self._rmqconnection.get_channel()
        self._logq = Queue(maxsize=settings.LOGQ_MAX_SIZE)

        # Set up publish message thread.
        self._logThread = threading.Thread(
            target=self._publish_message_loop,
            args=())
        self._logThread.start()

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
        self._logq.put(body)

    def disconnect(self):
        self._stopping = True
        # Wait for all messages to be sent

        # Allow extra time for remaining messages to purge
        time.sleep(1)
        # Close the connection and rejoin the log thread
        self._rmqconnection.close()
        self._logThread.join()

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


        self._connection = self._rmqconnection.get_connection()
        self._channel = self._rmqconnection.get_channel()

        log.debug('Connection is open again, recreating channel')
        self._channel = self._rmqconnection.create_channel()

    def _publish_message_loop(self):
        """
        Single thread function to read logq and publish log messages
        """
        while not self._stopping:
            # Block until a message body is available
            # TODO: Tidy up the double breaks.
            # Could raise an exception perhaps?
            while self._logq.empty():
                if self._stopping == True:
                    break
            if self._stopping:
                break

            self._sent += 1
            if self._sent % 1000 == 0:
                log.debug('Published {} messages. Queuesize is {}'
                          .format(self._sent, self._logq.qsize()))

            body = self._logq.get(block=True, timeout=None)
            self._connection.ioloop.add_callback(
                lambda: self._publish_message(body)
            )

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
                    properties=settings.LOG_PROPERTIES,
                    body=json.dumps(body)
                )
                message_sent = True
            except pika.exceptions.ChannelWrongStateError:
                log.error('Error sending message (ChannelWrongState),'
                          + ' attempting reconnection')
                self._recreate_channel()


# Set up telemetry object
rmqlog = RmqLogging()


def main():
    """
    Used for an example of how logging can be used
    TODO: Make it as an end to end test?
    """
    x = 10
    delay = 0.1
    print('Sending {} mesages with {}s delay'.format(str(x), str(delay)))
    for i in range(1, x+1):
        rmqlog.log(1, 'This is a debug log number ' + str(i))
        time.sleep(delay)
    print('Sent {} messages'.format(str(x)))
    time.sleep(2)
    rmqlog.disconnect()


if __name__ == '__main__':
    main()
