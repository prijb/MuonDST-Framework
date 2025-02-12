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
    parser.add_option('--inFile', action='store', type=str,  dest='inFile', default='none', help='Input file')
    parser.add_option('--inDir', action='store', type=str,  dest='inDir', default='none', help='Input dir')
    parser.add_option('--tag', action='store', type=str,  dest='tag', default='tag', help='Input dir')
    parser.add_option('--hlt', action='store', type=str,  dest='hlt', default='', help='HLT path')
    parser.add_option('--redirector', action='store', type=str,  dest='redirector', default='root://xrootd-cms.infn.it', help='the muon')
    parser.add_option('-s', '--step', action='store', type=int,  dest='step', default=0, help='Input dir')
    parser.add_option('-n', '--number', action='store', type=int,  dest='number', default=0, help='Input dir')
    (opts, args) = parser.parse_args()

    ## Running parameters
    l1seed = opts.l1
    inputdir = opts.inDir
    inputfile = opts.inFile
    step = opts.step
    number = opts.number
    tag = opts.tag
    hlt = opts.hlt
    redirector = opts.redirector # root://cmsxrootd.fnal.gov | root://hip-cms-se.csc.fi | root://xrootd-cms.infn.it
    #redirector = ''
    central = True
    
    ## Load samples
    #inputdir = '/eos/user/f/fernance/DST-Muons/2024E_dimuon/ScoutingPFRun3/2024E_dimuon/240610_213819' # 2024D
    if inputfile!='none':
        files = [inputfile]
    elif inputdir!='none':
        print('Reading from ', inputdir)
        print('Redirector ', redirector)
        nfiles = 0
        files = []
        if redirector!='none':
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
                        #tchain.Add(os.path.join(root, f))
                        files.append(os.path.join(root, f))
                        nfiles += 1
                        if nfiles > 5: break
    nfiles = len(files)

    ## Load dataframe
    print(files)
    rdf = r.RDataFrame("Events", files)
    print(f'Init RDataFrame with {rdf.Count().GetValue()} entries in files from {step*number} to {step*number + number}')
    

    ## DST path selection
    if (hlt != '' and hlt!='none'):
        rdf = rdf.Filter("%s  == 1"%(hlt))

    ## Number of muons selection
    # nScoutingMuonNoVtx > 1
    #rdf = rdf.Filter("(nScoutingMuonNoVtx > 1)")
    #rdf = rdf.Filter("(n%s > 1)"%(muon))

    minPt = 3.

    ## Definitions
    print('Setting definitions...')
    
    #tightId = "(MuonVtx_pt > 10 && abs(MuonVtx_eta) < 2.4 && MuonVtx_normalizedChi2 < 10 && MuonVtx_type==14 && MuonVtx_nValidRecoMuonHits > 0 && MuonVtx_nRecoMuonMatchedStations > 0 && MuonVtx_nValidPixelHits > 0 && MuonVtx_nTrackerLayersWithMeasurement > 5 && abs(MuonVtx_trk_dxy) < 0.2 && abs(MuonVtx_trk_dz) < 0.5)"
    #tightId = "(MuonVtx_pt > 10 && abs(MuonVtx_eta) < 2.4 && MuonVtx_normalizedChi2 < 10 && MuonVtx_type==14 && abs(MuonVtx_trk_dxy) < 0.2 && abs(MuonVtx_trk_dz) < 0.5)"
    tightId = "(MuonVtx_pt > 10 && abs(MuonVtx_eta) < 2.4 && MuonVtx_normalizedChi2 < 10 && MuonVtx_type==14)"
    rdf = rdf.Define('SelMuonVtx_pt', "MuonVtx_pt[%s]"%tightId)
    rdf = rdf.Define('SelMuonVtx_eta', "MuonVtx_eta[%s]"%tightId)
    rdf = rdf.Define('SelMuonVtx_phi', "MuonVtx_phi[%s]"%tightId)
    rdf = rdf.Define('SelMuonVtx_charge', "MuonVtx_charge[%s]"%tightId)
    rdf = rdf.Define("SelDiMuonVtx_mass", "(ROOT::Math::PtEtaPhiMVector(SelMuonVtx_pt[0], SelMuonVtx_eta[0], SelMuonVtx_phi[0], 0.105658) + ROOT::Math::PtEtaPhiMVector(SelMuonVtx_pt[1], SelMuonVtx_eta[1], SelMuonVtx_phi[1], 0.105658)).M()")
    rdf = rdf.Define('nSelMuonVtx', "SelMuonVtx_pt.size()")

    #rdf = rdf.Define("%s_vec"%(muon), "GetTLorentzVector(%s_pt, %s_eta, %s_phi, 0.106)"%(muon,muon,muon))
    #rdf = rdf.Define("Di%s_idx"%(muon), "GetDimuonPairs(%s_charge, %s_vec, %f)"%(muon,muon, minPt))
    #rdf = rdf.Define("Good_Di%s_idx"%(muon), "PruneDimuonPairs(Di%s_idx, Di%s_idx)"%(muon,muon))
    ##rdf = rdf.Define("Di%s_mass"%(muon), "GetDimuonMass(Good_Di%s_idx, %s_vec)"%(muon,muon))
    #rdf = rdf.Define("Di%s_mass"%(muon), "GetDimuonMass(Di%s_idx, %s_vec)"%(muon,muon))
    #rdf = rdf.Define("Di%s_idx_leading"%(muon), "Di%s_idx[0]"%(muon))
    #rdf = rdf.Define("Di%s_idx_subleading"%(muon), "Di%s_idx[1]"%(muon))
    #rdf = rdf.Define("Di%s_vec_leading"%(muon), "%s_vec[Di%s_idx_leading]"%(muon,muon))
    #rdf = rdf.Define("Di%s_vec_subleading"%(muon), "%s_vec[Di%s_idx_subleading]"%(muon,muon))
    #rdf = rdf.Define("Di%s_pt_leading"%(muon), "Di%s_vec_leading.Pt()"%(muon))
    #rdf = rdf.Define("Di%s_eta_leading"%(muon), "Di%s_vec_leading.Eta()"%(muon))
    #rdf = rdf.Define("Di%s_pt_subleading"%(muon), "Di%s_vec_subleading.Pt()"%(muon))
    #rdf = rdf.Define("Di%s_eta_subleading"%(muon), "Di%s_vec_subleading.Eta()"%(muon))
    print('Definitions set')
    #rdf.Display(["Di%s_idx"%(muon), "Good_Di%s_idx"%(muon)]).Print()
    rdf.Display({"SelMuonVtx_pt"}).Print()
    
    ## Post-filter
    rdf = rdf.Filter("nSelMuonVtx == 2")
    rdf = rdf.Filter("SelMuonVtx_charge[0]*SelMuonVtx_charge[1] < 0")
    rdf_Z = rdf.Filter("(SelDiMuonVtx_mass > 81 && SelDiMuonVtx_mass < 101)")
    rdf_Ztight = rdf.Filter("(SelDiMuonVtx_mass > 85 && SelDiMuonVtx_mass < 97)")

    rdf.Display({"SelDiMuonVtx_mass"}).Print()
    print(f'RDataFrame has {rdf.Count().GetValue()} entries')

    histos = []
    histo_mass = rdf_Z.Histo1D(('SelDiMuonVtx_mass', r'; Dimuon $m_{\mu\mu}$ (GeV); Number of dimuons', 50, 81, 101), 'SelDiMuonVtx_mass')
    histo_pt = rdf_Ztight.Histo1D(('SelMuonVtx_pt', r'; Muon $p_{T}$ (GeV); Number of muons', 40, 0, 80), 'SelMuonVtx_pt')
    histo_eta = rdf_Ztight.Histo1D(('SelMuonVtx_eta', r'; Muon $|\eta|$; Number of muons', 40, -2.5, 2.5), 'SelMuonVtx_eta')
    histos.append(histo_mass)
    histos.append(histo_pt)
    histos.append(histo_eta)

    #c1 = r.TCanvas("c1", "")
    #histo.Draw()
    #c1.Print("prueba.png")

    ## Filling
    #mbins = [0.215]
    #while (mbins[-1]<250):
    #    mbins.append(1.01*mbins[-1])
    #pt_bins = np.linspace(0, 50, 101)
    #eta_bins = np.linspace(-3, 3, 51)
    #phi_bins = np.linspace(-3.14, 3.14, 51)
    #mass_jpsi_bins = np.linspace(2.8, 3.4, 101)

    #histos = []
    #if doEfficiencies:
    #    histos.append(rdf.Histo1D(('Di%s_leadingPt_denominator'%(muon), r'; Leading muon $p_{T}$ (GeV); Number of dimuons', len(np.array(pt_bins))-1, np.array(pt_bins)), "Di%s_pt_leading"%(muon)))
    #    histos.append(rdf.Histo1D(('Di%s_subleadingPt_denominator'%(muon), r'; Subleading muon $p_{T}$ (GeV); Number of dimuons', len(np.array(pt_bins))-1, np.array(pt_bins)), "Di%s_pt_subleading"%(muon)))
    #    for l1group in L1Seeds.keys():
    #        icond = ""
    #        for seed in L1Seeds[l1group]:
    #            icond += "%s || "%(seed)
    #        irdf = rdf.Filter("(%s)"%(icond[:-4]))
    #        histos.append(irdf.Histo1D(('Di%s_leadingPt_numerator_%s'%(muon,l1group), r'; Leading muon $p_{T}$ (GeV); Number of dimuons', len(np.array(pt_bins))-1, np.array(pt_bins)), "Di%s_pt_leading"%(muon)))
    #        histos.append(irdf.Histo1D(('Di%s_subleadingPt_numerator_%s'%(muon,l1group), r'; Subleading muon $p_{T}$ (GeV); Number of dimuons', len(np.array(pt_bins))-1, np.array(pt_bins)), "Di%s_pt_subleading"%(muon)))
    #else:
    #    for l1group in L1Seeds.keys():
    #        icond = ""
    #        for seed in L1Seeds[l1group]:
    #            icond += "%s || "%(seed)
    #        irdf = rdf.Filter("(%s)"%(icond[:-4]))
    #        #histos.append(irdf.Histo1D(('Di%s_mass_%s'%(muon,l1group), r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', len(np.array(mbins))-1, np.array(mbins)), 'Di%s_mass'%(muon)))
    #        histos.append(irdf.Histo1D(('Di%s_mass_jpsi%s'%(muon,l1group), r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', len(np.array(mass_jpsi_bins))-1, np.array(mass_jpsi_bins)), 'Di%s_mass'%(muon)))
    #for histo in histos:
    #    print('Histogram with %f'%(histo.GetEntries()))

    ### Save histograms
    outputdir = '/eos/user/f/fernance/DST-Muons' + '/ScoutingOutput_DataVSMC/'
    print('Saving in %s'%outputdir)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    if 'mc' in inputfile.split('/')[-1]:
        out_ = r.TFile(outputdir + 'output_mc.root', 'RECREATE')
    else:
        out_ = r.TFile(outputdir + 'output_data.root', 'RECREATE')
    for h in histos:
        h_ = h.GetValue()
        h_.Write()
    out_.Close()


