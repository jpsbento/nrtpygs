# rabbitmq server setup for rcsmq testing
FROM rabbitmq:3-management-alpine


# Set the localhost so other services can address
ENV RMQ_HOST localhost

# Set the PIDfile location
# See https://www.rabbitmq.com/relocate.html for other env vars
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

RUN mkdir -p /opt/code/rmq
ADD ./docker/rmq/rmq-setup.sh /opt/code/rmq/
ADD ./docker/rmq/rmq-usersetup.sh /opt/code/rmq/

CMD ["/opt/code/rmq/rmq-setup.sh"]
