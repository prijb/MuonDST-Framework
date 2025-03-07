import ROOT as r
from ROOT import gDirectory, gROOT, gStyle, gPad
import optparse
import os
from include.plotTools import *

if __name__ == "__main__":

    r.gROOT.LoadMacro('include/tdrstyle.C')
    r.gROOT.SetBatch(1)
    r.setTDRStyle()
    r.gStyle.SetPadRightMargin(0.12)

    filename = '/eos/user/f/fernance/DST-Muons/ScoutingOutput_efficiencies/output_0.root'

    ## Plot histograms
    den_probe_pt = getObject(filename, 'probe_pt_denominator')
    num_probe_pt = getObject(filename, 'probe_pt_numerator')

    efficiency_pt_L1_SingleMu11_SQ14_BMTF = r.TEfficiency(num_probe_pt, den_probe_pt)

    plotEfficiencyHEP('efficiency_pt_L1_SingleMu11_SQ14_BMTF', efficiency_pt_L1_SingleMu11_SQ14_BMTF, 'prueba', 'L1_SingleMu11_SQ14_BMTF', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency')