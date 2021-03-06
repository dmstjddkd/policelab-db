FROM ubuntu:18.04

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV UID 1000
ENV GID 1000

ADD . /opt/policelab-server
WORKDIR /opt/policelab-server

RUN groupadd -g $GID policelab-server && useradd -u $UID -g policelab-server policelab-server

RUN apt update && \
	apt install -y python3 python3-pip supervisor && \
	rm -rf /var/lib/apt/lists/* && \
	pip3 --no-cache-dir install pipenv

RUN pipenv install --system --deploy

ENTRYPOINT supervisord -n -c /etc/supervisor/supervisord.conf
