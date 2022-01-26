"""Compare event selections between BBF and "Jake" analyzers.
# ============================================================================
# Created: 2021-12-16
# Updated: 2022-01-26
# Creator: Jake Rosenzweig
# Comment: Useful for doing event synchronization.
# ============================================================================
"""
import sys
from ROOT import TFile
# Local imports.
from sidequests.classes.filecomparer import (
    FileRunLumiEvent, get_list_of_entries
    )
from Utils_Python.Utils_Files import (
    open_json, save_to_pkl, open_pkl, check_overwrite
    )
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from sidequests.funcs.evt_comparison import (
    print_evt_info_bbf, analyze_single_evt
    )
from skimmers.select_evts_2P2plusF_3P1plusF import infile_FR_wz_removed

from sidequests.data.filepaths import (
    infile_filippo_data_2018_fromhpg,
    fakerates_WZremoved
    )


# inpkl_bbf_2p2f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_2p2f.pkl"
# inpkl_bbf_3p1f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_3p1f.pkl"
# inpkl_jake_2p2f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_2p2f.pkl"
# inpkl_jake_3p1f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_3p1f.pkl"
# infile_root_jake = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root"

intxt_jake_3p1f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_3p1f.txt"
intxt_jake_2p2f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_2p2f.txt"
intxt_fili_3p1f = "../txt/data2018_filippo_evtids_3p1f.txt"

infile_FR_wz_removed = fakerates_WZremoved

explain_skipevent = True
verbose = False
use_exact_entry = True
infile_exact_entries = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/scripts/bbf_unique3p1f_comparedtojake.out"

write_tree = 0 

if write_tree:
    write_tree_info_to_txt(
        infile_root_jake,
        infile_txt_jake,
        m4l_lim=(105, 140),
        keep_2P2F=False,
        keep_3P1F=True,
        fs=1,
        print_every=100000
        )

# Get 3P1F events from Filippo's 2018 Data rootfile.
# ls_evtids_jake_3p1f = open_pkl(inpkl_jake_3p1f)
# set_evtids_bbf_3p1f = open_pkl(inpkl_bbf_3p1f)

# Load Jake's file into a file analyzer. Do same for Filippo's.
frle_jake_3p1f = FileRunLumiEvent(txt=intxt_jake_3p1f)
frle_fili_3p1f = FileRunLumiEvent(txt=intxt_fili_3p1f)
# frle_jake_3p1f = FileRunLumiEvent(ls_tup_evtid=ls_evtids_jake_3p1f)
# frle_fili_3p1f = FileRunLumiEvent(set_tup_evtid=set_evtids_bbf_3p1f)

#=== Look at events in common. ===#
# frle_jake_3p1f.analyze_evtids(frle_fili_3p1f, event_type="common", print_evts=False)

# Look at BBF unique events.
fili_unique_evts = frle_fili_3p1f.analyze_evtids(frle_jake_3p1f, event_type="unique", print_evts=False)

tf = TFile.Open(infile_filippo_data_2018_fromhpg)
tree_bbf = tf.Get("passedEvents")

if use_exact_entry:
    ls_uniq_entries = get_list_of_entries(infile_exact_entries)
    for entry in ls_uniq_entries:
        analyze_single_evt(
            tree_bbf,
            run=None, lumi=None, event=None,
            entry=entry,
            fw="bbf", which="first"
            )
        analyze_single_evt(
            tree_bbf,
            run=None, lumi=None, event=None,
            entry=entry,
            fw="jake", which="first",
            infile_FR_wz_removed=infile_FR_wz_removed,
            explain_skipevent=explain_skipevent,
            verbose=verbose
            )
        print("=#" * 39)
        print("=#" * 39)
        print("=#" * 39)
else:
    # Not sure which entry to use. Find using exactly run, lumi, event.
    for ct, tup_fili_uniq_evtid in enumerate(fili_unique_evts):
        # if ct == 1:
        #     break
        run, lumi, event = tup_fili_uniq_evtid
        ls_bbf_evt_ndx = analyze_entry(
            tree_bbf, entry=None, run=run, lumi=lumi, event=event,
            fw="bbf", which="first"

            tree, run, lumi, event, entry=None, fw="bbf", which="all",
            evt_start=0, evt_end=-1, print_every=10000,
            infile_FR_wz_removed=infile_FR_wz_removed,
            explain_skipevent=True,
            verbose=False
            )
        print()