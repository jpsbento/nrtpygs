# Development Workflow Procedures and Tips

## Prerequisites
Your system must have docker and docker-compose installed.

In addition python3 with Flake8 or other linting tools.

The Github CLI is also usefull to perform github actions. It can be installed
on Ubuntu systems with the following commands;

```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
sudo apt-add-repository https://cli.github.com/packages
sudo apt update
sudo apt install gh
```
Instructions for the gh CLI can be found here;
https://cli.github.com/manual/index


## Development Tips
The docker-compose.yml file has a couple of items which make development easier

* The `rmq` container maps the RabbitMQ management and service ports to the
local machine. This means that you can run local scripts to communicate with
the `rmq` server without having to be on the container network. Also the
management web interface is available locally.

* The `gsi` container maps the local `rmqclient/` filesystem into the container.
This means that any code changes to the `rmqclient/` folder do not require
rebuilding of the gsi container, just that it is rerun (or maybe not even!)

* To test locally you will need the secrets.env and environment.env variables
loaded in your shell (**note**, BASH shell is assumed). To acheive
this you can use the following commands;
```shell
export $(grep -v '^#' secret.env | xargs)
export $(grep -v '^#' environment.env | xargs)
```

* You may have to overwrite hostnames however, as they use 'friendly'
names inside the docker network which is not available to the host system.
In particular the rmq ports are mapped to the localhost so you need to do,
```shell
export RMQ_HOST=127.0.0.1
```


## Branch naming
Branch names should indicate if it is a bugfix, feature or enhancement
and use the format below;

```
bugfix/fix-autoconnect
feature/add-telemetry
enhancement/refactor-configuration
```

## Development Workflow
The workflow is as follows;

### Creating a new branch
* Clone the repository and create a new development branch (see branch naming)
```shell
git clone https://github.com/newrobotictelescope/rcs-gsi
cd rcs-gsi
cp testsecret.env secret.env
git checkout -b <branch-name>
```

* Develop and Test frequently using the `gsi` image with pytest entrypoint
```shell
docker-compose up gsi
```
* Commit and Push frequently
```shell
git push origin <branch-name>
```

When ready to create a pull request or merge to main;

* Run the flake8 linter and correct issues until it passes.
```shell
pip install flake8
flake8
```

* Make sure the local tests pass
```shell
docker-compose up gsi
```

* Make a final commit and push
```shell
git add .
git commit -m "<Commit message"
git push origin <branch-name>
```

### Creating a pull request

* Create a pull request either on github or using the github CLI tool;
```
# Create a pull request interactively
$> ~/Projects/my-project$ gh pr create
Creating pull request for feature-branch into main in owner/repo
? Title My new pull request
? Body [(e) to launch nano, enter to skip]
http://github.com/owner/repo/pull/1
~/Projects/my-project$
```

* At this point you can revert back to the main branch and update to the latest
version. Then you're set to rebranch the next feature, bugfix or enhancement!
Alternatively, you can remove the whole rcs-gsi folder and reclone if required.
```shell
git checkout main
git pull origin main
```

* To tidy up you can also delete the local branch (as it will be removed on the
remote once merged anyway)

```shell
git branch --delete <branch-name>
```

### Authorising a pull request and merging
The following steps should be performed by an **authorised person only**;

* Check all CI/CD tests have passed
* Make sure any conflicts are resolved
* Resolve the pull request by merging onto the main branch

```shell
gh pr list
gh pr merge [<number> | <branch>]
```

**NOTE** choose to delete the branch once the pull request has been approved
and it has been merged onto the main development branch. If not selected you can
delete on github website or can do it locally using git;

```shell
git push origin --delete <branch-name>
```
See more info here
https://www.freecodecamp.org/news/how-to-delete-a-git-branch-both-locally-and-remotely/

** The above happen in loops until a release needs to be made **


* Create new release to trigger pushing to Dockerhub
Do this on github or with the github CLI. The tag name **MUST** be numeric
only, with decimal places allowed. `1.13` is valid `v1.21` is **not valid**
```shell
gh release create <tag>
```

* Check on Dockerhub that the release has worked!
