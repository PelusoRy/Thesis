FROM ubuntu:20.04

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -y install \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \ 
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        libsqlite3-dev \
        libbz2-dev \
        wget \
        nmap \
        pip \
        net-tools \
        iproute2 \
        iputils-ping \
        nano \
        vim \
        openssh-client \
        traceroute \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get purge -y imagemagick imagemagick-6-common 

RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz \
    && tar -xzf Python-3.11.0.tgz \
    && cd Python-3.11.0 \
    && ./configure --enable-optimizations \
    && make altinstall

RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1

RUN pip install nornir nornir-utils nornir-napalm nornir_netmiko

WORKDIR /usr/app/src

COPY /Nornir/Python/. ./

RUN mkdir ~/.ssh

RUN mv config ~/.ssh/
