![Flake8](https://github.com/NewRoboticTelescope/rcs-gsi/workflows/Flake8/badge.svg) ![CI Testing](https://github.com/NewRoboticTelescope/rcs-gsi/workflows/CI%20Testing/badge.svg) ![Docker Version](https://img.shields.io/docker/v/4mnrt/gsi?label=Docker%20Version&style=plastic) ![Docker Image Size](https://img.shields.io/docker/image-size/4mnrt/gsi?label=Docker%20image%20size&style=plastic)

# rcs-gsi
Repository for the Robotic Control System - Generic Services Image

This repository contains;
* The RabbitMQ definition and setup for the RCS containerised middleware -rmq
* Code for rcsmq - The python Library for RCS services to communicate with rmq
* Docker file to create the Genric Services Image which is used for RCS
servcies - gsi


## Requirements
* docker
* docker-compose


## Usage
A `secrets.env` file needs to be created and stored in the top level of the
directory. This contains the usernames and passwords for servcies to
communicate with the rabbitmq server. This file is never tracked and should not
be uploaded to github.
For interagtion testing a testsecrets.env is used, so you will need to;

```shell
cp testsecrets.env secrets.env
```

### Starting rmq

This will start rmq (RCS message queue) server in detatched mode.

```shell
docker-compose up -d rmq
```

The rabbitmq server has the ports mapped locally for testing to localhost.
The management interface can be accessed in a webrowser
(i.e. http://127.0.0.1:15672/)

The services in the test system can however communicate using friendly names
within their own default bridge newtork. The rabbitmq host is addressed using
an `RMQ_HOST` environment variable specified in `environment.env`.

With the RabbitMQ connection port mapped `5672:5672`, test services can also
be run locally connecting to the RabbitMQ server without having to be within
the docker bridge network.

### Starting gsi

gsi is specified in the docker compose file to start with a pytest entrypoint.
This means the container is run once. This will run pytest on the `opt/code/`
directory, without creating any pytest cache files. Infact this is set up in the
`docker-compose.yml` to map the local `rcsmq` directory to `opt/code/`. This means
that code can be modified locally and tested in the container without requiring
rebuild.

```
docker-compose up gsi
```

This command can actually be run on it's own without bringing up rmq, as gsi
depends on rmq in the `docker-compose.yml`

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
After making any changes to anything in the `docker` folder, you will need to
rebuild the containers for this to take effect. This can be done with the
following commands.

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

## Modifying Rabbitmq settings
rmq is setup via `docker-compose.yml`, using the files in `docker/rmq/`. Here
there are shell scripts to set up the users. In addition, all settings of the
rmq server can be specified in `rabbitmq.config` (general server settings)
and `rmq-definitions.json` (exchange / binding / queue settings).
See the following for more info - https://www.rabbitmq.com/configure.html

If these settings are changed you need to rebuild the container images.


## Workflows
There are 3 workflows in operation and stored in [.github/workflows/](.githubworkflows)
* primary-workflow.yml - main testing workflow running pytest on gsi
* flake8.yml - python linter for rcsmq
* publish.yml - triggered on release action to push gsi to dockerhub

See [docs/workflows.md](docs/workflows.md) for more info.
