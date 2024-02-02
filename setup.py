#!/usr/bin/env python3
# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)

from setuptools import find_packages, setup

setup(
    name='wazo-agentd',
    version='0.1',
    description='Wazo agentd server',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    package_data={'wazo_agentd.swagger': ['*.yml']},
    entry_points={
        'console_scripts': [
            'wazo-agentd=wazo_agentd.main:main',
            'wazo-agentd-wait=wazo_agentd.wait:main',
        ],
        'wazo_agentd.plugins': [
            'agents = wazo_agentd.plugins.agents.plugin:Plugin',
            'agent = wazo_agentd.plugins.agent.plugin:Plugin',
            'api = wazo_agentd.plugins.api.plugin:Plugin',
            'status = wazo_agentd.plugins.status.plugin:Plugin',
        ],
    },
)
