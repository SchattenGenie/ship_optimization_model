#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from flask import Flask, jsonify
from flask import request as flask_request
from threading import Thread
import config
import run_ship
import json
import uuid

app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    magnet_config = json.loads(flask_request.data)
    job_uuid: str = str(uuid.uuid4())
    Thread(target=run_ship.run_simulation, kwargs=dict(magnet_config=magnet_config, job_uuid=job_uuid)).start()
    return job_uuid


@app.route('/retrieve_result', methods=['POST'])
def retrieve_result():
    data = json.loads(flask_request.data)
    result = run_ship.get_result(data['uuid'])
    return result


def main():
    app.run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
