import datetime
import pika
from nrtpygs.mqclient.mqconnection import MqConnection
import nrtpygs.customlogger as log
from queue import Queue
import json
import time
import threading


class MqProducer():

    def __init__(self, exchange='sequencer', routing_key='rmq.sequencer'):
        self._sent = 0
        self._sending_message = False
        self._stopping = False
        self._await_reconnect = False
        self._rmqconnection = MqConnection('producer')
        self._connection = self._rmqconnection.connect()
        self._channel = self._rmqconnection.get_channel()
        self._prodq = Queue(maxsize=0)
        self.exchange = exchange
        self.routing_key = routing_key
        self._logger = log.get_logger()

        # Set up publish message thread.
        self._prodThread = threading.Thread(
            target=self._publish_message_loop,
            args=())
        self._prodThread.start()

    def produce(self, message):
        """
        Add message to python queue
        """
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        body = {
            'timestamp': time,
            'message': message,
        }
        self._prodq.put(body)

    def disconnect(self):
        self._logger.info('Disconnecting Production Connection')
        self._stopping = True
        # Wait for all messages to be sent

        while not self._prodq.empty():
            time.sleep(0.1)
            pass
        # Allow extra time for remaining messages to purge
        time.sleep(0.5)
        # Close the connection and rejoin the log thread
        self._rmqconnection.close()
        self._prodThread.join()

    def _await_new_channel(self):
        """
        Await RmqConnection to reconnect and create a new channel
        """
        self._logger.info('Awaiting channel recreation')
        self._logger.debug('Waiting on connection to reopen')
        self._connection = self._rmqconnection.get_connection()
        self._logger.debug('Connection is open again')
        self._channel = self._rmqconnection.get_channel()
        self._logger.debug('Channel is open again')
        self._await_reconnect = False

    def _publish_message_loop(self):
        """
        Single thread function to read prodq and publish messages
        """
        self._logger.debug('Starting publish message loop')
        while True:
            # Stop the loop consuming all resource
            # max rate 10kHz
            time.sleep(0.0001)
            if self._await_reconnect:
                self._await_new_channel()

            if not self._prodq.empty() and not self._sending_message:
                self._sending_message = True
                self._connection.ioloop.add_callback(self._publish_message)
                self._sent += 1
                if self._sent % 1000 == 0:
                    self._logger.debug(
                        'Published {} messages. Queuesize is {}'
                        .format(self._sent, self._prodq.qsize())
                    )

            if self._prodq.empty() and self._stopping:
                break

    def _publish_message(self):
        """
        Publish message in a loop until it is sent. If there is an exception
        then recreate the send channel on the autoreconnected connection
        """
        body = self._prodq.get(block=True, timeout=None)
        try:
            self._channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                properties=pika.BasicProperties(
                    content_type='json',
                    delivery_mode=2,
                ),
                body=json.dumps(body)
            )

        except pika.exceptions.ChannelWrongStateError:
            self._logger.error(
                'Error sending message (ChannelWrongState), reconnecting'
            )
            self._await_reconnect = True
        self._sending_message = False


def main():
    """
    Used for an example of how to use the producer
    to publish messages to a specific queue, because this uses a
    direct exchange
    """
    # Set up telemetry object
    rmqprod = MqProducer(exchange="sequencer", routing_key="SEQ.request")
    data = {
        "data": "test"
    }
    rmqprod.produce(data)
    rmqprod.disconnect()


if __name__ == '__main__':
    main()
