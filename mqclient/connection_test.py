import os
from mqclient.mqproducer import MqProducer

os.environ['SER_TLA'] = "TST"
os.environ['RMQ_USER'] = "rmq-admin"
os.environ['RMQ_PASS'] = "rmq-admin"
os.environ['RMQ_HOST'] = "localhost"

producer = MqProducer()
print("Finished setting up client")


def submit_sequence():
    data = {
        "data": "test"
    }
    try:
        producer.produce(data)
    except Exception as e:
        raise ("Problem: %s" % e)
    return "Success"


if __name__ == '__main__':
    # This will run the app for testing purposes
    submit_sequence()
