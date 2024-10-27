# NRTPYGS
Repository for the New Robotic Telescope Generic Services Python Module

This repository contains;
* Code for an inmemory storage, such as Redis. 
* Code for rmqclient - The python Library for RCS services to communicate with a
* A time series client code for InfluxDB instance. 

This is structured to be the source code for a python module, which is built and deployed onto a 
google cloud python registry automatically. 

## Using this module

#### Installation

In order to make use of this module, Simply either install the package using pip:

`pip install --index-url https://europe-west1-python.pkg.dev/nrtljmu/nrt-python-registry/simple/ nrtpygs`

or add these lines to the requirements.txt file: 

`--extra-index-url https://europe-west1-python.pkg.dev/nrtljmu/nrt-python-registry/simple/`
`nrtpygs==0.25.3`

#### Env variables

These are the list of required environment variables your app or container must have setup for this code to work:

RMQ_HOST=localhost  # The RabbitMQ server options if using rabbitmq
RMQ_USER=rmq
RMQ_PASS=rmq
ADM_USER=rmq-admin
ADM_PASS=rmq-admin

REDIS_HOST=localhost    # The Redis parameters if using redis
REDIS_USERNAME=default
REDIS_PASSWORD=redis_password


INFLUX_HOST = influxhost    # The InfluxDB if using InfluxDB.
INFLUX_PORT = influxport
DOCKER_INFLUXDB_INIT_USERNAME = influxusername
DOCKER_INFLUXDB_INIT_PASSWORD = influxpassword
DOCKER_INFLUXDB_INIT_BUCKET = influxdb


#### Using the module in the code

Then, within your python code, simply import the module and use it. An example is below that consumes a rabbitmq message and publushes to redis. : 

```
from nrtpygs.mqclient.mqconsumer import MqConsume
from nrtpygs.inmemclient.producer import Producer


# Setting up a Rabbitmq consumer and a Redis producer 
consume = MqConsume()
redis_producer = Producer()
log.info('Attempting connection now!')
consume.consume(
    EXCHANGE,
    ['#'],
    ROUTING_KEY,
    msgcallback,
    durable=True,
    #arguments={
    #    'x-queue-type': 'classic',
    #    'x-max-priority': 3
    #}
)


def msgcallback(self, ch, method, props, body):
    print(props.app_id, body)
    log.info('Message received. Content: %s' % body)
    log.info('Pushing to Redis')
    try:
        redis_producer.publish("key", {'value':0, 'unit':'m/s'})
    except Exception as e:
        log.error('An error occured pushing payload to Redis: %s' % e)
        return

```


More documentation is available by consulting the py-generic-services repository. 