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
import docker
import uuid
import docker
from shutil import copy, rmtree
import numpy as np
import config
from redis import Redis
import traceback


redis = Redis()
client = docker.from_env()


def create_job(host_dir, container_dir, command):
    container = client.containers.run(
        image='vbelavin/ship_simple_model',
        detach=True,
        command=command,
        volumes={host_dir: {'bind': container_dir, 'mode': 'rw'}}
    )
    return container


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
    command = "alienv setenv -w /sw FairShip/latest -c /run_simulation.sh {}".format(num_repetitions)
    result = {
        'uuid': None,
        'container_id': None,
        'container_status': 'starting',
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))
    container = create_job(host_dir=host_outer_dir, container_dir=container_dir, command=command)
    result = {
        'uuid': job_uuid,
        'container_id': container.id,
        'container_status': container.status,
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))
    try:
        container.wait()

        muons_momentum_plus = np.load('{0}/output_mu/muons_momentum.npy'.format(host_dir))
        muons_momentum_minus = np.load('{0}/output_antimu/muons_momentum.npy'.format(host_dir))

        veto_points_plus = np.load('{0}/output_mu/veto_points.npy'.format(host_dir))
        veto_points_minus = np.load('{0}/output_antimu/veto_points.npy'.format(host_dir))

        container.reload()
        result = {
            'uuid': job_uuid,
            'container_id': container.id,
            'container_status': container.status,
            'muons_momentum': np.concatenate([muons_momentum_plus, muons_momentum_minus], axis=0).tolist(),
            'veto_points': np.concatenate([veto_points_plus, veto_points_minus], axis=0).tolist(),
            'message': None
        }
        redis.set(job_uuid, json.dumps(result))
    except Exception as e:
        container.reload()
        result = {
            'uuid': job_uuid,
            'container_id': container.id,
            'container_status': "failed",
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
