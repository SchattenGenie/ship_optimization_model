import sys
import numpy as np
sys.path.append("../")

from ship_shield_optimisation.ship.geometry import GeometryManipulator

def test_geo():
    gm = GeometryManipulator()
    geofile = gm.generate_magnet_geofile("test_geo.root", gm.default_magnet_config)
    l, w, tracker_ends = gm.extract_l_and_w(geofile, "full_ship_geo_test.root")
    print(tracker_ends)
    print("L={} cm, W={} kg".format(l, w))

def test_params_striping():
    stripped_length = 42
    gm = GeometryManipulator()
    full_vector = np.random.rand(56)
    stripped_vector = gm.strip_fixed_parameters(full_vector)
    assert len(stripped_vector) == stripped_length
    assert (full_vector[~gm.fixed_params_mask] == full_vector[~gm.fixed_params_mask]).all()

def test_params_imputing():
    stripped_length = 42
    gm = GeometryManipulator()
    stripped_vector = np.random.rand(stripped_length)
    full_vector = gm.input_fixed_params(stripped_vector)
    assert (full_vector[gm.fixed_params_mask] == gm.default_magnet_config[gm.fixed_params_mask]).all()
    assert (full_vector[~gm.fixed_params_mask] == stripped_vector).all()


if __name__ == '__main__':
    test_geo()
    test_params_striping()
    test_params_imputing()