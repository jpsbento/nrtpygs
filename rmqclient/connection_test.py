import os
os.environ['SER_TLA'] = "TST"

os.environ['RMQ_USER'] = "rmq"
os.environ['RMQ_PASS'] = "rmq"
os.environ['RMQ_HOST'] = "localhost"

from rmqclient.rmqproducer import RmqProducer

producer = RmqProducer()
print("Finished setting up client")

def submit_sequence():
    data = {
        "data": "test"
    }
    try:
        #producer.call("TLA", "sequence", data)
        producer.produce(data)
        producer.disconnect()
    except Exception as e:
        raise "Problem"
    return "Success"


if __name__ == '__main__':
    # This will run the app for testing purposes
    submit_sequence()