## Image to build from sources

FROM debian:wheezy
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
ADD . /usr/src/agentd
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/src/agentd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-agentd.log
RUN mkdir -p /etc/xivo-agentd
RUN mkdir /var/lib/xivo-agentd
RUN cp -r etc/* /etc
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /usr/src/agentd

EXPOSE 9493

CMD xivo-agentd -f 
