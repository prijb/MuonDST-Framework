import ROOT as r
import numpy as np
import optparse
from include.plotTools import *
import __main__
import mplhep as hep
import matplotlib.pyplot as plt
import time

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
    parser.add_option('--inDir', action='store', type=str,  dest='inDir', default='Total', help='Input dir')
    parser.add_option('--tag', action='store', type=str,  dest='tag', default='tag', help='Input dir')
    parser.add_option('--hlt', action='store', type=str,  dest='hlt', default='DST_PFScouting_DoubleMuon', help='HLT path')
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
    redirector = True
    
    ## Load samples
    #inputdir = '/eos/user/f/fernance/DST-Muons/2024E_dimuon/ScoutingPFRun3/2024E_dimuon/240610_213819' # 2024D
    print('Reading from ', inputdir)
    nfiles = 0
    files = []
    if redirector:
        tlab = int(time.time())
        os.system(f'xrdfs root://hip-cms-se.csc.fi ls {inputdir} > temp.txt')
        with open('temp.txt', 'r') as file:
            fileNames = file.readlines()
            print(fileNames)
            for f in fileNames[step*number:number*(step+1)]:
                if '.root' in f:
                    print('Including root://hip-cms-se.csc.fi://%s file'%(f))
                    #tchain.Add(os.path.join('davs://redirector.t2.ucsd.edu:1095', f))
                    files.append('root://hip-cms-se.csc.fi://'+f[:-1])
        os.system('rm temp.txt')
    else:
        tchain = r.TChain('Events')
        for root, dirs, files in os.walk(inputdir):
            for f in files:
                if '.root' in f:
                    print('Including %s file'%(f))
                    tchain.Add(os.path.join(root, f))
                    nfiles += 1
                    #break
    nfiles == len(files)

    ## Load dataframe
    print(files)
    rdf = r.RDataFrame("Events", files)
    print(f'Init RDataFrame with {rdf.Count().GetValue()} entries in files from {step*number} to {step*number + number}')
    
    ## DST path selection
    rdf = rdf.Filter("%s  == 1"%(hlt))

    ## Definitions
    print('Setting definitions...')
    #rdf = rdf.Define("SVNoVtx_pt1", "GetElements<float>(MuonNoVtx_pt, SVNoVtx_idx1)")
    print('Definitions set')
    
    ## Main Vtx case
    #rdf = rdf.Define("SVNoVtx_OS", "(SVNoVtx_charge1*SVNoVtx_charge2 < 0)")
    
    ## L1 rdfs (Saved for later because it is not included in Nano so far)
    #if l1seed == 'Total':
    #    condition = '(L1_DoubleMu_15_7 || L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7 || L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18 || L1_DoubleMu8_SQ || L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6 || L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4 || L1_DoubleMu4p5_SQ_OS_dR_Max1p2 || L1_DoubleMu0_Upt15_Upt7 | L1_DoubleMu0_Upt6_IP_Min1_Upt4)'
    #    rdf = rdf.Filter(condition)
    #else:
    #    rdf = rdf.Filter("%s == 1"%(l1seed))
    #print(f'{l1seed} RDataFrame has {rdf.Count().GetValue()} entries')
    print(f'RDataFrame has {rdf.Count().GetValue()} entries')

    ## Filling
    histo_cfg = []
    mbins = [0.215]
    while (mbins[-1]<250):
        mbins.append(1.01*mbins[-1])
    pt_bins = np.linspace(0, 50, 101)
    eta_bins = np.linspace(-3, 3, 51)
    phi_bins = np.linspace(-3.14, 3.14, 51)
    #histo_cfg.append(['SelSVNoVtx_mass', r'; Mass $m_{\mu\mu}$ (GeV); Number of dimuons', np.array(mbins)])
    histo_cfg.append(['ScoutingMuonVtx_pt', r'; Muon $p_{T}$ (GeV); Number of muons', pt_bins])
    #histo_cfg.append(['ScoutingMuonVtx_eta', r'; Muon $\eta$ (GeV); Number of muons', eta_bins])
    histo_cfg.append(['ScoutingMuonVtx_phi', r'; Muon $\phi$ (GeV); Number of muons', phi_bins])
    histo_cfg.append(['ScoutingMuonNoVtx_pt', r'; Muon $p_{T}$ (GeV); Number of muons', pt_bins])
    #histo_cfg.append(['ScoutingMuonNoVtx_eta', r'; Muon $\eta$ (GeV); Number of muons', eta_bins])
    histo_cfg.append(['ScoutingMuonNoVtx_phi', r'; Muon $\phi$ (GeV); Number of muons', phi_bins])
    #histo_cfg.append(['MuonNoVtx_eta', r'; Muon $\eta$; Number of muons', np.linspace(-2.5, 2.5, 101)])

    histos = []
    for cfg in histo_cfg:
        histos.append(rdf.Histo1D((cfg[0], cfg[1], len(cfg[2])-1, cfg[2]), cfg[0]))
        print('Histogram with %f'%(histos[-1].GetEntries()))

    ## Save histograms
    outputdir = '/eos/user/f/fernance/DST-Muons' + '/ScoutingOutput_%s_%s/'%(tag, l1seed)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    out_ = r.TFile(outputdir + 'output_%s_%s_%s.root'%(tag, l1seed, str(step)), 'RECREATE')
    for h in histos:
        h.Write()
    out_.Close()


