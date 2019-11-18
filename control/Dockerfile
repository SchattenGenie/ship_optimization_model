FROM ubuntu:18.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-dev python3-pip nginx \
    gcc git wget g++ build-essential python3-setuptools apt-transport-https \
    ca-certificates curl gnupg-agent vim software-properties-common redis-server && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && apt-get install -y kubectl && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* && \
    pip3 install wheel && \
    pip3 install uwsgi numpy scipy Flask requests schema redis pykube


USER root
EXPOSE 5432
WORKDIR /ship_shield_optimisation