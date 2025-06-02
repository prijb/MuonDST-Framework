import os
import sys
import json
import uproot
import numpy as np
import awkward as ak
import optparse
helper_path = os.path.join(os.getcwd(), "macros/include")
if os.path.isdir(helper_path):
    sys.path.append(helper_path)
else:
    raise Exception("Note: The script must be run from the main dir")
from helper import helper

class Skimmer:
    def __init__(self, json_file="job_new.json", in_file=["NanoAOD.root"], index=0, golden_json=False):
        self.json_file = json_file
        self.in_file= in_file
        self.index = index
        self.golden_json = golden_json
        if golden_json:
            self.read_golden()
        self.read_json()
        self.process()

    def read_json(self):
        with open(self.json_file) as read_file:
            self.json_data = json.load(read_file)
        self.objects = self.json_data["objects"]
        self.triggers = self.json_data["triggers"]
        self.unprefs = []
        self.defaults = []
        self.defaults.extend(self.unprefs)
        self.defaults.extend(["event", "run", "luminosityBlock"])

    def read_golden(self):
        with open(self.golden_json) as read_file:
            self.golden_data = json.load(read_file)

        self.valid_runs = set()
        for run_str, lumi_ranges in self.golden_data.items():
            run = int(run_str)
            for lumi_start, lumi_end in lumi_ranges:
                for lumi in range(lumi_start, lumi_end + 1):
                    self.valid_runs.add((run, lumi))

        print("Selected runs and lumis from golden_json")
        #print(self.valid_runs[:20])
        
    def process(self):
        output = "/eos/user/f/fernance/DST-Muons/skims"
        out_file = f"{output}/skimmed_{self.index}_{self.in_file[0].split('/')[-1]}"
        out_file = out_file.replace('\n', '')
        write_file = uproot.recreate(out_file, compression=uproot.LZMA(1))
        kept = {}
        for file in self.in_file:
            print("Analyzing file: ", file)
            os.system(f"xrdcp {file} .")
            open_file = uproot.open(file.split('/')[-1])
            in_tree = open_file["Events"]
            branches = in_tree.keys()
            print(f"""Initial number of events: {len(in_tree["run"].array())}""")

            if self.golden_json:
                print("Applying golden json")
                MASK_golden = False
                in_tree_runs = ak.to_numpy(in_tree["run"].array())
                in_tree_lmsc = ak.to_numpy(in_tree["luminosityBlock"].array())
                MASK_golden = np.array([(r, l) in self.valid_runs for r, l in zip(in_tree_runs, in_tree_lmsc)])
            else:
                print("Not applying golden json")
                MASK_golden = True

            MASK_trigger = False
            for trigger in self.triggers:
                MASK_trigger = (MASK_trigger | in_tree[trigger].array())

            MASK = (MASK_trigger & MASK_golden)

            to_keep = {}

            for d in self.defaults:
                for b in branches:
                    if b.startswith(d):
                        to_keep[b] = in_tree[b].array()[MASK]

            for o in self.objects.keys():
                object_branches = []
                for b in self.objects[o]:
                    object_branches.append(o + "_" + b)
                to_keep[o] = ak.zip({ob.replace(f"{o}_", "") : in_tree[ob].array()[MASK] for ob in object_branches})

            for t in self.triggers:
                for b in branches:
                    if b == t:
                        to_keep[b] = in_tree[b].array()[MASK]

            for b in to_keep:
                if b not in kept:
                    kept[b] = to_keep[b]
                else:
                    kept[b] = ak.concatenate([kept[b], to_keep[b]])

            print(f"""Skimmed number of events: {len(to_keep["run"])}""")
            os.system(f"rm {file.split('/')[-1]}")

        print("Printing out objects/variables to keep")
        for k, b in to_keep.items():
            print(f"  {k}")

        write_file["Events"] = kept

if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog [opts] FilenameWithSamples', version='%prog 1.0')
    parser.add_option('--dataset', action='store', type=str,  dest='dataset', default='', help='Input dataset')
    parser.add_option('--redirector', action='store', type=str,  dest='redirector', default='root://xrootd-cms.infn.it', help='Redirector to use to access the samples')
    parser.add_option('--input', action='store', type=str,  dest='input', default='', help='List of files')
    parser.add_option('-s', '--step', action='store', type=int,  dest='step', default=0, help='Step file')
    parser.add_option('-n', '--number', action='store', type=int,  dest='number', default=0, help='Number of files for given step')
    (opts, args) = parser.parse_args()

    dataset = opts.dataset
    redirector = opts.redirector
    step = opts.step
    number = opts.number
    input_file = opts.input

    if input_file=='':
        help = helper(dataset, True, redirector)
        files = help.getFiles(step, number) 
    else:
        with open(input_file, 'r') as f:
            files = [redirector +'/' + _ for _ in f.readlines()]
            if number:
                files = files[step*number:number*(step+1)]
    print(f"We have {len(files)} files to read")

    golden_file="/eos/user/c/cmsdqm/www/CAF/certification/Collisions25/DCSOnly_JSONS/dailyDCSOnlyJSON/Collisions25_13p6TeV_Latest.json"

    Skimmer(in_file=files, index=opts.step, golden_json=golden_file)


