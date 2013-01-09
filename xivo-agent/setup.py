#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo-agent',
    version='0.1',
    description='XiVO agent server and client',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.fr/',
    license='GPLv3',
    packages=['xivo_agent',
              'xivo_agent.ami',
              'xivo_agent.ami.actions',
              'xivo_agent.ami.actions.common',
              'xivo_agent.bin',
              'xivo_agent.ctl',
              'xivo_agent.ctl.commands',
              'xivo_agent.service',
              'xivo_agent.service.steps'],
    scripts=['bin/xivo-agentd',
             'bin/xivo-agentctl'],
)
