import os
import logging as log

# Local logging settings
LOGLEVEL = log.INFO
LOGFILE = 'redisclient.log'

# Service specific settings for the rmqclient
TLA = os.environ['SER_TLA']


LOGLEVELS = {
    5: 'CRT',
    4: 'ERR',
    3: 'WRN',
    2: 'INF',
    1: 'DBG',
}
