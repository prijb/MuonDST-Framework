# Inclusive version of make_2025Performance.py (literally no selections, not even trigger)
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
    def __init__(self, useVtx=False, lumi_mask=None):
        self.useVtx = useVtx

        self.muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"
        self.lumi_mask = LumiMask(lumi_mask) if lumi_mask is not None else None

        # Debug
        print("\nProcessor initialised with following attributes")
        print(f"Muon collection: {self.muon_collection_key}")
        if lumi_mask is not None: print(f"Lumi mask applied from {lumi_mask}")

    def process(self, events):
        muon_collection_key = self.muon_collection_key
        cutflow_axis = hist.axis.StrCategory([], growth=True, name="cutflow", label="Cutflow")
        h_cutflow = hist.Hist(
            cutflow_axis, 
            hist.axis.Regular(1, 0, 1, name="cutflow_count", label="Count"), 
            storage="weight", 
            label="Counts"
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
        h_cutflow.fill(cutflow="num_events", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuonVtx"])*0)

        # Luminosity mask
        if self.lumi_mask is not None:
            print("Applying luminosity mask...")
            good_lumi_mask = self.lumi_mask(events.run, events.luminosityBlock)
            events = events[good_lumi_mask]
        h_cutflow.fill(cutflow="num_events_lumi", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuonVtx"])*0)


        events = events[ak.num(events[muon_collection_key]) >= 1]
        # Sort the muons
        muons = events[muon_collection_key]
        muons_pt_order = ak.argsort(muons.pt, axis=1, ascending=False)
        muons = muons[muons_pt_order]

        h_cutflow.fill(cutflow="num_events_selection", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuonVtx"])*0)

        # Recompute the dxy and dz using given recipe
        pvs = events["ScoutingPrimaryVertex"][:, 0]
        trk_eta = muons.trk_eta
        trk_phi = muons.trk_phi
        trk_pt = muons.trk_pt
        trk_px = trk_pt * np.cos(trk_phi)
        trk_py = trk_pt * np.sin(trk_phi)
        trk_pz = trk_pt * np.sinh(trk_eta)
        trk_pt2 = trk_pt**2
        trk_dx = muons.trk_vx - pvs.x
        trk_dy = muons.trk_vy - pvs.y
        trk_dz = muons.trk_vz - pvs.z
        trk_dxy_recomputed = ((-trk_dx * trk_py) + (trk_dy * trk_px)) / trk_pt
        trk_dz_recomputed = trk_dz - ((trk_dx * trk_px) + (trk_dy * trk_py)) * (trk_pz / trk_pt2)


        # Fill histograms
        h_pt.fill(pt=ak.flatten(muons.pt))
        h_eta.fill(eta=ak.flatten(muons.eta))
        h_phi.fill(phi=ak.flatten(muons.phi))
        h_eta_phi.fill(eta=ak.flatten(muons.eta), phi=ak.flatten(muons.phi))
        h_dxy.fill(dxy=ak.flatten(muons.trk_dxy))
        h_dxy_recomputed.fill(dxy_recomputed=ak.flatten(trk_dxy_recomputed))
        h_dxy_recomputed_zoom.fill(dxy_recomputed_zoom=ak.flatten(trk_dxy_recomputed))
        h_dz.fill(dz=ak.flatten(muons.trk_dz))
        h_dz_recomputed.fill(dz_recomputed=ak.flatten(trk_dz_recomputed))
        h_dz_recomputed_zoom.fill(dz_recomputed_zoom=ak.flatten(trk_dz_recomputed))
        h_pixelLayers.fill(pixelLayers=ak.flatten(muons.nPixelLayersWithMeasurement))
        h_phi_pixelLayers.fill(phi=ak.flatten(muons.phi), pixelLayers=ak.flatten(muons.nPixelLayersWithMeasurement))
        h_eta_pixelLayers.fill(eta=ak.flatten(muons.eta), pixelLayers=ak.flatten(muons.nPixelLayersWithMeasurement))
        h_trackerLayers.fill(trackerLayers=ak.flatten(muons.nTrackerLayersWithMeasurement))
        h_phi_trackerLayers.fill(phi=ak.flatten(muons.phi), trackerLayers=ak.flatten(muons.nTrackerLayersWithMeasurement))
        h_eta_trackerLayers.fill(eta=ak.flatten(muons.eta), trackerLayers=ak.flatten(muons.nTrackerLayersWithMeasurement))
        h_vx.fill(vx=ak.flatten(muons.trk_vx))
        h_vy.fill(vy=ak.flatten(muons.trk_vy))
        h_vz.fill(vz=ak.flatten(muons.trk_vz))
        h_pv_x.fill(pv_x=pvs.x)
        h_pv_y.fill(pv_y=pvs.y)
        h_pv_z.fill(pv_z=pvs.z)


        # Recalculate the above for the closest PV in distance (this causes the condor jobs to be on hold)
        muon_pv_pair = ak.cartesian({"muon": muons, "pv": events["ScoutingPrimaryVertex"]}, nested=True)
        muon_pv_pair_args = ak.argcartesian({"muon": muons, "pv": events["ScoutingPrimaryVertex"]}, nested=True)
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
    parser = argparse.ArgumentParser("Dummy script that just returns a histogram with the total number of events in the dataset")
    parser.add_argument("--infile", type=str, nargs="+", help="Input files")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    # Processor specific
    parser.add_argument("--useVtx", action="store_true", help="Use vtx muons")
    parser.add_argument("--lumi_mask", type=str, help="Path to luminosity mask if exists")
    # Dask related 
    parser.add_argument("--daskcondor", action="store_true", help="Use dask for processing (Do not use if individual job is on condor)")
    parser.add_argument("--daskcluster", type=str, choices=['lxplus', 'lxic'], default='lxic', help="Cluster type to use for dask (default: lxic)")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile 
    outfile = args.outfile
    useVtx = args.useVtx
    lumi_mask = args.lumi_mask
    dask_condor = args.daskcondor
    dask_cluster = args.daskcluster

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

        if args.cluster == 'lxplus':
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

        elif args.cluster == 'iclx':
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


    processor_instance = MonitoringProcessor(useVtx=useVtx, lumi_mask=lumi_mask)
    executor = processor.DaskExecutor(client=client, retries=10)
    run = processor.Runner(
        executor=executor,
        schema=ScoutingNanoAODSchema,
        xrootdtimeout=300,
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