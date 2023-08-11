import datetime
from nrtpygs.inmemclient.connection import Connection
import logging as log
import json


class Producer():

    def __init__(self, source='Unknown', cluster=True):
        self.source = source
        self._cluster = Connection()
        self._connection = self._cluster.connect(cluster=cluster)

    def publish(self, key, value):
        """
        Add message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'timestamp': time,
            'source': self.source,
            'value': value,
        }
        log.debug('Setting key %s' % key)
        try:
            log.debug('Publishing')
            self._connection.publish(key, json.dumps(body))
            log.debug('Setting')
            self._connection.set(key, json.dumps(body))
        except Exception as e:
            log.error('Unable to publish message for key %s: %s' % (key, e))

    def disconnect(self):
        log.info('Disconnecting Production Connection')
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
    prod.produce('message', data)
    prod.disconnect()


if __name__ == '__main__':
    main()
