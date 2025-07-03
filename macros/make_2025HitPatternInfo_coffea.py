import matplotlib.pyplot as plt
import mplhep
import hist
import glob
import pickle
from tqdm import tqdm
	
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import uproot
import awkward as ak
import coffea
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, ScoutingNanoAODSchema

## Python version for HitPattern.h https://github.com/cms-sw/cmssw/blob/master/DataFormats/TrackReco/interface/HitPattern.h
class HitPattern:

    def __init__(self):
        self.HIT_LENGTH = 12 # as defined in CMSSW

    ## adaptation of getHitPatternByAbsoluteIndex https://github.com/cms-sw/cmssw/blob/dd8becf551ac8cd90a9c5899411abb48dd2e66e6/DataFormats/TrackReco/src/HitPattern.cc#L316
    def getHitPatternByAbsoluteIndex(self, position, hitCount, hitPattern, verbose=False):
        if position >= hitCount:
            return 0
        bitEndOffset = (position + 1) * self.HIT_LENGTH
        secondWord = bitEndOffset >> 4 # Eliminates 4 LSB
        secondWordBits = bitEndOffset & (16 - 1) # bitEndOffset % 16, gets the 4 LSB
        if (secondWordBits >= self.HIT_LENGTH): # When the hit is fully inside of a single word
            lowBitsToTrash = secondWordBits - self.HIT_LENGTH # We remove the extra bits at the end of the second word
            myResult = (hitPattern[secondWord] >> lowBitsToTrash) & ((1 << self.HIT_LENGTH) - 1) # Gets the 11 ones
            return myResult
        else:
            firstWordBits = self.HIT_LENGTH - secondWordBits
            firstWordBlock = hitPattern[secondWord - 1] >> (16 - firstWordBits)
            if (secondWordBits==0):
                return firstWordBlock
            else:
                secondWordBlock = hitPattern[secondWord] & ((1 << secondWordBits) - 1)
                myResult = firstWordBlock + (secondWordBlock << firstWordBits)
                return myResult

verbose = True

print("Everything imported")
fname = "/eos/user/f/fernance/DST-Muons/samples/e0e9c734-dead-4179-b699-f6b75d0e4502.root"
events = NanoEventsFactory.from_root(
    fname+":Events",
    delayed=False,
    entry_start=0,
    entry_stop=100000,
    schemaclass=ScoutingNanoAODSchema,
    metadata={"dataset": "ScoutingPFRun3_2025C"},
).events()

print("Everything loaded")

print(sorted(events.fields))

# Filter by number of muons
events = events[ak.num(events['ScoutingMuonVtx']) > 1]

### Nested operations to add the hitPattern
patterns     = events["ScoutingMuonVtxHitPattern"]["hitPattern"]
offsets  = events["ScoutingMuonVtx"]["oScoutingMuonVtxHitPattern"]
counts   = events["ScoutingMuonVtx"]["nScoutingMuonVtxHitPattern"]
#
n_muons_per_event = ak.num(events["ScoutingMuonVtx"])
#
grouped_hitPattern = ak.Array([
    [pattern_evt[o : o + n] for o, n in zip(evt_offsets, evt_counts)]
    for pattern_evt, evt_offsets, evt_counts in zip(patterns, offsets, counts)
])
#    
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_hitPattern,
    "hitPattern"
)
#
print("Finished the nesting for hitPattern")

### Nested operations to add the vertices
vtxs     = events["ScoutingMuonVtxDisplacedVertex"]
vtxIndx  = events["ScoutingMuonVtxVtxIndx"]["vtxIndx"]
offsets  = events["ScoutingMuonVtx"]["oScoutingMuonVtxVtxIndx"]
counts   = events["ScoutingMuonVtx"]["nScoutingMuonVtxVtxIndx"]
#
n_muons_per_event = ak.num(events["ScoutingMuonVtx"])
#
# indexes for all SV
grouped_idx = ak.Array([
    [vtxIndx_evt[o : o + n] for o, n in zip(evt_offsets, evt_counts)]
    for vtxIndx_evt, evt_offsets, evt_counts in zip(vtxIndx, offsets, counts)
])
#
# indexes for valid SV
flat_idx_valid = ak.Array([
    [evt_vtxIndx[i] for i in range(o , o+n) if evt_vtxs[evt_vtxIndx[i]].isValidVtx]
    for evt_vtxIndx, evt_offsets, evt_counts, evt_vtxs in zip(vtxIndx, offsets, counts, vtxs)
    for o, n in zip(evt_offsets, evt_counts)
])
grouped_idx_valid = ak.unflatten(flat_idx_valid, n_muons_per_event)
#
# Here we are going to get only the valid ones
displaced_vertices = ak.Array([
    [vtxs_evt[i] for i in idxs]
    for vtxs_evt, idxs_evt in zip(vtxs, grouped_idx_valid)
    for idxs in idxs_evt
])
grouped_vtx = ak.unflatten(displaced_vertices, n_muons_per_event)
#
best_vtxIndx_perMuon = ak.Array([
    evt_vtxIndx_valid[np.argmin(evt_vtxs_valid.chi2)] if len(evt_vtxs_valid.chi2) > 0 else -1
    for evt_vtxs_valid, evt_vtxIndx_valid in zip(displaced_vertices, flat_idx_valid)
])
grouped_bestIdx = ak.unflatten(best_vtxIndx_perMuon, n_muons_per_event)
#
#best_displaced_vertices = ak.Array([
#    vtxs_evt[idxs_evt] if idxs_evt > -1 else None
#    for vtxs_evt, idxs_evt in zip(vtxs, ak.flatten(grouped_bestIdx))
#])
#grouped_bestVtx = ak.unflatten(best_displaced_vertices, ak.num(grouped_bestIdx))
best_displaced_vertices = ak.Array([
    evt_vtxs_valid[np.argmin(evt_vtxs_valid.chi2)] if len(evt_vtxs_valid) > 0 else None
    for evt_vtxs_valid in displaced_vertices
])
grouped_bestVtx = ak.unflatten(best_displaced_vertices, n_muons_per_event)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_idx,
    "vtxIndx"
)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_idx_valid,
    "vtxIndxValid"
)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_vtx,
    "displaced_vertices"
)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_bestIdx,
    "bestVtxIndx"
)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_bestVtx,
    "bestVtx"
)
#
print("Finished the nesting for the vertices")

HP = HitPattern()

## Restrict our reading to muons ONLY with a good vtx (not the best way to do it though)
events["ScoutingMuonVtx"] = events["ScoutingMuonVtx"][events["ScoutingMuonVtx"]["bestVtxIndx"] > -1]
# and filter again:
events = events[ak.num(events['ScoutingMuonVtx']) > 1]

print(events["ScoutingMuonVtx"]["bestVtx"][0])
print(ak.fields(events["ScoutingMuonVtx"]["bestVtx"]))

## Lxy computation
bestVtx = events["ScoutingMuonVtx"]["bestVtx"]
lxy = (bestVtx.x**2 + bestVtx.y**2)**0.5
bestVtx = ak.with_field(bestVtx, lxy, "lxy")
events["ScoutingMuonVtx"] = ak.with_field(events["ScoutingMuonVtx"], bestVtx, "bestVtx")

## Cross-check with one event
if verbose:
    sel_event = events[1]
    for i, muon in enumerate(sel_event["ScoutingMuonVtx"]):
        print(f"MuonVtx {i+1}: pt={muon['pt']:<7.3f} eta={muon['eta']:<7.3f} phi={muon['phi']:<7.3f}, bestVtx={muon['bestVtx'].lxy}, pixel={muon['nValidPixelHits']}, strip={muon['nValidStripHits']}")
        print(f"{ak.to_list(muon['hitPattern'])}")
        print(f"{len(ak.to_list(muon['hitPattern']))}")
        for j in range(muon['trk_hitPattern_hitCount']):
            result = HP.getHitPatternByAbsoluteIndex(j, muon['trk_hitPattern_hitCount'], muon['hitPattern'])
            print(format(result, '012b'))

## Nested operations to save the hits
hitPatterns = events["ScoutingMuonVtx"]["hitPattern"]
hitCounts   = events["ScoutingMuonVtx"]["trk_hitPattern_hitCount"]
#
all_hits = ak.Array([
    [HP.getHitPatternByAbsoluteIndex(i, muon_hitCount, muon_hitPattern) for i in range(muon_hitCount)]
    for muon_hitCounts,muon_hitPatterns in zip(hitCounts, hitPatterns)
    for muon_hitCount,muon_hitPattern in zip(muon_hitCounts, muon_hitPatterns)
])
n_muons_per_event = ak.num(events["ScoutingMuonVtx"]) # Need redefinition because we have filtered (again, very ugly)
grouped_hits = ak.unflatten(all_hits, n_muons_per_event)
#
events["ScoutingMuonVtx"] = ak.with_field(
    events["ScoutingMuonVtx"],
    grouped_hits,
    "hitPattern_hits"
)

## Assign a lxy to every hit in the muon thanks to the vtx association
flat_lxy = ak.flatten(
    ak.broadcast_arrays(
        events["ScoutingMuonVtx"]["hitPattern_hits"],
        events["ScoutingMuonVtx"]["bestVtx"].lxy
    )[1],
    axis=None
)

flat_hits = ak.flatten(events["ScoutingMuonVtx"]["hitPattern_hits"], axis=None)

if verbose:
    print(flat_lxy)
    print(flat_hits)

### Define the masks for each detector:
mask_PXB = ((flat_hits >> 7) & 0b11111) == 0b01001
mask_PXF = ((flat_hits >> 7) & 0b11111) == 0b01010
mask_TIP = ((flat_hits >> 7) & 0b11111) == 0b01011
mask_TID = ((flat_hits >> 7) & 0b11111) == 0b01100
mask_TOB = ((flat_hits >> 7) & 0b11111) == 0b01101
mask_TEC = ((flat_hits >> 7) & 0b11111) == 0b01110

lxy_PXB = flat_lxy[mask_PXB]
lxy_PXF = flat_lxy[mask_PXF]
lxy_TIP = flat_lxy[mask_TIP]
lxy_TID = flat_lxy[mask_TID]
lxy_TOB = flat_lxy[mask_TOB]
lxy_TEC = flat_lxy[mask_TEC]

h_lxy_PXB = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()
h_lxy_PXF = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()
h_lxy_TIP = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()
h_lxy_TID = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()
h_lxy_TOB = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()
h_lxy_TEC = hist.new.Reg(40, 0, 40, name="lxy", label="lxy [cm]").Double()

h_lxy_PXB.fill(lxy=lxy_PXB)
h_lxy_PXF.fill(lxy=lxy_PXF)
h_lxy_TIP.fill(lxy=lxy_TIP)
h_lxy_TID.fill(lxy=lxy_TID)
h_lxy_TOB.fill(lxy=lxy_TOB)
h_lxy_TEC.fill(lxy=lxy_TEC)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
mplhep.cms.label("Preliminary - Scouting NanoAOD", data=True, year='2025', com='13.6', ax=ax)
h_lxy_PXB.plot(ax=ax, color="firebrick")
h_lxy_PXF.plot(ax=ax, color="orange")
h_lxy_TIP.plot(ax=ax, color="gold")
h_lxy_TID.plot(ax=ax, color="forestgreen")
h_lxy_TOB.plot(ax=ax, color="royalblue")
h_lxy_TEC.plot(ax=ax, color="darkblue")
ax.set_xlim(0, 40)
#ax.set_ylim(1, 1e8)
ax.set_xlabel(r"Muon $l_{xy}$ [cm]")
ax.set_ylabel("Number of hits")
#ax.set_xscale("log")
ax.set_yscale("log")
fig.savefig("hist_hits.png", dpi=300)

## Stacked histograms
h_lxy = hist.Hist.new.StrCat(["PXB", "PXF", "TIP", "TID", "TOB", "TEC"], name="subdet", label="Subdetector") \
              .Reg(40, 0, 40, name="lxy", label="lxy [cm]") \
              .Double()
h_lxy.fill(subdet="PXB", lxy=lxy_PXB)
h_lxy.fill(subdet="PXF", lxy=lxy_PXF)
h_lxy.fill(subdet="TIP", lxy=lxy_TIP)
h_lxy.fill(subdet="TID", lxy=lxy_TID)
h_lxy.fill(subdet="TOB", lxy=lxy_TOB)
h_lxy.fill(subdet="TEC", lxy=lxy_TEC)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
mplhep.cms.label("Preliminary - Scouting NanoAOD", data=True, year='2025', com='13.6', ax=ax)
mplhep.histplot(
    [h_lxy_PXB.values(), h_lxy_PXF.values(), h_lxy_TIP.values(), h_lxy_TID.values(), h_lxy_TOB.values(), h_lxy_TEC.values()],
    bins = h_lxy_PXB.axes[0].edges,
    color = ["firebrick", "orange", "gold", "forestgreen", "royalblue", "darkblue"],
    edgecolor="black",
    ax=ax, stack=True, histtype='fill', label=["PXB", "PXF", "TIP", "TID", "TOB", "TEC"])
ax.set_xlim(0, 40)
ax.set_xlabel(r"Muon $l_{xy}$ [cm]")
ax.set_ylabel("Number of hits")
#ax.set_yscale("log")
ax.legend()
fig.savefig("hist_hits_stacked.png", dpi=300)



## Define masks for every detector
