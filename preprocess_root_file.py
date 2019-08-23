# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict
import math
import sys
import ROOT
import os


def process_file(filename):
    directory = os.path.dirname(os.path.abspath(filename))
    file = ROOT.TFile(filename)

    tree = file.Get("cbmsim")
    print("Total events:{}".format(tree.GetEntries()))

    MUON = 13
    muons = []
    veto_points = []

    for index, event in enumerate(tree):

        muon = []
        for hit in event.MCTrack:
            if abs(hit.GetPdgCode()) == MUON and hit.GetMotherId() == -1:
                muon.append([
                    hit.GetPx(),
                    hit.GetPy(),
                    hit.GetPz(),
                    hit.GetPdgCode()
                ])

        muon_veto_points = []
        for hit in event.vetoPoint:
            if hit.GetTrackID() == 0 and \
                    -13001 <= hit.GetZ() <= -12998:
                # Middle or inital stats??
                pos_begin = ROOT.TVector3()
                hit.Position(pos_begin)
                muon_veto_points.append([pos_begin.X(), pos_begin.Y(), pos_begin.Z()])
        if len(muon_veto_points) != 1:
            continue
        else:
            muons.extend(muon)
            veto_points.extend(muon_veto_points)

    np.save(os.path.join(directory, "muons_momentum"), np.array(muons))
    np.save(os.path.join(directory, "veto_points"), np.array(veto_points))


if __name__ == "__main__":
    filename = sys.argv[1]
    process_file(filename)
