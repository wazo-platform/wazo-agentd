# wazo-agentd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-agentd)](https://jenkins.wazo.community/job/wazo-agentd)

## Running unit tests

```sh
apt-get install libpq-dev python3-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py3
```

## Docker

The official docker image for this service is `wazopbx/wazo-agentd`.

### Getting the image

To download the latest image from the docker hub

```sh
docker pull wazopbx/wazo-agentd
```

### Running wazo-agentd

```sh
docker run wazopbx/wazo-agentd
```

### Building the image

Building the docker image:

```sh
docker build -t wazopbx/wazo-agentd .
```
