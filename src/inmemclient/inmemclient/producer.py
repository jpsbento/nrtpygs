import datetime
from inmemclient.connection import Connection
import logging as log


class Producer():

    def __init__(self):
        self._connection = Connection()
        self._connection = self._connection.connect()
        
        
    def publish(self, key, value):
        """
        Add message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'timestamp': time,
            'value': value,
        }
        log.debug('Setting key %s' % key)
        try: 
            log.debug('Publishing')
            self._connection.publish(key, str(body))
            log.debug('Setting')            
            self._connection.set(key,str(body))
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
