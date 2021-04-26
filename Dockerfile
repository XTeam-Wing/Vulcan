FROM ubuntu:18.04

ENV LC_ALL C.UTF-8

RUN mkdir -p /opt/Vulcan
COPY . /opt/Vulcan

# Init
RUN set -x \
    # You may need this if you're in Mainland China
    && sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list \
    ###
    && apt-get update \
    && apt-get install -y python3.7 python3.7-dev python3-pip python3-setuptools \
    wget nmap curl mongodb masscan redis-server vim net-tools git unzip \
    ruby ruby-dev \
    && apt-get -y install libfontconfig libnss3 libgconf-2-4 libnss3-dev

RUN python3.7 -m pip install pip \
    && python3.7 -m pip install --upgrade pip \
    && python3.7 -m pip config set global.index-url 'http://mirrors.aliyun.com/pypi/simple' \
    && pip install pyOpenSSL -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip install pycrypto -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip install cryptography -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    ###

RUN python3.7 -m pip install --upgrade pip
RUN apt-get install -y  libsasl2-dev python-dev libldap2-dev libssl-dev

RUN pip install -r /opt/Vulcan/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com  \
    && chmod +x /opt/Vulcan/migration/docker_init.sh


WORKDIR '/opt/Vulcan'
ENTRYPOINT ["/opt/Vulcan/migration/docker_init.sh"]


EXPOSE 5000
EXPOSE 6000
EXPOSE 53
