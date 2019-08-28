#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from flask import Flask, jsonify
from flask import request as flask_request
import config
import run_ship
import json


app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def simulate():
    magnet_config = json.loads(flask_request.data)
    result = run_ship.run_simulation(magnet_config)
    return result

# TODO: lazy evaluation
@app.route('/retrieve_result', methods=['POST'])
def retrieve_result():
    data = json.loads(flask_request.data)
    result = get_result(data['uiid'])
    # if result is None
    # that there are two possible situations
    # calculation is not finished yet
    # or no key!
    return result


def main():
    app.run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
