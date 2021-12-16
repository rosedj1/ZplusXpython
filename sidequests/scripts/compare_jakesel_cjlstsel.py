"""Compares event selections between BBF, CJLST, and "Jake" analyzers.
# ============================================================================
# Created: 2021-12-02
# Creator: Jake Rosenzweig
# Comment: Useful for doing event synchronization.
# ============================================================================
"""
import sys
from ROOT import TFile
from contextlib import redirect_stdout  # Having trouble with `tee`.

from sidequests.data.filepaths import (
    infile_elisa_3p1f, infile_elisa_2p2f,
    infile_matteo_data2018_fromhpg, infile_filippo_data_2018_fromhpg
    )
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
from sidequests.funcs.evt_comparison import analyze_single_evt
from Utils_Python.Utils_Files import (
    open_json, save_to_pkl, open_pkl, check_overwrite
    )
from Utils_Python.printing import print_header_message

verbose = 1
explain_skipevent = 0
overwrite = 0
print_n_common_evts = 1
smartcut_ZapassesZ1sel = 0

use_analyzer_cjlst = 0
use_analyzer_bbf = 0
use_analyzer_jake = 0

save_bbf_pkl = 0
open_bbf_pkl = 0
# Premade dict of event IDs from Filippo's 2018 Data.
pathpkl_bbf_evtid_set = "../pkls/bbf_evtid_set_data2018.pkl"

# infile_json = "../../sidequests/json/cjlstevtsel_2p2f_3p1f_widebins_includepassfullsel.json"
infile_json = "../../sidequests/json/cjlstOSmethodevtsel_2p2plusf_3p1plusf.json"

outlog_cjlst = "../logs/test/elisa_unique_3p1f_analyzercjlst.log"
outlog_bbf   = "../logs/test/elisa_unique_3p1f_analyzerbbf.log"
outlog_jake  = "../logs/test/elisa_unique_3p1f_analyzerjake.log"

user_evtid = None #(322605, 54, 99454570)  # Specific event, otherwise use `None`.

scan_all_evts = 0  # Once BBF finds event index, it will give it to Jake.
evt_start_bbfandjake = 6867156  #3333890  # Specific event, otherwise use `None`.
evt_start_cjlst = None#76161          # Specific event, otherwise use `None`.

if __name__ == '__main__':
    check_overwrite(outlog_cjlst, outlog_bbf, outlog_jake,
        overwrite=overwrite)
    assert not (save_bbf_pkl and open_bbf_pkl), "Open or save pkl. Not both."
    request_single_evt = (user_evtid is not None)
    if scan_all_evts == 0:
        if use_analyzer_cjlst:
            assert evt_start_cjlst is not None
        if use_analyzer_bbf or use_analyzer_jake:
            assert evt_start_bbfandjake is not None
    # Get 3P1F events from Filippo's 2018 Data rootfile.
    d_jakeusingcjlstevtsel_2p2f_3p1f = open_json(infile_json)
    ls_3p1f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_3p1f"] > 0]
    ls_2p2f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_2p2f"] > 0]

    # Load Elisa's file into a file analyzer. Do same for Filippo's.
    frle_elisa_3p1f   = FileRunLumiEvent(txt=infile_elisa_3p1f, ls_str_evtid=None)
    frle_elisa_2p2f   = FileRunLumiEvent(txt=infile_elisa_2p2f, ls_str_evtid=None)
    frle_filippo_3p1f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_3p1f_evtid_filippo)
    frle_filippo_2p2f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_2p2f_evtid_filippo)

    #--- Grab all Elisa's unique 3P1F events. ---#
    elisa_evts_3p1f_unique = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="unique")
    elisa_evts_2p2f_unique = frle_elisa_2p2f.analyze_evtids(frle_filippo_2p2f, event_type="unique")
    with open("", "w") as f:

    #--- Count number of common events. ---#
    if print_n_common_evts:
        evts_3p1f_common = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="common")
        evts_2p2f_common = frle_elisa_2p2f.analyze_evtids(frle_filippo_2p2f, event_type="common")

    sys.exit()
    f_cjlst = TFile.Open(infile_matteo_data2018_fromhpg, "read")
    tree_cjlst = f_cjlst.Get("CRZLLTree/candTree")
    print("Opened CJLST file.")

    f_bbf = TFile.Open(infile_filippo_data_2018_fromhpg)
    tree_bbf = f_bbf.Get("passedEvents")
    print("Opened Filippo's 2018 Data file (BBF).")

    tree_jake = tree_bbf.Clone()
    print("Cloned BBF tree for Jake analysis.")

    # Made hash table of BBF event IDs to see if CJLST is even inside.
    if save_bbf_pkl:
        print(f"Making look-up table of all BBF events.")
        bbf_evtid_set = {(evt.Run, evt.LumiSect, evt.Event,) for evt in tree_bbf}
        save_to_pkl(
            bbf_evtid_set,
            pathpkl_bbf_evtid_set,
            overwrite=True
            )
    if open_bbf_pkl:
        bbf_evtid_set = open_pkl(pathpkl_bbf_evtid_set)

    #######################################
    #--- LOOP OVER CJLST UNIQUE EVENTS ---#
    #######################################
    # Find out why Jake's vers of CJLST evt selection did not choose these events.
    n_tot = len(elisa_evts_3p1f_unique)
    for ct, evtid in enumerate(elisa_evts_3p1f_unique):
        write_mode = "w" if ct == 0 else "a"

        if user_evtid is not None:
            # Automagically unpacks the tuple!
            run, lumi, event = user_evtid
            evt_msg = f"Analyzing single event: {run}:{lumi}:{event}"
        else:
            # Run over unique 3P1F events.
            run, lumi, event = evtid
            evt_msg = (
                f"CJLST unique 3P1F event {run}:{lumi}:{event} "
                f"({ct+1}/{n_tot})"
                )
        print_header_message(evt_msg, pad_char="@", n_center_pad_chars=5)

        if use_analyzer_cjlst:
            print_header_message("ANALYZER: CJLST")
            if scan_all_evts:
                evt_start = 0
                evt_end = -1
            else:    
                evt_start = evt_start_cjlst
                evt_end = evt_start + 1
            ls_cjlst_evt_ndx = analyze_single_evt(tree_cjlst, run, lumi, event, fw="cjlst", which="all",
                            evt_start=evt_start, evt_end=evt_end, print_every=10000)
            # DISGUSTING HACK.
            # Linux `tee` command won't print to screen and file for some reason...
            # (`python script.py | tee output.txt`)
            # So I analyze the files twice:
            # once to print to screen and the other to save to file...
            print("Writing to CJLST log file...")
            with open(outlog_cjlst, write_mode) as f:
                with redirect_stdout(f):
                    print_header_message(evt_msg, pad_char="@", n_center_pad_chars=5)
                    for ndx in ls_cjlst_evt_ndx:
                        _ = analyze_single_evt(tree_cjlst, run, lumi, event, fw="cjlst", which="all",
                                    evt_start=ndx, evt_end=ndx+1, print_every=10000)
        
        # BBF and Jake analyzers study the same root file.
        # Therefore they use exactly the same events, indices, etc.
        ndx_bbf = None
        if use_analyzer_bbf:
            # First check if event is even in BBF NTuple.
            if evtid not in bbf_evtid_set:
                msg = (
                    f"\n\n** Skipping event {evtid}. "
                    f"Not found in BBF NTuple. ({ct+1}/{n_tot}) **\n\n"
                    )
                print(msg)
                with open(outlog_bbf, write_mode) as f:
                    f.write(msg)
                with open(outlog_jake, write_mode) as f:
                    f.write(msg)
                continue
            print_header_message("ANALYZER: BBF")
            if scan_all_evts:
                evt_start = 0
                evt_end = -1
            else: 
                evt_start = evt_start_bbfandjake
                evt_end = evt_start + 1
            ls_bbf_evt_ndx = analyze_single_evt(tree_bbf, run, lumi, event, fw="bbf", which="first",
                            evt_start=evt_start, evt_end=evt_end, print_every=500000)
            ndx_bbf = ls_bbf_evt_ndx[0]
            # HACK:
            print("Writing to BBF log file...")
            with open(outlog_bbf, write_mode) as f:
                with redirect_stdout(f):
                    print_header_message(evt_msg, pad_char="@", n_center_pad_chars=5)
                    _ = analyze_single_evt(tree_bbf, run, lumi, event, fw="bbf", which="first",
                            evt_start=ndx_bbf, evt_end=ndx_bbf+1, print_every=500000)

        if use_analyzer_jake:
            if evt_start_bbfandjake is not None:
                print(f"Using evt index from BBF: {evt_start_bbfandjake}")
                # First preference is to use user-specified event.
                evt_start = evt_start_bbfandjake
                evt_end = evt_start + 1
            elif ndx_bbf is not None:
                # Use index found by BBF analyzer.
                evt_start = ndx_bbf
                evt_end = evt_start + 1
            elif scan_all_evts:
                evt_start = 0
                evt_end = -1
            else:
                raise ValueError("Confusing if statements...")
            print_header_message("ANALYZER: Jake")
            evt_loop_evtselcjlst_atleast4leps(tree_jake, outfile_root=None, outfile_json=None,
                                              start_at_evt=evt_start, break_at_evt=evt_end, fill_hists=False,
                                              explain_skipevent=explain_skipevent, verbose=verbose, print_every=50000,
                                              smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel)
            print("Writing to JAKE log file...")
            evt_key = f"{run}:{lumi}:{event}"
            with open(outlog_jake, write_mode) as f:
                with redirect_stdout(f):
                    print_header_message(evt_msg, pad_char="@", n_center_pad_chars=5)
                    print(f"Searching for event ID {evt_key} in JAKE framework")
                    print(f"Event {evt_key} found. Index: {evt_start}")
                    evt_loop_evtselcjlst_atleast4leps(tree_jake, outfile_root=None, outfile_json=None,
                                              start_at_evt=evt_start, break_at_evt=evt_end, fill_hists=False,
                                              explain_skipevent=explain_skipevent, verbose=verbose, print_every=50000,
                                              smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel)
