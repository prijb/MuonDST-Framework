# Evaluate performance of muons in 2025 Scouting Nano (options for HLT, prescaled L1 seeds, resonance based selection and lumi masking)
import argparse
import os
import sys
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from collections import defaultdict
import uproot
import awkward as ak
import hist
from hist import Hist
import coffea
from coffea import processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, ScoutingNanoAODSchema
from coffea.nanoevents.methods import candidate
from coffea.dataset_tools import (
    apply_to_fileset,
    max_chunks,
    preprocess,
)

import dask
from dask.distributed import Client, LocalCluster
import socket

# Lumi mask
from coffea.lumi_tools import LumiMask

# Dask port check
def check_port(port):
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", port))
        available = True
    except Exception:
        available = False
    sock.close()
    return available

# Processor definition
class MonitoringProcessor(processor.ProcessorABC):
    def __init__(self, hltpath=None, prescalel1=False, useVtx=False, resonance_mask=None, no_dimuon=False, lumi_mask=None):
        self.hltpath = hltpath.replace("DST_", "")
        self.prescalel1 = prescalel1
        self.useVtx = useVtx
        self.resonance_mask = resonance_mask
        self.no_dimuon = no_dimuon

        # Set unprescaled L1 seeds
        # Prescales set only for muon triggers for now
        if "DoubleMuon" in self.hltpath:
            self.l1_triggers = [
                "DoubleMu8_SQ",
                "DoubleMu_15_7",
                "DoubleMu0_Upt6_SQ_er2p0",
                "DoubleMu0_Upt7_SQ_er2p0",
                "DoubleMu0_Upt8_SQ_er2p0",
                "DoubleMu0_Upt6_IP_Min1_Upt4",
                "DoubleMu0_Upt15_Upt7",
                "DoubleMu0er1p4_SQ_OS_dR_Max1p4",
                "DoubleMu4er2p0_SQ_OS_dR_Max1p6",
                "DoubleMu4p5_SQ_OS_dR_Max1p2",
                "DoubleMu4p5er2p0_SQ_OS_Mass_Min7",
            ]
        elif "SingleMuon" in self.hltpath:
            self.l1_triggers = [
                "SingleMu11_SQ14_BMTF",
                "SingleMu13_SQ14_BMTF",
            ]
        else:
            print(f"No L1 seeds initialised for path {self.hltpath}")

        self.muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"
        self.lumi_mask = LumiMask(lumi_mask) if lumi_mask is not None else None

        # Debug
        print("\nProcessor initialised with following attributes")
        print(f"HLT selection: {self.hltpath}")
        print(f"Select only unprescaled L1 seeds: {self.prescalel1}")
        print(f"Muon collection: {self.muon_collection_key}")
        if lumi_mask is not None: print(f"Lumi mask applied from {lumi_mask}")
        print(f"No dimuons: {no_dimuon}")
        if self.resonance_mask is not None: print(f"Selecting muons from resonance: {self.resonance_mask}")

    def process(self, events):
        muon_collection_key = self.muon_collection_key
        cutflow_axis = hist.axis.StrCategory([], growth=True, name="cutflow", label="Cutflow")
        h_cutflow = hist.Hist(
            cutflow_axis, 
            hist.axis.Regular(1, 0, 1, name="cutflow_count", label="Count"), 
            storage="weight", 
            label="Counts"
        )
        h_nmuon = hist.Hist(
            hist.axis.Regular(10, 0, 10, name="nmuon", label="nMuons"),
            storage="weight"
        )
        # Event quantities
        h_mass = hist.Hist(
            hist.axis.Regular(15000, 0, 150, name="mass", label="Mass [GeV]"),
            storage="weight"
        )
        h_mass_Z = hist.Hist(
            hist.axis.Regular(100, 71, 111, name="mass", label="Mass [GeV]"),
            storage="weight"
        )
        h_mass_JPsi = hist.Hist(
            hist.axis.Regular(75, 2.8, 3.4, name="mass", label="Mass [GeV]"),
            storage="weight"
        )
        h_pt = hist.Hist(
            hist.axis.Regular(100, 0, 100, name="pt", label="Pt [GeV]"),
            storage="weight"
        )
        h_eta = hist.Hist(
            hist.axis.Regular(100, -3, 3, name="eta", label="Eta"),
            storage="weight"
        )
        h_phi = hist.Hist(
            hist.axis.Regular(100, -4, 4, name="phi", label="Mass"),
            storage="weight"
        )
        h_eta_phi = hist.Hist(
            hist.axis.Regular(100, -3, 3, name="eta", label="Eta"),
            hist.axis.Regular(100, -4, 4, name="phi", label="Mass"),
            storage="weight"
        )
        h_dxy = hist.Hist(
            hist.axis.Regular(100, -5, 5, name="dxy", label="dxy"),
            storage="weight"
        )
        h_dxy_recomputed = hist.Hist(
            hist.axis.Regular(100, -5, 5, name="dxy_recomputed", label="dxy_recomputed"),
            storage="weight"
        )
        h_dxy_recomputed_zoom = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="dxy_recomputed_zoom", label="dxy_recomputed_zoom"),
            storage="weight"
        )
        h_dz = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="dz", label="dz"),
            storage="weight"
        )
        h_dz_recomputed = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="dz_recomputed", label="dz_recomputed"),
            storage="weight"
        )
        h_dz_recomputed_zoom = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="dz_recomputed_zoom", label="dz_recomputed_zoom"),
            storage="weight"
        )
        h_pixelLayers = hist.Hist(
            hist.axis.Regular(10, 0, 10, name="pixelLayers", label="Number of pixel layers"),
            storage="weight"
        )
        h_phi_pixelLayers = hist.Hist(
            hist.axis.Regular(100, -4, 4, name="phi", label="Phi"),
            hist.axis.Regular(10, 0, 10, name="pixelLayers", label="Number of pixel layers"),
            storage="weight"
        )
        h_eta_pixelLayers = hist.Hist(
            hist.axis.Regular(100, -3, 3, name="eta", label="Eta"),
            hist.axis.Regular(10, 0, 10, name="pixelLayers", label="Number of pixel layers"),
            storage="weight"
        )
        h_trackerLayers = hist.Hist(
            hist.axis.Regular(20, 0, 20, name="trackerLayers", label="Number of tracker layers"),
            storage="weight"
        )
        h_phi_trackerLayers = hist.Hist(
            hist.axis.Regular(100, -4, 4, name="phi", label="Phi"),
            hist.axis.Regular(20, 0, 20, name="trackerLayers", label="Number of tracker layers"),
            storage="weight"
        )
        h_eta_trackerLayers = hist.Hist(
            hist.axis.Regular(100, -3, 3, name="eta", label="Eta"),
            hist.axis.Regular(20, 0, 20, name="trackerLayers", label="Number of tracker layers"),
            storage="weight"
        )
        # Bin the J/Psi mass in terms of dimuon eta
        h_mass_JPsi_eta = hist.Hist(
            hist.axis.Regular(75, 2.8, 3.4, name="mass", label="Mass [GeV]"),
            hist.axis.Regular(100, -3, 3, name="eta", label="Eta"),
            storage="weight"
        )
        # Extra PV and muon position related quantities
        h_vx = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="vx", label="Muon vx"),
            storage="weight",
        )
        h_vy = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="vy", label="Muon vy"),
            storage="weight",
        )
        h_vz = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="vz", label="Muon vz"),
            storage="weight",
        )
        h_pv_x = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="pv_x", label="PV x"),
            storage="weight",
        )
        h_pv_y = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="pv_y", label="PV y"),
            storage="weight",
        )
        h_pv_z = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="pv_z", label="PV z"),
            storage="weight",
        )
        h_matched_pv_z = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="matched_pv_z", label="Matched PV z"),
            storage="weight",
        )
        h_dxy_recomputed_closestpv = hist.Hist(
            hist.axis.Regular(100, -5, 5, name="dxy_recomputed_closestpv", label="dxy_recomputed_closestpv"),
            storage="weight"
        )
        h_dxy_recomputed_closestpv_zoom = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="dxy_recomputed_closestpv_zoom", label="dxy_recomputed_closestpv_zoom"),
            storage="weight"
        )
        h_dz_recomputed_closestpv = hist.Hist(
            hist.axis.Regular(100, -20, 20, name="dz_recomputed_closestpv", label="dz_recomputed_closestpv"),
            storage="weight"
        )
        h_dz_recomputed_closestpv_zoom = hist.Hist(
            hist.axis.Regular(100, -0.5, 0.5, name="dz_recomputed_closestpv_zoom", label="dz_recomputed_closestpv_zoom"),
            storage="weight"
        )

        # Starting event count
        h_cutflow.fill(cutflow="num_events", cutflow_count=ak.ones_like(events["event"])*0)

        # Luminosity mask
        if self.lumi_mask is not None:
            print("Applying luminosity mask...")
            good_lumi_mask = self.lumi_mask(events.run, events.luminosityBlock)
            events = events[good_lumi_mask]
        h_cutflow.fill(cutflow="num_events_lumi", cutflow_count=ak.ones_like(events["event"])*0)

        # Apply HLT selection
        if self.hltpath is not None:
            events = events[events["DST"][self.hltpath]]
        h_cutflow.fill(cutflow="num_events_hlt", cutflow_count=ak.ones_like(events["event"])*0)

        # Apply L1 selection
        if self.prescalel1:
            for i_l1_trigger, l1_trigger in enumerate(self.l1_triggers):
                if i_l1_trigger == 0:
                    l1_mask = events["L1"][l1_trigger]
                else:
                    l1_mask = l1_mask | events["L1"][l1_trigger]
            events = events[l1_mask]
        h_cutflow.fill(cutflow="num_events_l1", cutflow_count=ak.ones_like(events["event"])*0)

        # Apply just single muon selections
        if self.no_dimuon:
            print(f"\nSingle muon selections")
            events = events[ak.num(events[muon_collection_key]) >= 1]
            # Sort the muons
            muons = events[muon_collection_key]
            muons_pt_order = ak.argsort(muons.pt, axis=1, ascending=False)
            muons = muons[muons_pt_order]
            
            eta_filter = np.abs(muons.eta) < 2.4
            normchi2_filter = muons.normchi2 < 3.0
            muon_filter = eta_filter & normchi2_filter
            print(f"Applying basic filters on muons")
            muons = muons[muon_filter]
            muon_num_filter = ak.num(muons) >= 1 
            events = events[muon_num_filter]
            muons = muons[muon_num_filter]
            muons_selected = muons

            # Fill dummy values for dimuon mass
            h_mass.fill(mass=ak.ones_like(events["event"])*0.0)
            h_mass_Z.fill(mass=ak.ones_like(events["event"])*0.0)
            h_mass_JPsi.fill(mass=ak.ones_like(events["event"])*0.0)
            h_mass_JPsi_eta.fill(mass=ak.ones_like(events["event"])*0.0, eta=ak.ones_like(events["event"])*0.0)
        else:
            print(f"\nDimuon selections")
            events = events[ak.num(events[muon_collection_key]) >= 2]
            # Sort the muons
            muons = events[muon_collection_key]
            muons_pt_order = ak.argsort(muons.pt, axis=1, ascending=False)
            muons = muons[muons_pt_order]
            
            # Apply basic filters on muons (eta and normchi2) and only save events with at least two muons passing selections
            eta_filter = np.abs(muons.eta) < 2.4
            normchi2_filter = muons.normchi2 < 3.0
            muon_filter = eta_filter & normchi2_filter
            print(f"Applying basic filters on muons")
            muons = muons[muon_filter]
            muon_num_filter = ak.num(muons) >= 2 
            events = events[muon_num_filter]
            muons = muons[muon_num_filter]

            # Make dimuon candidates
            dimuons = ak.combinations(muons, 2, fields=["muon_i", "muon_j"])
            dimuons_idx = ak.argcombinations(muons, 2, fields=["muon_i", "muon_j"])
            muon_i, muon_j = ak.unzip(dimuons)
            # Dimuon selections
            dimuon_dr_ij = muon_i.delta_r(muon_j)
            dr_filter = dimuon_dr_ij > 0.1
            os_filter = muon_i.charge != muon_j.charge
            dimuon_filter = dr_filter & os_filter
            dimuons = dimuons[dimuon_filter]
            dimuons_idx = dimuons_idx[dimuon_filter]
            muon_i, muon_j = ak.unzip(dimuons)
            muon_idx_i, muon_idx_j = ak.unzip(dimuons_idx)
            # Get the first dimuon candidate and stitch their indices together
            muon_idx_i_leading = ak.firsts(muon_idx_i)
            muon_idx_j_leading = ak.firsts(muon_idx_j)
            muon_idx_isnone = ak.is_none(muon_idx_i_leading)
            muon_idx_i_leading = muon_idx_i_leading[~muon_idx_isnone]
            muon_idx_j_leading = muon_idx_j_leading[~muon_idx_isnone]
            events = events[~muon_idx_isnone]
            muons = muons[~muon_idx_isnone]

            # Selected muons
            muons_to_select = ak.concatenate([ak.singletons(muon_idx_i_leading), ak.singletons(muon_idx_j_leading)], axis=1)
            local_idx = ak.local_index(muons, axis=1)
            select_mask = ((local_idx == muon_idx_i_leading[:, None]) | (local_idx == muon_idx_j_leading[:, None]))
            muons_selected = muons[select_mask]

            h_cutflow.fill(cutflow="num_events_selection", cutflow_count=ak.ones_like(events["event"])*0)
            
            # Remake the dimuon system and apply a resonance selection if needed
            dimuons = muons_selected[:, 0] + muons_selected[:, 1]
            h_mass.fill(mass=dimuons.mass)
            h_mass_Z.fill(mass=dimuons.mass)
            h_mass_JPsi.fill(mass=dimuons.mass)
            h_mass_JPsi_eta.fill(mass=dimuons.mass, eta=dimuons.eta)

            # Apply a resonance selection if required
            resonance_mask = ak.ones_like(dimuons.mass, dtype=bool)
            if self.resonance_mask == "kshort":
                print("Selecting only dimuons in mass range [0.434, 0.49]")
                resonance_mask = (dimuons.mass > 0.434) & (dimuons.mass < 0.49)
            elif self.resonance_mask == "eta":
                print("Selecting only dimuons in mass range [0.527, 0.573]")
                resonance_mask = (dimuons.mass > 0.527) & (dimuons.mass < 0.573)
            elif self.resonance_mask == "rho":
                print("Selecting only dimuons in mass range [0.748, 0.812]")
                resonance_mask = (dimuons.mass > 0.748) & (dimuons.mass < 0.812)
            elif self.resonance_mask == "jpsi":
                print("Selecting only dimuons in mass range [3.0, 3.2]")
                resonance_mask = (dimuons.mass > 3.0) & (dimuons.mass < 3.2)
            elif self.resonance_mask == "psi2s":
                print("Selecting only dimuons in mass range [3.55, 3.805]")
                resonance_mask = (dimuons.mass > 3.55) & (dimuons.mass < 3.805)
            elif self.resonance_mask == "upsilon":
                print("Selecting only dimuons in mass range [9.9, 10.8]")
                resonance_mask = (dimuons.mass > 9.9) & (dimuons.mass < 10.8)
            elif self.resonance_mask == "z":
                print("Selecting only dimuons in mass range [71, 111]")
                resonance_mask = (dimuons.mass > 71) & (dimuons.mass < 111)
            elif self.resonance_mask == "all":
                print("Using OR of dimuon resonances: kshort, eta, rho, jpsi, psi2s, upsilon, z")
                resonance_mask = (
                    ((dimuons.mass > 0.434) & (dimuons.mass < 0.49)) |
                    ((dimuons.mass > 0.527) & (dimuons.mass < 0.573)) |
                    ((dimuons.mass > 0.748) & (dimuons.mass < 0.812)) |
                    ((dimuons.mass > 3.0) & (dimuons.mass < 3.2)) |
                    ((dimuons.mass > 3.55) & (dimuons.mass < 3.805)) |
                    ((dimuons.mass > 9.9) & (dimuons.mass < 10.8)) |
                    ((dimuons.mass > 71) & (dimuons.mass < 111))
                )
            else:
                resonance_mask = ak.ones_like(dimuons.mass, dtype=bool)

            events = events[resonance_mask]
            muons_selected = muons_selected[resonance_mask]
            dimuons = dimuons[resonance_mask]

        # Recompute the dxy and dz using given recipe
        pvs = events["ScoutingPrimaryVertex"][:, 0]
        trk_eta = muons_selected.trk_eta
        trk_phi = muons_selected.trk_phi
        trk_pt = muons_selected.trk_pt
        trk_px = trk_pt * np.cos(trk_phi)
        trk_py = trk_pt * np.sin(trk_phi)
        trk_pz = trk_pt * np.sinh(trk_eta)
        trk_pt2 = trk_pt**2
        trk_dx = muons_selected.trk_vx - pvs.x
        trk_dy = muons_selected.trk_vy - pvs.y
        trk_dz = muons_selected.trk_vz - pvs.z
        trk_dxy_recomputed = ((-trk_dx * trk_py) + (trk_dy * trk_px)) / trk_pt
        trk_dz_recomputed = trk_dz - ((trk_dx * trk_px) + (trk_dy * trk_py)) * (trk_pz / trk_pt2)


        # Fill histograms
        h_nmuon.fill(nmuon=ak.num(events[muon_collection_key].pt))
        h_pt.fill(pt=ak.flatten(muons_selected.pt))
        h_eta.fill(eta=ak.flatten(muons_selected.eta))
        h_phi.fill(phi=ak.flatten(muons_selected.phi))
        h_eta_phi.fill(eta=ak.flatten(muons_selected.eta), phi=ak.flatten(muons_selected.phi))
        h_dxy.fill(dxy=ak.flatten(muons_selected.trk_dxy))
        h_dxy_recomputed.fill(dxy_recomputed=ak.flatten(trk_dxy_recomputed))
        h_dxy_recomputed_zoom.fill(dxy_recomputed_zoom=ak.flatten(trk_dxy_recomputed))
        h_dz.fill(dz=ak.flatten(muons_selected.trk_dz))
        h_dz_recomputed.fill(dz_recomputed=ak.flatten(trk_dz_recomputed))
        h_dz_recomputed_zoom.fill(dz_recomputed_zoom=ak.flatten(trk_dz_recomputed))
        h_pixelLayers.fill(pixelLayers=ak.flatten(muons_selected.nPixelLayersWithMeasurement))
        h_phi_pixelLayers.fill(phi=ak.flatten(muons_selected.phi), pixelLayers=ak.flatten(muons_selected.nPixelLayersWithMeasurement))
        h_eta_pixelLayers.fill(eta=ak.flatten(muons_selected.eta), pixelLayers=ak.flatten(muons_selected.nPixelLayersWithMeasurement))
        h_trackerLayers.fill(trackerLayers=ak.flatten(muons_selected.nTrackerLayersWithMeasurement))
        h_phi_trackerLayers.fill(phi=ak.flatten(muons_selected.phi), trackerLayers=ak.flatten(muons_selected.nTrackerLayersWithMeasurement))
        h_eta_trackerLayers.fill(eta=ak.flatten(muons_selected.eta), trackerLayers=ak.flatten(muons_selected.nTrackerLayersWithMeasurement))
        h_vx.fill(vx=ak.flatten(muons_selected.trk_vx))
        h_vy.fill(vy=ak.flatten(muons_selected.trk_vy))
        h_vz.fill(vz=ak.flatten(muons_selected.trk_vz))
        h_pv_x.fill(pv_x=pvs.x)
        h_pv_y.fill(pv_y=pvs.y)
        h_pv_z.fill(pv_z=pvs.z)


        # Recalculate the above for the closest PV in distance (this causes the condor jobs to be on hold)
        muon_pv_pair = ak.cartesian({"muon": muons_selected, "pv": events["ScoutingPrimaryVertex"]}, nested=True)
        muon_pv_pair_args = ak.argcartesian({"muon": muons_selected, "pv": events["ScoutingPrimaryVertex"]}, nested=True)
        muon_pv_pair_dist = np.sqrt(
            (muon_pv_pair.muon.trk_vx - muon_pv_pair.pv.x)**2 + \
            (muon_pv_pair.muon.trk_vy - muon_pv_pair.pv.y)**2 + \
            (muon_pv_pair.muon.trk_vz - muon_pv_pair.pv.z)**2
        )
        muon_pv_pair_dist_order = ak.argsort(muon_pv_pair_dist, axis=2, ascending=True)
        muon_pv_pair = muon_pv_pair[muon_pv_pair_dist_order]
        muon_pv_pair_args = muon_pv_pair_args[muon_pv_pair_dist_order]
        muon_pv_pair_muons, muon_pv_pair_pvs = ak.unzip(muon_pv_pair)
        muon_pv_pair_muons = muon_pv_pair_muons[:, :, 0]
        muon_pv_pair_pvs = muon_pv_pair_pvs[:, :, 0]
        muon_pv_pair_muons_pt = muon_pv_pair_muons.trk_pt
        muon_pv_pair_muons_px = muon_pv_pair_muons_pt * np.cos(muon_pv_pair_muons.trk_phi)
        muon_pv_pair_muons_py = muon_pv_pair_muons_pt * np.sin(muon_pv_pair_muons.trk_phi)
        muon_pv_pair_muons_pz = muon_pv_pair_muons_pt * np.sinh(muon_pv_pair_muons.trk_eta)
        muon_pv_pair_muons_pt2 = muon_pv_pair_muons_pt**2
        trk_dx_closestpv = muon_pv_pair_muons.trk_vx - muon_pv_pair_pvs.x
        trk_dy_closestpv = muon_pv_pair_muons.trk_vy - muon_pv_pair_pvs.y
        trk_dz_closestpv = muon_pv_pair_muons.trk_vz - muon_pv_pair_pvs.z
        trk_dxy_recomputed_closestpv = ((-trk_dx_closestpv * muon_pv_pair_muons_py) + (trk_dy_closestpv * muon_pv_pair_muons_px)) / muon_pv_pair_muons_pt
        trk_dz_recomputed_closestpv = trk_dz_closestpv - ((trk_dx_closestpv * muon_pv_pair_muons_px) + (trk_dy_closestpv * muon_pv_pair_muons_py)) * (muon_pv_pair_muons_pz / (muon_pv_pair_muons_pt**2))

        h_dxy_recomputed_closestpv.fill(dxy_recomputed_closestpv=ak.flatten(trk_dxy_recomputed_closestpv))
        h_dxy_recomputed_closestpv_zoom.fill(dxy_recomputed_closestpv_zoom=ak.flatten(trk_dxy_recomputed_closestpv))
        h_dz_recomputed_closestpv.fill(dz_recomputed_closestpv=ak.flatten(trk_dz_recomputed_closestpv))
        h_dz_recomputed_closestpv_zoom.fill(dz_recomputed_closestpv_zoom=ak.flatten(trk_dz_recomputed_closestpv))
        h_matched_pv_z.fill(matched_pv_z=ak.flatten(muon_pv_pair_pvs.z))

        return {
            "cutflow": h_cutflow,
            "nmuon": h_nmuon,
            "mass": h_mass,
            "mass_Z": h_mass_Z,
            "mass_JPsi": h_mass_JPsi,
            "pt": h_pt,
            "eta": h_eta,
            "phi": h_phi,
            "eta_phi": h_eta_phi,
            "dxy": h_dxy,
            "dxy_recomputed": h_dxy_recomputed,
            "dxy_recomputed_zoom": h_dxy_recomputed_zoom,
            "dz": h_dz,
            "dz_recomputed": h_dz_recomputed,
            "dz_recomputed_zoom": h_dz_recomputed_zoom,
            "pixelLayers": h_pixelLayers,
            "phi_pixelLayers": h_phi_pixelLayers,
            "eta_pixelLayers": h_eta_pixelLayers,
            "trackerLayers": h_trackerLayers,
            "phi_trackerLayers": h_phi_trackerLayers,
            "eta_trackerLayers": h_eta_trackerLayers,
            "mass_JPsi_eta": h_mass_JPsi_eta,
            "vx": h_vx,
            "vy": h_vy,
            "vz": h_vz,
            "pv_x": h_pv_x,
            "pv_y": h_pv_y,
            "pv_z": h_pv_z,
            "matched_pv_z": h_matched_pv_z,
            "dxy_recomputed_closestpv": h_dxy_recomputed_closestpv,
            "dxy_recomputed_closestpv_zoom": h_dxy_recomputed_closestpv_zoom,
            "dz_recomputed_closestpv": h_dz_recomputed_closestpv,
            "dz_recomputed_closestpv_zoom": h_dz_recomputed_closestpv_zoom,
        }

    def postprocess(self, accumulator):
        pass

def main():
    parser = argparse.ArgumentParser("Script that plots muons with trigger and quality selections applied (optionally also dimuon info)")
    parser.add_argument("--infile", type=str, nargs="+", help="Input files")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    parser.add_argument("--redirector", "-r", type=str, help="XRootD redirector (e.g., root://xrootd-cms.infn.it/)")
    # Processor specific
    parser.add_argument("--hltpath", type=str, help="HLT path to select events with (eg. DST_PFScouting_DoubleMuonVtx)")
    parser.add_argument("--prescalel1", action="store_true", help="Select only events that pass unprescaled L1 seeds")
    parser.add_argument("--useVtx", action="store_true", help="Use vtx muons")
    parser.add_argument("--resonance_mask", type=str, help="Resonance mask applied to dimuons (eg. jpsi)")
    parser.add_argument("--no_dimuon", action="store_true", help="Selections do not use dimuons")
    parser.add_argument("--lumi_mask", type=str, help="Path to luminosity mask if exists")
    parser.add_argument("--year", type=int, default=2024, help="Data year (for naming Scouting Muon type)")
    # Dask related 
    parser.add_argument("--daskcondor", action="store_true", help="Use dask for processing (Do not use if individual job is on condor)")
    parser.add_argument("--daskcluster", type=str, choices=['lxplus', 'lxic'], default='lxic', help="Cluster type to use for dask (default: lxic)")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile 
    outfile = args.outfile
    hltpath = args.hltpath
    prescalel1 = args.prescalel1
    useVtx = args.useVtx
    resonance_mask = args.resonance_mask
    no_dimuon = args.no_dimuon
    lumi_mask = args.lumi_mask
    dask_condor = args.daskcondor
    dask_cluster = args.daskcluster

    # Input is a text file 
    if (len(infile) == 0) and (".txt" in infile[0]):
        print(f"{infile} is a text file, searching for files to add to filelist")
        infile_txt = infile[0]
        infile = []
        with open(infile_txt, 'r') as f:
            for line in f:
                file_path = line.strip()
                if file_path:  # Skip empty lines
                    if args.redirector is not None:
                        filename_i = f"{args.redirector}{file_path}"
                    else:
                        filename_i = file_path
                    infile.append(filename_i)

    print(f"Processing files: {infile}")
    fileset = {"2025": infile}

    # Default client
    client = Client()

    # If using dask over condor
    if dask_condor:
        print(f"\nUsing dask itself for condor scheduling")
        os.makedirs(f"{cwd}/dask_logs", exist_ok=True)

        # Environment related settings
        env_extra = [
            f"cd {cwd}",
            "source /home/hep/pb4918/cms_source.sh",
            "source /home/hep/pb4918/mambainit.sh",
            "micromamba activate coffea_env",
            f"export X509_USER_PROXY=proxy",
        ]

        if dask_cluster == 'lxplus':
            print("Using lxplus Dask cluster")

            if not check_port(60000):
                raise RuntimeError(
                    f"Port '60000' is now occupied on this node. Try another one."
                )

            from dask_lxplus import CernCluster
            cluster =  CernCluster(
                cores=1,
                memory='3GB',
                disk='10GB',
                death_timeout = '60',
                lcg = False,
                nanny = False,
                container_runtime = "none",
                log_directory = "/eos/user/p/ppradeep/HLTScouting/MuonPOG/CMSSW_15_0_8/src/MuonDST-Framework/logs",
                scheduler_options={
                    'port': 8786,
                    'host': socket.gethostname(),
                    },
                job_extra={
                    '+JobFlavour': '"longlunch"',
                    },
                extra = ['--worker-port 10000:10100'],
                python=sys.executable,
                worker_command="distributed.cli.dask_worker",
                job_script_prologue=env_extra,
            )
            cluster.adapt(minimum=6, maximum=250)
            print(cluster.job_script())
            client = Client(cluster)
            client.wait_for_workers(1)

        elif dask_cluster == 'iclx':
            print("Using iclx Dask cluster")

            if not check_port(8786):
                raise RuntimeError(
                    f"Port '8786' is now occupied on this node. Try another one."
                )

            from dask_iclx import ICCluster
            cluster = ICCluster(
                cores = 1,
                memory = '3000MB',
                disk = '10GB',
                death_timeout = '60',
                lcg = False,
                nanny = False,
                container_runtime = 'none',
                log_directory = f'{cwd}/dask_logs',
                scheduler_options = {
                    'port': 60000,
                    'host': socket.gethostname(),
                    'dashboard_address': ':8787',
                },
                job_extra = {
                    "+MaxRuntime": "7199",
                },
                name="ClusterName",
                job_script_prologue=env_extra,
            ) 
            cluster.adapt(minimum=6, maximum=250)
            print(cluster.job_script())
            client = Client(cluster)
            client.wait_for_workers(1)

        else:
            print(f"Unknown exception: --daskcondor enabled yet invalid cluster choice")

    print(f"Dask Client: {client}")


    processor_instance = MonitoringProcessor(hltpath=hltpath, prescalel1=prescalel1, useVtx=useVtx, resonance_mask=resonance_mask, no_dimuon=no_dimuon, lumi_mask=lumi_mask)
    executor = processor.DaskExecutor(client=client, retries=3)
    run = processor.Runner(
        executor=executor,
        schema=ScoutingNanoAODSchema,
        xrootdtimeout=60,
        chunksize=500000,
    )
    output = run(
        fileset,
        treename="Events",
        processor_instance=processor_instance,
    )

    print(output)

    # All the keys in the output are histograms
    print(f"\nSaving output to {outfile}")
    with uproot.recreate(outfile) as f:
        for key, hist in output.items():
            f[key] = hist

if __name__ == "__main__":
    main()