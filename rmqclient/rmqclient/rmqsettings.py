import os
import logging as log

PIKA_LOGLEVEL = log.WARN
RMQ_LOGLEVEL = log.DEBUG
RMQ_LOGFILE = 'rmq.log'

# settings for the rmqmodule
TLA = os.environ['SER_TLA']

# Maximum python queue size. 0=Inifinite
LOGQ_MAX_SIZE = 0


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
