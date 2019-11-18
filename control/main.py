#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from flask import Flask, jsonify
from flask import request as flask_request
from threading import Thread
import config
from control import run_job
import json
import uuid

app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    parameters = json.loads(flask_request.data)
    magnet_config = parameters["shape"]
    requested_num_events = parameters["n_events"]
    requested_num_events = min(requested_num_events, config.EVENTS_TOTAL)
    job_uuid: str = str(uuid.uuid4())
    n_events_per_job = requested_num_events #  // config.N_JOBS

    Thread(target=run_job.run_simulation, kwargs=dict(
        magnet_config=magnet_config,
        job_uuid=job_uuid,
        n_events=n_events_per_job,
        first_event=0)
           ).start()
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
