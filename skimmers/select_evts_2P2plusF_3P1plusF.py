"""Select 2P2+F and 3P1+F events. Add new branches to TTree in new file.
#=============================================================================
# Syntax:
#   python <this_script>.py
#   Flags:
#       -x : overwrite existing files
#       -v : verbose output
# Notes:
#   This code selects 2P2+F and 3P1+F reducible background events.
#   It considers events with >4 leptons and properly handles all possible
#   lepton quartets. Each passing quartet is saved as an entry in a new
#   TTree. The BBF HZZ Analyzer does not yet do handle same-event quartets.
#   The input files for this script should be root files produced from the
#   BBF HZZ Analyzer.
# 
#   In effect this is an updated event selection that bypasses the branches:
#       - passedZXCRSelection
#       - nZXCRFailedLeptons
# 
#   This code makes a json file which stores the Run:Lumi:Event of all
#   events which pass 3P1F or 2P2F event selection. It also creates a TH2
#   of per-event 3P1F 4-lep quartets vs. per-event 2P2F 4-lep quartets and
#   writes the hist in a root file. You can draw the TH2 with:
#       `draw_th2_plots.py`
#     
#   User should review the parameters located just after the imports.
# 
#   New branches added to TTree:
#         TODO: Update this list of new branches.
#       - is2P2F        (int)
#       - is3P1F        (int)
#       - isMCzz        (int)
#       - fr2           (float)
#       - fr3           (float)
#       - eventWeightFR (float)
# 
# is2P2F
# is3P1F
# isData
# isMCzz
# fr2_down
# fr2
# fr2_up
# fr3_down
# fr3
# fr3_up
# eventWeightFR_down
# eventWeightFR
# eventWeightFR_up
#             "lep_RedBkgindex
# 
#         NOTE: 
#         For 3P1F: event.eventWeight * (fr / (1-fr))
#         For 2P2F: event.eventWeight * (fr2 / (1-fr2)) * (fr3 / (1-fr3))
#             Data returns events with old_calculated_weight = 1.
#             ZZ has NTuple eventWeight scaled by:
#                 k_qqZZ_qcd_M * k_qqZZ_ewk * xs * LUMI_INT / sum_weights
#     - lep_RedBkgindex (int arr[4])
# Author: Jake Rosenzweig
# Created: 2021-11-30
# Updated: 2022-03-03
#=============================================================================
"""
import os
import argparse
from ROOT import TFile
# Local modules.
from sidequests.funcs.evt_loops import (
    evt_loop_evtsel_2p2plusf3p1plusf_subevents
    )
from sidequests.data.filepaths import (
    data_2016_UL_ge4lepskim,
    data_2017_UL, data_2017_UL_ge3lepskim, data_2017_UL_ge4lepskim,
    data_2018_UL, data_2018_UL_ge3lepskim, data_2018_UL_ge4lepskim,
    mc_2016_UL_ZZ_ge4lepskim,
    mc_2017_UL_ZZ, mc_2017_UL_ZZ_ge3lepskim,
    mc_2018_UL_ZZ, mc_2018_UL_ZZ_ge3lepskim,
    # infile_filippo_data_2018_fromhpg,
    # infile_filippo_zz_2018_fromhpg,
    # mc_2018_zz_hpg,
    fakerates_WZremoved_2017_UL,
    fakerates_WZremoved_2018_UL,
    fakerates_WZremoved_2016_UL_woFSR,
    fakerates_WZremoved_2017_UL_woFSR,
    fakerates_WZremoved_2018_UL_woFSR
    )
from Utils_Python.Utils_Files import check_overwrite
from Utils_Python.Commands import shell_cmd
from constants.analysis_params import (
    LUMI_INT_2016_UL, LUMI_INT_2017_UL, LUMI_INT_2018_UL,
    dct_sumgenweights_2016_UL,
    dct_sumgenweights_2017_UL,
    dct_sumgenweights_2018_UL,
    # n_sumgenweights_dataset_dct_jake,
    # n_sumgenweights_dataset_dct_filippo,
    dct_xs_jake
    )

#########################
#--- User Parameters ---#
#########################
# Files to analyze.
d_nicknames_files = {
    # 'Data': data_2016_UL_ge4lepskim,
    # 'ZZ': mc_2016_UL_ZZ,
    'ZZ': mc_2016_UL_ZZ_ge4lepskim,

    # 'Data': data_2017_UL,
    # 'Data': data_2017_UL_ge3lepskim,
    # 'Data': data_2017_UL_ge4lepskim,
    # 'ZZ': mc_2017_UL_ZZ,
    # 'ZZ': mc_2017_UL_ZZ_ge3lepskim,

    # 'Data': data_2018_UL,
    # 'Data': data_2018_UL_ge3lepskim,
    # 'Data': data_2018_UL_ge4lepskim,
    # 'ZZ': mc_2018_UL_ZZ,
    # 'ZZ': mc_2018_UL_ZZ_ge3lepskim,

    # "Data" : infile_filippo_data_2018_fromhpg,
    # "ZZ" : mc_2018_zz_hpg,
    # "ZZ" : infile_filippo_zz_2018_fromhpg,
}
year = 2016
genwgts_dct = dct_sumgenweights_2016_UL
int_lumi = LUMI_INT_2016_UL
infile_FR_wz_removed = fakerates_WZremoved_2016_UL_woFSR
dct_xs = dct_xs_jake

start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 50000
smartcut_ZapassesZ1sel = False  # Literature sets this to False.

explain_skipevent = 0
keep_only_mass4lgt0 = 1
match_lep_Hindex = 1  # Only keep quartets that perfectly match lep_Hindex.
recalc_mass4l_vals = 0
allow_ge4tightleps = 1  # To sync with BBF Ana, set to True.
skip_passedFullSelection = 1  # To sync with BBF Ana, set to True.

fill_hists = 1
hadd_files = 0

outdir_root = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/"
outdir_json = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/json/"
# Produces a root file with TTree and hists, and a json file with evtID info.
# basename gets appended with file nickname:
outfile_basename = "redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_ZZ"
#=========================#
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-i', '--infile',          type=str, dest="infile", help="input root file")
    # parser.add_argument('-r', '--infile_fakerate', type=str, dest="infile_fr", help="input root file with fake rate hists (WZ removed)")
    # parser.add_argument('-o', '--outfile',         type=str, dest="outfile", help="output rootfile")
    # parser.add_argument('-n', '--nickname',        type=str, dest="name", help="nickname of file/process ('ZZ' or 'Data')")
    parser.add_argument('-x', '--overwrite', dest="overwrite", action="store_true", help="overwrite output file (1) or not (0)")
    parser.add_argument('-v', '--verbose',   dest="verbose",   action="store_true", help="verbose (1) or not (0)")
    args = parser.parse_args()
    # infile = args.infile
    # infile_FR_wz_removed = args.infile_fr
    # outfile_root = args.outfile
    # name = args.name
    overwrite = args.overwrite
    verbose = args.verbose

    assert all(
        str(year) in name for name in list(d_nicknames_files.values())
        )

    # Base names below will have name of data type appended ("Data", "ZZ").
    outfile_base_root = f"{outfile_basename}.root"
    outfile_base_json = f"{outfile_basename}_counter.json"

    if hadd_files:
        # Store the hadded file at the same place as input files.
        # Can only hadd if you process more than 1 file to process.
        # You may just have to hadd manually.
        all_names = '_'.join(d_nicknames_files.keys())
        new_filename = outfile_base_root.replace(
                        ".root",
                        f"_{year}_{all_names}.root"
                        )
        outfile_hadd = os.path.join(outdir_root, new_filename)
        check_overwrite(outfile_hadd, overwrite=overwrite)

    ls_all_outfiles = []
    for name, inpath in d_nicknames_files.items():

        ending = f"{year}_{name}"
        new_base_json = outfile_base_json.replace(".json", f"_{ending}.json")
        new_base_root = outfile_base_root.replace(".root", f"_{ending}.root")
        outfile_root = os.path.join(outdir_root, new_base_root)
        outfile_json = os.path.join(outdir_json, new_base_json)
        
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
            infile_fakerates=infile_FR_wz_removed,
            genwgts_dct=genwgts_dct,
            dct_xs=dct_xs,
            outfile_root=outfile_root,
            outfile_json=outfile_json,
            name=name,
            int_lumi=int_lumi,
            start_at_evt=start_at_evt,
            break_at_evt=break_at_evt,
            fill_hists=fill_hists,
            explain_skipevent=explain_skipevent,
            verbose=verbose,
            print_every=print_every,
            smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
            overwrite=overwrite,
            keep_only_mass4lgt0=keep_only_mass4lgt0,
            match_lep_Hindex=match_lep_Hindex,
            recalc_mass4l_vals=recalc_mass4l_vals,
            allow_ge4tightleps=allow_ge4tightleps,
            skip_passedFullSelection=skip_passedFullSelection,
            )
        ls_all_outfiles.append(outfile_root)

    # End loop over analyzer.
    if hadd_files:
        all_outfiles = ' '.join(ls_all_outfiles)
        shell_cmd(f"hadd -f {outfile_hadd} {all_outfiles}")
