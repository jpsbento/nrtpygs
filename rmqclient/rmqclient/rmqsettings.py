import os
import pika
import logging as log

# Local logging settings
PIKA_LOGLEVEL = log.WARN
RMQ_LOGLEVEL = log.DEBUG
RMQ_LOGFILE = 'rmqclient.log'

# Service specific settings for the rmqclient
TLA = os.environ['SER_TLA']
USR = os.environ['SER_USR']

# Maximum python queue size for logging and telemetry. 0=Inifinite
LOGQ_MAX_SIZE = 0
TELQ_MAX_SIZE = 0

LOG_PROPERTIES = pika.BasicProperties(
    content_type='json',
    delivery_mode=2,
    app_id=TLA,
)

TEL_PROPERTIES = pika.BasicProperties(
    content_type='json',
    delivery_mode=2,
    app_id=TLA
)

# Priorities for both Python Queue and RabbitMQ
# Althogh RabbitMQ needs a flip!
# A lower number is higher priority
TEL_PRIORITIES = {
    'tel': 3,
    'alm': 2,
    'evn': 1,
}

EXCHANGES = {
    'rpc': 'rmq.direct',
    'tel': 'rmq.telemetry',
    'log': 'rmq.logging',
}

LOGLEVELS = {
    5: 'CRT',
    4: 'ERR',
    3: 'WRN',
    2: 'INF',
    1: 'DBG',
}
