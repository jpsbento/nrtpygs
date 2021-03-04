from rmqconnection import RmqConnection
from rmqlogging import rmqlogging


class RmqTelemetry():

    def __init__():
        self._connection = RmqConnection()
        self._connection.connect()
        self._channel = self._connection
        pass

    def recreate_channel():
        try
            self._channel.close()
        Except exception as e

    def pub():
        """
        Publish telemetry message
        """

        pass








# Set up telemetry object
rmqtelemetry = RmqTelemetry()
