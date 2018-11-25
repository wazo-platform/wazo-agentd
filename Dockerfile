FROM python:3.5-stretch
MAINTAINER Wazo Maintainers <dev@wazo.community>

ADD . /usr/src/agentd
ADD ./contribs/docker/certs /usr/share/xivo-certs

WORKDIR /usr/src/agentd

RUN true \
    && adduser --quiet --system --group xivo-agentd \
    && mkdir -p /etc/xivo-agentd/conf.d \
    && install -o xivo-agentd -g xivo-agentd -d /var/run/xivo-agentd \
    && touch /var/log/xivo-agentd.log \
    && chown xivo-agentd:xivo-agentd /var/log/xivo-agentd.log \
    && pip install -r requirements.txt \
    && python setup.py install \
    && cp -r etc/* /etc \
    && apt-get -yqq autoremove \
    && openssl req -x509 -newkey rsa:4096 -keyout /usr/share/xivo-certs/server.key -out /usr/share/xivo-certs/server.crt -nodes -config /usr/share/xivo-certs/openssl.cfg -days 3650

EXPOSE 9493

CMD ["xivo-agentd", "-f"]
