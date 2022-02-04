"""Print info comparing event selections between BBF and "Jake" analyzers.
# ============================================================================
# Created: 2021-12-16
# Updated: 2022-02-03
# Creator: Jake Rosenzweig
# Comment: Useful for doing event synchronization.
# ============================================================================
"""
import sys
from ROOT import TFile
# Local imports.
from sidequests.classes.filecomparer import (
    FileRunLumiEvent, get_list_of_entries,
    write_tree_info_to_txt
    )
from Utils_Python.Utils_Files import (
    open_json, save_to_pkl, open_pkl, check_overwrite
    )
from Utils_Python.printing import print_periodic_evtnum, print_header_message
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from sidequests.funcs.evt_comparison import (
    print_evt_info_bbf, analyze_single_evt, find_runlumievent_using_entry
    )
from skimmers.select_evts_2P2plusF_3P1plusF import infile_FR_wz_removed

from sidequests.data.filepaths import (
    infile_filippo_data_2018_fromhpg,
    fakerates_WZremoved
    )
from constants.analysis_params import (
    n_sumgenweights_dataset_dct_jake,
    xs_dct_jake
    )

infile_fakerates = fakerates_WZremoved

analyze_using = "jake"  # Choose between: "jake" or "bbf".
allow_ge4tightleps = 1

start_at = 95615
end_at = start_at + 1

# Filippo's unique 3P1F 4mu events.
# They all have at least 4 tight leptons!
ls_tup_unique_fili = [
    (322492, 778, 1346201480),
    (321961, 189, 343183869),
    (321909, 32, 57978416),
    (321396, 930, 1447135355),
    (325022, 162, 228256467),
    (317320, 504, 706020777),
    (315689, 604, 672709805),
    (315713, 819, 996429494),
    (316758, 674, 941538912),
    (325022, 1263, 1789168728),
    (316766, 1907, 2626778761),
    (317661, 556, 813675880),
    (319449, 364, 498050124),
    ]

ls_tup_unique_jake = [
    # Jake's unique 3P1F 4mu events.
    # (321887, 450, 722204060),
    # (315689, 342, 398232246),
    # (319991, 777, 1213672625),
    # (322599, 224, 359072495),
    # (316766, 179, 208365005),
    # (319524, 885, 1310553109),
    # (317291, 636, 878537435),
    # (322348, 827, 1498597313),
    # (321434, 39, 65055154)

    (321010, 33, 54826308),
    (316218, 760, 1057128632),
    (324980, 1481, 2730022725),
    ]

# CHOOSE A LIST FROM ABOVE TO USE!
ls_tup_unique = ls_tup_unique_jake

# Use Jake's analyzer on Filippo's unique events to see why Jake's FW failed.
f = TFile.Open(infile_filippo_data_2018_fromhpg, "read")
tree = f.Get("passedEvents")

# Run over root file and compare each event to event of interest.
# Pro: only 1 for loop over entire root file.
# Con: events of interest are analyzed in the order as found in NTuple.
if end_at == -1:
    end_at = tree.GetEntries()
for evt_num in range(start_at, end_at):
    print_periodic_evtnum(evt_num, end_at, print_every=500000)
    # tree.GetEntry(evt_num)
    tup_evtid = find_runlumievent_using_entry(tree, evt_num, fw="bbf")
    if tup_evtid in ls_tup_unique:
        run, lumi, event = tup_evtid
        analyze_single_evt(
            tree, run=run, lumi=lumi, event=event, entry=evt_num,
            fw=analyze_using, which="first",
            evt_start=0, evt_end=-1, print_every=500000,
            infile_fakerates=infile_fakerates,
            genwgts_dct=n_sumgenweights_dataset_dct_jake,
            xs_dct=xs_dct_jake,
            allow_ge4tightleps=allow_ge4tightleps,
            explain_skipevent=True,
            verbose=True
            )
    
# # inpkl_bbf_2p2f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_2p2f.pkl"
# # inpkl_bbf_3p1f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_3p1f.pkl"
# # inpkl_jake_2p2f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_2p2f.pkl"
# # inpkl_jake_3p1f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_3p1f.pkl"
# # infile_root_jake = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root"

# intxt_jake_3p1f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_3p1f.txt"
# intxt_jake_2p2f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_2p2f.txt"
# intxt_fili_3p1f = "../txt/data2018_filippo_evtids_3p1f.txt"

# infile_FR_wz_removed = fakerates_WZremoved

# explain_skipevent = True
# verbose = False
# use_exact_entry = True
# infile_exact_entries = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/scripts/bbf_unique3p1f_comparedtojake.out"

# # Get 3P1F events from Filippo's 2018 Data rootfile.
# # ls_evtids_jake_3p1f = open_pkl(inpkl_jake_3p1f)
# # set_evtids_bbf_3p1f = open_pkl(inpkl_bbf_3p1f)

# # Load Jake's file into a file analyzer. Do same for Filippo's.
# frle_jake_3p1f = FileRunLumiEvent(txt=intxt_jake_3p1f)
# frle_fili_3p1f = FileRunLumiEvent(txt=intxt_fili_3p1f)
# # frle_jake_3p1f = FileRunLumiEvent(ls_tup_evtid=ls_evtids_jake_3p1f)
# # frle_fili_3p1f = FileRunLumiEvent(set_tup_evtid=set_evtids_bbf_3p1f)

# #=== Look at events in common. ===#
# # frle_jake_3p1f.analyze_evtids(frle_fili_3p1f, event_type="common", print_evts=False)

# # Look at BBF unique events.
# fili_unique_evts = frle_fili_3p1f.analyze_evtids(frle_jake_3p1f, event_type="unique", print_evts=False)

# tf = TFile.Open(infile_filippo_data_2018_fromhpg)
# tree_bbf = tf.Get("passedEvents")

# if use_exact_entry:
#     ls_uniq_entries = get_list_of_entries(infile_exact_entries)
#     for entry in ls_uniq_entries:
#         analyze_single_evt(
#             tree_bbf,
#             run=None, lumi=None, event=None,
#             entry=entry,
#             fw="bbf", which="first"
#             )
#         analyze_single_evt(
#             tree_bbf,
#             run=None, lumi=None, event=None,
#             entry=entry,
#             fw="jake", which="first",
#             infile_FR_wz_removed=infile_FR_wz_removed,
#             explain_skipevent=explain_skipevent,
#             verbose=verbose
#             )
#         print("=#" * 39)
#         print("=#" * 39)
#         print("=#" * 39)
# else:
#     # Not sure which entry to use. Find using exactly run, lumi, event.
#     for ct, tup_fili_uniq_evtid in enumerate(fili_unique_evts):
#         # if ct == 1:
#         #     break
#         run, lumi, event = tup_fili_uniq_evtid
#         ls_bbf_evt_ndx = analyze_entry(
#             tree_bbf, entry=None, run=run, lumi=lumi, event=event,
#             fw="bbf", which="first"

#             tree, run, lumi, event, entry=None, fw="bbf", which="all",
#             evt_start=0, evt_end=-1, print_every=10000,
#             infile_FR_wz_removed=infile_FR_wz_removed,
#             explain_skipevent=True,
#             verbose=False
#             )
#         print()