from array import array
import ROOT as r
import os
from ShipGeoConfig import ConfigRegistry
import shipDet_conf
import numpy as np


class GeometryManipulator(object):
    def __init__(self, geometry_dir="shield_files/geometry/"):
        self.geometry_dir = geometry_dir
        self.default_magnet_config = np.array([70.0, 170.0, 208.0, 207.0, 281.0, 248.0, 305.0,
        242.0, 40.0, 40.0, 150.0, 150.0, 2.0, 2.0, 80.0, 80.0, 150.0, 150.0, 2.0, 2.0,
        72.0, 51.0, 29.0, 46.0, 10.0, 7.0, 54.0, 38.0, 46.0, 192.0, 14.0, 9.0, 10.0,
        31.0, 35.0, 31.0, 51.0, 11.0, 3.0, 32.0, 54.0, 24.0, 8.0, 8.0, 22.0, 32.0,
        209.0, 35.0, 8.0, 13.0, 33.0, 77.0, 85.0, 241.0, 9.0, 26.0])

        self.fixed_ranges = [(0, 2), (8, 20)]
        mask = [index for interval in self.fixed_ranges for index in range(*interval)]
        self.fixed_params_mask = np.zeros(len(self.default_magnet_config), dtype=bool)
        self.fixed_params_mask[mask] = True

    def strip_fixed_parameters(self, magnet_parameters):
        return np.array(magnet_parameters)[~ self.fixed_params_mask]

    def input_fixed_params(self, magnet_parameters):
        full_parameters = np.zeros(len(self.default_magnet_config))
        full_parameters[self.fixed_params_mask] = self.default_magnet_config[self.fixed_params_mask]
        full_parameters[~self.fixed_params_mask] = magnet_parameters
        return full_parameters

    def generate_magnet_geofile(self, geofile, params):
        f = r.TFile.Open(os.path.join(self.geometry_dir, geofile), 'recreate')
        parray = r.TVectorD(len(params), array('d', params))
        parray.Write('params')
        f.Close()
        print('Geofile constructed at ' + os.path.join(self.geometry_dir, geofile))
        return geofile

    def get_magnet_mass(self, muonShield):
        """Calculate magnet weight [kg]
        Assumes magnets contained in `MuonShieldArea` TGeoVolumeAssembly and
        contain `Magn` in their name. Calculation is done analytically by
        the TGeoVolume class.
        """
        nodes = muonShield.GetNodes()
        m = 0.
        for node in nodes:
            volume = node.GetVolume()
            if 'Mag' in volume.GetName():
                m += volume.Weight(0.01, 'a')
        return m

    def get_magnet_length(self, muonShield):
        """Ask TGeoShapeAssembly for magnet length [cm]
        Note: Ignores one of the gaps before or after the magnet
        Also note: TGeoShapeAssembly::GetDZ() returns a half-length
        """
        length = 2 * muonShield.GetShape().GetDZ()
        return length

    def get_tracker_position(self, sensitive_plane):
            pass
            #print(dir(node))
            #return node.GetZ(), node.GetDZ()


    def extract_l_and_w(self, magnet_geofile, full_geometry_file, run=None):
        if not run:
            ship_geo = ConfigRegistry.loadpy(
                '$FAIRSHIP/geometry/geometry_config.py',
                Yheight=10,
                tankDesign=5,
                muShieldDesign=8,
                muShieldGeo=os.path.join(self.geometry_dir, magnet_geofile))

            print
            'Config created with ' + os.path.join(self.geometry_dir, magnet_geofile)

            outFile = r.TMemFile('output', 'create')
            run = r.FairRunSim()
            run.SetName('TGeant4')
            run.SetOutputFile(outFile)
            run.SetUserConfig('g4Config.C')
            shipDet_conf.configure(run, ship_geo)
            run.Init()
        run.CreateGeometryFile(os.path.join(self.geometry_dir, full_geometry_file))
        sGeo = r.gGeoManager
        muonShield = sGeo.GetVolume('MuonShieldArea')
        L = self.get_magnet_length(muonShield)
        W = self.get_magnet_mass(muonShield)
        g = r.TFile.Open(os.path.join(self.geometry_dir, magnet_geofile), 'read')
        params = g.Get("params")
        f = r.TFile.Open(os.path.join(self.geometry_dir, full_geometry_file), 'update')
        f.cd()
        length = r.TVectorD(1, array('d', [L]))
        length.Write('length')
        weight = r.TVectorD(1, array('d', [W]))
        weight.Write('weight')
        params.Write("params")

        # Extract coordinates of senstive plane
        nav = r.gGeoManager.GetCurrentNavigator()
        nav.cd("sentsitive_tracker_1")
        tmp = nav.GetCurrentNode().GetVolume().GetShape()
        o = [tmp.GetOrigin()[0], tmp.GetOrigin()[1], tmp.GetOrigin()[2]]
        local = array('d', o)
        globOrigin = array('d', [0, 0, 0])
        nav.LocalToMaster(local, globOrigin)

        sensitive_plane = sGeo.GetVolume('sentsitive_tracker')

        left_end, right_end = globOrigin[2] - sensitive_plane.GetShape().GetDZ(),\
                              globOrigin[2] + sensitive_plane.GetShape().GetDZ()
        return L, W, (left_end, right_end)

    def create_context(self, f_name='magnet_geo_tmp.root'):
        magnet_geofile = self.generate_magnet_geofile(f_name, self.default_magnet_config)
        ship_geo = ConfigRegistry.loadpy(
            '$FAIRSHIP/geometry/geometry_config.py',
            Yheight=10,
            tankDesign=5,
            muShieldDesign=8,
            muShieldGeo=os.path.join(self.geometry_dir, magnet_geofile))

        print
        'Config created with ' + os.path.join(self.geometry_dir, magnet_geofile)

        outFile = r.TMemFile('output', 'create')
        run = r.FairRunSim()
        run.SetName('TGeant4')
        run.SetOutputFile(outFile)
        run.SetUserConfig('g4Config.C')
        shipDet_conf.configure(run, ship_geo)
        run.Init()
        return run

    def query_params(self, params):
        magnet_geofile = self.generate_magnet_geofile("query_geo.root", params)
        ship_geo = ConfigRegistry.loadpy(
            '$FAIRSHIP/geometry/geometry_config.py',
            Yheight=10,
            tankDesign=5,
            muShieldDesign=8,
            muShieldGeo=os.path.join(self.geometry_dir, magnet_geofile))
        #shipDet_conf.configure(run, ship_geo)

        outFile = r.TMemFile('output', 'create')
        run = r.FairRunSim()
        run.SetName('TGeant4')
        run.SetOutputFile(outFile)
        run.SetUserConfig('g4Config.C')
        shipDet_conf.configure(run, ship_geo)
        run.Init()
        sGeo = r.gGeoManager
        muonShield = sGeo.GetVolume('MuonShieldArea')
        L = self.get_magnet_length(muonShield)
        W = self.get_magnet_mass(muonShield)
        return L, W