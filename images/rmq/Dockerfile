# rabbitmq server setup for rmqclient testing
FROM rabbitmq:3-management-alpine


# Set the localhost so other services can address
ENV RMQ_HOST localhost

# Set the PIDfile location
# See https://www.rabbitmq.com/relocate.html for other env vars
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

RUN mkdir -p /opt/code/rmq
ADD ./images/rmq/rmq-setup.sh \
 ./images/rmq/rmq-usersetup.sh /opt/code/rmq/
 
ADD --chown=rabbitmq:rabbitmq ./images/rmq/rabbitmq.config \
 ./images/rmq/rmq-definitions.json /etc/rabbitmq/

CMD ["/opt/code/rmq/rmq-setup.sh"]
