from nrtpygs.timeseriesclient.connection import Connection
from nrtpygs.logging import get_logger
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point


class Producer():

    def __init__(self):
        self._influxdb = Connection()
        self._influxClient = self._influxdb.connect()
        self._write_api = self._influxClient.write_api(
            write_options=SYNCHRONOUS)
        self._logger = get_logger()

    def write(self, fields, tags={"site": "nrt"}):
        """
        Add message to python queue
        """

        try:
            data = Point(self._influxdb._source)
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
