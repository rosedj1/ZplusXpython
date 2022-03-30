"""Select 2P2F and 3P1F lepton quartets. Add new branches to TTree.
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
#   TTree. The xBF HZZ Analyzer does not yet handle multiple quartets within
#   the same event. The input files for this script should be root files
#   produced from the xBF HZZ Analyzer.
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
# Updated: 2022-03-08
#=============================================================================
"""
import os
import argparse
from ROOT import TFile
# Local modules.
from sidequests.funcs.evt_loops import (
    select_redbkg_evts
    )
from Utils_Python.Utils_Files import check_overwrite, make_dirs
from Utils_Python.Commands import shell_cmd

#########################
#--- User Parameters ---#
#########################
# Files to analyze.
d_nicknames_files = {
    "REPLACE_NAME": "REPLACE_FILE",
}
year = REPLACE_YEAR
genwgts_dct = REPLACE_DCT_SUMGENWGTS
int_lumi = REPLACE_LUMI
infile_FR_wz_removed = "REPLACE_FAKERATE_INFILE"
dct_xs = REPLACE_DCT_XS

start_at_evt = 0
break_at_evt = REPLACE_BREAK_AT  # Use -1 to run over all events.
print_every = REPLACE_PRINT_EVERY
explain_skipevent = 0

#=== Bools to control analysis flow. ===#
# Choose one or the other, or neither.
sync_with_xBFAna = 1  # If True, will override the bools below.
use_multiquart_sel = 0

#=== Alternatively, fine-tune the analyzer. ===#
stop_when_found_3p1f = 1  # If a 3P1F ZZ cand is found, don't build 2P2F.
match_lep_Hindex = 0  # Only keep quartets whose Z1 and Z2 match lep_Hindex.
keep_one_quartet = 0
recalc_masses = 1
skip_mass4l_lessthan0 = 0
skip_passedFullSelection = 1
allow_z1_failing_leps = 1

smartcut_ZapassesZ1sel = 0  # Literature sets this to False.
fill_hists = 0
hadd_files = 0

# outdir_root = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/test/verify/"
outdir_root = "REPLACE_OUTDIR_ROOTFILES"
outdir_json = "REPLACE_OUTDIR_JSON"
# Produces a root file with TTree and hists, and a json file with evtID info.
# basename gets appended with file nickname:
# outfile_basename = "osmethodnew_UL_somenegfrs_stopwhenfound3p1f_nomatchlepHindex_multiquart_recalcmasses_noskipmass4llt0_allowz1failleps"
outfile_basename = "REPLACE_PREFIX"
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

    year_in_name = [infile_FR_wz_removed] + list(d_nicknames_files.values())
    assert all(str(year) in name for name in year_in_name)

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
        
        make_dirs(
            os.path.dirname(outfile_root),
            os.path.dirname(outfile_json),
            )

        infile = TFile.Open(inpath, "read")
        tree = infile.Get("passedEvents")
        print(
            f"Successfully opened:\n{inpath}\n"
            f"  Processing: year={year}, name={name}"
            )

        select_redbkg_evts(
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
            skip_mass4l_lessthan0=skip_mass4l_lessthan0,
            match_lep_Hindex=match_lep_Hindex,
            recalc_masses=recalc_masses,
            skip_passedFullSelection=skip_passedFullSelection,
            stop_when_found_3p1f=stop_when_found_3p1f,
            keep_one_quartet=keep_one_quartet,
            use_multiquart_sel=use_multiquart_sel,
            allow_z1_failing_leps=allow_z1_failing_leps,
            sync_with_xBFAna=sync_with_xBFAna,
            )
        ls_all_outfiles.append(outfile_root)

    # End loop over analyzer.
    if hadd_files:
        all_outfiles = ' '.join(ls_all_outfiles)
        shell_cmd(f"hadd -f {outfile_hadd} {all_outfiles}")
