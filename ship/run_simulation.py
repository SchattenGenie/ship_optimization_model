import json
import numpy as np
import os
from run_ship import SHIPRunner
from geometry import GeometryManipulator
from utils import process_file
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--shield_params", type=str)
parser.add_argument("--n_events", type=int, default=1000)
parser.add_argument("--first_event", type=int, default=0)

def main(shield_params, n_events, first_event):
    """
    Gets vector of optimised shield parameters(not full one), run SHiP simulation
    saves dict of magnet length, weight, optimised_paramteters, input kinematics and output hit distribution
    :return:
    """
    shield_params = np.array([float(x.strip()) for x in shield_params.split(',')], dtype=float)
    # print(shield_params)
    gm = GeometryManipulator()

    geofile = gm.generate_magnet_geofile("magnet_geo.root", list(gm.input_fixed_params(shield_params)))
    ship_runner = SHIPRunner(geofile)
    fair_runner = ship_runner.run_ship(n_events=n_events, first_event=first_event)

    l, w, tracker_ends = gm.extract_l_and_w(geofile, "full_ship_geofile.root", fair_runner)
    muons_stats = process_file(ship_runner.output_file, tracker_ends, apply_acceptance_cut=True, debug=False)
    if len(muons_stats) == 0:
        veto_points, muon_kinematics = np.array([]), np.array([])
    else:
        veto_points = muons_stats[:, -2:]
        muon_kinematics = muons_stats[:, :-2]

    returned_params = {
        "l": l,
        "w": w,
        "params": shield_params.tolist(),
        "kinematics": muon_kinematics.tolist(),
        "veto_points": veto_points.tolist()
    }

    with open(os.path.join(ship_runner.output_dir, "optimise_input.json"), "w") as f:
        json.dump(returned_params, f)



if __name__ == '__main__':
    args = parser.parse_args()
    main(shield_params=args.shield_params, n_events=args.n_events, first_event=args.first_event)