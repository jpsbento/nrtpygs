import datetime
import pika
from mqconnection import MqConnection
import logging as log
from queue import Queue
import json
import time
import threading

import mqsettings as settings


class MqLogging():

    def __init__(self):
        self._sent = 0
        self._sending_message = False
        self._stopping = False
        self._await_reconnect = False
        self._rmqconnection = MqConnection('rmqlogger')
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
        log.info('Disconnecting Logging Connection')
        self._stopping = True
        # Wait for all messages to be sent

        while not self._logq.empty():
            time.sleep(0.1)
            pass
        # Allow extra time for remaining messages to purge
        time.sleep(0.5)
        # Close the connection and rejoin the log thread
        self._rmqconnection.close()
        self._logThread.join()

    def _await_new_channel(self):
        """
        Await RmqConnection to reconnect and create a new channel
        """
        log.info('Awaiting channel recreation')
        log.debug('Waiting on connection to reopen')
        self._connection = self._rmqconnection.get_connection()
        log.debug('Connection is open again')
        self._channel = self._rmqconnection.get_channel()
        log.debug('Channel is open again')
        self._await_reconnect = False

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

            if not self._logq.empty() and not self._sending_message:
                self._sending_message = True
                self._connection.ioloop.add_callback(self._publish_message)
                self._sent += 1
                if self._sent % 1000 == 0:
                    log.debug(
                        'Published {} telemetry messages. Queuesize is {}'
                        .format(self._sent, self._logq.qsize())
                    )

            if self._logq.empty() and self._stopping:
                break

    def _publish_message(self):
        """
        Publish message in a loop until it is sent. If there is an exception
        then recreate the send channel on the autoreconnected connection
        """
        body = self._logq.get(block=True, timeout=None)
        try:
            self._channel.basic_publish(
                exchange=settings.EXCHANGES['log'],
                routing_key='rcs.' + settings.TLA + '.' + body['level'],
                properties=settings.LOG_PROPERTIES,
                body=json.dumps(body)
            )

        except pika.exceptions.ChannelWrongStateError:
            log.error(
                'Error sending message (ChannelWrongState), reconnecting'
            )
            self._await_reconnect = True
        self._sending_message = False


# Set up telemetry object
rmqlog = MqLogging()


def main():
    """
    Used for an example of how logging can be used
    TODO: Make it as an end to end test?
    """
    x = 100000
    delay_ms = 0
    print('Sending {} mesages with {}ms delay'.format(str(x), str(delay_ms)))
    for i in range(1, x + 1):
        rmqlog.log(1, 'This is a debug log number ' + str(i))
        time.sleep(delay_ms / 1000)
    print('Sent {} messages'.format(str(x)))
    rmqlog.disconnect()


if __name__ == '__main__':
    main()
