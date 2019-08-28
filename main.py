#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from flask import Flask, jsonify
from flask import request as flask_request
from threading import Thread
import config
import run_ship
import json
import uiid

app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    magnet_config = json.loads(flask_request.data)
    job_uiid = str(uuid.uuid4())
    Thread(target=run_ship.run_simulation, kwargs=dict(magnet_config=magnet_config, job_uiid=job_uiid)).start()
    return job_uiid

# TODO: lazy evaluation
@app.route('/retrieve_result', methods=['POST'])
def retrieve_result():
    data = json.loads(flask_request.data)
    result = run_ship.get_result(data['uiid'])
    # if result is None
    # that there are two possible situations
    # calculation is not finished yet
    # or no key!
    return result


def main():
    app.run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
