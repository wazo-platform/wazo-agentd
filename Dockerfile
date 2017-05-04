FROM debian:jessie

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

ADD . /usr/src/agentd
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/src/agentd

RUN apt-get -qq update \
    && apt-get -qq -y install \
                      git \
                      apt-utils \
                      python-pip \
                      python-dev \
                      libpq-dev \
                      libyaml-dev

RUN true \
    && pip install -r requirements.txt \
    && python setup.py install \
    && touch /var/log/xivo-agentd.log \
    && mkdir -p /etc/xivo-agentd/conf.d \
    && mkdir /var/lib/xivo-agentd \
    && mkdir /var/run/xivo-agentd \
    && cp -r etc/* /etc \
    && apt-get clean \

EXPOSE 9493

CMD ["xivo-agentd", "-f"]
