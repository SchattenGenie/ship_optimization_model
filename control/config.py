#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# parameters of server
HOST = '0.0.0.0'
PORT = '5444'
K8S_PROXY = 'http://127.0.0.1:8002'
AZ_DIRECTORY = 'temp'
HOST_DIRECTORY = '/mnt/shipfs/temp'
HOST_MUON_DIRECTORY = '/mnt/shipfs'
FLASK_CONTAINER_DIRECTORY = '/root/temp'
SHIP_CONTAINER_DIRECTORY = '/root/host_directory'
SHIP_MUON_DIRECTORY = '/ship/muon_input'
DATA_FILE = "reweighted_input_test.root"
EVENTS_TOTAL = 485879
TIME_LIMIT = 45.  # time limit per job in minutes

JOB_SPEC = {
  "apiVersion": "batch/v1",
  "kind": "Job",
  "metadata": {
    "name": "ship-job-{}"
  },
  "spec": {
    "ttlSecondsAfterFinished": 14400,
    "template": {
      "spec": {
        "containers": [
          {
            "name": "ship",
            "env": [
              {
                "name": "AZKEY",
                "value": os.environ["AZKEY"],
              }
            ],
            "image": "shir994/fairship:k8s_mount_logs_v4",
            "command": [
              "alienv",
              "setenv",
              "-w",
              "/sw",
              "FairShip/latest",
              "-c",
              "/ship/run_simulation.sh",
            ],
            "resources": {
              "requests": {
                "memory": "1.2Gi",
                "cpu": "1"
              },
              "limits": {
                "memory": "1.2Gi",
                "cpu": "1"
              }
            },
            "volumeMounts": [
            ]
          }
        ],
        "hostNetwork": True,
        "restartPolicy": "Never",
        "volumes": [
        ]
      }
    },
    "backoffLimit": 1
  }
}
