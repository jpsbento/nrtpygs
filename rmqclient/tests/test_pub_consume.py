import time
from rmqclient.rmqlogging import rmqlog
from rmqclient.rmqtelemetry import rmqtel
from rmqclient.rmqconsume import RmqConsume


class CountMessages():
    def __init__(self):
        self.messages = 0

    def callback(self, ch, method, props, body):
        self.messages += 1


def publish_100_logs():
    for i in range(1, 101):
        rmqlog.log(3, 'This is warning log number {}'.format(i))
    rmqlog.disconnect()


def consume_100_logs():
    counter = CountMessages()
    consume = RmqConsume()
    consume.consume(
        'rmq.logging',
        ['#'],
        'LOG.complete',
        counter.callback,
        durable=True)

    # Allow time for messages to be consumed.
    time.sleep(2)
    consume.disconnect()
    assert counter.messages == 100


def publish_100_telemetry():
    for i in range(1, 101):
        rmqtel.tel('TestValue', 122.3)
    rmqtel.disconnect()


def consume_100_telemetry():
    counter = CountMessages()
    consume = RmqConsume()
    consume.consume(
        'rmq.telemetry',
        ['#'],
        'TEL.complete',
        counter.callback,
        durable=True,
        arguments={
            'x-queue-type': 'classic',
            'x-max-priority': 3,
        }
    )

    # Allow time for messages to be consumed.
    time.sleep(2)
    consume.disconnect()
    assert counter.messages == 100


def test_pub_consume_logs():
    publish_100_logs()
    consume_100_logs()


def test_pub_consume_tel():
    rmqtel.disconnect()
    # publish_100_telemetry()
    # consume_100_telemetry()
