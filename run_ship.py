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
from shutil import copy
import numpy as np
import config
from redis import Redis


redis = Redis()
client = docker.from_env()


def create_job(host_dir, container_dir, command):
    container = client.containers.run(
        image='vbelavin/ship_simple_model',
        detach=True,
        command=command,
        volumes={container_dir: {'bind': host_dir, 'mode': 'rw'}}
    )
    return container


def run_simulation(magnet_config, job_uiid):
    # make random directory for ship docker
    # to store input files and output files
    input_dir = 'input_dir_{}'.format(job_uiid)
    host_dir = '{}/{}'.format(config.CONTAINER_DIRECTORY, input_dir)
    host_dir = os.path.abspath(host_dir)
    host_outer_dir = '{}/{}'.format(config.HOST_DIRECTORY, input_dir)
    os.mkdir(host_dir)

    # save magnet config for ship
    # in host directory
    magnet_config_path = os.path.join(host_dir, 'magnet_config.json')
    with open(magnet_config_path, 'w', encoding='utf-8') as f:
        json.dump(magnet_config, f, ensure_ascii=False, indent=4)

    # copy preprocessing file to destination
    copy('./preprocess_root_file.py', host_dir)

    # set container dir
    container_dir = '/root/host_directory'

    # TODO: use python docker sdk
    num_repetitions = 1000
    command = "alienv setenv -w /sw FairShip/latest -c /run_simulation.sh {}".format(num_repetitions)
    container = create_job(host_dir=host_dir, container_dir=container_dir, command=command)
    result = {
        'uiid': job_uiid,
        'container_id': container.id,
        'container_status': container.status
    }

    redis.hmset(job_uiid, result)
    container.wait()

    muons_momentum_plus = np.load('{0}/output_mu/muons_momentum.npy'.format(host_dir))
    muons_momentum_minus = np.load('{0}/output_antimu/muons_momentum.npy'.format(host_dir))

    veto_points_plus = np.load('{0}/output_mu/veto_points.npy'.format(host_dir))
    veto_points_minus = np.load('{0}/output_antimu/veto_points.npy'.format(host_dir))

    container.reload()
    result = {
        'uiid': job_uiid,
        'container_id': container.id,
        'container_status': container.status,
        'muons_momentum': np.concatenate([muons_momentum_plus, muons_momentum_minus], axis=0).tolist(),
        'veto_points': np.concatenate([veto_points_plus, veto_points_minus], axis=0).tolist()
    }
    redis.hmset(job_uiid, result)
    return result


def get_result(job_uiid):
    result = redis.hgetall(job_uiid)
    if result is None:
        return 'No key'
    if result['container_status'] == 'exited':
        return result
    else:
        container = client.get(result['container_id'])
        container.reload()
        return container.status