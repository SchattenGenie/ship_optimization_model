FROM ubuntu:18.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-dev python3-pip nginx \
    gcc git wget g++ build-essential python3-setuptools && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* && \
    pip3 install wheel && \
    pip3 install uwsgi numpy scipy

RUN cd /root && git clone https://github.com/SchattenGenie/ship_optimization_model.git

WORKDIR /ship_optimization_model
CMD [ "uwsgi", "--ini", "app.ini" ]