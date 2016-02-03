xivo-agentd
===========

[![Build Status](https://travis-ci.org/xivo-pbx/xivo-agentd.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-agentd)


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```


Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
