import datetime
from nrtpygs.inmemclient.connection import Connection
import nrtpygs.customlogger as log
import json


class Producer():

    def __init__(self, source='Unknown'):
        self.source = source
        self._cluster = Connection()
        self._connection = self._cluster.connect()
        self._logger = log.get_logger()

    def publish(self, key, value):
        """
        Add message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'timestamp': time,
            'source': self.source,
            'content': value,
        }
        self._logger.debug('Setting key %s' % key)
        try:
            self._logger.debug('Publishing')
            self._connection.publish(key, json.dumps(body))
            self._logger.debug('Setting')
            self._connection.set(key, json.dumps(body))
        except Exception as e:
            self._logger.error('Unable to publish message for key %s: %s' % (key, e))

    def disconnect(self):
        self._logger.info('Disconnecting Production Connection')
        self._stopping = True
        # Wait for all messages to be sent

        # Close the connection and rejoin the log thread
        self._connection.close()


def main():
    """
    Used for an example of how to use the producer
    to publish messages to a specific queue, because this uses a
    direct exchange
    """
    # Set up telemetry object
    prod = Producer()
    data = {
        "data": "test"
    }
    prod.publish('message', data)
    prod.disconnect()


if __name__ == '__main__':
    main()
