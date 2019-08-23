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


client = docker.from_env()


def create_job(host_dir, container_dir, command="/bin/sh -c 'head -1 input.txt > output.txt'"):
    container = client.containers.run(
        image='vbelavin/ship_simple_model',
        privileged=True,
        remove=False,
        detach=False,
        tty=True,
        command=command,
        stdin_open=True,
        stderr=True,
        volumes={container_dir: {'bind': host_dir, 'mode': 'rw'}}
    )
    return container


def run_simulation(magnet_config):
    # make random directory for ship docker
    # to store input files and output files
    host_dir = './input_dir_{}'.format(str(uuid.uuid4()))
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
    magnet_config_path_container = os.path.join(container_dir, 'magnet_conig.json')

    """# run docker
    command = [
        # setup env
        # "alienv enter -w /sw FairShip/latest",
        # copy magnet config
        "cp {} $FAIRSHIP/diff-model".format(magnet_config_path_container),
        # run with muon
        "python $FAIRSHIP/macro/run_simScript.py --PG --pID 13 -n 100 --Estart 1 --Eend 10 --FastMuon -o {}/output_mu".format(
            container_dir),
        # run with anti muon
        "python $FAIRSHIP/macro/run_simScript.py --PG --pID -13 -n 100 --Estart 1 --Eend 10 --FastMuon -o {}/output_antimu".format(
            container_dir),
        # run preprocessing
        "python {0}/preprocess_root_file.py {0}/output_mu/ship.conical.PG_13-TGeant4.root".format(container_dir),
        "python {0}/preprocess_root_file.py {0}/output_mu/ship.conical.PG_13-TGeant4.root".format(container_dir)
    ]"""

    # command = " && ".join(command)
    create_job(host_dir=host_dir, container_dir=container_dir)

    muons_momentum_plus = np.load('{0}/output_mu/muons_momentum.npy'.format(host_dir))
    muons_momentum_minus = np.load('{0}/output_antimu/muons_momentum.npy'.format(host_dir))

    veto_points_plus = np.load('{0}/output_mu/veto_points.npy'.format(host_dir))
    veto_points_minus = np.load('{0}/output_antimu/veto_points.npy'.format(host_dir))

    result = {
        'muons_momentum': np.contacenate([muons_momentum_plus, muons_momentum_minus], axis=0),
        'veto_points': np.contacenate([veto_points_plus, veto_points_minus], axis=0)
    }
    return result
