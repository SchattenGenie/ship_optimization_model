# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import subprocess
import shutil
import json
import hashlib
from collections import defaultdict
import time
import requests
import config
import uuid
from shutil import copy, rmtree
import numpy as np
import config
from redis import Redis
import traceback
import pykube
from copy import deepcopy

config_k8s = pykube.KubeConfig.from_url(config.K8S_PROXY)
api = pykube.HTTPClient(config_k8s)
api.timeout = 1e6
redis = Redis()


def status_checker(job):
    active = job.obj['status'].get('active', 0)
    succeeded = job.obj['status'].get('succeeded', 0)
    failed = job.obj['status'].get('failed', 0)
    if succeeded:
        return 'succeeded'
    elif active:
        return 'wait'
    elif failed:
        return 'failed'
    return 'wait'


def run_simulation(magnet_config, job_uuid, n_events, first_event):
    # make random directory for ship docker
    # to store input files and output files
    input_dir = 'input_dir_{}'.format(job_uuid)
    flask_host_dir = '{}/{}'.format(config.FLASK_CONTAINER_DIRECTORY, input_dir)
    flask_host_dir = os.path.abspath(flask_host_dir)
    host_outer_dir = '{}/{}'.format(config.HOST_DIRECTORY, input_dir)
    os.mkdir(flask_host_dir)

    # save magnet config for ship
    # in host directory
    magnet_config_path = os.path.join(flask_host_dir, "magnet_params.json")
    with open(magnet_config_path, 'w', encoding='utf-8') as f:
        json.dump(magnet_config, f, ensure_ascii=False, indent=4)
    result = {
        'uuid': None,
        'container_id': None,
        'container_status': 'starting',
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))

    JOB_SPEC = deepcopy(config.JOB_SPEC)
    job_spec_config_file = os.path.join(flask_host_dir, "job_spec.json")
    # JOB_SPEC["spec"]["containers"][0]["volumeMounts"][0]["mountPath"] = SHIP_CONTAINER_DIRECTORY
    print(host_outer_dir)
    JOB_SPEC["spec"]["template"]["spec"]["volumes"][0]["hostPath"]["path"] = host_outer_dir
    JOB_SPEC["metadata"]["name"] = "ship-job-{}".format(job_uuid)
    JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(",".join(map(str, magnet_config)))
    JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(str(n_events))
    JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(str(0))
    print(JOB_SPEC)
    with open(job_spec_config_file, 'w', encoding='utf-8') as f:
        json.dump(JOB_SPEC, f, ensure_ascii=False, indent=4)
    job = pykube.Job(api, JOB_SPEC)
    job.create()

    result = {
        'uuid': job_uuid,
        'container_id': job.obj['metadata']['name'],
        'container_status': job.obj['status'],
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))
    time.sleep(1.)
    job.reload()
    print(os.listdir(flask_host_dir))
    status = 'wait'
    try:
        while status == 'wait':
            time.sleep(10)
            job.reload()
            status = status_checker(job=job)
        if status == 'failed':
            raise(ValueError("JOB FAILED!!!!"))

        print(job.obj)
        time.sleep(60)
        print(os.listdir(flask_host_dir))
        with open('{}/{}'.format(flask_host_dir, 'optimise_input.json'), 'r') as j:
            optimise_input = json.loads(j.read())

        result = {
            'uuid': job_uuid,
            'container_id': job.obj['metadata']['name'],
            'container_status': job.obj['status'],
            'kinematics': optimise_input["kinematics"],
            "params": optimise_input["params"],
            "veto_points": optimise_input["veto_points"],
            "l": optimise_input["l"],
            "w": optimise_input["w"],
            'message': None
        }
        redis.set(job_uuid, json.dumps(result))

    except Exception as e:
        print(e, traceback.print_exc())
        result = {
            'uuid': job_uuid,
            'container_id': job.obj['metadata']['name'],
            'container_status': job.obj['status'],
            'muons_momentum': None,
            'veto_points': None,
            'message': traceback.format_exc()
        }
        redis.set(job_uuid, json.dumps(result))
    # shutil.rmtree(flask_host_dir)
    print(os.listdir(flask_host_dir))
    return result


def get_result(job_uuid):
    result = redis.get(job_uuid)
    if result is None:
        return {
            'uuid': None,
            'container_id': None,
            'container_status': 'failed',
            'muons_momentum': None,
            'veto_points': None
        }
    result = json.loads(result)
    return result
