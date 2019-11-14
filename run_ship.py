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
import docker
from shutil import copy, rmtree
import numpy as np
import config
from redis import Redis
import traceback
import pykube

redis = Redis()
config_k8s = pykube.KubeConfig.from_url(config.K8S_PROXY)
api = pykube.HTTPClient(config_k8s)
api.timeout = 1e6


def status_checker(job):
    active = job['status'].get('active', 0)
    succeeded = job['status'].get('succeeded', 0)
    failed = job['status'].get('failed', 0)
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
    host_dir = '{}/{}'.format(config.CONTAINER_DIRECTORY, input_dir)
    host_dir = os.path.abspath(host_dir)
    host_outer_dir = '{}/{}'.format(config.HOST_DIRECTORY, input_dir)
    os.mkdir(host_dir)

    # save magnet config for ship
    # in host directory
    magnet_config_path = os.path.join(host_dir, "magnet_params.json")
    with open(magnet_config_path, 'w', encoding='utf-8') as f:
        json.dump(magnet_config, f, ensure_ascii=False, indent=4)

    # copy preprocessing file to destination
    copy('./preprocess_root_file.py', host_dir)

    # set container dir
    container_dir = '/root/host_directory'

    num_repetitions = magnet_config.get('num_repetitions', 100)
    result = {
        'uuid': None,
        'container_id': None,
        'container_status': 'starting',
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))
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

    status = 'wait'
    try:
        while status == 'wait':
            time.sleep(10)
            job.reload()
            status = status_checker(job=job)
        if status == 'failed':
            raise(ValueError("JOB FAILED!!!!"))

        muons_momentum_plus = np.load('{0}/output_mu/muons_momentum.npy'.format(host_dir))
        muons_momentum_minus = np.load('{0}/output_antimu/muons_momentum.npy'.format(host_dir))

        veto_points_plus = np.load('{0}/output_mu/veto_points.npy'.format(host_dir))
        veto_points_minus = np.load('{0}/output_antimu/veto_points.npy'.format(host_dir))

        container.reload()
        result = {
            'uuid': job_uuid,
            'container_id': job.obj['metadata']['name'],
            'container_status': job.obj['status'],
            'muons_momentum': np.concatenate([muons_momentum_plus, muons_momentum_minus], axis=0).tolist(),
            'veto_points': np.concatenate([veto_points_plus, veto_points_minus], axis=0).tolist(),
            'message': None
        }
        redis.set(job_uuid, json.dumps(result))

    except Exception as e:
        print(e, traceback.print_exc())
        container.reload()
        result = {
            'uuid': job_uuid,
            'container_id': job.obj['metadata']['name'],
            'container_status': job.obj['status'],
            'muons_momentum': None,
            'veto_points': None,
            'message': traceback.format_exc()
        }
        redis.set(job_uuid, json.dumps(result))
    shutil.rmtree(host_dir)
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
