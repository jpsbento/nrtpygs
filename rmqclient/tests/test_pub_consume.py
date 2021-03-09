import time
from rmqclient.rmqlogging import rmqlog
from rmqclient.rmqconsume import RmqConsume


class CountMessages():
    def __init__(self):
        self.messages = 0

    def callback(self, ch, method, props, body):
        self.messages += 1


def publish_100_logs():
    for i in range(1, 10):
        rmqlog.log(3, 'This is warning log number {}'.format(i))
        time.sleep(0.05)
    time.sleep(1)
    rmqlog.disconnect()


def consume_100_logs():
    counter = CountMessages()
    consume = RmqConsume()
    consume.consume(
        'rmq.logging',
        ['#'],
        'LOG.complete',
        counter.callback)

    # Allow time for messages to be consumed
    time.sleep(3)
    consume.disconnect()
    assert counter.messages == 100


def test_pub_consume():
    publish_100_logs()
    consume_100_logs()
