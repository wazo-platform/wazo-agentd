#!/usr/bin/env python3
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-agent',
    version='0.1',
    description='Wazo agent server',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/wazo-agentd'],
    package_data={
        'wazo_agent.swagger': ['*.yml'],
    }
)
