## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    git \
    apt-utils \
    python-pip \
    python-dev \
    libpq-dev \
    libyaml-dev

# Install xivo-agentd
WORKDIR /usr/src
ADD . /usr/src/agentd
WORKDIR agentd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-agentd.log
RUN mkdir -p /etc/xivo-agentd
RUN mkdir /var/lib/xivo-agentd
RUN cp -a etc/xivo-agentd/* /etc/xivo-agentd/
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /usr/src/agentd

CMD xivo-agentd -f 
