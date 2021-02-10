![Pylint](https://github.com/NewRoboticTelescope/rcs-gsi/workflows/Pylint/badge.svg) ![CI Testing](https://github.com/NewRoboticTelescope/rcs-gsi/workflows/CI%20Testing/badge.svg)

# rcs-gsi
Repository for the Robotic Control System - Generic Services Image repository.

This repository contains;
* rcsmq library for communications with RabbitMQ
* Dockerfiles and scripts for setting up containers for testing
* A docker-compose file for bringing up a test system


## Requirements
* docker
* docker-compose


## Usage
A `secrets.env` file needs to be created and stored in the top level of the dircetory. This needs to contain 4 environment variables as shown below, which setup up a RCS MQ (RMQ) user and password and also a Admin (ADM) user and password which can login to the rabbitmq management interface.

```
RMQ_USER=rcs
RMQ_PASS=rcs-password
ADM_USER=rcsadmin
ADM_PASS=rcsadmin-password
```

### Starting the system for the first time
To start the systems the user needs to run (in the project root directory).
To bring in detached mode add the -d flag;

```shell
docker-compose up -d
```

This should build and bring up 3 services;
* gsi - will will exit immediately. Only required to create image.
* rmq - which will set up the users
* test-service - which inherits the gsi image and loads the tests

The rabbitmq server has the ports mapped locally for testing to localhost.
The management interface can be accessed in a webrowser
(i.e. http://127.0.0.1:15672/)

The services in the test system can however communicate using friendly names
within their own default bridge newtork. The rabbitmq host is addressed using
an `RMQ_HOST` environment variable specified in `environment.env`.

With the RabbitMQ connection port mapped `5672:5672`, test services can also
be run locally connecting to the RabbitMQ server without having to be within
the docker bridge network.

### Stopping / Restarting / Bringing Down the system
This will stop the containers
```shell
docker-compose stop
```

This will Restart the conatiners
```shell
docker-compose start
```

This will stop and remove the conatiners
```shell
docker-compose down
```

### Rebuilding the system
After making any changes to code (rcsmq and tests), you will need to rebuild
the containers. This can be done with the following commands.

```shell
docker-compose down
docker-compose build
docker-compose up -d
```
or with the single command;
```shell
docker-compose up --build -d
```

**NOTE** Due to caching, this should only take a couple of seconds as only
changes to the code in the docker files needs to be made. Downloading of all
dependencies and their configuration does not need to be repeated.
