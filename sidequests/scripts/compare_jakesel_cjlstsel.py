import sys
from ROOT import TFile

from sidequests.data.filepaths import infile_elisa_3p1f, infile_elisa_2p2f, infile_matteo_data2018, infile_filippo_data_2018_fromlxp
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
from sidequests.funcs.evt_comparison import analyze_single_evt
from Utils_Python.Utils_Files import open_json
from Utils_Python.printing import print_header_message

verbose = 1
explain_skipevent = 1
print_n_common_evts = 0
smartcut_ZapassesZ1sel = 0

use_analyzer_cjlst = 1
use_analyzer_bbf = 1
use_analyzer_jake = 1

user_evtid = None #(319528, 23, 29973732)  # Specific event, otherwise use `None`.
run_over_elisa_unique_3p1f = 1

scan_all_evts = 1  # Once BBF finds event index, it will give it to Jake.
evt_start_bbfandjake = None #3333890  # Specific event, otherwise use `None`.
evt_start_cjlst = None#76161          # Specific event, otherwise use `None`.

if __name__ == '__main__':
    request_single_evt = (user_evtid is not None)
    msg = "Either specify a `user_evtid` or `run_over_elisa_unique_3p1f`."
    assert (run_over_elisa_unique_3p1f ^ request_single_evt), msg
    if scan_all_evts == 0:
        if use_analyzer_cjlst:
            assert evt_start_cjlst is not None
        if use_analyzer_bbf or use_analyzer_jake:
            assert evt_start_bbfandjake is not None
    # Get 3P1F events from Filippo's 2018 Data rootfile.
    d_jakeusingcjlstevtsel_2p2f_3p1f = open_json("../../sidequests/json/cjlstevtsel_2p2f_3p1f_widebins_includepassfullsel.json")
    ls_3p1f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_3p1f"] > 0]
    ls_2p2f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_2p2f"] > 0]

    # Load Elisa's file into a file analyzer. Do same for Filippo's.
    frle_elisa_3p1f   = FileRunLumiEvent(txt=infile_elisa_3p1f, ls_str_evtid=None)
    frle_elisa_2p2f   = FileRunLumiEvent(txt=infile_elisa_2p2f, ls_str_evtid=None)
    frle_filippo_3p1f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_3p1f_evtid_filippo)
    frle_filippo_2p2f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_2p2f_evtid_filippo)

    #--- Grab all Elisa's unique 3P1F events. ---#
    elisa_evts_3p1f_unique = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="unique")
    #--- Count number of common events. ---#
    if print_n_common_evts:
        evts_3p1f_common = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="common")
        evts_2p2f_common = frle_elisa_2p2f.analyze_evtids(frle_filippo_2p2f, event_type="common")

    f_cjlst = TFile.Open(infile_matteo_data2018, "read")
    tree_cjlst = f_cjlst.Get("CRZLLTree/candTree")
    print("Opened CJLST file.")

    f_bbf = TFile.Open(infile_filippo_data_2018_fromlxp)
    tree_bbf = f_bbf.Get("passedEvents")
    print("Opened Filippo's 2018 Data file (BBF).")

    tree_jake = tree_bbf.Clone()
    print("Cloned BBF tree for Jake analysis.")

    # Find out why Jake's vers of CJLST evt selection did not choose these events.
    for evtid in elisa_evts_3p1f_unique:
        # Automagically unpacks the tuple!
        if user_evtid is not None:
            run, lumi, event = user_evtid
            msg = f"Analyzing single event: {run}:{lumi}:{event}"
        else:
            # Run over unique 3P1F events.
            run, lumi, event = evtid
            msg = (
                f"CJLST kept this 3P1F event, but Jake did not: "
                f"{run}:{lumi}:{event}"
                )
        print_header_message(msg, pad_char="@", n_center_pad_chars=5)

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
                            #    evt_start=evt_start_cjlst, evt_end=evt_start_cjlst+1, print_every=10000)
        ndx_bbf = None
        if use_analyzer_bbf:
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
