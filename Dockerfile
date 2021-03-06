FROM ubuntu:18.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-dev python3-pip nginx \
    gcc git wget g++ build-essential python3-setuptools apt-transport-https \
    ca-certificates curl gnupg-agent vim software-properties-common redis-server && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    apt-key fingerprint 0EBFCD88 && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* && \
    pip3 install wheel && \
    pip3 install uwsgi numpy scipy Flask requests docker schema redis

# RUN cd /root
# && git clone https://github.com/SchattenGenie/ship_optimization_model.git
# COPY . /root/ship_shield_optimisation/


USER root
EXPOSE 5432
WORKDIR /ship_shield_optimisation

# CMD [ "uwsgi", "--ini", "app.ini" ]