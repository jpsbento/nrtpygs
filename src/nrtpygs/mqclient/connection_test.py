from nrtpygs.mqclient.mqproducer import MqProducer
import os

os.environ['RMQ_USER'] = "guest"
os.environ['RMQ_PASS'] = "guest"
os.environ['RMQ_HOST'] = "localhost"

producer = MqProducer(exchange="sequencer", routing_key="rcs.TST")
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
