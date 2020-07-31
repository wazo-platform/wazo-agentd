FROM python:3.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN python -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY . /usr/src/agentd
WORKDIR /usr/src/agentd
RUN pip install -r requirements.txt
RUN python setup.py install

FROM python:3.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-agentd /etc/wazo-agentd
RUN true \
    && adduser --quiet --system --group wazo-agentd \
    && mkdir -p /etc/wazo-agentd/conf.d \
    && install -o wazo-agentd -g wazo-agentd /dev/null /var/log/wazo-agentd.log

EXPOSE 9493

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-agentd"]
