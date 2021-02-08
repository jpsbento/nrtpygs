# File to setup the Rabbitmq server for RCS operation
# This calls sub setup operations

#!/bin/sh

/opt/code/rmq/rmq-usersetup.sh &

rabbitmq-server $@
