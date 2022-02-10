# rmq Specific Usage

The following are notes on the 4mnrt/rmq implementation and some usages for
development, testing and debugging locally

## Server settings
This is currently specified in a definitions.json file

## Log file locations
To look at logs from rmq in realtime use;
```
docker logs --follow rmq
```

## Login 
To login to the system go to http://127.0.0.1:15672/ and use the username 
and password in the secrets.env file.