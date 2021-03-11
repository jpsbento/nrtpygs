# rabbitmq server setup for rmqclient testing
FROM rabbitmq:3-management-alpine


# Set the localhost so other services can address
ENV RMQ_HOST localhost

# Set the PIDfile location
# See https://www.rabbitmq.com/relocate.html for other env vars
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

RUN mkdir -p /opt/code/rmq
ADD ./docker/rmq/rmq-setup.sh /opt/code/rmq/
ADD ./docker/rmq/rmq-usersetup.sh /opt/code/rmq/

WORKDIR /etc/rabbitmq

ADD ./docker/rmq/rabbitmq.config /etc/rabbitmq/
ADD ./docker/rmq/rmq-definitions.json /etc/rabbitmq/

RUN chown rabbitmq:rabbitmq /etc/rabbitmq/*

CMD ["/opt/code/rmq/rmq-setup.sh"]
