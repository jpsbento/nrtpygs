from nrtpygs.timeseriesclient.connection import Connection
import nrtpygs.customlogger as log
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point


class Producer():

    def __init__(self, source='Unknown'):
        self._influxdb = Connection()
        self._influxClient = self._influxdb.connect()
        self._write_api = self._influxClient.write_api(
            write_options=SYNCHRONOUS)
        self._logger = log.get_logger()
        self.source = source

    def write(self, fields, tags={"site": "nrt"}):
        """
        Add message to time series
        """

        try:
            data = Point(measurement_name=self.source)
            [data.tag(k, v) for k, v in tags.items()]
            [
                data.field(k, v) if isinstance(v, (int, float))
                else self._logger.debug(
                    f"Non-numerical value for '{k}': \
                        {v} and not added to InfluxDB"
                )
                for k, v in fields.items()
            ]
            self._logger.debug("Writing value %s" % str(data))
            return self._write_api.write(
                bucket=self._influxdb.database, record=data
                )
        except Exception as e:
            self._logger.error(
                'Unable to write data for measurement %s: %s' % (
                    str(fields), e
                    )
            )
