xivo-agentd
===========

[![Build Status](https://travis-ci.org/wazo-pbx/xivo-agentd.png?branch=master)](https://travis-ci.org/wazo-pbx/xivo-agentd)


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```

Running docker
--------------

    docker run -e XIVO_UUID=no-uuid -v $(pwd):/usr/src/agentd -it xivo-agentd bash
