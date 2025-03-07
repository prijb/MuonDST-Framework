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
doEfficiencies = True
doTagAndProbe = True
display = False

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
    parser.add_option('--l1', action='store', type=str,  dest='l1', default='Total', help='Total or L1 seed name')
    parser.add_option('--doEfficiency', action='store', type=int,  dest='l1', default=0, help='Select if the code runs efficiencies')
    parser.add_option('--inDir', action='store', type=str,  dest='inDir', default='Total', help='Input dir')
    parser.add_option('--tag', action='store', type=str,  dest='tag', default='tag', help='Input dir')
    parser.add_option('--hlt', action='store', type=str,  dest='hlt', default='', help='HLT path')
    parser.add_option('--muon', action='store', type=str,  dest='muon', default='ScoutingMuonNoVtx', help='the muon')
    parser.add_option('--redirector', action='store', type=str,  dest='redirector', default='root://xrootd-cms.infn.it', help='the muon')
    parser.add_option('-s', '--step', action='store', type=int,  dest='step', default=0, help='Input dir')
    parser.add_option('-n', '--number', action='store', type=int,  dest='number', default=0, help='Input dir')
    (opts, args) = parser.parse_args()

    ## Running parameters
    l1seed = opts.l1
    inputdir = opts.inDir
    step = opts.step
    number = opts.number
    tag = opts.tag
    hlt = opts.hlt
    muon = opts.muon
    redirector = opts.redirector # root://cmsxrootd.fnal.gov | root://hip-cms-se.csc.fi | root://xrootd-cms.infn.it
    #redirector = ''
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
    rdf = rdf.Filter("(DST_PFScouting_ZeroBias == 1 || DST_PFScouting_DoubleEG == 1 || DST_PFScouting_JetHT == 1)")
    print(f' > RDataFrame with {rdf.Count().GetValue()} entries after DST filtering')

    ## Histogram container
    histos = []

    if doTagAndProbe:

        ## Pre-filter the events to have exactly 2 muons
        rdf = rdf.Filter("nScoutingMuonVtx == 2")
        print(f' > RDataFrame with {rdf.Count().GetValue()} entries after 2 muon filtering')

        ## Definitions
        print('Setting definitions for tag and probe...')

        tagDef = "(ScoutingMuonVtx_pt[0] < ScoutingMuonVtx_pt[1]) ? ScoutingMuonVtx_{0}[0] : ScoutingMuonVtx_{0}[1]"
        probeDef = "(ScoutingMuonVtx_pt[0] < ScoutingMuonVtx_pt[1]) ? ScoutingMuonVtx_{0}[1] : ScoutingMuonVtx_{0}[0]"

        vars = ["pt", "eta", "phi", "trk_chi2", "trk_ndof", "nValidPixelHits"]

        for var in vars:
            rdf = rdf.Define("tag_{0}".format(var), tagDef.format(var))
            rdf = rdf.Define("probe_{0}".format(var), probeDef.format(var))
        rdf = rdf.Define("tnp_mass", "(ROOT::Math::PtEtaPhiMVector(tag_pt, tag_eta, tag_phi, 0.105658) + ROOT::Math::PtEtaPhiMVector(probe_pt, probe_eta, probe_phi, 0.105658)).M()")

        print('Definitions set')

        ## Post-filter
        rdf = rdf.Filter("tnp_mass > 2.80 && tnp_mass < 3.4")
        rdf = rdf.Filter("tag_pt > 2 && abs(tag_eta) < 2.4 && tag_trk_chi2/tag_trk_ndof < 3 && tag_nValidPixelHits > 0")
        rdf = rdf.Filter("abs(probe_eta) < 0.83")
        print(f' > RDataFrame with {rdf.Count().GetValue()} entries after tag-probe selection')

        ## Display
        if display:
            rdf.Display(["tag_pt"]).Print()

        ## Get passed rdf:
        rdf_den = rdf
        rdf_num = rdf.Filter("L1_SingleMu11_SQ14_BMTF")
        print(f' > RDataFrame with {rdf.Count().GetValue()} entries passing L1_SingleMu11_SQ14_BMTF')

        ### Filling
        mbins = [0.215]
        while (mbins[-1]<250):
            mbins.append(1.01*mbins[-1])
        pt_bins = np.linspace(0, 50, 101)
        eta_bins = np.linspace(-3, 3, 51)
        phi_bins = np.linspace(-3.14, 3.14, 51)
        mass_jpsi_bins = np.linspace(2.8, 3.4, 101)
        #
        #
        histos.append(rdf_den.Histo1D(("probe_pt_denominator", r'; Leading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))
        histos.append(rdf_num.Histo1D(("probe_pt_numerator", r'; Leading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "probe_pt"))

    else:
        ## Definitions
        #rdf = rdf.Range(0, 500000)
        rdf = rdf.Filter("nScoutingMuonVtx > 0")
        print('Setting definitions for tag and probe...')

        rdf = rdf.Define("ScoutingMuonVtx_imax", "ROOT::VecOps::ArgMax(ScoutingMuonVtx_pt)")

        #vars = ["pt", "eta", "phi", "trk_chi2", "trk_ndof", "nValidRecoMuonHits", "nRecoMuonMatchedStations", "nValidPixelHits", "nTrackerLayersWithMeasurement"]
        vars = ["pt", "eta", "nValidPixelHits", "nTrackerLayersWithMeasurement", "trk_chi2", "trk_ndof"]
        for var in vars:
            rdf = rdf.Define("muon_{0}".format(var), "ScoutingMuonVtx_{0}[ScoutingMuonVtx_imax]".format(var))

        print('Definitions set')
        print("ScoutingMuonVtx_imax" in rdf.GetColumnNames())

        ## Display
        if display:
            rdf.Display("ScoutingMuonVtx_imax").Print()

        ## Post-filter
        rdf = rdf.Filter("muon_pt > 2 && abs(muon_eta) < 1.4 && muon_nTrackerLayersWithMeasurement > 5 && muon_nValidPixelHits > 0 && muon_trk_chi2/muon_trk_ndof < 3")

        ## Get passed rdf:
        rdf_den = rdf
        rdf_num = rdf.Filter("L1_SingleMu11_SQ14_BMTF")
        print(f' > RDataFrame with {rdf.Count().GetValue()} entries passing L1_SingleMu11_SQ14_BMTF')

        ### Filling
        mbins = [0.215]
        while (mbins[-1]<250):
            mbins.append(1.01*mbins[-1])
        pt_bins = np.linspace(0, 50, 101)
        eta_bins = np.linspace(-3, 3, 51)
        phi_bins = np.linspace(-3.14, 3.14, 51)
        mass_jpsi_bins = np.linspace(2.8, 3.4, 101)
        #
        #
        histos.append(rdf_den.Histo1D(("probe_pt_denominator", r'; Leading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "muon_pt"))
        histos.append(rdf_num.Histo1D(("probe_pt_numerator", r'; Leading muon $p_{T}$ (GeV); Number of events', len(np.array(pt_bins))-1, np.array(pt_bins)), "muon_pt"))

    ### Summary
    for histo in histos:
        print('Histogram with %f'%(histo.GetEntries()))

    ### Save histograms
    outputdir = '/eos/user/f/fernance/DST-Muons' + '/ScoutingOutput_efficiencies/'
    print('Saving in %s'%outputdir)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    out_ = r.TFile(outputdir + 'output_%s.root'%(str(step)), 'RECREATE')
    for h in histos:
        h_ = h.GetValue()
        h_.Write()
    out_.Close()
