FROM python:3.5-stretch
MAINTAINER Wazo Maintainers <dev@wazo.community>

ADD . /usr/src/agentd
ADD ./contribs/docker/certs /usr/share/xivo-certs

WORKDIR /usr/src/agentd

RUN true \
    && adduser --quiet --system --group wazo-agentd \
    && mkdir -p /etc/wazo-agentd/conf.d \
    && install -o wazo-agentd -g wazo-agentd -d /var/run/wazo-agentd \
    && touch /var/log/wazo-agentd.log \
    && chown wazo-agentd:wazo-agentd /var/log/wazo-agentd.log \
    && pip install -r requirements.txt \
    && python setup.py install \
    && cp -r etc/* /etc \
    && apt-get -yqq autoremove \
    && openssl req -x509 -newkey rsa:4096 -keyout /usr/share/xivo-certs/server.key -out /usr/share/xivo-certs/server.crt -nodes -config /usr/share/xivo-certs/openssl.cfg -days 3650 \
    && chown wazo-agentd:wazo-agentd /usr/share/xivo-certs/*

EXPOSE 9493

CMD ["wazo-agentd", "-f"]
