#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parameters of server
HOST = '0.0.0.0'
PORT = '5433'
K8S_PROXY = 'http://127.0.0.1:8002'
HOST_DIRECTORY = '/mnt/shipfs/temp'
HOST_MUON_DIRECTORY = '/mnt/shipfs'
FLASK_CONTAINER_DIRECTORY = '/root/temp'
SHIP_CONTAINER_DIRECTORY = '/root/host_directory'
SHIP_MUON_DIRECTORY = '/ship/muon_input'

EVENTS_TOTAL = 485879
N_JOBS = 1

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
            "image": "vbelavin/ship_full",
            "command": [
              "alienv",
              "setenv",
              "-w",
              "/sw",
              "FairShip/latest",
              "-c",
              "/ship/run_simulation.sh",
            ],
            "volumeMounts": [
              {
                "mountPath": SHIP_CONTAINER_DIRECTORY,
                "name": "data"
              },
              {
                "mountPath": SHIP_MUON_DIRECTORY,
                "name": "muon"
              }
            ]
          }
        ],
        "restartPolicy": "Never",
        "volumes": [
          {
            "name": "data",
            "hostPath": {
              "path": "{}/{}",
              "type": "Directory"
            }
          },
          {
            "name": "muon",
            "hostPath": {
              "path": HOST_MUON_DIRECTORY,
              "type": "Directory"
            }
          }
        ]
      }
    },
    "backoffLimit": 1
  }
}
