# wazo-agentd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-agentd)](https://jenkins.wazo.community/job/wazo-agentd)

## Running unit tests

```sh
apt-get install libpq-dev python3-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py311
```

## Docker

The official docker image for this service is `wazoplatform/wazo-agentd`.

### Getting the image

To download the latest image from the docker hub

```sh
docker pull wazoplatform/wazo-agentd
```

### Running wazo-agentd

```sh
docker run wazoplatform/wazo-agentd
```

### Building the image

Building the docker image:

```sh
docker build -t wazoplatform/wazo-agentd .
```

## Development

Processing is split among the following steps, in order:

* HTTP request
* HTTP parser: `http.py`
* Service Proxy (exposes all available operations, calls handler): `service/proxy.py`
* Service Handler (adapts query to manager operations, calls manager): `service/handler/*.py`
* Service manager (validation, triggers action): `service/manager/*.py`
* Service action (updates DB, sends messages and events): `service/action/*.py`
