#!/usr/bin/env python3
# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-agentd',
    version='0.1',
    description='Wazo agentd server',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    package_data={'wazo_agentd.swagger': ['*.yml']},
    entry_points={
        'console_scripts': [
            'wazo-agentd=wazo_agentd.main:main',
            'wazo-agentd-wait=wazo_agentd.wait:main',
        ],
    },
)
