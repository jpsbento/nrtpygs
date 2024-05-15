import nrtpygs.customlogger as log
import os
import influxdb_client

class Connection():
    """
    Class to provide connection and new channel options to the rmq server
    At present a single channel is opened and the object returned.
    """

    def __init__(self):
        try:
            # This needs the host and port in this format:
            # http://localhost:8086
            self._url = os.environ['INFLUX_HOST']
            self._username = os.environ['DOCKER_INFLUXDB_INIT_USERNAME']
            self._password = os.environ['DOCKER_INFLUXDB_INIT_PASSWORD']
            self.database = os.environ['DOCKER_INFLUXDB_INIT_BUCKET']
            self._token = os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']
            self._org = 'NRT'
            self.client = None
            self._logger = log.get_logger()
            
        except KeyError as e:
            # Handle the case when any of the environment variables are missing
            self._logger.error(f"Missing environment variable: {e}")
        except Exception as e:
            # Handle other exceptions
            self._logger.error(f"An unexpected error occurred: {e}")
        # Format influxdb url to conform with the influxdb-client
        # library requirement to have the full URL
        if 'http' not in self._url:
            self._url = "http://" + self._url

    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """

        self._logger.debug('Connecting to %s', self._url)
        try:
            self.client = influxdb_client.InfluxDBClient(
                url=self._url,
                token=self._token,
                org=self._org
            )

            return self.client
        except Exception as e:
            self._logger.error('Unable to connect to Influx Database: %s' % e)

    def get_client(self):
        if self.client.ping():
            return self.client
        else:
            return None

    def close(self):
        if self.client:
            self.client.close()
            self._logger.debug('Connection to influxDB closed')
