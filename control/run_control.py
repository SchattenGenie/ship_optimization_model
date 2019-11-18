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


redis = Redis()
config_k8s = pykube.KubeConfig.from_url(config.K8S_PROXY)
api = pykube.HTTPClient(config_k8s)
api.timeout = 1e6


def extract_file_from_container(container, path, local_filename, remote_full_path):
    f = open(os.path.join(path, local_filename + '.tar'), 'wb')
    bits, stat = container.get_archive(remote_full_path)
    for chunk in bits:
        f.write(chunk)
    f.close()
    tar = tarfile.open(os.path.join(path, local_filename + '.tar'))
    for member in tar.getmembers():
        f = tar.extractfile(member)
        content = f.read()
    return content.decode()



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


def run_simulation(magnet_config, job_uuid):
    # make random directory for ship docker
    # to store input files and output files
    input_dir = 'input_dir_{}'.format(job_uuid)
    flask_host_dir = '{}/{}'.format(config.FLASK_CONTAINER_DIRECTORY, input_dir)
    flask_host_dir = os.path.abspath(flask_host_dir)
    host_outer_dir = '{}/{}'.format(config.HOST_DIRECTORY, input_dir)
    print(os.mkdir(flask_host_dir))

    # save magnet config for ship
    # in host directory
    magnet_config_path = os.path.join(flask_host_dir, "magnet_params.json")
    with open(magnet_config_path, 'w', encoding='utf-8') as f:
        json.dump(magnet_config, f, ensure_ascii=False, indent=4)

    # copy preprocessing file to destination
    copy('./preprocess_root_file.py', flask_host_dir)

    result = {
        'uuid': None,
        'container_id': None,
        'container_status': 'starting',
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))

    JOB_SPEC = deepcopy(config.JOB_SPEC)

    # JOB_SPEC["spec"]["containers"][0]["volumeMounts"][0]["mountPath"] = SHIP_CONTAINER_DIRECTORY
    JOB_SPEC["spec"]["template"]["spec"]["volumes"][0]["hostPath"]["path"] = host_outer_dir
    JOB_SPEC["metadata"]["name"] = "ship-job-{}".format(job_uuid)

    job = pykube.Job(api, json.dumps(JOB_SPEC))
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

    status = 'wait'
    try:
        while status == 'wait':
            time.sleep(10)
            job.reload()
            status = status_checker(job=job)
        if status == 'failed':
            raise(ValueError("JOB FAILED!!!!"))

        optimise_input = json.loads(extract_file_from_container(container, host_dir,
                                                                "optimise_input",
                                                                "/ship/shield_files/outputs/optimise_input.json"))

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
    shutil.rmtree(flask_host_dir)
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
