import os
os.environ['SER_TLA'] = "TST"

os.environ['RMQ_USER'] = "rmq-admin"
os.environ['RMQ_PASS'] = "rmq-admin"
os.environ['RMQ_HOST'] = "localhost"

from rmqclient.rmqproducer import RmqProducer
from rmqclient.rmqtelemetry import RmqTelemetry

producer = RmqProducer()
#telemetry = RmqTelemetry()
print("Finished setting up client")


def submit_sequence():
    data = {
        "data": "test"
    }
    try:
        producer.produce(data)
        #telemetry.tel('Key','Value')
        #producer.produce(data)
        #producer.disconnect()
    except Exception as e:
        raise "Problem"
    return "Success"


if __name__ == '__main__':
    # This will run the app for testing purposes
    submit_sequence()