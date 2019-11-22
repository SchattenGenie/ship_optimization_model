#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from flask import Flask, jsonify
from flask import request as flask_request
from threading import Thread
import config
import run_job
import json
import uuid

app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    parameters = json.loads(flask_request.data)
    magnet_config = parameters["shape"]
    n_jobs = parameters.get("n_jobs", 6)
    job_uuid: str = str(uuid.uuid4())

    Thread(target=run_job.run_simulation, kwargs=dict(
        magnet_config=magnet_config,
        job_uuid=job_uuid,
        n_jobs=n_jobs
    )
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
