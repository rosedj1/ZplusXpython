"""Select 2P2+F and 3P1+F events and add new branches to TTree in new file.
==============================================================================
Author: Jake Rosenzweig
Created: 2021-11-30
Updated: 2021-12-13
Notes: This code makes a json file which stores the Run:Lumi:Event of all
  events which pass 3T1L or 2T2L event selection. It also creates a TH2
  of per-event 3T1L 4-lep combos vs. per-event 2T2L 4-lep combos and stores
  the hist in a root file. You can draw the TH2 with:
      `draw_th2_plots.py`
  
===============================================

NOTE:
    Uses updated event selection which bypasses passedZXCRSelection.

New branches added:
- is2P2F : int
- is3P1F : int
- isMCzz : int
- weightwithFRratios : float
    For 3P1F: event.eventWeight * (fr / (1-fr))
    For 2P2F: event.eventWeight * (fr2 / (1-fr2)) * (fr3 / (1-fr3))
    NOTE: 
        Data returns events with old_calculated_weight = 1.
        ZZ has NTuple eventWeight scaled by k_qqZZ_qcd_M * k_qqZZ_ewk * xs * LUMI_INT / sum_weights
"""
import os
from ROOT import TFile
import argparse
# Local modules.
from sidequests.funcs.evt_loops import (
    evt_loop_evtsel_2p2plusf3p1plusf_subevents
    )
from sidequests.data.filepaths import (
    infile_filippo_data_2018_fromhpg,
    mc_2018_zz_hpg
    )
from Utils_Python.Utils_Files import check_overwrite
from Utils_Python.Commands import shell_cmd

# Files to analyze.
d_nicknames_files = {
    "Data" : infile_filippo_data_2018_fromhpg,
    "ZZ" : mc_2018_zz_hpg,
}

int_lumi = 59830
year = 2018
explain_skipevent = 0
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 500000

fill_hists = 1
hadd_files = 1
smartcut_ZapassesZ1sel = False  # Literature sets this to False.

# infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZLL_CR/Data_2018_NoDuplicates.root"
# Little difference between using lepFSR and not, when reconstructing mZ1:
infile_FR_wz_removed = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/uselepFSRtocalc_mZ1/Hist_Data_ptl3_WZremoved.root"

outdir = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/"
# These base names will have name of data type appended ("Data", "ZZ").
outfile_base_root = "rootfiles/test/cjlstOSmethodevtsel_2p2plusf_3p1plusf_mass4lgt0_fixfr3.root"
outfile_base_json = "json/test/cjlstOSmethodevtsel_2p2plusf_3p1plusf_mass4lgt0_fixfr3_counter.json"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-i', '--infile',          type=str, dest="infile", help="input root file")
    # parser.add_argument('-r', '--infile_fakerate', type=str, dest="infile_fr", help="input root file with fake rate hists (WZ removed)")
    # parser.add_argument('-o', '--outfile',         type=str, dest="outfile", help="output rootfile")
    # parser.add_argument('-n', '--nickname',        type=str, dest="name", help="nickname of file/process ('ZZ' or 'Data')")
    parser.add_argument('-x', '--overwrite',       dest="overwrite", action="store_true", help="overwrite output file (1) or not (0)")
    parser.add_argument('-v', '--verbose',       dest="verbose", action="store_true", help="verbose output (1) or not (0)")
    args = parser.parse_args()

    # infile = args.infile
    # infile_FR_wz_removed = args.infile_fr
    # outfile_root = args.outfile
    # name = args.name
    overwrite = args.overwrite
    verbose = args.verbose

    if hadd_files:
        # Store the hadded file at the same place as input files.
        all_names = '_'.join(d_nicknames_files.keys())
        new_filename = outfile_base_root.replace(
                        ".root",
                        f"_{all_names}.root"
                        )
        outfile_hadd = os.path.join(outdir, new_filename)
        check_overwrite(outfile_hadd, overwrite=overwrite)

    ls_all_outfiles = []
    for name, inpath in d_nicknames_files.items():

        ending = f"{year}_{name}"
        new_base_json = outfile_base_json.replace(".json", f"_{ending}.json")
        new_base_root = outfile_base_root.replace(".root", f"_{ending}.root")
        outfile_json = os.path.join(outdir, new_base_json)
        outfile_root = os.path.join(outdir, new_base_root)
        
        # If the given root file path is an absolute path, make sure dir exists.
        if "/" in outfile_root:
            os.makedirs(
                os.path.dirname(outfile_root), exist_ok=True
                )

        infile = TFile.Open(inpath, "read")
        tree = infile.Get("passedEvents")
        print(
            f"Successfully opened:\n{inpath}\n"
            f"  Processing: year={year}, name={name}"
            )

        evt_loop_evtsel_2p2plusf3p1plusf_subevents(
            tree,
            infile_FR_wz_removed=infile_FR_wz_removed,
            outfile_root=outfile_root, outfile_json=outfile_json,
            name=name, int_lumi=int_lumi,
            start_at_evt=start_at_evt, break_at_evt=break_at_evt,
            fill_hists=fill_hists,
            explain_skipevent=explain_skipevent,
            verbose=verbose, print_every=print_every,
            smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
            overwrite=overwrite
            )
        
        ls_all_outfiles.append(outfile_root)

    # End loop over analyzer.
    if hadd_files:
        all_outfiles = ' '.join(ls_all_outfiles)
        shell_cmd(f"hadd -f {outfile_hadd} {all_outfiles}")
