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

    filename = '/eos/user/f/fernance/DST-Muons/Reconstruction-studies/HZdZd/v8/output_all.root'
    #filename = '/eos/user/f/fernance/DST-Muons/Reconstruction-studies/BToPhi_MPhi-3p35_ctau-10mm/output_all.root'

    ## Plot histograms
    #histo_pt_std = getObject(filename, 'histo_pt_std')
    #histo_eta_std = getObject(filename, 'histo_eta_std')
    #histo_phi_std = getObject(filename, 'histo_phi_std')
#
    #histo_pt_vtx = getObject(filename, 'histo_pt_vtx')
    #histo_eta_vtx = getObject(filename, 'histo_eta_vtx')
    #histo_phi_vtx = getObject(filename, 'histo_phi_vtx')
#
    #histo_pt_novtx = getObject(filename, 'histo_pt_novtx')
    #histo_eta_novtx = getObject(filename, 'histo_eta_novtx')
    #histo_phi_novtx = getObject(filename, 'histo_phi_novtx')
    histo_lxy_gen = getObject(filename, 'histo_lxy_gen')
 
    histo_pt_comp_isNoVtx = getObject(filename, 'histo_pt_comp_isNoVtx')
    histo_pt_comp_isVtx = getObject(filename, 'histo_pt_comp_isVtx')

    efficiency_pt_novtx = getObject(filename, 'efficiency_pt_novtx')
    efficiency_pt_vtx = getObject(filename, 'efficiency_pt_vtx')
    efficiency_pt_or = getObject(filename, 'efficiency_pt_or')
    efficiency_lxy_novtx = getObject(filename, 'efficiency_lxty_novtx')
    efficiency_lxy_vtx = getObject(filename, 'efficiency_lxy_vtx')
    efficiency_lxy_or = getObject(filename, 'efficiency_lxty_or')

    #plotSimple([histo_pt_std, histo_pt_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])
    #plotSimple([histo_eta_std, histo_eta_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])
    #plotSimple([histo_phi_std, histo_phi_novtx], 'prueba', option = 'HIST', ylog = False, rebin = False, maxDigits = False, extralabel = 'JPsiToMuMu_PT-0to100 - GRun V107', labels = ['Default', 'ROIs + doublet-recovery'])
#
    #plotSimpleEfficiency(efficiency_pt_novtx, 'prueba', option = 'AP', extralabel = '')
    #plotSimpleEfficiency(efficiency_pt_std, 'prueba', option = 'AP', extralabel = '')

    plotHistograms('histo_lxy_gen', [histo_lxy_gen], r'Generated muon $l_{xy}$ (cm)', r'm = 6 GeV, $c\tau =$ 10 mm', False, year=2024, lumi='X', ylog=False, xlog=False, extra = '')
    plotHistogram2D('histo_pt_comp_isNoVtx', histo_pt_comp_isNoVtx, 'Scouting muon (NoVtx)', 'prueba', r'Generated muon $p_T$ (GeV)', r'Reconstructed muon $p_T$ (GeV)', year='2024', lumi='')
    plotHistogram2D('histo_pt_comp_isVtx', histo_pt_comp_isVtx, 'Scouting muon (Vtx)', 'prueba', r'Generated muon $p_T$ (GeV)', r'Reconstructed muon $p_T$ (GeV)', year='2024', lumi='')
    plotEfficiencyComparisonHEP('recoMuonEff_pt', [efficiency_pt_novtx,efficiency_pt_vtx, efficiency_pt_or], 'prueba', ['Scouting muon (NoVtx)', 'Scouting muon (Vtx)', 'Scouting muon (Vtx OR NoVtx)'], xaxis = r'Generated muon $p_T$ (GeV)', yaxis='Reconstruction efficiency')
    plotEfficiencyComparisonHEP('recoMuonEff_lxy', [efficiency_lxy_novtx, efficiency_lxy_vtx, efficiency_lxy_or], 'prueba', ['Scouting muon (NoVtx)', 'Scouting muon (Vtx)', 'Scouting muon (Vtx OR NoVtx)'], xaxis = r'Generated muon $l_{xy}$ (cm)', yaxis='Reconstruction efficiency')
