#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import request as flask_request
# from threading import Thread
from multiprocessing import Process
from control import run_job
from control import config
import json
import uuid

app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    parameters = json.loads(flask_request.data)
    magnet_config = parameters["shape"]
    n_jobs = parameters.get("n_jobs", 6)
    n_events = parameters.get("n_events", None)
    input_file = parameters.get("input_file")
    const_field = parameters.get("const_field")
    job_uuid: str = str(uuid.uuid4())

    Process(target=run_job.run_simulation, kwargs=dict(
        magnet_config=magnet_config,
        job_uuid=job_uuid,
        n_jobs=n_jobs,
        n_events=n_events,
        input_file=input_file,
        const_field=const_field)
    ).start()
    return job_uuid


@app.route('/retrieve_result', methods=['POST'])
def retrieve_result():
    data = json.loads(flask_request.data)
    result = run_job.get_result(data['uuid'])
    return result


def main():
    app.run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
