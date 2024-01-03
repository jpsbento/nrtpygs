import logging
import os
import timeout_decorator
import influxdb_client

# Configure the logging settings
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
        except KeyError as e:
            # Handle the case when any of the environment variables are missing
            logging.error(f"Missing environment variable: {e}")
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An unexpected error occurred: {e}")
        # Format influxdb url to conform with the influxdb-client
        # library requirement to have the full URL
        if 'http' not in self._url:
            self._url = "http://" + self._url

    @timeout_decorator.timeout(20)
    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """

        logging.debug('Connecting to %s', self._url)
        try:
            self.client = influxdb_client.InfluxDBClient(
                url=self._url,
                token=self._token,
                org=self._org
            )

            return self.client
        except Exception as e:
            logging.error('Unable to connect to Influx Database: %s' % e)

    @timeout_decorator.timeout(20)
    def get_client(self):
        if self.client.ping():
            return self.client
        else:
            return None

    @timeout_decorator.timeout(20)
    def close(self):
        if self.client:
            self.client.close()
            logging.debug('Connection to influxDB closed')
