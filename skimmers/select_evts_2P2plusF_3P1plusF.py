"""Select 2P2+F and 3P1+F events and add new branches to TTree in new file.
==============================================================================
Author: Jake Rosenzweig
Created: 2021-11-30
Updated: 2021-12-09
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
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from Utils_Python.Utils_Files import check_overwrite

explain_skipevent = 0
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 250000
fill_hists = 0
smartcut_ZapassesZ1sel = False  # Literature sets this to False.

# infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZLL_CR/Data_2018_NoDuplicates.root"
# Little difference between using lepFSR and not, when reconstructing mZ1:
infile_FR_wz_removed = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/uselepFSRtocalc_mZ1/Hist_Data_ptl3_WZremoved.root"

outdir = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/"
outfile_base_root = "tests/h2_cjlstOSmethodevtsel_2p2plusf_3p1plusf_ONLYFIRSTZZCAND.root"
outfile_base_json = "tests/cjlstOSmethodevtsel_2p2plusf_3p1plusf_ONLYFIRSTZZCAND.json"

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

    outfile_json = os.path.join(outdir, outfile_base_json)
    outfile_root = os.path.join(outdir, outfile_base_root)
    
    # If the given root file path is an absolute path, make sure dir exists.
    if "/" in outfile_root:
        os.makedirs(
            os.path.dirname(outfile_root), exist_ok=True
            )

    f_filippo_data2018 = TFile.Open(infile_filippo_data_2018_fromhpg)
    tree = f_filippo_data2018.Get("passedEvents")
    print(f"Successfully opened:\n{infile_filippo_data_2018_fromhpg}")

    evt_loop_evtsel_2p2plusf3p1plusf_subevents(
        tree,
        infile_FR_wz_removed=infile_FR_wz_removed,
        outfile_root=outfile_root, outfile_json=outfile_json,
        name="Data",
        start_at_evt=start_at_evt, break_at_evt=break_at_evt,
        fill_hists=fill_hists, explain_skipevent=explain_skipevent, verbose=verbose,
        print_every=print_every, smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
        overwrite=overwrite
        )

