import ROOT as r
import numpy as np
import optparse
from include.plotTools import *
import __main__
import mplhep as hep
import matplotlib.pyplot as plt
import time
from include.helper import helper

PWD = ''
for _p,path in enumerate(os.path.abspath(__main__.__file__).split('/')):
       if _p == len(os.path.abspath(__main__.__file__).split('/')) - 1: break
       PWD += path + '/'
print(PWD)

r.gROOT.LoadMacro(PWD+'include/tdrstyle.C')
r.gROOT.LoadMacro(PWD+'libraries/muon_scouting_run3.C')
r.gROOT.SetBatch(1)
r.setTDRStyle()
hep.style.use("CMS")

### Configuration
display = False
onlyDPNote = True

print("Number of operating threads:", r.ROOT.GetThreadPoolSize())
if not display:
    r.EnableImplicitMT()
print("Number of operating threads after enabled:", r.ROOT.GetThreadPoolSize())

### Plotting functions

def getValues(histo):
    values = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
    return np.array(values)

def plotHistograms(name, histos, var, bins, labels, isstack, ylog=False, xlog=False):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h in histos:
        hs.append(getValues(h))
    fig, ax = plt.subplots(figsize=(12, 9))
    htype = 'fill' if isstack else 'step'
    hep.histplot(
        hs,
        bins=bins,
        histtype=htype,
        color=colors[:len(hs)],
#        alpha=0.8,
        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax,
    )
    hep.cms.label("Preliminary", data=True, year='2024D', lumi='X', com='13.6')
    ax.set_xlabel(histos[0].GetXaxis().GetTitle(), fontsize=20)
    ax.set_ylabel("Events", fontsize=20)
    if ylog:
        ax.set_yscale('log')
        ax.set_ylim(0.1, 100*max([max(x) for x in hs]))
    if xlog:
        ax.set_xscale('log')
    ax.set_xlim(bins[0], bins[-1])
    legsize = 15 if len(labels)<7 else 10
    ax.legend(fontsize=15)
    fig.savefig(name+".png", dpi=140)
    

if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog [opts] FilenameWithSamples', version='%prog 1.0')
    parser.add_option('--inDir', action='store', type=str,  dest='inDir', default='Total', help='Input dir')
    parser.add_option('--hlt', action='store', type=str,  dest='hlt', default='all', help='HLT path for denominator')
    parser.add_option('--redirector', action='store', type=str,  dest='redirector', default='root://xrootd-cms.infn.it', help='Redirector to use to access the samples')
    parser.add_option('-s', '--step', action='store', type=int,  dest='step', default=0, help='Step file')
    parser.add_option('-n', '--number', action='store', type=int,  dest='number', default=0, help='Number of files for given step')
    (opts, args) = parser.parse_args()

    ## Running parameters
    inputdir = opts.inDir
    step = opts.step
    number = opts.number
    hlt = opts.hlt
    redirector = opts.redirector # root://cmsxrootd.fnal.gov | root://hip-cms-se.csc.fi | root://xrootd-cms.infn.it
    central = True
    
    ## Load samples
    #inputdir = '/eos/user/f/fernance/DST-Muons/2024E_dimuon/ScoutingPFRun3/2024E_dimuon/240610_213819' # 2024D
    print('Reading from ', inputdir)
    print('Redirector ', redirector)
    nfiles = 0
    files = []
    if redirector:
        print('Going to use helper.py')
        help = helper(inputdir, central, redirector)
        files = help.getFiles(step, number)
    else:
        tchain = r.TChain('Events')
        for root, dirs, files in os.walk(inputdir):
            for f in files:
                if '.root' in f:
                    print(root, f)
                    print(os.path.join(root, f))
                    files.append(os.path.join(root, f))
                    nfiles += 1
                    if nfiles > 5: break
    nfiles == len(files)

    ## Load dataframe
    print(files)
    rdf = r.RDataFrame("Events", files)
    print(f'Init RDataFrame with {rdf.Count().GetValue()} entries in files from {step*number} to {step*number + number}')
    

    ## DST path selection
    print(f' > Denominator is: %s'%(hlt))
    if hlt == 'all':
        rdf = rdf.Filter("(DST_PFScouting_ZeroBias == 1 || DST_PFScouting_DoubleEG == 1 || DST_PFScouting_JetHT == 1)")
    else:
        rdf = rdf.Filter("(%s == 1)"%hlt)
    print(f' > RDataFrame with {rdf.Count().GetValue()} entries after DST filtering')

    ## Histogram container and definitions
    histos = []
    #
    mbins = [0.215]
    while (mbins[-1]<250):
        mbins.append(1.01*mbins[-1])
    pt_bins = np.linspace(0, 50, 101)
    sigdxy_bins = np.linspace(0, 5, 20)
    eta_bins = np.linspace(-3, 3, 51)
    phi_bins = np.linspace(-3.14, 3.14, 51)
    mass_jpsi_bins = np.linspace(2.8, 3.4, 101)
    #

    ## Pre-filter the events to have exactly 2 muons
    rdf = rdf.Filter("nScoutingMuonVtx == 2")
    rdf = rdf.Filter("ScoutingMuonVtx_charge[0]*ScoutingMuonVtx_charge[1] < 0")
    print(f' > RDataFrame with {rdf.Count().GetValue()} entries after 2 muon filtering')

    ## Definitions
    print('Setting definitions for tag and probe...')

    # tag : leading, probe : subleading 
    tagDef = "(ScoutingMuonVtx_pt[0] > ScoutingMuonVtx_pt[1]) ? ScoutingMuonVtx_{0}[0] : ScoutingMuonVtx_{0}[1]"
    probeDef = "(ScoutingMuonVtx_pt[0] > ScoutingMuonVtx_pt[1]) ? ScoutingMuonVtx_{0}[1] : ScoutingMuonVtx_{0}[0]"

    vars = ["pt", "eta", "phi", "trk_dxy", "trk_dxyError"]

    for var in vars:
        rdf = rdf.Define("tag_{0}".format(var), tagDef.format(var))
        rdf = rdf.Define("probe_{0}".format(var), probeDef.format(var))
    rdf = rdf.Define("tnp_mass", "(ROOT::Math::PtEtaPhiMVector(tag_pt, tag_eta, tag_phi, 0.105658) + ROOT::Math::PtEtaPhiMVector(probe_pt, probe_eta, probe_phi, 0.105658)).M()")
    rdf = rdf.Define("tnp_dR", "ROOT::Math::VectorUtil::DeltaR(ROOT::Math::PtEtaPhiMVector(tag_pt, tag_eta, tag_phi, 0.105658), ROOT::Math::PtEtaPhiMVector(probe_pt, probe_eta, probe_phi, 0.105658))")
    #rdf = rdf.Define("tag_dxysig", "abs(tag_trk_dxy/tag_trk_dxyError)")
    rdf = rdf.Define("tag_absdxy", "abs(tag_trk_dxy)")

    print('Definitions set')

    # L1_DoubleMu_15_7
    if not onlyDPNote:
        rdf_den_L1_DoubleMu_15_7 = rdf.Filter("tag_pt > 15")
        rdf_num_L1_DoubleMu_15_7 = rdf_den_L1_DoubleMu_15_7.Filter("L1_DoubleMu_15_7")
        histos.append(rdf_den_L1_DoubleMu_15_7.Histo1D(("probe_pt_denominator_L1_DoubleMu_15_7", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num_L1_DoubleMu_15_7.Histo1D(("probe_pt_numerator_L1_DoubleMu_15_7", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        print(f' > Efficiencies done for L1_DoubleMu_15_7')

    # L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7
    if not onlyDPNote:
        rdf_den_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 = rdf.Filter("tnp_mass > 7.0 && abs(tag_eta) < 2.0 && abs(probe_eta) < 2.0")
        rdf_num_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 = rdf_den_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7.Filter("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7")
        histos.append(rdf_den_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7.Histo1D(("probe_pt_denominator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7.Histo1D(("probe_pt_numerator_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        print(f' > Efficiencies done for L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7')
    
    # L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6
    if not onlyDPNote:
        rdf_den_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 = rdf.Filter("abs(tag_eta) < 2.0 && abs(probe_eta) < 2.0")
        rdf_num_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 = rdf_den_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6.Filter("L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6")
        histos.append(rdf_den_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6.Histo1D(("probe_pt_denominator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6.Histo1D(("probe_pt_numerator_L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        print(f' > Efficiencies done for L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6')
    
    # L1_DoubleMu4p5_SQ_OS_dR_Max1p2
    if not onlyDPNote:
        rdf_den_L1_DoubleMu4p5_SQ_OS_dR_Max1p2 = rdf
        rdf_num_L1_DoubleMu4p5_SQ_OS_dR_Max1p2 = rdf_den_L1_DoubleMu4p5_SQ_OS_dR_Max1p2.Filter("L1_DoubleMu4p5_SQ_OS_dR_Max1p2")
        histos.append(rdf_den_L1_DoubleMu4p5_SQ_OS_dR_Max1p2.Histo1D(("probe_pt_denominator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num_L1_DoubleMu4p5_SQ_OS_dR_Max1p2.Histo1D(("probe_pt_numerator_L1_DoubleMu4p5_SQ_OS_dR_Max1p2", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        print(f' > Efficiencies done for L1_DoubleMu4p5_SQ_OS_dR_Max1p2')
    
    # L1_DoubleMu8_SQ
    if not onlyDPNote:
        rdf_den_L1_DoubleMu8_SQ = rdf
        rdf_num_L1_DoubleMu8_SQ = rdf_den_L1_DoubleMu8_SQ.Filter("L1_DoubleMu8_SQ")
        histos.append(rdf_den_L1_DoubleMu8_SQ.Histo1D(("probe_pt_denominator_L1_DoubleMu8_SQ", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num_L1_DoubleMu8_SQ.Histo1D(("probe_pt_numerator_L1_DoubleMu8_SQ", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        print(f' > Efficiencies done for L1_DoubleMu8_SQ')

    # L1_DoubleMu0_Upt6_IP_Min1_Upt4 (This is weird, needs to be revisited)
    if not onlyDPNote:
        rdf_den_L1_DoubleMu0_Upt6_IP_Min1_Upt4 = rdf.Filter("tag_pt > 6. && probe_pt > 4. && abs(tag_eta) < 0.8 && abs(probe_eta) < 0.8")
        rdf_num_L1_DoubleMu0_Upt6_IP_Min1_Upt4 = rdf_den_L1_DoubleMu0_Upt6_IP_Min1_Upt4.Filter("L1_DoubleMu0_Upt6_IP_Min1_Upt4")
        histos.append(rdf_den_L1_DoubleMu0_Upt6_IP_Min1_Upt4.Histo1D(("probe_IP_denominator_L1_DoubleMu0_Upt6_IP_Min1_Upt4", r'; Subleading muon IP (cm); Number of events', len(np.array(sigdxy_bins))-1, np.array(sigdxy_bins)), "tag_absdxy"))
        histos.append(rdf_num_L1_DoubleMu0_Upt6_IP_Min1_Upt4.Histo1D(("probe_IP_numerator_L1_DoubleMu0_Upt6_IP_Min1_Upt4", r'; Subleading muon IP (cm); Number of events', len(np.array(sigdxy_bins))-1, np.array(sigdxy_bins)), "tag_absdxy"))
        print(f' > Efficiencies done for L1_DoubleMu0_Upt6_IP_Min1_Upt4')

    # L1_DoubleMu0_Upt6_SQ_er2p0
    rdf_den_L1_DoubleMu0_Upt6_SQ_er2p0 = rdf.Filter("abs(tag_eta) < 2.0 && abs(probe_eta) < 2.0")
    rdf_num_L1_DoubleMu0_Upt6_SQ_er2p0 = rdf_den_L1_DoubleMu0_Upt6_SQ_er2p0.Filter("L1_DoubleMu0_Upt6_SQ_er2p0")
    histos.append(rdf_den_L1_DoubleMu0_Upt6_SQ_er2p0.Histo1D(("probe_pt_denominator_L1_DoubleMu0_Upt6_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    histos.append(rdf_num_L1_DoubleMu0_Upt6_SQ_er2p0.Histo1D(("probe_pt_numerator_L1_DoubleMu0_Upt6_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    print(f' > Efficiencies done for L1_DoubleMu0_Upt6_SQ_er2p0')

    # L1_DoubleMu0_Upt7_SQ_er2p0
    rdf_den_L1_DoubleMu0_Upt7_SQ_er2p0 = rdf.Filter("abs(tag_eta) < 2.0 && abs(probe_eta) < 2.0")
    rdf_num_L1_DoubleMu0_Upt7_SQ_er2p0 = rdf_den_L1_DoubleMu0_Upt7_SQ_er2p0.Filter("L1_DoubleMu0_Upt7_SQ_er2p0")
    histos.append(rdf_den_L1_DoubleMu0_Upt7_SQ_er2p0.Histo1D(("probe_pt_denominator_L1_DoubleMu0_Upt7_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    histos.append(rdf_num_L1_DoubleMu0_Upt7_SQ_er2p0.Histo1D(("probe_pt_numerator_L1_DoubleMu0_Upt7_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    print(f' > Efficiencies done for L1_DoubleMu0_Upt7_SQ_er2p0')

    # L1_DoubleMu0_Upt8_SQ_er2p0
    rdf_den_L1_DoubleMu0_Upt8_SQ_er2p0 = rdf.Filter("abs(tag_eta) < 2.0 && abs(probe_eta) < 2.0")
    rdf_num_L1_DoubleMu0_Upt8_SQ_er2p0 = rdf_den_L1_DoubleMu0_Upt8_SQ_er2p0.Filter("L1_DoubleMu0_Upt8_SQ_er2p0")
    histos.append(rdf_den_L1_DoubleMu0_Upt8_SQ_er2p0.Histo1D(("probe_pt_denominator_L1_DoubleMu0_Upt8_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    histos.append(rdf_num_L1_DoubleMu0_Upt8_SQ_er2p0.Histo1D(("probe_pt_numerator_L1_DoubleMu0_Upt8_SQ_er2p0", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    print(f' > Efficiencies done for L1_DoubleMu0_Upt8_SQ_er2p0')

    # DST_PFScouting_DoubleMuon
    rdf_den_HLT = rdf
    rdf_num_HLT = rdf_den_HLT.Filter("DST_PFScouting_DoubleMuon == 1")
    histos.append(rdf_den_HLT.Histo1D(("probe_pt_denominator_HLT", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    histos.append(rdf_num_HLT.Histo1D(("probe_pt_numerator_HLT", r'; Subleading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
    print(f' > Efficiencies done for HLT')

    ### Summary
    for histo in histos:
        print('Histogram with %f'%(histo.GetEntries()))

    ### Save histograms
    outputdir = '/eos/user/f/fernance/DST-Muons' + '/ScoutingOutput_efficiencies_DoubleMuon_%s/'%(hlt)
    print('Saving in %s'%outputdir)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    out_ = r.TFile(outputdir + 'output_%s.root'%(str(step)), 'RECREATE')
    for h in histos:
        h_ = h.GetValue()
        h_.Write()
    out_.Close()
