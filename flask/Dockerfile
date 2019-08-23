FROM ubuntu:18.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-dev python3-pip nginx git wget && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* && \
    pip3 install uwsgi numpy scipy &&
    git clone git@github.com:SchattenGenie/ship_optimization_model.git

WORKDIR /root/ship_optimization_model
CMD [ "uwsgi", "--ini", "app.ini" ]