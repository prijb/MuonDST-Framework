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

    filename = 'output.root'

    ## Plot histograms
    histo_pt_std = getObject(filename, 'histo_pt_std')
    histo_eta_std = getObject(filename, 'histo_eta_std')
    histo_phi_std = getObject(filename, 'histo_phi_std')

    histo_pt_vtx = getObject(filename, 'histo_pt_vtx')
    histo_eta_vtx = getObject(filename, 'histo_eta_vtx')
    histo_phi_vtx = getObject(filename, 'histo_phi_vtx')

    histo_pt_novtx = getObject(filename, 'histo_pt_novtx')
    histo_eta_novtx = getObject(filename, 'histo_eta_novtx')
    histo_phi_novtx = getObject(filename, 'histo_phi_novtx')

    efficiency_pt_novtx = getObject(filename, 'efficiency_pt_novtx')
    efficiency_pt_std = getObject(filename, 'efficiency_pt_std')

    plotSimple([histo_pt_std, histo_pt_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])
    plotSimple([histo_eta_std, histo_eta_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])
    plotSimple([histo_phi_std, histo_phi_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])

    plotSimpleEfficiency(efficiency_pt_novtx, 'prueba', option = 'AP', extralabel = '')
    plotSimpleEfficiency(efficiency_pt_std, 'prueba', option = 'AP', extralabel = '')

    plotEfficiencyV2('comparisonV5', efficiency_pt_novtx, efficiency_pt_std, 'prueba', 'ROI + Doublet-recovery', 'Default', 'JPsiToMuMu_PT-0to100 - GRun V107', ylog = False, rebin = False)

