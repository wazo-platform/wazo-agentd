xivo-agentd
===========

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-agentd)](https://jenkins.wazo.community/job/xivo-agentd)


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```
