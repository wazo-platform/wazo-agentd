# xivo-agentd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-agentd)](https://jenkins.wazo.community/job/xivo-agentd)


## Running unit tests

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```

## Docker

The official docker image for this service is `wazopbx/xivo-agentd`.


### Getting the image

To download the latest image from the docker hub

```sh
docker pull wazopbx/xivo-agentd
```


### Running xivo-agentd

```sh
docker run wazopbx/xivo-agentd
```

### Building the image

Building the docker image:

```sh
docker build -t wazopbx/xivo-agentd .
```
