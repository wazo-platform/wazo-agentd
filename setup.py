#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-agent',
    version='0.1',
    description='XiVO agent server and client',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.io/',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/xivo-agentd',
             'bin/xivo-agentctl'],
)
