Dockerfile for XiVO agentd

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-agentd github.com/xivo-pbx/xivo-agentd

Or directly in the sources in contribs/docker

    docker build -t xivo-agentd .
  
## Usage

To run the container, do the following:

    docker run -d -v /conf/agentd:/etc/xivo-agentd/conf.d -p 9493:9493 xivo-agentd

On interactive mode :

    docker run -v /conf/agentd:/etc/xivo-agentd/conf.d -p 9493:9493 -it xivo-agentd bash

After launch xivo-agentd.

    xivo-agentd -f

## Infos

- Using docker version 1.5.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'
