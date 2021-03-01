# settings for the rmqmodule

# Maximum python queue size. 0=Inifinite
LOGQ_MAX_SIZE = 0

# Wait time before returning connection to allow initialisation(ms)
CONNECTION_WAIT_TIME = 100

EXCHANGES = {
    'rpc': 'rmq.direct'
    'tel': 'rmq.telemetry'
    'log': 'rmq.logging'
}

# Log Levels
LOGLEVELS = {
    0: 'CRT',
    1: 'SYS',
    2: 'ERR',
    3: 'WRN',
    4: 'INF',
    5: 'DBG',
}
