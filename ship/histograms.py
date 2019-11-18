from array import array
import numpy as np
import ROOT as r
import rootpy.ROOT as r
from rootpy.plotting import Canvas, Hist2D
import os


class HistogramManipulator(object):
    def __init__(self, input_directory="muon_input"):
        self.input_directory = input_directory

    def reweight_histogram_as_oliver(self, input_file, output_file):
        """
        This function will apply the same weightning procedure as described in Oliver thesis.
        :param input_file:
        :param output_file:
        :return:
        """
        input_file = os.path.join(self.input_directory, input_file)
        output_file = os.path.join(self.input_directory, output_file)

        f = r.TFile.Open(input_file, 'read')
        intuple = f.Get('pythia8-Geant4')
        out = r.TFile.Open(output_file, 'recreate')
        outtuple = intuple.CloneTree(0)
        h = Hist2D(100, 0, 350, 100, 0, 6)
        for muon in intuple:
            px = muon.px
            py = muon.py
            pz = muon.pz
            p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
            pt = np.sqrt(px ** 2 + py ** 2)
            b = int(p / 350. * 100) + 1, int(pt / 6. * 100) + 1
            if h[b].value < 100:
                h.Fill(p, pt)
                a = array('f', [y for x in muon.values() for y in x])
                outtuple.Fill(a)
        outtuple.Write()
        del outtuple
        intuple = out.Get('pythia8-Geant4')
        for muon in intuple:
            px = muon.px
            py = muon.py
            pz = muon.pz
            p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
            pt = np.sqrt(px ** 2 + py ** 2)
            b = int(p / 350. * 100) + 1, int(pt / 6. * 100) + 1
            a = array('f', [y for x in muon.values() for y in x])
            if h[b].value < 10:
                n = int(10 / h[b].value)
                for _ in range(n):
                    phi = r.gRandom.Uniform(0., 2.) * r.TMath.Pi()
                    px = pt * r.TMath.Cos(phi)
                    py = pt * r.TMath.Sin(phi)
                    a[1] = px
                    a[2] = py
                    intuple.Fill(a)
            a[1] = + pt
            a[2] = 0
            intuple.Fill(a)
            a[1] = - pt
            a[2] = 0
            intuple.Fill(a)
        # intuple.Write()
        # intuple.create_branches({'seed': 'F'})
        # for muon in intuple:
        #     # print muon.keys()
        #     a = array('f', [y for x in muon.values() for y in x])
        #     muon.seed = hash(sum(a))
        #     intuple.Fill()
        intuple.Write()

    def plot_distribution(self, output_file):
        f = r.TFile.Open(os.path.join(self.input_directory, output_file), 'read')
        intuple = f.Get('pythia8-Geant4')
        h = Hist2D(100, 0, 350, 100, 0, 6)
        for muon in intuple:
            px = muon.px
            py = muon.py
            pz = muon.pz
            p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
            pt = np.sqrt(px ** 2 + py ** 2)
            h.Fill(p, pt)
        c = Canvas()
        r.gStyle.SetOptStat(11111111)
        h.Draw("colz")
        c.Draw()
        c.SaveAs(os.path.join(self.input_directory, "p_dist.png"))