import logging
import os
import timeout_decorator
from influxdb import InfluxDBClient

# Configure the logging settings
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Connection parameters to the RabbitMQ server from ENV_VARS
    INFLUX_HOST = os.environ['INFLUX_HOST']
    INFLUX_PORT = os.environ['INFLUX_PORT']
    INFLUX_USERNAME = os.environ['DOCKER_INFLUXDB_INIT_USERNAME']
    INFLUX_PASSWORD = os.environ['DOCKER_INFLUXDB_INIT_PASSWORD']
    INFLUX_DATABASE = os.environ['DOCKER_INFLUXDB_INIT_BUCKET']

    # Your code for connecting to RabbitMQ server and other operations can go here

except KeyError as e:
    # Handle the case when any of the environment variables are missing
    logging.error(f"Missing environment variable: {e}")
except Exception as e:
    # Handle other exceptions
    logging.error(f"An unexpected error occurred: {e}")

class Connection():
    """
    Class to provide connection and new channel options to the rmq server
    At present a single channel is opened and the object returned.
    """

    def __init__(self):
        self._host = INFLUX_HOST
        self._port = INFLUX_PORT
        self._username = INFLUX_USERNAME
        self._password = INFLUX_PASSWORD
        self._database = INFLUX_DATABASE
        self.client = None
        
    @timeout_decorator.timeout(20)
    def connect(self):
        """
        Create a connection, start the ioloop to connect
        inside a thread and then return the connection
        """

        logging.debug('Connecting to %s', INFLUX_HOST)
        try:
            self.client = InfluxDBClient(self._host, self._port, self._username, self._password, self._database)
            return self.client
        except:
            logging.error('Unable to connect to Influx Database')

        

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

