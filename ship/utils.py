# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict
import math
import sys
import ROOT
import os


def check_acceptance(hit, bound=(330, 530)):
    """
    :param hit:
    :param bound: acceptance bounds (X,Y) in cm
    :return:
    """
    return abs(hit.GetX()) <= bound[0] and abs(hit.GetY()) <= bound[1]


def process_file(filename, tracker_ends=None, epsilon=1e-9, debug=True,
                 apply_acceptance_cut=False):
    file = ROOT.TFile(filename)

    tree = file.Get("cbmsim")
    print("Total events:{}".format(tree.GetEntries()))

    MUON = 13
    muons_stats = []
    events_with_more_than_two_hits_per_mc = 0
    empty_hits = "Not implemented"

    for index, event in enumerate(tree):
        if index % 5000 == 0:
            print("N events processed: {}".format(index))
        mc_pdgs = []

        for hit in event.MCTrack:
            mc_pdgs.append(hit.GetPdgCode())

        muon_veto_points = defaultdict(list)
        for hit in event.vetoPoint:
            if hit.GetTrackID() >= 0 and\
               abs(mc_pdgs[hit.GetTrackID()]) == MUON and\
               tracker_ends[0] - epsilon <= hit.GetZ() <= tracker_ends[1] + epsilon:
                if apply_acceptance_cut:
                    if check_acceptance(hit):
                        # Middle or inital stats??
                        pos_begin = ROOT.TVector3()
                        hit.Position(pos_begin)
                        # Extracting only XY coordinates
                        muon_veto_points[hit.GetTrackID()].append([pos_begin.X(), pos_begin.Y()])
                else:
                    pos_begin = ROOT.TVector3()
                    hit.Position(pos_begin)
                    # Extracting only XY coordinates
                    muon_veto_points[hit.GetTrackID()].append([pos_begin.X(), pos_begin.Y()])

        for index, hit in enumerate(event.MCTrack):
            if index in muon_veto_points:
                if debug:
                    print("PDG: {}, mID: {}".format(hit.GetPdgCode(), hit.GetMotherId()))
                    assert abs(hit.GetPdgCode()) == MUON
                muon = [
                    hit.GetPx(),
                    hit.GetPy(),
                    hit.GetPz(),
                    hit.GetStartX(),
                    hit.GetStartY(),
                    hit.GetStartZ(),
                    hit.GetPdgCode()
                ]
                muons_stats.append(muon + muon_veto_points[index][0])
                if len(muon_veto_points[index]) > 1:
                    events_with_more_than_two_hits_per_mc += 1
                    continue

    print("events_with_more_than_two_hits_per_mc: {}".format(events_with_more_than_two_hits_per_mc))
    print("Stopped muons: {}".format(empty_hits))
    print("Total events returned: {}".format(len(muons_stats)))
    return np.array(muons_stats)



if __name__ == "__main__":
    filename = sys.argv[1]
    process_file(filename)
