import json
import numpy as np
import os
from run_ship import SHIPRunner
from geometry import GeometryManipulator
from utils import process_file
import argparse
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument("--shield_params", type=str)

def main(shield_params):
    shield_params = np.array([float(x.strip()) for x in shield_params.split(',')], dtype=float)
    print(shield_params)
    gm = GeometryManipulator()

    geofile = gm.generate_magnet_geofile(GEOFILE, list(gm.input_fixed_params(shield_params)))
    # l, w, tracker_ends = gm.extract_l_and_w(geofile, "full_ship_geofile_query.root")
    #
    # returned_params = {
    #     "l": l,
    #     "w": w
    # }
    #
    # ship_runner = SHIPRunner(geofile)
    # with open(os.path.join(ship_runner.output_dir, "query_params.json"), "w") as f:
    #     json.dump(returned_params, f)


if __name__ == '__main__':
    args = parser.parse_args()
    main(shield_params=args.shield_params)
