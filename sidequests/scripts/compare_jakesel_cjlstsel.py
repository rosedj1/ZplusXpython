import sys
from ROOT import TFile

from sidequests.data.filepaths import infile_elisa_3p1f, infile_elisa_2p2f, infile_matteo_data2018, infile_filippo_data_2018_fromlxp
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
from sidequests.funcs.evt_comparison import analyze_single_evt
from Utils_Python.Utils_Files import open_json
from Utils_Python.printing import print_header_message

evt_start_bbf = 3333890
evt_start_cjlst = 76161
verbose = True
explain_skipevent = True

# Get 3P1F events from Filippo's 2018 Data rootfile.
d_jakeusingcjlstevtsel_2p2f_3p1f = open_json("../../sidequests/json/cjlstevtsel_2p2f_3p1f_widebins.json")
ls_3p1f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_3p1f"] > 0]
ls_2p2f_evtid_filippo = [evtid for evtid, d_small in d_jakeusingcjlstevtsel_2p2f_3p1f.items() if d_small["num_combos_2p2f"] > 0]

# Load Elisa's file into a file analyzer. Do same for Filippo's.
frle_elisa_3p1f   = FileRunLumiEvent(txt=infile_elisa_3p1f, ls_str_evtid=None)
# frle_elisa_2p2f   = FileRunLumiEvent(txt=infile_elisa_2p2f, ls_str_evtid=None)
frle_filippo_3p1f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_3p1f_evtid_filippo)
# frle_filippo_2p2f = FileRunLumiEvent(txt=None, ls_str_evtid=ls_2p2f_evtid_filippo)

#--- Grab all Elisa's unique 3P1F events. ---#
elisa_evts_3p1f_unique = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="unique")
#--- Count number of common events. ---#
# evts_3p1f_common = frle_elisa_3p1f.analyze_evtids(frle_filippo_3p1f, event_type="common")
# evts_2p2f_common = frle_elisa_2p2f.analyze_evtids(frle_filippo_2p2f, event_type="common")

f_cjlst = TFile.Open(infile_matteo_data2018, "read")
tree_cjlst = f_cjlst.Get("CRZLLTree/candTree")
print("Opened CJLST file.")

f_bbf = TFile.Open(infile_filippo_data_2018_fromlxp)
tree_bbf = f_bbf.Get("passedEvents")
print("Opened Filippo's 2018 Data file (BBF).")

tree_jake = tree_bbf.Clone()
print("Cloned BBF tree for Jake analysis.")

# Find out why Jake's vers of CJLST evt selection did not choose these events.
for u_evtid in elisa_evts_3p1f_unique:
    run, lumi, event = u_evtid  # Automagically unpacks the tuple!
    msg = (
        f"CJLST kept this 3P1F event, but BBF/Jake did not: "
        f"{run}:{lumi}:{event}"
        )
    print_header_message(msg, pad_char="@", n_center_pad_chars=5)

    # CJLST.
    print_header_message("CJLST")
    ls_cjlst_evt_ndx = analyze_single_evt(tree_cjlst, run, lumi, event, fw="cjlst", which="all",
                       evt_start=evt_start_cjlst, evt_end=evt_start_cjlst+1, print_every=10000)

    # BBF.
    # print_header_message("BBF")
    # ls_bbf_evt_ndx = analyze_single_evt(tree_bbf, run, lumi, event, fw="bbf", which="first",
    #                    evt_start=evt_start_bbf, evt_end=evt_start_bbf+1, print_every=500000)
    # ndx = ls_bbf_evt_ndx[0]

    # Jake.
    print_header_message("Investigate why Jake's selection failed:")
    evt_loop_evtselcjlst_atleast4leps(tree_jake, outfile_root=None, outfile_json=None,
                                        start_at_evt=evt_start_bbf, break_at_evt=evt_start_bbf+1, fill_hists=False,
                                        explain_skipevent=explain_skipevent, verbose=verbose, print_every=50000)
    print("DONE ANALYZING SINGLE EVENT FOR NOW")
    break


    
    