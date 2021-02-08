FROM alpine:3.13 AS compile-image

# Add requirements for python and pip
RUN apk add --update python3

RUN mkdir -p /opt/code
WORKDIR /opt/code

# Install dependencies
RUN apk add python3-dev build-base gcc linux-headers postgresql-dev libffi-dev

# Create a virtual environment for all the Python dependencies
RUN python3 -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --upgrade pip

# Install other dependencies
COPY rcsmq/requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt


########
# This image is the runtime, will copy the dependencies from the other
########
FROM alpine:3.13 AS runtime-image

# Install python
RUN apk add --update python3

RUN mkdir -p /opt/


# Create a user to run the service
RUN addgroup -S rcs
RUN adduser -H -D -S rcs
USER rcs

# Copy the venv with compile dependencies from the compile-image
COPY --chown=rcs:rcs --from=compile-image /opt/venv /opt/venv
# Be sure to activate the venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the code
COPY --chown=rcs:rcs rcsmq/ /opt/code/
