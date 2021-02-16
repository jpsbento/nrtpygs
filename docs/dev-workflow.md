# Development Workflow Procedures and Tips

The workflow is as follows;

* Clone the repository and create a new development branch (see branch naming)
```shell
git clone https://github.com/newrobotictelescope/rcs-gsi
cd rcs-gsi
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

* Create a pull request either on github or using the github CLI tool;
```
# Create a pull request interactively
~/Projects/my-project$ gh pr create
Creating pull request for feature-branch into main in owner/repo
? Title My new pull request
? Body [(e) to launch nano, enter to skip]
http://github.com/owner/repo/pull/1
~/Projects/my-project$
```

* Create new release to trigger pushing to Dockerhub

Do this on github or with the github CLI. The tag name **MUST** be numeric
only, with decimal places allowed. `1.13` is valid `v1.21` is **not valid**

```
gh release create <tag>
```


## Branch naming
Branch names should indicate if it is a bugfix, feature or enhancement
and use the format below;

```
bugfix/fix-autoconnect
feature/add-telemetry
enhancement/refactor-configuration
```

## Development Tips
The docker-compose.yml file has a couple of items which make development easier

* The `rmq` container maps the RabbitMQ management and service ports to the
local machine. This means that you can run local scripts to communicate with the
rmq server without having to be on the container network. Also the management
web interface is available locally.

* The `gsi` container maps the local `rcsmq/` filesystem into the container.
This means that



## Local Tests


## Commit to Github


## Create a Release
