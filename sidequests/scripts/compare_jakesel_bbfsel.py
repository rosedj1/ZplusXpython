"""Compares event selections between BBF and "Jake" analyzers.
# ============================================================================
# Created: 2021-12-16
# Creator: Jake Rosenzweig
# Comment: Useful for doing event synchronization.
# ============================================================================
"""
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

infile_bbf = infile_filippo_data_2018_fromhpg
infile_jake = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_mass4lgt0_2018_Data.root"

inpkl_bbf_2p2f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_2p2f.pkl"
inpkl_bbf_3p1f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_3p1f.pkl"
inpkl_jake_2p2f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_2p2f.pkl"
inpkl_jake_3p1f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_3p1f.pkl"

use_exact_entry = True
infile_exact_entries = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/scripts/output_diffbetween_jakeandbbf_3p1f.txt"
# import sys
# from ROOT import TFile
# from contextlib import redirect_stdout  # Having trouble with `tee`.

# from sidequests.data.filepaths import (
#     infile_elisa_3p1f, infile_elisa_2p2f,
#     infile_matteo_data2018_fromhpg, infile_filippo_data_2018_fromhpg
#     )
# from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
# from sidequests.funcs.evt_comparison import analyze_single_evt
# from Utils_Python.printing import print_header_message

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

def analyze_entry(
    tree, entry=None, run=None, lumi=None, event=None,
    fw="jake", which="first"
    ):
    """Analyze one event found by either `entry` OR `run`, `lumi`, `event`.
    
    Args:
    """
    if entry is None:
        assert all(x is not None for x in (run, lumi, event))
        evt_start = 0
        evt_end = -1
    else:
        evt_start = entry
        evt_end = entry + 1
        ls_bbf_evt_ndx = analyze_single_evt(tree, run, lumi, event, fw=fw, which=which,
                        evt_start=evt_start, evt_end=evt_end, print_every=500000)
        print()

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
    for entry in ls_uniq_entries[:2]:
        analyze_entry(
            tree_bbf, entry=entry, run=None, lumi=None, event=None,
            fw="bbf", which="first"
            )
        analyze_entry(
            tree_bbf, entry=entry, run=None, lumi=None, event=None,
            fw="jake", which="first"
            )
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