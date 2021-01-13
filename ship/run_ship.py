import os
from time import sleep
import numpy as np
import copy
import json
import argparse
import shutil
import subprocess
import ROOT as r
import shipunit as u
import geomGeant4
from ShipGeoConfig import ConfigRegistry
import shipDet_conf
import saveBasicParameters
from ROOT import TVector3


class SHIPRunner(object):
    def __init__(self, shield_geofile, same_seed=1, file_name="muon_input/pythia8_Geant4_10.0_withCharmandBeauty0_mu.root",
                 step_geo=False, const_field=True):
        self.firstEvent = 0
        self.dy = 10.
        self.vessel_design = 6
        self.shield_design = 8
        self.tau_target_design = 3 #dummy value
        self.mcEngine = 'TGeant4'
        self.same_seed = same_seed
        self.theSeed = 1
        self.geometry_dir = "./shield_files/geometry/"
        self.shield_geo_file = os.path.join(self.geometry_dir, shield_geofile)
        self.output_dir = "./shield_files/outputs/"
        self.output_file = os.path.join(self.output_dir, "ship.conical.MuonBack-TGeant4.root")
        self.input_file = os.path.join("./muon_input", file_name)
        self.step_geo = step_geo
        self.const_field = const_field

    def run_ship(self, phiRandom=False, followMuon=True, n_events=-1, first_event=0):
        """
        phiRandom = False  # only relevant for muon background generator
        followMuon = True  # only transport muons for a fast muon only background
        """
        r.gErrorIgnoreLevel = r.kWarning
        r.gSystem.Load('libpythia8')

        print ('FairShip setup to produce', n_events, 'events')
        r.gRandom.SetSeed(self.theSeed)
        ship_geo = ConfigRegistry.loadpy(
            '$FAIRSHIP/geometry/geometry_config.py',
            Yheight=self.dy,
            tankDesign=self.vessel_design,
            muShieldDesign=self.shield_design,
            muShieldGeo=self.shield_geo_file,
            muShieldStepGeo=self.step_geo,
            nuTauTargetDesign=self.tau_target_design
        )
        ship_geo.muShield.WithConstField = self.const_field
        print("CONST FIELD:{}".format(ship_geo.muShield.WithConstField))
        print("STPEGEO:{}".format(self.step_geo))

        run = r.FairRunSim()
        run.SetName(self.mcEngine)  # Transport engine
        run.SetOutputFile(self.output_file)  # Output file
        # user configuration file default g4Config.C
        run.SetUserConfig('g4Config.C')
        modules = shipDet_conf.configure(run, ship_geo)
        primGen = r.FairPrimaryGenerator()
        primGen.SetTarget(ship_geo.target.z0 + 50 * u.m, 0.)
        MuonBackgen = r.MuonBackGenerator()
        MuonBackgen.Init(self.input_file, first_event, phiRandom)
        MuonBackgen.SetSmearBeam(3 * u.cm)  # beam size mimicking spiral
        if self.same_seed:
            MuonBackgen.SetSameSeed(self.same_seed)
        primGen.AddGenerator(MuonBackgen)
        if not n_events:
            n_events = MuonBackgen.GetNevents()
        else:
            n_events = min(n_events, MuonBackgen.GetNevents())
        print ('Process ', n_events, ' from input file, with Phi random=', phiRandom)
        if followMuon:
            modules['Veto'].SetFastMuon()
        run.SetGenerator(primGen)
        run.SetStoreTraj(r.kFALSE)
        run.Init()
        print ('Initialised run.')
        # geomGeant4.setMagnetField()
        if hasattr(ship_geo.Bfield, "fieldMap"):
            fieldMaker = geomGeant4.addVMCFields(ship_geo, '', True)
        fieldMaker.plotField(1, TVector3(-7000.0, -3000.0, 10.0), TVector3(-300.0, 300.0, 6.0), os.path.join(self.output_dir, 'Bzx.png'))
        fieldMaker.plotField(2, TVector3(-7000.0, -3000.0, 10.0), TVector3(-400.0, 400.0, 6.0), os.path.join(self.output_dir, 'Bzy.png'))
        print ('Start run of {} events.'.format(n_events))
        run.Run(n_events)
        print ('Finished simulation of {} events.'.format(n_events))

        geofile_output_path = os.path.join(self.output_dir,
                                           "geofile_full.fe_{}_n_events_{}.root" .format(first_event, n_events))
        run.CreateGeometryFile(geofile_output_path)
        # save ShipGeo dictionary in geofile
        saveBasicParameters.execute(geofile_output_path, ship_geo)
        return run


if __name__ == '__main__':
    ship_runner = SHIPRunner()
    ship_runner.run_ship(n_events=1000)
