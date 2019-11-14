#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parameters of server
HOST = '0.0.0.0'
PORT = '5432'
K8S_PROXY = 'http://127.0.0.1:8002'
HOST_DIRECTORY = '/mnt/belavin/temp'
CONTAINER_DIRECTORY = '/root/temp'


JOB_SPEC = {
  "apiVersion": "batch/v1",
  "kind": "Job",
  "metadata": {
    "name": "ship-job-{}"
  },
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "ship",
            "image": "vbelavin/ship_simple_model",
            "command": [
              "alienv",
              "setenv",
              "-w",
              "/sw",
              "FairShip/latest",
              "-c",
              "/run_simulation.sh",
              "{}"
            ],
            "volumeMounts": [
              {
                "mountPath": "/root/host_directory",
                "name": "data"
              }
            ]
          }
        ],
        "restartPolicy": "Never",
        "volumes": [
          {
            "name": "data",
            "hostPath": {
              "path": "/mnt/shipfs/{}",
              "type": "Directory"
            }
          }
        ]
      }
    },
    "backoffLimit": 1
  }
}