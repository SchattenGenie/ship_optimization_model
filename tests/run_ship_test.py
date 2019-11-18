import sys
sys.path.append("../")

from ship_shield_optimisation.ship.run_ship import SHIPRunner
from ship_shield_optimisation.ship.geometry import GeometryManipulator


def test_ship():
    gm = GeometryManipulator()
    geofile = gm.generate_magnet_geofile("test_geo.root", gm.default_magnet_config)
    runner = SHIPRunner(geofile)
    runner.run_ship()

if __name__ == '__main__':
    test_ship()