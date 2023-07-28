import datetime
from nrtpygs.timeseriesclient.connection import Connection
import logging as log


class Producer():

    def __init__(self):
        self._influxdb = Connection()
        self._influxClient = self._influxdb.connect()

    def write(self, measurement, fields, tags={"site": "nrt"}):
        """
        Add message to python queue
        """

        log.debug('Setting measurement %s' % measurement)
        try:
            data = [{
                "measurement": measurement,
                "tags": tags,
                "time": datetime.datetime.now().isoformat(),
                "fields": fields
                }]
            self._influxClient.write_points(data)
        except Exception as e:
            log.error('Unable to write data for measurement %s: %s' %
                      (measurement, e))
