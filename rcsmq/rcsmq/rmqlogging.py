from rmqconnection import RmqConnection
from queue import Queue
import json
import time
import threading


import rmqsettings as settings

LOGLEVELS = {
    0: 'CRT',
    1: 'SYS',
    2: 'ERR',
    3: 'WRN',
    4: 'INF',
    5: 'DBG',
}


class RmqLogging():

    def __init__(self):
        self._connection = RmqConnection()
        self._connection.connect()
        self._channel = self._connection.create_channel()
        self.logq = Queue(maxsize=settings.LOGQ_MAX_SIZE)
        self.logThread = threading.Thread(target=self._publish_message_loop)
        self.logThread.start()


    def _create_channel(self):
        """
        Recreate the channel if there is a publish error
        """
        try:
            self._channel.close()
        except Exception as e:
            print('Received Exception', e)
        self._channel = self._connection


    def log(self, log_level, message):
        """
        Add logging message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = (
            [
                'log', time + '    ' +
                self.modTLA + '    ' +
                settings.LOGLEVELS[log_level] + '    ' +
                message
            ]
        )
        self.logq.put(body)

    def _publish_message_loop(self):
        """
        Single thread function to read logq and publish
        """
        while True:
            type, body = self.logq.get(block=True, timeout=None)
            self.logchannel.basic_publish(
                exchange='',
                routing_key='RLS',
                properties=properties,
                body=body
            )
        pass


# Set up telemetry object
rmqlogging = RmqLogging()
