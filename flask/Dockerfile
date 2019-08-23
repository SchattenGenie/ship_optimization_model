FROM ubuntu:18.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-dev python3-pip nginx \
    gcc git wget g++ build-essential python3-setuptools apt-transport-https \
    ca-certificates curl gnupg-agent vim software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    apt-key fingerprint 0EBFCD88 && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* && \
    pip3 install wheel && \
    pip3 install uwsgi numpy scipy Flask requests docker schema

RUN cd /root && git clone https://github.com/SchattenGenie/ship_optimization_model.git

USER root
EXPOSE 6432
EXPOSE 54432
WORKDIR /root/ship_optimization_model

CMD [ "uwsgi", "--ini", "app.ini" ]