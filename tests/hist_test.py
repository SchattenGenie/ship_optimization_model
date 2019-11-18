import sys
sys.path.append("../")

from ship_shield_optimisation.ship.histograms import HistogramManipulator


def test_hist():
    hm = HistogramManipulator()
    hm.reweight_histogram_as_oliver("pythia8_Geant4-withCharm_onlyMuons_4magTarget.root",
                                    "reweighted_input_test.root")
    hm.plot_distribution("reweighted_input_test.root")

if __name__ == '__main__':
    test_hist()
