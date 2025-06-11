import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
import mplhep
import hist
import glob
import pickle
from tqdm import tqdm

## Analysis info
MUON = "Vtx"
TRIGGER = ["DST_PFScouting_DoubleMuonNoVtx", "DST_PFScouting_DoubleMuonVtx"]


## Open the file
selected_branches = []
selected_branches += TRIGGER
selected_branches.append("nScoutingMuon%s"%(MUON))
selected_branches.append("ScoutingMuon%s_pt"%(MUON))
selected_branches.append("ScoutingMuon%s_eta"%(MUON))
selected_branches.append("ScoutingMuon%s_phi"%(MUON))
selected_branches.append("ScoutingMuon%s_charge"%(MUON))

## Histogram to fill
h_mass = hist.new.Reg(1500, 0, 110, name="mass", label="Mass [GeV]").Double()
h_pt = hist.new.Reg(100, 0, 100, name="pt", label="Pt [GeV]").Double()
h_eta = hist.new.Reg(100, -3, 3, name="eta", label="Eta").Double()
h_phi = hist.new.Reg(100, -4, 4, name="phi", label="Mass").Double()

## Data
indir = "/eos/user/f/fernance/DST-Muons/skims_2025C"
#indir = "/eos/user/f/fernance/DST-Muons/skims_2024I"
files = glob.glob(f"{indir}/*.root")
#events = uproot.open("/afs/cern.ch/work/f/fernance/private/Scouting/2025Analysis/CMSSW_15_0_5/src/MuonDST-Framework/skimmed_0_NanoAOD.root")["Events"].arrays(selected_branches, library="ak")

#files = files[:10]

for f in tqdm(files, desc="Progress"):
   
    events = uproot.open(f)["Events"].arrays(selected_branches, library="ak")

    if len(events) == 0:
        continue

    #print(f"> Opened sample with {len(events)} events")
    
    ## Filter by trigger

    #events = events[ events[TRIGGER] == True ]
    MASK_trigger = False
    for trigger in TRIGGER:
        MASK_trigger = (MASK_trigger | events[trigger])
    
    #print(f"> {len(events)} events survive DST_PFScouting_DoubleMuonNoVtx")
    
    ## Filter by number of muons
    events = events[ events["nScoutingMuon%s"%(MUON)] > 1]

    #print(ak.fields(events[1]))
    #print(events[1]["ScoutingMuon%s_pt"%(MUON)])
    
    #print(f"> {len(events)} events have at least 2 ScoutingMuonNoVtx")
    
    ## Get leading and subleading muons and save their indices in two new variables "muon1" and "muon2"
    events["ScoutingMuon%s_idx"%(MUON)] = ak.local_index(events["ScoutingMuon%s_pt"%(MUON)])
    sorted_muons = ak.argsort(events["ScoutingMuon%s_pt"%(MUON)], axis=1, ascending=False)
    events = ak.with_field(events, sorted_muons[:, 0], "muon1")
    events = ak.with_field(events, sorted_muons[:, 1], "muon2")
    
    ## Filter by opposite charge of these two muons
    charge1 = ak.flatten( events["ScoutingMuon%s_charge"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    charge2 = ak.flatten( events["ScoutingMuon%s_charge"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    
    dimuon_charge = charge1 * charge2
    
    events = events[dimuon_charge < 0]
    
    #print(f"> {len(events)} events have at least a leading dimuon candidate with opposite charge")
    
    ## Filter by eta and pt between the muons
    eta1 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    eta2 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    pt1 = ak.flatten( events["ScoutingMuon%s_pt"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    pt2 = ak.flatten( events["ScoutingMuon%s_pt"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    
    events = events[(np.abs(eta1) < 2.4) & (np.abs(eta2) < 2.4)]
    
    ## Filter by deltaR distance between the muons
    eta1 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] ) ## Need to recompute eta because we filtered
    eta2 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] ) ## Need to recompute eta because we filtered
    phi1 = ak.flatten( events["ScoutingMuon%s_phi"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    phi2 = ak.flatten( events["ScoutingMuon%s_phi"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    
    deltaEta = np.abs(eta1 - eta2)
    deltaPhi = np.abs(phi1 - phi2)
    deltaPhi = np.where(deltaPhi > np.pi, 2 * np.pi - deltaPhi, deltaPhi)
    deltaR = np.sqrt(deltaEta**2 + deltaPhi**2)
    
    events = events[deltaR > 0.2]
    
    #
    #
    ## Basic kinematics
    pt = ak.flatten( events["ScoutingMuon%s_pt"%(MUON)] )
    eta = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)] )
    phi = ak.flatten( events["ScoutingMuon%s_phi"%(MUON)] )
    h_pt.fill(pt=pt)
    h_eta.fill(eta=eta)
    h_phi.fill(phi=phi)

    
    #
    #
    ## Get invariant mass
    pt1 = ak.flatten( events["ScoutingMuon%s_pt"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    pt2 = ak.flatten( events["ScoutingMuon%s_pt"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    eta1 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    eta2 = ak.flatten( events["ScoutingMuon%s_eta"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    phi1 = ak.flatten( events["ScoutingMuon%s_phi"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon1"] ] )
    phi2 = ak.flatten( events["ScoutingMuon%s_phi"%(MUON)][ events["ScoutingMuon%s_idx"%(MUON)] == events["muon2"] ] )
    
    mu_mass = 0.105
    pz1 = pt1 * np.sinh(eta1)
    pz2 = pt2 * np.sinh(eta2)
    px1 = pt1 * np.cos(phi1)
    px2 = pt2 * np.cos(phi2)
    py1 = pt1 * np.sin(phi1)
    py2 = pt2 * np.sin(phi2)
    E1  = np.sqrt(px1**2 + py1**2 + pz1**2 + mu_mass**2)
    E2  = np.sqrt(px2**2 + py2**2 + pz2**2 + mu_mass**2)
    
    invariant_mass = np.sqrt((E1 + E2)**2 - (px1 + px2)**2 - (py1 + py2)**2 - (pz1 + pz2)**2)
    
    h_mass.fill(mass=invariant_mass)


plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_mass.plot(ax=ax)
ax.set_xlim(0.1, 110)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_xscale("log")
ax.set_yscale("log")
fig.savefig("hist_invariant-mass_log.png", dpi=300)

with open("histos.pkl", "wb") as f:
    pickle.dump(h_mass, f)
    pickle.dump(h_pt, f)
    pickle.dump(h_eta, f)
    pickle.dump(h_phi, f)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_pt.plot(ax=ax)
ax.set_xlim(0, 100)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_yscale("log")
fig.savefig("hist_pt_log.png", dpi=300)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_eta.plot(ax=ax)
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_yscale("log")
fig.savefig("hist_eta_log.png", dpi=300)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_phi.plot(ax=ax)
ax.set_xlim(-4, 4)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_yscale("log")
fig.savefig("hist_phi_log.png", dpi=300)
