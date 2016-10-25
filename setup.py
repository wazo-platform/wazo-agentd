#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-agent',
    version='0.1',
    description='XiVO agent server',
    author='Avencall',
    author_email='dev@proformatique.com',
    url='http://git.xivo.io/',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/xivo-agentd'],
    package_data={
        'xivo_agent.swagger': ['*.yml'],
    }
)
