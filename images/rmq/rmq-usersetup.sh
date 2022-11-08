#!/bin/sh

# Create Rabbitmq user



# Wait for server to start then stop it after configuring users

rabbitmqctl wait --timeout 60 $RABBITMQ_PID_FILE
rabbitmqctl delete_user guest
rabbitmqctl add_user $RMQ_USER $RMQ_PASS 2>/dev/null
rabbitmqctl set_permissions -p / $RMQ_USER  ".*" ".*" ".*"
rabbitmqctl add_user $ADM_USER $ADM_PASS 2>/dev/null
rabbitmqctl set_user_tags $ADM_USER administrator
rabbitmqctl set_permissions -p / $ADM_USER  ".*" ".*" ".*"
echo "*** User '$RMQ_USER' with password '$RMQ_PASS' completed. ***"
echo "*** Admin User '$ADM_USER' with password '$ADM_PASS' completed. ***"
