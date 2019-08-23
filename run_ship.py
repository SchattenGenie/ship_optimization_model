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

client = docker.from_env()


def create_job(host_dir, container_dir, command):
    container = client.containers.run(
        image='vbelavin/ship_simple_model',
        remove=False,
        detach=False,
        command=command,
        tty=True,
        stdin_open=True,
        stderr=True,
        volumes={container_dir: {'bind': host_dir, 'mode': 'rw'}}
    )
    return container


def run_simulation(magnet_config):
    # make random directory for ship docker
    # to store input files and output files
    host_dir = '{}/input_dir_{}'.format(config.HOST_DIRECTORY, str(uuid.uuid4()))
    host_dir = os.path.abspath(host_dir)
    os.mkdir(host_dir)

    # save magnet config for ship
    # in host directory
    magnet_config_path = os.path.join(host_dir, 'magnet_conig.json')
    with open(magnet_config_path, 'w', encoding='utf-8') as f:
        json.dump(magnet_config, f, ensure_ascii=False, indent=4)

    # copy preprocessing file to destination
    copy('./preprocess_root_file.py', host_dir)

    # set container dir
    container_dir = '/root/host_directory'

    # command = "/bin/sh -c run_simulation.sh".format(host_dir)
    # create_job(host_dir=host_dir, container_dir=container_dir)
    process = subprocess.Popen([
        "docker", "run", "-v",
        "{}:{}:rw".format(host_dir, container_dir),
        "vbelavin/ship_simple_model"
    ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in process.stdout:
        print(line)
    process.wait()

    muons_momentum_plus = np.load('{0}/output_mu/muons_momentum.npy'.format(host_dir))
    muons_momentum_minus = np.load('{0}/output_antimu/muons_momentum.npy'.format(host_dir))

    veto_points_plus = np.load('{0}/output_mu/veto_points.npy'.format(host_dir))
    veto_points_minus = np.load('{0}/output_antimu/veto_points.npy'.format(host_dir))

    result = {
        'muons_momentum': np.contacenate([muons_momentum_plus, muons_momentum_minus], axis=0),
        'veto_points': np.contacenate([veto_points_plus, veto_points_minus], axis=0)
    }

    return result
