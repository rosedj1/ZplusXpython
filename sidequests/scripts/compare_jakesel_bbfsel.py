"""Compare event selections between BBF and "Jake" analyzers.
# ============================================================================
# Created: 2021-12-16
# Updated: 2021-12-21
# Creator: Jake Rosenzweig
# Comment: Useful for doing event synchronization.
# ============================================================================
"""
import sys
from ROOT import TFile
# Local imports.
from sidequests.classes.filecomparer import FileRunLumiEvent
from Utils_Python.Utils_Files import (
    open_json, save_to_pkl, open_pkl, check_overwrite
    )
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from sidequests.funcs.evt_comparison import (
    print_evt_info_bbf, analyze_single_evt
    )
from skimmers.select_evts_2P2plusF_3P1plusF import infile_FR_wz_removed

inpkl_bbf_2p2f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_2p2f.pkl"
inpkl_bbf_3p1f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_3p1f.pkl"
inpkl_jake_2p2f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_2p2f.pkl"
inpkl_jake_3p1f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_3p1f.pkl"

explain_skipevent = True
verbose = False
use_exact_entry = True
infile_exact_entries = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/scripts/bbf_unique3p1f_comparedtojake.out"

def get_list_of_entries(txt):
    """Return a list of entries (int) from a txt file."""
    ls_entries = []
    with open(txt, "r") as f:
        lines = f.readlines()
        for l in lines:
            if "Index" in l:
                str_num = l.split(": ")[1]
                entry = int(str_num.rstrip('\n'))
                ls_entries.extend([entry])
    return ls_entries

# if __name__ == '__main__':

# Get 3P1F events from Filippo's 2018 Data rootfile.
ls_evtids_jake_3p1f = open_pkl(inpkl_jake_3p1f)
set_evtids_bbf_3p1f = open_pkl(inpkl_bbf_3p1f)

# Load Jake's file into a file analyzer. Do same for Filippo's.
frle_jake_3p1f = FileRunLumiEvent(ls_tup_evtid=ls_evtids_jake_3p1f)
frle_fili_3p1f = FileRunLumiEvent(set_tup_evtid=set_evtids_bbf_3p1f)

#=== Look at events in common. ===#
# frle_jake_3p1f.analyze_evtids(frle_fili_3p1f, event_type="common", print_evts=False)
#================#
#=== PROGRESS ===#
#================#
# BBF analyzer selects all of Jake's 4144 evts... plus 145 more.
# WHY?

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
            )
        print()