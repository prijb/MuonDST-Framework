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

    filename = '/eos/user/f/fernance/DST-Muons/ScoutingOutput_efficiencies_DoubleMuon_all/output_all.root'

    ## Plot histograms
    #probe_pt_denominator_L1_DoubleMu_15_7 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu_15_7')
    #probe_pt_numerator_L1_DoubleMu_15_7 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu_15_7')
    ##
    #efficiency_pt_L1_DoubleMu_15_7 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu_15_7, probe_pt_denominator_L1_DoubleMu_15_7)
    #ttext = r'$p_{T}^{1} > 15$ GeV'
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu_15_7', efficiency_pt_L1_DoubleMu_15_7, 'prueba', 'L1_DoubleMu_15_7', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency', text=ttext)
    ##
    ##
    #probe_pt_denominator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7')
    #probe_pt_numerator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7')
    ##
    #efficiency_pt_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7, probe_pt_denominator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7)
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7', efficiency_pt_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7, 'prueba', 'L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency')
    ##
    ##
    #probe_pt_denominator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6')
    #probe_pt_numerator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6')
    ##
    #efficiency_pt_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6, probe_pt_denominator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6)
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6', efficiency_pt_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6, 'prueba', 'L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency')
    ##
    ##
    #probe_pt_denominator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2')
    #probe_pt_numerator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2')
    ##
    #efficiency_pt_L1_DoubleMu4p5_SQ_OS_dR_Max1p2 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2, probe_pt_denominator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2)
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu4p5_SQ_OS_dR_Max1p2', efficiency_pt_L1_DoubleMu4p5_SQ_OS_dR_Max1p2, 'prueba', 'L1_DoubleMu4p5_SQ_OS_dR_Max1p2', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency')
    ##
    ##
    #probe_pt_denominator_L1_DoubleMu8_SQ = getObject(filename, 'probe_pt_denominator_L1_DoubleMu8_SQ')
    #probe_pt_numerator_L1_DoubleMu8_SQ = getObject(filename, 'probe_pt_numerator_L1_DoubleMu8_SQ')
    ##
    #efficiency_pt_L1_DoubleMu8_SQ = r.TEfficiency(probe_pt_numerator_L1_DoubleMu8_SQ, probe_pt_denominator_L1_DoubleMu8_SQ)
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu8_SQ', efficiency_pt_L1_DoubleMu8_SQ, 'prueba', 'L1_DoubleMu8_SQ', xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency')
    ##
    ##
    #probe_pt_denominator_L1_DoubleMu0_Upt6_IP_Min1_Upt4 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu0_Upt6_IP_Min1_Upt4')
    #probe_pt_numerator_L1_DoubleMu0_Upt6_IP_Min1_Upt4 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu0_Upt6_IP_Min1_Upt4')
    ##
    #efficiency_pt_L1_DoubleMu0_Upt6_IP_Min1_Upt4 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu0_Upt6_IP_Min1_Upt4, probe_pt_denominator_L1_DoubleMu0_Upt6_IP_Min1_Upt4)
    ##
    #plotEfficiencyHEP('efficiency_pt_L1_DoubleMu0_Upt6_IP_Min1_Upt4', efficiency_pt_L1_DoubleMu0_Upt6_IP_Min1_Upt4, 'prueba', 'L1_DoubleMu0_Upt6_IP_Min1_Upt4', xaxis = r'Scouting Vtx muon |d_{xy}| (cm)', yaxis='L1 efficiency')
    #
    #
    probe_pt_denominator_L1_DoubleMu0_Upt6_SQ_er2p0 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu0_Upt6_SQ_er2p0')
    probe_pt_numerator_L1_DoubleMu0_Upt6_SQ_er2p0 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu0_Upt6_SQ_er2p0')
    probe_pt_denominator_L1_DoubleMu0_Upt7_SQ_er2p0 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu0_Upt7_SQ_er2p0')
    probe_pt_numerator_L1_DoubleMu0_Upt7_SQ_er2p0 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu0_Upt7_SQ_er2p0')
    probe_pt_denominator_L1_DoubleMu0_Upt8_SQ_er2p0 = getObject(filename, 'probe_pt_denominator_L1_DoubleMu0_Upt8_SQ_er2p0')
    probe_pt_numerator_L1_DoubleMu0_Upt8_SQ_er2p0 = getObject(filename, 'probe_pt_numerator_L1_DoubleMu0_Upt8_SQ_er2p0')
    #
    efficiency_pt_L1_DoubleMu0_Upt6_SQ_er2p0 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu0_Upt6_SQ_er2p0, probe_pt_denominator_L1_DoubleMu0_Upt6_SQ_er2p0)
    efficiency_pt_L1_DoubleMu0_Upt7_SQ_er2p0 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu0_Upt7_SQ_er2p0, probe_pt_denominator_L1_DoubleMu0_Upt7_SQ_er2p0)
    efficiency_pt_L1_DoubleMu0_Upt8_SQ_er2p0 = r.TEfficiency(probe_pt_numerator_L1_DoubleMu0_Upt8_SQ_er2p0, probe_pt_denominator_L1_DoubleMu0_Upt8_SQ_er2p0)
    #
    plotEfficiencyComparisonHEP('efficiency_pt_L1_DoubleMu0_UptX_SQ_er2p0', [efficiency_pt_L1_DoubleMu0_Upt6_SQ_er2p0, efficiency_pt_L1_DoubleMu0_Upt7_SQ_er2p0, efficiency_pt_L1_DoubleMu0_Upt8_SQ_er2p0], 'prueba', ['L1_DoubleMu0_Upt6_SQ_er2p0', 'L1_DoubleMu0_Upt7_SQ_er2p0', 'L1_DoubleMu0_Upt8_SQ_er2p0'], xaxis = r'Scouting Vtx muon $p_T$ (GeV)', yaxis='L1 efficiency', ratio=False)
    #
    #
    probe_pt_denominator_HLT = getObject(filename, 'probe_pt_denominator_HLT')
    probe_pt_numerator_HLT = getObject(filename, 'probe_pt_numerator_HLT')
    #
    efficiency_pt_HLT = r.TEfficiency(probe_pt_numerator_HLT, probe_pt_denominator_HLT)
    #
    plotEfficiencyHEP('efficiency_pt_HLT', efficiency_pt_HLT, 'prueba', 'DST_PFScouting_DoubleMuon', xaxis = r'Scouting Vtx muon $p_{T}$ (GeV)', yaxis='HLT efficiency')






