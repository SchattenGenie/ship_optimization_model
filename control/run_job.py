# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys
import subprocess
import shutil
import json
import hashlib
from collections import defaultdict
import time
import requests
import uuid
from shutil import copy, rmtree
import numpy as np
from redis import Redis
import traceback
import pykube
from copy import deepcopy
from control import config
import datetime
from dateutil import parser, tz

#config_k8s = pykube.KubeConfig.from_url(config.K8S_PROXY)
config_k8s = pykube.KubeConfig.from_file(config.K8S_CONFIG)
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


# def job_status(jobs_status):
#     if 'failed' in jobs_status:
#         return 'failed'
#     elif all([status == 'succeeded' for status in jobs_status]):
#         return 'exited'
#     return 'wait'

# Consider job successful if at least one portion was calculated
def job_status(jobs_status):
    if "succeeded" in jobs_status:
        return 'exited'
    elif 'failed' in jobs_status:
        return 'failed'
    return 'wait'


def run_simulation(magnet_config, job_uuid, n_jobs, n_events, input_file, const_field):
    # make random directory for ship docker
    # to store input files and output files
    input_dir = 'input_dir_{}'.format(job_uuid)
    flask_host_dir = '{}/{}'.format(config.FLASK_CONTAINER_DIRECTORY, input_dir)
    flask_host_dir = os.path.abspath(flask_host_dir)
    # host_outer_dir = '{}/{}'.format(config.HOST_DIRECTORY, input_dir)
    az_outer_dir = '{}/{}'.format(config.AZ_DIRECTORY, input_dir)
    os.mkdir(flask_host_dir)
    sys.stdout = open(os.path.join(flask_host_dir, "out.txt"), "w", buffering=1)
    sys.stderr = open(os.path.join(flask_host_dir, "err.txt"), "w", buffering=1)

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

    job_spec_config_file = os.path.join(flask_host_dir, "job_spec.json")
    jobs = []
    uuids = []

    N_EVENTS = config.EVENTS_TOTAL if n_events is None else min(n_events, config.EVENTS_TOTAL)
    chunk_size = N_EVENTS // n_jobs
    for part_number in range(n_jobs):
        start_event_num = chunk_size * part_number
        if part_number + 1 == n_jobs:
            chunk_size += N_EVENTS % n_jobs - 1
        JOB_SPEC = deepcopy(config.JOB_SPEC)
        flask_host_dir_part = '{}/part_{}'.format(flask_host_dir, part_number)
        az_outer_dir_part = '{}/part_{}'.format(az_outer_dir, part_number)
        os.mkdir(flask_host_dir_part)
        magnet_config_path_part = os.path.join(flask_host_dir_part, "magnet_params.json")
        with open(magnet_config_path_part, 'w', encoding='utf-8') as f:
            json.dump(magnet_config, f, ensure_ascii=False, indent=4)
        per_job_uuid = "{}-{}".format(job_uuid, part_number)
        JOB_SPEC["metadata"]["name"] = "ship-job-{}".format(per_job_uuid)
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(",".join(map(str, magnet_config)))
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(str(chunk_size))
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(str(start_event_num))
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(input_file)
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(str(config.STEP_GEO))
        JOB_SPEC["spec"]["template"]["spec"]["containers"][0]["command"].append(az_outer_dir_part)
        # print(JOB_SPEC)
        job_spec_config_file = os.path.join(flask_host_dir_part, "job_spec.json")
        with open(job_spec_config_file, 'w', encoding='utf-8') as f:
            json.dump(JOB_SPEC, f, ensure_ascii=False, indent=4)
        job = pykube.Job(api, JOB_SPEC)
        job.create()
        jobs.append(job)
        uuids.append(per_job_uuid)

    result = {
        'uuid': uuids,
        'container_id': [job.obj['metadata']['name'] for job in jobs],
        'container_status': job_status([status_checker(job) for job in jobs]),
        'message': None
    }
    redis.set(job_uuid, json.dumps(result))
    time.sleep(1.)
    [job.reload() for job in jobs]
    print(os.listdir(flask_host_dir))
    finished = False
    print([job.obj for job in jobs])
    start_time = time.time()
    failed_jobs = set()
    try:
        while not finished:
            statuses = []
            time.sleep(10)
            for index, job in enumerate(jobs):
                if index in failed_jobs:
                    statuses.append('failed')
                    continue
                status = 'wait'
                try:
                    job.reload()
                    status = status_checker(job=job)
                    if status == "succeeded":
                        print("JOB: {} finished".format(index))
                    elif status == "wait":
                        job_start_time = parser.parse(job.obj["metadata"]["creationTimestamp"])
                        dt = (datetime.datetime.now(tz.tzlocal()) - job_start_time).seconds / 60
                        print("JOB: {}, DT {}:".format(index, dt))
                        if dt > config.TIME_LIMIT:
                            status = "failed"
                            print("TIME LIMIT per job exceeded, deleting: {}".format(job.obj['metadata']['name']))
                            job.delete()
                            failed_jobs.add(index)
                except requests.exceptions.HTTPError as e:
                    # except only internet errors
                    print(e, traceback.print_exc())
                statuses.append(status)
            if 'wait' in statuses:
                finished = False
            else:
                finished = True
        time.sleep(20)
        # print(os.listdir(flask_host_dir))


        # collect data from succesfully finished jobs
        optimise_inputs = []
        for part_number, job in enumerate(jobs):
            if part_number in failed_jobs:
                continue
            with open('{}/{}'.format("{}/part_{}".format(flask_host_dir, part_number), 'job_status.json'), 'w') as j:
                json.dump(job.obj, j)
            if status_checker(job=job) == 'succeeded' and \
               os.path.exists('{}/{}'.format("{}/part_{}".format(flask_host_dir, part_number), 'optimise_input.json')):
                with open('{}/{}'.format("{}/part_{}".format(flask_host_dir, part_number), 'optimise_input.json'), 'r') as j:
                    optimise_input = json.loads(j.read())
                optimise_inputs.append(optimise_input)

        kinematics = sum([optimise_input["kinematics"] for optimise_input in optimise_inputs], [])
        params = [optimise_input["params"] for optimise_input in optimise_inputs]
        params = params[0] if params else None
        veto_points = sum([optimise_input["veto_points"] for optimise_input in optimise_inputs], [])
        l = [optimise_input["l"] for optimise_input in optimise_inputs]
        l = l[0] if l else None
        w = [optimise_input["w"] for optimise_input in optimise_inputs]
        w = w[0] if w else None

        status = job_status([status_checker(job) for job in jobs])
        if not optimise_inputs:
            status = "failed"
        result = {
            'uuid': uuids,
            'container_id': [job.obj['metadata']['name'] for job in jobs],
            'container_status': status,
            'kinematics': kinematics,
            "params": params,
            "veto_points": veto_points,
            "l": l,
            "w": w,
            'message': None
        }
        redis.set(job_uuid, json.dumps(result))

    except Exception as e:
        print(e, traceback.print_exc())
        result = {
            'uuid': uuids,
            'container_id': [job.obj['metadata']['name'] for job in jobs],
            'container_status': 'failed',
            'muons_momentum': None,
            'veto_points': None,
            'message': traceback.format_exc()
        }
        redis.set(job_uuid, json.dumps(result))
    # shutil.rmtree(flask_host_dir)
    # print(os.listdir(flask_host_dir))
    return result


def get_result(job_uuid):
    result = redis.get(job_uuid)
    if result is None:
        return {
            'uuid': None,
            'container_id': None,
            'container_status': 'wait',
            'muons_momentum': None,
            'veto_points': None
        }
    result = json.loads(result)
    return result
