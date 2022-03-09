import warnings
from ROOT import TFile
import numpy as np
from array import array
# Local imports.
from Utils_Python.Utils_Physics import perc_diff, calc_mass4l_from_idcs
from Utils_Python.printing import (
    print_periodic_evtnum, print_skipevent_msg, pretty_print_dict,
    print_header_message
    )
from Utils_Python.Utils_Files import save_to_json, check_overwrite
from classes.zzpair import (
    # myleps_pass_cjlst_osmethod_selection,
    get_ZZcands_from_myleps_OSmethod
    )
from classes.mylepton import (
    make_filled_mylep_ls,
    get_n_tight_myleps, get_n_loose_myleps, has_2p2f_leps, has_3p1f_leps,
    )
from classes.quartetcategorizer import QuartetCategorizer
from sidequests.funcs.cjlst_handling import (
    is_tight_cjlst_lep, convert_to_bbf_fs, print_evt_info_cjlst
    )
from sidequests.containers.dicts_th1 import (
    make_dct_hists_all_crs,
    make_dct_hists_all_crs_data
    )
from sidequests.containers.hists_th1 import (
    h1_data_3p1f_m4l,
    h1_data_2p2f_m4l,
    h1_data_3p1fpred_m4l,
    h1_data_2p2fpred_m4l,
    h1_data_2p2fin3p1f_m4l,
    h1_data_n2p2f_combos,
    h1_data_n3p1f_combos,
    h1_zz_2p2f_m4l,
    h1_zz_3p1f_m4l,
    h1_zz_2p2fpred_m4l,
    h1_zz_3p1fpred_m4l,
    h1_zz_n2p2f_combos,
    h1_zz_n3p1f_combos,
    )
from sidequests.containers.hists_th2 import h2_n3p1fcombos_n2p2fcombos
from sidequests.classes.cjlstflag import CjlstFlag
from scripts.helpers.analyzeZX import (
    get_evt_weight, check_which_Z2_leps_failed,
    retrieve_FR_hists, get_fakerate_and_error_mylep,
    calc_fakerate_up, calc_fakerate_down,
    calc_wgt_2p2f_cr, calc_wgt_3p1f_cr
    )
from constants.analysis_params import (
    dct_xs_jake, n_sumgenweights_dataset_dct_jake
    )
from constants.finalstates import dct_finalstates_str2int

# from scipy.special import binom

def make_evt_info_d():
    """Return a dict of counters for info in event loop.
    
    key (str): String of information about event loop.
    val (int): Starts at 0. Gets incremented when necessary in event loop.
    """
    tup = (
        # These will be dict keys whose values start at 0 and then increment.
        "n_evts_lt4_leps",
        # "n_evts_lt1looselep",
        # "n_evts_lt2tightleps",
        # "n_evts_gt3tightleps",
        # "n_evts_not2or3tightleps",
        "n_evts_novalid2P2For3P1F_ZZcands",
        # "n_quartets_zerogoodZZcands",
        # "n_evts_nosubevtspassingsel",
        "n_evts_passedFullSelection",
        # "n_evts_passedZXCRSelection",
        # "n_evts_lt2_zcand",
        # "n_evts_ne2_zcand",
        # "n_evts_lt4tightpluslooseleps",
        # "n_evts_no4lep_combos",
        # "n_combos_4tightleps",
        "n_good_redbkg_evts",
        "n_good_3p1f_evts",
        "n_good_2p2f_evts",
        "n_tot_3p1f_quartets",
        "n_tot_2p2f_quartets",
        "n_evts_skip_mass4l_le0",
        "n_quartets_skip_lep_Hindex_mismatch"
    )
    return {s : 0 for s in tup}

# def evt_loop_evtselcjlst_atleast4leps(tree, outfile_root=None, outfile_json=None,
#                                       start_at_evt=0, break_at_evt=-1, fill_hists=True,
#                                       explain_skipevent=False, verbose=False, print_every=50000,
#                                       smartcut_ZapassesZ1sel=False):
#     """Apply CJLST's RedBkg event selection to all events in tree.
    
#     NOTE:
#         - Asks for AT LEAST 4 leptons per event.
#         - When an event has >4 leptons, then multiple combinations
#         of 2P2F/3P1F are possible.
#         - Does NOT select the BEST ZZ candidate per event.
#         If there are >1 ZZ candidates that pass ZZ selections,
#         then it takes all possible valid 4-lepton combinations
#         and analyzes each individually.

#     New reducible background analyzer to bypass nZXCRFailedLeptons.
#     # ============================================================================
#     # Author: Jake Rosenzweig
#     # Created: 2021-11-16
#     # Updated: 2021-12-02
#     # ============================================================================

#     Args:
#         smartcut_ZapassesZ1sel (bool, optional):
#             In the smart cut, the literature essentially says that if a Za
#             looks like a more on-shell Z boson than the Z1 AND if the Zb is a
#             low mass di-lep resonance, then veto the whole ZZ candidate.
#             However, literature doesn't check for Za passing Z1 selections!
#             Set this to True if you require Za to pass Z1 selections.
#             Default is False.
#     """
#     evt_info_d = make_evt_info_d()
#     evt_info_2p2f_3p1f_d = {}

#     if outfile_root is not None:
#         new_file = TFile.Open(outfile_root, "recreate")
#     # new_tree = 
#     n_tot = tree.GetEntries()
#     if verbose:
#         print(f"Total number of events: {n_tot}")
#     print("Looking for AT LEAST 4 leptons per event.")
#     for evt_num in range(start_at_evt, n_tot):

#         if evt_num == break_at_evt:
#             break

#         print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

#         tree.GetEntry(evt_num)
#         run = tree.Run
#         lumi = tree.LumiSect
#         event = tree.Event

#         # EVENTUALLY REMOVE THIS AND MAKE SURE RESULTS ARE THE SAME.
#         # Don't want signal region events:
#         # if tree.passedFullSelection:
#         #     if verbose: print_skipevent_msg("SR", evt_num, run, lumi, event)
#         #     evt_info_d["n_evts_passedFullSelection"] += 1
#         #     continue

#         # Check the number of leptons in this event.
#         n_tot_leps = len(tree.lepFSR_pt)

#         # Ensure at least 4 leptons in event:
#         if n_tot_leps < 4:
#             if verbose: print_skipevent_msg("n_leps < 4", evt_num, run, lumi, event)
#             evt_info_d["n_evts_lt4_leps"] += 1
#             continue
            
#         # Initialize ALL leptons (there can be more than 4 leptons).
#         mylep_ls = make_filled_mylep_ls(tree)
#         n_tight_leps = get_n_tight_myleps(mylep_ls)
#         n_loose_leps = get_n_loose_myleps(mylep_ls)

#         # Preliminary checks.
#         if n_tight_leps < 2:
#             evt_info_d["n_evts_lt2tightleps"] += 1
#             if explain_skipevent:
#                 msg = f"Number of tight leptons ({n_tight_leps}) < 2"
#                 print_skipevent_msg(msg, evt_num, run, lumi, event)
#             continue
#         if n_loose_leps < 1:
#             evt_info_d["n_evts_lt1looselep"] += 1
#             if explain_skipevent:
#                 msg = f"Number of loose leptons ({n_loose_leps}) < 1"
#                 print_skipevent_msg(msg, evt_num, run, lumi, event)
#             continue
     
#         # Check if any four-lep combos have 2P2F or 3P1F leptons.
#         # NOTE: This does not mean they pass selection yet!
#         fourlep_combos = []
#         fourlep_combos.extend(find_combos_2tight2loose(mylep_ls))
#         fourlep_combos.extend(find_combos_3tight1loose(mylep_ls))
#         if len(fourlep_combos) == 0:
#             evt_info_d["n_evts_no4lep_combos"] += 1
#             if explain_skipevent:
#                 msg = (
#                     f"Found 0 four-lep combos of type 2P2F or 3P1F."
#                     f"  n_tight_leps={n_tight_leps}, "
#                     f"  n_loose_leps={n_loose_leps}"
#                 )
#                 print_skipevent_msg(msg, evt_num, run, lumi, event)
#             continue

#         print(f"WHAT THE HELL ARE YOU?")
#         print(f"len(fourlep_combos) = {len(fourlep_combos)}")
#         _ = [lep.print_info() for lep in fourlep_combos[0]]

#         # Check which four-lep combos pass ZZ selections.
#         n_tot_2p2f_quartets = 0
#         n_tot_3p1f_quartets_this_event = 0
#         for fourlep_tup in fourlep_combos:
            # if not myleps_pass_cjlst_osmethod_selection(
#                     fourlep_tup, verbose=verbose, explain_skipevent=explain_skipevent,
#                     smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
#                     run=run, lumi=lumi, event=event, entry=evt_num):
#                 continue
#             # Make sure it's not a SR event:
#             if get_n_tight_myleps(fourlep_tup) == 4:
#                 evt_info_d["n_combos_4tightleps"] += 1
#                 if explain_skipevent:
#                     print("Skipping 4-lep combo: 4 tight leptons.")
#                 continue

#             # Good RedBkg event!
#             if has_2p2f_leps(fourlep_tup):
#                 n_tot_2p2f_quartets += 1
#             elif has_3p1f_leps(fourlep_tup):
#                 n_tot_3p1f_quartets_this_event += 1
#             else:
#                 raise ValueError("Something is wrong with event selection.")
#         # End loop over all possible four-lepton combinations.
#         evt_id = f"{run} : {lumi} : {event}"
#         if verbose:
#             print(
#                 f"Event passed CJLST OS Method Selections:\n"
#                 f"{evt_id} (entry {evt_num})"
#                 )
        
#         has_good_2p2f_combos = (n_tot_2p2f_quartets > 0)
#         has_good_3p1f_combos = (n_tot_3p1f_quartets_this_event > 0)

#         evt_info_d["n_good_redbkg_evts"] += 1
#         if has_good_2p2f_combos:
#             evt_info_d["n_good_2p2f_evts"] += 1
#         if has_good_3p1f_combos:
#             evt_info_d["n_good_3p1f_evts"] += 1
        
#         if fill_hists:
#             if has_good_2p2f_combos or has_good_3p1f_combos:
#                 h1_n2p2f_combos.Fill(n_tot_2p2f_quartets, 1)
#                 h1_n3p1f_combos.Fill(n_tot_3p1f_quartets_this_event, 1)
#                 h2_n3p1fcombos_n2p2fcombos.Fill(
#                     n_tot_2p2f_quartets,
#                     n_tot_3p1f_quartets_this_event,
#                     1)
            
#                 evt_info_2p2f_3p1f_d[evt_id] = {
#                     "num_combos_2p2f" : n_tot_2p2f_quartets,
#                     "num_combos_3p1f" : n_tot_3p1f_quartets_this_event,
#                 }
#     print("End loop over events.")

#     pretty_print_dict(evt_info_d)
#     if outfile_root is not None:
#         h1_n2p2f_combos.Write()
#         h1_n3p1f_combos.Write()
#         h2_n3p1fcombos_n2p2fcombos.Write()
#         new_file.Close()
#         print(f"Hists stored in root file:\n{outfile_root}")

#     if outfile_json is not None:
#         save_to_json(evt_info_2p2f_3p1f_d, outfile_json, overwrite=True,
#                     sort_keys=False)

def select_evts_2P2F_3P1F_multiquartets(
    tree,
    infile_fakerates,
    genwgts_dct,
    dct_xs,
    outfile_root=None, outfile_json=None,
    name="", int_lumi=-1,
    start_at_evt=0, break_at_evt=-1,
    fill_hists=True,
    explain_skipevent=False, verbose=False, print_every=50000,
    smartcut_ZapassesZ1sel=False,
    overwrite=False,
    keep_only_mass4lgt0=False,
    match_lep_Hindex=False,
    recalc_mass4l_vals=False,
    skip_passedFullSelection=True,
    stop_when_found_3p1f=True,
    keep_first_quartet=False,
    ):
    """Apply RedBkg multi-lepton quartet selection to all events in tree.

    NOTE:
        A "quartet" is a combination of 4-leptons.
        Each event may have multiple leptons quartets.
        If an event has both a 3P1F quartet and a 2P2F quartet,
        then the 3P1F one takes priority. The 2P2F quartet will be skipped.

    TODO Update below:
    Select events with:
        - Exactly 3 leptons passing tight selection and at least 1 failing.
        - Exactly 2 leptons passing tight selection and at least 2 failing.
        - When an event has >4 leptons, then multiple combinations
            of 2P2F/3P1F are possible.
            Suppose you have an event with 5 leptons, 3 of which pass tight
            selection and 2 fail tight selection.
            Then we have two different ways to make a 3P1F combo
            (two 3P1F subevents).
        - Does NOT select the BEST ZZ candidate per event.
            If there are >1 ZZ candidates that pass ZZ selections,
            then each ZZ cand is saved as a separate entry in the TTree.
            This means a single event can show up multiple times in a TTree,
            if there are multiple valid 4-lepton combinations ("quartets").
    
    Args:
        outfile_root (str):
            Path to store root file.
            TTree of selected events will be made.
            If `fill_hists` is True, then will store histograms.
        smartcut_ZapassesZ1sel (bool, optional):
            In the smart cut, the literature essentially says that if a Za
            looks like a more on-shell Z boson than the Z1 AND if the Zb is a
            low mass di-lep resonance, then veto the whole ZZ candidate.
            However, literature doesn't check for Za passing Z1 selections!
            Set this to True if you require Za to pass Z1 selections.
            Default is False.
        keep_only_mass4lgt0 (bool, optional):
            If True, then skip events whose tree.mass4l <= 0.
            This is useful when you need to use the values that are already
            stored in the BBF NTuple.
            Default is False.
        match_lep_Hindex (bool, optional):
            If True, then only keep the quartets whose selected lepton indices
            exactly match those found in the vector tree.lep_Hindex.
            Good for synchronizing with the BBF Analyzer.
            Default is False.
        recalc_mass4l_vals (bool, optional):
            If True, recalculate mass4l of selected lepton quartet and
            corresponding massZ1 and massZ2 values.
        stop_when_found_3p1f (bool, optional):
            If True, if at least one valid 3P1F ZZ candidate was found,
            do not look for any 2P2F candidates. Defaults to True.
    TODO Update above:
    """
    if fill_hists:
        # Prep histograms.
        d_hists = {
            "Data" : {
                "2p2f" : {
                    "mass4l" : h1_data_2p2f_m4l,
                    "n_quartets" : h1_data_n2p2f_combos,
                },
                "3p1f" : {
                    "mass4l" : h1_data_3p1f_m4l,
                    "n_quartets" : h1_data_n3p1f_combos,
                }
            },
            "ZZ" : {
                "2p2f" : {
                    "mass4l" : h1_zz_2p2f_m4l,
                    "n_quartets" : h1_zz_n2p2f_combos,
                },
                "3p1f" : {
                    "mass4l" : h1_zz_3p1f_m4l,
                    "n_quartets" : h1_zz_n3p1f_combos,
                }
            },
        }
    
    evt_info_d = make_evt_info_d()  # Info for printing.
    evt_info_2p2f_3p1f_d = {}  # Info for json file.

    assert infile_fakerates is not None
    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end = \
        retrieve_FR_hists(infile_fakerates)

    if outfile_json is not None:
        check_overwrite(outfile_json, overwrite=overwrite)
    
    # Make pointers to store new values. 
    ptr_finalState = np.array([0], dtype=int)
    ptr_nZXCRFailedLeptons = np.array([0], dtype=int)
    ptr_is2P2F = np.array([0], dtype=int)  # Close enough to bool lol.
    ptr_is3P1F = np.array([0], dtype=int)
    ptr_isData = np.array([0], dtype=int)
    ptr_isMCzz = np.array([0], dtype=int)
    ptr_fr2_down = array('f', [0.])
    ptr_fr2 = array('f', [0.])
    ptr_fr2_up = array('f', [0.])
    ptr_fr3_down = array('f', [0.])
    ptr_fr3 = array('f', [0.])
    ptr_fr3_up = array('f', [0.])
    ptr_eventWeightFR_down = array('f', [0.])
    ptr_eventWeightFR = array('f', [0.])
    ptr_eventWeightFR_up = array('f', [0.])
    ptr_lep_RedBkgindex = array('i', [0, 0, 0, 0])
    ptr_mass4l = array('f', [0.])
    ptr_massZ1 = array('f', [0.])
    ptr_massZ2 = array('f', [0.])
    # ptr_mass4l_vtxFSR_BS = array('f', [0.])
    # ptr_eventWeight = array('f', [0.])

    if outfile_root is not None:
        check_overwrite(outfile_root, overwrite=overwrite)
        new_file = TFile.Open(outfile_root, "recreate")
        print("Cloning TTree.")
        new_tree = tree.CloneTree(0)  # Clone 0 events.

        # Make new corresponding branches in the TTree.
        new_tree.Branch("is2P2F", ptr_is2P2F, "is2P2F/I")
        new_tree.Branch("is3P1F", ptr_is3P1F, "is3P1F/I")
        new_tree.Branch("isData", ptr_isData, "isData/I")
        new_tree.Branch("isMCzz", ptr_isMCzz, "isMCzz/I")
        new_tree.Branch("fr2_down", ptr_fr2_down, "fr2_down/F")
        new_tree.Branch("fr2", ptr_fr2, "fr2/F")
        new_tree.Branch("fr2_up", ptr_fr2_up, "fr2_up/F")
        new_tree.Branch("fr3_down", ptr_fr3_down, "fr3_down/F")
        new_tree.Branch("fr3", ptr_fr3, "fr3/F")
        new_tree.Branch("fr3_up", ptr_fr3_up, "fr3_up/F")
        new_tree.Branch("eventWeightFR_down", ptr_eventWeightFR_down, "eventWeightFR_down/F")
        new_tree.Branch("eventWeightFR", ptr_eventWeightFR, "eventWeightFR/F")
        new_tree.Branch("eventWeightFR_up", ptr_eventWeightFR_up, "eventWeightFR_up/F")
        # Record the indices of the leptons in passing quartet.
        new_tree.Branch(
            "lep_RedBkgindex",
            ptr_lep_RedBkgindex,
            "lep_RedBkgindex[4]/I"
            )

        # Modify existing values of branches.
        new_tree.SetBranchAddress("finalState", ptr_finalState)
        new_tree.SetBranchAddress("nZXCRFailedLeptons", ptr_nZXCRFailedLeptons)
        if recalc_mass4l_vals:
            new_tree.SetBranchAddress("mass4l", ptr_mass4l)
            new_tree.SetBranchAddress("massZ1", ptr_massZ1)
            new_tree.SetBranchAddress("massZ2", ptr_massZ2)

    n_tot = tree.GetEntries()
    print(
        f"Total number of events: {n_tot}\n"
        f"Looking for AT LEAST 4 leptons per event."
        )
    
    ####################
    #=== Event Loop ===#
    ####################
    isMCzz = 1 if name in "ZZ" else 0
    isData = 1 if name in "Data" else 0
    for evt_num in range(start_at_evt, n_tot):
        if evt_num == break_at_evt:
            break

        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        tree.GetEntry(evt_num)
        run = tree.Run
        lumi = tree.LumiSect
        event = tree.Event
        evt_id = f"{run} : {lumi} : {event}"
        
        ###################################
        #=== Initial event selections. ===#
        ###################################
        try:
            if not tree.passedTrig:
                continue
        except AttributeError:
            # Branch 'passedTrig' doesn't exist.
            warnings.warn(
                f"Branch passedTrig probably doesn't exist!\n"
                f"Ignoring passedTrig==1 criterion."
                )

        if skip_passedFullSelection and tree.passedFullSelection:
            if explain_skipevent:
                print_skipevent_msg(
                    "passedFullSelection == 1", evt_num, run, lumi, event
                    )
            evt_info_d["n_evts_passedFullSelection"] += 1
            continue

        if keep_only_mass4lgt0 and (tree.mass4l <= 0):
            evt_info_d["n_evts_skip_mass4l_le0"] += 1
            continue

        # Check the number of leptons in this event.
        n_tot_leps = len(tree.lep_pt)
        if verbose:
            print(f"  Total number of leptons found: {n_tot_leps}")

        # Ensure at least 4 leptons in event:
        if n_tot_leps < 4:
            if explain_skipevent:
                print_skipevent_msg("n_leps < 4", evt_num, run, lumi, event)
            evt_info_d["n_evts_lt4_leps"] += 1
            continue
            
        # Initialize ALL leptons (possibly >=4 leptons).
        mylep_ls = make_filled_mylep_ls(tree)
        n_tight_leps = get_n_tight_myleps(mylep_ls)
        n_loose_leps = get_n_loose_myleps(mylep_ls)
        if verbose:
            print(
                f"    Num leptons passing tight sel: {n_tight_leps}\n"
                f"    Num leptons failing tight sel: {n_loose_leps}"
               )
            for mylep in mylep_ls:
                mylep.print_info(oneline=True)

        if n_tight_leps < 2:
            evt_info_d["n_evts_lt2tightleps"] += 1
            if explain_skipevent:
                msg = f"  Contains {n_tight_leps} (< 2) tight leps."
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            continue

        ####################################################
        #=== Find best ZZ cand for each lepton quartet. ===#
        ####################################################
        quartcat = QuartetCategorizer(
                mylep_ls,
                verbose=verbose,
                explain_skipevent=explain_skipevent,
                smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                run=run, lumi=lumi, event=event, entry=evt_num,
                stop_when_found_3p1f=stop_when_found_3p1f
                )

        evt_is_3p1plusf = False
        evt_is_2p2plusf = False
        # Events with valid 3P1F ZZ cands have priority!
        # I.e. if an event has valid 3P1F ZZ cands,
        # then don't bother to check for 2P2F ZZ cands.
        if quartcat.has_valid_ZZcand_OS_3p1f:
            evt_is_3p1plusf = True
            n_valid_ZZcands_OS = quartcat.n_valid_ZZcands_OS_3p1f
            ls_valid_ZZcands_OS = quartcat.ls_valid_ZZcands_OS_3p1f
            cr_str = '3P1F'
        elif quartcat.has_valid_ZZcand_OS_2p2f:
            # No valid 3P1F valid_ZZcands_OS so look for 2P2F ones.
            evt_is_2p2plusf = True
            n_valid_ZZcands_OS = quartcat.n_valid_ZZcands_OS_2p2f
            ls_valid_ZZcands_OS = quartcat.ls_valid_ZZcands_OS_2p2f
            cr_str = '2P2F'
        else:
            if explain_skipevent:
                print_skipevent_msg(
                    "No valid 2P2F or 3P1F ZZ candidates.",
                    evt_num, run, lumi, event
                    )
            evt_info_d["n_evts_novalid2P2For3P1F_ZZcands"] += 1
            continue

        if verbose:
            print(f"  Found {n_valid_ZZcands_OS} {cr_str} ZZ candidates.")

        ##############################################################
        #=== Record each valid ZZ cand per quartet in this event. ===#
        ##############################################################
        for ndx_zzcand, zzcand in enumerate(ls_valid_ZZcands_OS, 1):
            nZXCRFailedLeptons = zzcand.get_num_failing_leps()
            # Make sure one of (but not both):
            # 1 lep failed and it's 3P1F or
            # 2 leps failed and it's 2P2F.
            forsure_3p1f = (nZXCRFailedLeptons == 1) and evt_is_3p1plusf
            forsure_2p2f = (nZXCRFailedLeptons == 2) and evt_is_2p2plusf
            assert forsure_3p1f ^ forsure_2p2f  # xor.

            # Event weight calculation.
            n_dataset_tot = float(genwgts_dct[name])
            evt_weight_calcd = get_evt_weight(
                dct_xs=dct_xs, Nickname=name, lumi=int_lumi, event=tree,
                n_dataset_tot=n_dataset_tot, orig_evt_weight=tree.eventWeight
                )
            
            # See which leptons from Z2 failed.
            n_fail_code = check_which_Z2_leps_failed(zzcand)

            mylep1_fromz1 = zzcand.z_fir.mylep1
            mylep2_fromz1 = zzcand.z_fir.mylep2
            mylep1_fromz2 = zzcand.z_sec.mylep1
            mylep2_fromz2 = zzcand.z_sec.mylep2
            #=== 3P1F subevent. ===#
            if n_fail_code == 2:
                # First lep from Z2 failed.
                # NOTE: Turns out this will never trigger!
                # This is due to the way that I build the 3P1F quartets.
                # I always place the 1 failing lepton as the 4th lepton.
                # Therefore, fr3 (the 4th lepton) will always be != 0.
                assert evt_is_3p1plusf
                assert mylep1_fromz2.is_loose
                fr2, fr2_err = get_fakerate_and_error_mylep(
                    mylep1_fromz2,
                    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
                    verbose=verbose
                    )
                fr2_down = calc_fakerate_down(fr2, fr2_err)  # Scale down.
                fr2_up = calc_fakerate_up(fr2, fr2_err)  # Scale up.
                fr3 = 0
                fr3_err = 0
                fr3_down = 0
                fr3_up = 0
                # Use fake rates to calculate new event weight.
                new_weight_down = (fr2_down / (1-fr2_down)) * evt_weight_calcd
                new_weight = (fr2 / (1-fr2)) * evt_weight_calcd
                new_weight_up = (fr2_up / (1-fr2_up)) * evt_weight_calcd
            elif n_fail_code == 3:
                # Second lep from Z2 failed.
                assert evt_is_3p1plusf
                assert mylep2_fromz2.is_loose
                fr2 = 0
                fr2_err = 0
                fr2_down = 0
                fr2_up = 0
                fr3, fr3_err = get_fakerate_and_error_mylep(
                    mylep2_fromz2,
                    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
                    verbose=verbose
                    )
                fr3_down = calc_fakerate_down(fr3, fr3_err)  # Scale down.
                fr3_up = calc_fakerate_up(fr3, fr3_err)  # Scale up.
                # Use fake rates to calculate new event weight.
                new_weight_down = (fr3_down / (1-fr3_down)) * evt_weight_calcd
                new_weight = (fr3 / (1-fr3)) * evt_weight_calcd
                new_weight_up = (fr3_up / (1-fr3_up)) * evt_weight_calcd
            #=== 2P2F subevent. ===#
            elif n_fail_code == 5:
                # Both leps failed.
                assert evt_is_2p2plusf
                fr2, fr2_err = get_fakerate_and_error_mylep(
                    mylep1_fromz2,
                    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
                    verbose=verbose
                    )
                fr3, fr3_err = get_fakerate_and_error_mylep(
                    mylep2_fromz2,
                    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
                    verbose=verbose
                    )
                fr2_down = calc_fakerate_down(fr2, fr2_err)  # Scale down.
                fr2_up = calc_fakerate_up(fr2, fr2_err)  # Scale up.
                fr3_down = calc_fakerate_down(fr3, fr3_err)  # Scale down.
                fr3_up = calc_fakerate_up(fr3, fr3_err)  # Scale up.
                # Use fake rates to calculate new event weight.
                new_weight_down = (fr2_down / (1-fr2_down)) * (fr3_down / (1-fr3_down)) * evt_weight_calcd
                new_weight = (fr2 / (1-fr2)) * (fr3 / (1-fr3)) * evt_weight_calcd
                new_weight_up = (fr2_up / (1-fr2_up)) * (fr3_up / (1-fr3_up)) * evt_weight_calcd

            if match_lep_Hindex:
                # Make sure mass4l vars in TTree come from same leps
                # as the leps that built the ZZ candidate I selected.
                lep_Hindex_ls = list(tree.lep_Hindex)
                myleps_ls_ptorder = zzcand.z_fir.get_mylep_idcs_pTorder() + \
                                    zzcand.z_sec.get_mylep_idcs_pTorder()
                raise RuntimeError(
                    f'Need to update this to allow for matches, like:\n'
                    f'  lep_Hindex = [2, 3, 1, 4]\n'
                    f'  this_quart = [3, 2, 1, 4]\n'
                    f'  that_quart = [3, 2, 4, 1]\n'
                    f'All of which should be valid matches!'
                    )
                if lep_Hindex_ls != myleps_ls_ptorder:
                    evt_info_d["n_quartets_skip_lep_Hindex_mismatch"] += 1
                    continue

            if verbose:
                print(
                    f"ZZcand is {'3P1F' if evt_is_3p1plusf else '2P2F'}\n"
                    f"  This fail code: {n_fail_code}\n"
                    f"  Z2 lep codes FOR DEBUGGING:\n"
                    f"  ===========================\n"
                    f"  0, if neither lep from Z2 failed\n"
                    f"  2, if first lep from Z2 failed\n"
                    f"  3, if second lep from Z2 failed\n"
                    f"  5, if both leps from Z2 failed\n"
                    f"  ===========================\n"
                    f"  fr2_down={fr2_down:.6f}, fr3_down={fr3_down:.6f}\n"
                    f"       fr2={fr2:.6f},      fr3={fr3:.6f}\n"
                    f"    fr2_up={fr2_up:.6f},   fr3_up={fr3_up:.6f}\n"
                    f"         tree.eventWeight = {tree.eventWeight:.6f}\n"
                    f"         evt_weight_calcd = {evt_weight_calcd:.6f}\n"
                    f"          new_weight_down = {new_weight_down:.6f}\n"
                    f"               new_weight = {new_weight:.6f}\n"
                    f"            new_weight_up = {new_weight_up:.6f}"
                )
                n_zzcands = len(ls_valid_ZZcands_OS)
                zzcand.print_info(
                    name=f"SELECTED ZZ CAND ({ndx_zzcand}/{n_zzcands})"
                    )

            # Save this quartet in TTree. Fill branches.
            lep_idcs = [
                mylep1_fromz1.ndx_lepvec,
                mylep2_fromz1.ndx_lepvec,
                mylep1_fromz2.ndx_lepvec,
                mylep2_fromz2.ndx_lepvec,
                ]
            ptr_finalState[0] = dct_finalstates_str2int[zzcand.get_finalstate()]
            ptr_nZXCRFailedLeptons[0] = nZXCRFailedLeptons
            ptr_is2P2F[0] = evt_is_2p2plusf
            ptr_is3P1F[0] = evt_is_3p1plusf
            ptr_isData[0] = isData
            ptr_isMCzz[0] = isMCzz
            ptr_fr2_down[0] = fr2_down
            ptr_fr2[0] = fr2
            ptr_fr2_up[0] = fr2_up
            ptr_fr3_down[0] = fr3_down
            ptr_fr3[0] = fr3
            ptr_fr3_up[0] = fr3_up
            ptr_eventWeightFR_down[0] = new_weight_down
            ptr_eventWeightFR[0] = new_weight
            ptr_eventWeightFR_up[0] = new_weight_up
            ptr_lep_RedBkgindex[0] = lep_idcs[0]
            ptr_lep_RedBkgindex[1] = lep_idcs[1]
            ptr_lep_RedBkgindex[2] = lep_idcs[2]
            ptr_lep_RedBkgindex[3] = lep_idcs[3]

            if recalc_mass4l_vals:
                ptr_massZ1[0] = zzcand.z_fir.get_mass()
                ptr_massZ2[0] = zzcand.z_sec.get_mass()
                ptr_mass4l[0] = zzcand.get_m4l()
                # Getting an IndexError since there is a discrepancy in the length
                # of vectors, like `lep_pt` and `vtxLepFSR_BS_pt`.
                # ptr_mass4l[0] = calc_mass4l_from_idcs(
                #     tree, lep_idcs, kind="lepFSR"
                #     )
                # ptr_mass4l_vtxFSR_BS[0] = calc_mass4l_from_idcs(
                #     tree, lep_idcs, kind="vtxLepFSR_BS"
                #     )

            # Save each quartet (ZZcand) as a separate entry in TTree.
            if outfile_root is not None:
                new_tree.Fill()

            if verbose:
                print(
                    f"** ZZ cand {ndx_zzcand} passed OS Method Sel: **\n"
                    f"   CR {cr_str}: {evt_id}, (row {evt_num})"
                    )

            if keep_first_quartet:
                warnings.warn(
                    f'Keeping only the first (arbitrary!) '
                    f'lepton quartet found in the event.'
                    )
                break
        # End loop over quartets.

        # Final counts.
        evt_info_d["n_good_redbkg_evts"] += 1
        if evt_is_3p1plusf:
            cr = "3p1f"
            n_quartets_3p1f = n_valid_ZZcands_OS
            n_quartets_2p2f = 0
            evt_info_d["n_tot_3p1f_quartets"] += n_quartets_3p1f
            evt_info_d["n_good_3p1f_evts"] += 1
        if evt_is_2p2plusf:
            cr = "2p2f"
            n_quartets_3p1f = 0
            n_quartets_2p2f = n_valid_ZZcands_OS
            evt_info_d["n_tot_2p2f_quartets"] += n_quartets_2p2f
            evt_info_d["n_good_2p2f_evts"] += 1

        evt_info_2p2f_3p1f_d[evt_id] = {
            "num_combos_2p2f" : n_quartets_2p2f,
            "num_combos_3p1f" : n_quartets_3p1f,
            }

        if fill_hists:
            d_hists[name][cr]["mass4l"].Fill(tree.mass4l, new_weight)
            d_hists[name][cr]["n_quartets"].Fill(n_valid_ZZcands_OS, 1)
            h2_n3p1fcombos_n2p2fcombos.Fill(n_quartets_2p2f, n_quartets_3p1f, 1)
    print("End loop over events.")

    print("Event info:")
    pretty_print_dict(evt_info_d)

    if outfile_root is not None:
        print(f"Writing tree to root file:\n{outfile_root}")
        new_tree.Write()

        if fill_hists:
            print(f"Writing hists to root file:\n{outfile_root}")
            for d_name in d_hists.values():
                for d_cr in d_name.values():
                    for h in d_cr.values():
                        h.Write()
            h2_n3p1fcombos_n2p2fcombos.Write()

        new_file.Close()

    if outfile_json is not None:
        save_to_json(evt_info_2p2f_3p1f_d, outfile_json, overwrite=overwrite,
                    sort_keys=False)

# def evt_loop_evtsel_WCF(
#     tree,
#     infile_fakerates,
#     genwgts_dct,
#     dct_xs,
#     outfile_root=None, outfile_json=None,
#     name="", int_lumi=59830,
#     start_at_evt=0, break_at_evt=-1,
#     fill_hists=True,
#     explain_skipevent=False, verbose=False, print_every=50000,
#     smartcut_ZapassesZ1sel=False,
#     overwrite=False,
#     keep_only_mass4lgt0=False,
#     match_lep_Hindex=False,
#     recalc_mass4l_vals=False,
#     skip_passedFullSelection=True,
#     ):
#     """Select RedBkg wrong charge/flavor events.

#     Select events in which:
#         - Z1 is built from OSSF leptons.
#         - Z2 is built from a pair of leptons that are, either:
#             * SSSF: same sign, same flavor => e.g. [mu^+, mu^+], [e^-, e^-]
#             * OSOF: opp. sign, opp. flavor => e.g. [mu^+, e^-]
#         - When an event has >4 leptons, then multiple combinations
#             of 2P2F/3P1F are possible.
#             Suppose you have an event with 5 leptons, 3 of which pass tight
#             selection and 2 fail tight selection.
#             Then we have two different ways to make a 3P1F combo
#             (two 3P1F subevents).
#             NOTE: ^Not implemented yet!
#         - Does NOT select the BEST ZZ candidate per event.
#             If there are >1 ZZ candidates that pass ZZ selections,
#             then each ZZ cand is saved as a separate entry in the TTree.
#             This means a single event can show up multiple times in a TTree,
#             if there are multiple valid 4-lepton combinations ("quartets").

#     Args:
#         outfile_root (str):
#             Path to store root file.
#             TTree of selected events will be made.
#             If `fill_hists` is True, then will store histograms.
#         smartcut_ZapassesZ1sel (bool, optional):
#             In the smart cut, the literature essentially says that if a Za
#             looks like a more on-shell Z boson than the Z1 AND if the Zb is a
#             low mass di-lep resonance, then veto the whole ZZ candidate.
#             However, literature doesn't check for Za passing Z1 selections!
#             Set this to True if you require Za to pass Z1 selections.
#             Default is False.
#         keep_only_mass4lgt0 (bool, optional):
#             If True, then skip events whose tree.mass4l <= 0.
#             This is useful when you need to use the values that are already
#             stored in the BBF NTuple.
#             Default is False.
#         match_lep_Hindex (bool, optional):
#             If True, then only keep the quartets whose selected lepton indices
#             exactly match those found in vector tree.lep_Hindex.
#             Good for synchronizing with the BBF Analyzer.
#             Default is False.
#         recalc_mass4l_vals (bool, optional):
#             If True, recalculate mass4l of selected lepton quartet and
#             corresponding massZ1 and massZ2 values.
#     """
#     if fill_hists:
#         # Prep histograms.
#         d_hists = {
#             "Data" : {
#                 "2p2f" : {
#                     "mass4l" : h1_data_2p2f_m4l,
#                     "combos" : h1_data_n2p2f_combos,
#                 },
#                 "3p1f" : {
#                     "mass4l" : h1_data_3p1f_m4l,
#                     "combos" : h1_data_n3p1f_combos,
#                 }
#             },
#             "ZZ" : {
#                 "2p2f" : {
#                     "mass4l" : h1_zz_2p2f_m4l,
#                     "combos" : h1_zz_n2p2f_combos,
#                 },
#                 "3p1f" : {
#                     "mass4l" : h1_zz_3p1f_m4l,
#                     "combos" : h1_zz_n3p1f_combos,
#                 }
#             },
#         }
    
#     evt_info_d = make_evt_info_d()  # Info for printing.
#     evt_info_2p2f_3p1f_d = {}  # Info for json file.

#     assert infile_fakerates is not None
#     h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end = retrieve_FR_hists(
#                                                     infile_fakerates
#                                                     )

#     if outfile_json is not None:
#         check_overwrite(outfile_json, overwrite=overwrite)
    
#     # Make pointers to store new values. 
#     ptr_finalState = np.array([0], dtype=int)
#     ptr_nZXCRFailedLeptons = np.array([0], dtype=int)
#     ptr_is2P2F = np.array([0], dtype=int)  # Close enough to bool lol.
#     ptr_is3P1F = np.array([0], dtype=int)
#     ptr_isData = np.array([0], dtype=int)
#     ptr_isMCzz = np.array([0], dtype=int)
#     ptr_fr2_down = array('f', [0.])
#     ptr_fr2 = array('f', [0.])
#     ptr_fr2_up = array('f', [0.])
#     ptr_fr3_down = array('f', [0.])
#     ptr_fr3 = array('f', [0.])
#     ptr_fr3_up = array('f', [0.])
#     ptr_eventWeightFR_down = array('f', [0.])
#     ptr_eventWeightFR = array('f', [0.])
#     ptr_eventWeightFR_up = array('f', [0.])
#     ptr_lep_RedBkgindex = array('i', [0, 0, 0, 0])
#     ptr_mass4l = array('f', [0.])
#     ptr_massZ1 = array('f', [0.])
#     ptr_massZ2 = array('f', [0.])
#     # ptr_mass4l_vtxFSR_BS = array('f', [0.])
#     # ptr_eventWeight = array('f', [0.])

#     if outfile_root is not None:
#         check_overwrite(outfile_root, overwrite=overwrite)
#         new_file = TFile.Open(outfile_root, "recreate")
#         print("Cloning TTree.")
#         new_tree = tree.CloneTree(0)  # Clone 0 events.

#         # Make new corresponding branches in the TTree.
#         new_tree.Branch("is2P2F", ptr_is2P2F, "is2P2F/I")
#         new_tree.Branch("is3P1F", ptr_is3P1F, "is3P1F/I")
#         new_tree.Branch("isData", ptr_isData, "isData/I")
#         new_tree.Branch("isMCzz", ptr_isMCzz, "isMCzz/I")
#         new_tree.Branch("fr2_down", ptr_fr2_down, "fr2_down/F")
#         new_tree.Branch("fr2", ptr_fr2, "fr2/F")
#         new_tree.Branch("fr2_up", ptr_fr2_up, "fr2_up/F")
#         new_tree.Branch("fr3_down", ptr_fr3_down, "fr3_down/F")
#         new_tree.Branch("fr3", ptr_fr3, "fr3/F")
#         new_tree.Branch("fr3_up", ptr_fr3_up, "fr3_up/F")
#         new_tree.Branch("eventWeightFR_down", ptr_eventWeightFR_down, "eventWeightFR_down/F")
#         new_tree.Branch("eventWeightFR", ptr_eventWeightFR, "eventWeightFR/F")
#         new_tree.Branch("eventWeightFR_up", ptr_eventWeightFR_up, "eventWeightFR_up/F")
#         # Record the indices of the leptons in passing quartet.
#         new_tree.Branch(
#             "lep_RedBkgindex",
#             ptr_lep_RedBkgindex,
#             "lep_RedBkgindex[4]/I"
#             )

#         # Modify existing values of branches.
#         new_tree.SetBranchAddress("finalState", ptr_finalState)
#         new_tree.SetBranchAddress("nZXCRFailedLeptons", ptr_nZXCRFailedLeptons)
#         if recalc_mass4l_vals:
#             new_tree.SetBranchAddress("mass4l", ptr_mass4l)
#             new_tree.SetBranchAddress("massZ1", ptr_massZ1)
#             new_tree.SetBranchAddress("massZ2", ptr_massZ2)

#     n_tot = tree.GetEntries()
#     print(
#         f"Total number of events: {n_tot}\n"
#         f"Looking for AT LEAST 4 leptons per event."
#         )
    
#     ####################
#     #=== Event Loop ===#
#     ####################
#     isMCzz = 1 if name in "ZZ" else 0
#     isData = 1 if name in "Data" else 0
#     for evt_num in range(start_at_evt, n_tot):
#         if evt_num == break_at_evt:
#             break

#         print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

#         tree.GetEntry(evt_num)
#         run = tree.Run
#         lumi = tree.LumiSect
#         event = tree.Event
#         evt_id = f"{run} : {lumi} : {event}"
        
#         ###################################
#         #=== Initial event selections. ===#
#         ###################################
#         try:
#             if not tree.passedTrig:
#                 continue
#         except AttributeError:
#             # Branch 'passedTrig' doesn't exist.
#             warnings.warn(
#                 f"Branch passedTrig probably doesn't exist!\n"
#                 f"Ignoring passedTrig==1 criterion."
#                 )

#         if skip_passedFullSelection and tree.passedFullSelection:
#             if explain_skipevent:
#                 print_skipevent_msg(
#                     "passedFullSelection == 1", evt_num, run, lumi, event
#                     )
#             evt_info_d["n_evts_passedFullSelection"] += 1
#             continue

#         if keep_only_mass4lgt0 and (tree.mass4l <= 0):
#             evt_info_d["n_evts_skip_mass4l_le0"] += 1
#             continue

#         # Check the number of leptons in this event.
#         n_tot_leps = len(tree.lepFSR_pt)
#         if verbose: print(f"  Total number of leptons found: {n_tot_leps}")

#         # Ensure at least 4 leptons in event:
#         if n_tot_leps < 4:
#             if explain_skipevent:
#                 print_skipevent_msg("n_leps < 4", evt_num, run, lumi, event)
#             evt_info_d["n_evts_lt4_leps"] += 1
#             continue
            
#         # Initialize ALL leptons (possibly >=4 leptons).
#         mylep_ls = make_filled_mylep_ls(tree)
#         n_tight_leps = get_n_tight_myleps(mylep_ls)
#         n_loose_leps = get_n_loose_myleps(mylep_ls)

#         if n_tight_leps < 2:
#             evt_info_d["n_evts_lt2tightleps"] += 1
#             if explain_skipevent:
#                 msg = f"  Contains {n_tight_leps} (< 2) tight leps."
#                 print_skipevent_msg(msg, evt_num, run, lumi, event)
#             continue

#         # Guaranteed to have at least 4 leptons per event.
#         # At least 2 tight leptons.
#         # The remaining leptons should be loose.

#         #############################################################
#         #=== Make all lepton quartets (i.e. make all subevents). ===#
#         #############################################################
#         evt_is_2p2plusf = False
#         evt_is_3p1plusf = False
#         err_msg = (
#             f"  Should not get here. Correct the logic!\n"
#             f"    n_loose_leps={n_loose_leps}, n_tight_leps={n_tight_leps}, "
#             f"entry {evt_num}"
#             )
#         if n_tight_leps == 2:
#             if n_loose_leps < 2:
#                 print(err_msg)
#                 for lep in mylep_ls:
#                     lep.print_info()
#                 raise RuntimeError
#             # Event has 2P2F quartet(s).
#             evt_is_2p2plusf = True
#             fourlep_combos = find_combos_2tight2loose(mylep_ls)
#         elif n_tight_leps == 3:
#             if n_loose_leps < 1:
#                 print(err_msg)
#                 for lep in mylep_ls:
#                     lep.print_info()
#                 raise RuntimeError
#             # Event has 3P1F quartet(s).
#             evt_is_3p1plusf = True
#             fourlep_combos = find_combos_3tight1loose(mylep_ls)
#         elif n_tight_leps >= 4:
#             print(
#                 f"  [WARNING] Found {n_tight_leps} tight leptons, "
#                 f"but may assign quartets as 3P1F if found!"
#                 )
#             evt_is_3p1plusf = True
#             fourlep_combos = find_combos_3tight1loose(mylep_ls)
#         else:
#             raise ValueError(err_msg)
        
#         #################################################
#         #=== Analyze each lepton quartet (subevent). ===#
#         #################################################
#         n_quartets_2p2f = 0
#         n_quartets_3p1f = 0
#         if verbose:
#             print(f"  Found {len(fourlep_combos)} quartets.")
            
#         for fourlep_tup in fourlep_combos:
#             # Check which four-lep combos pass ZZ selections.
#             # Get the better ZZ cand from a single lepton quartet.
#             ls_zzcand = get_ZZcands_from_myleps_OSmethod(
#                     fourlep_tup,
#                     verbose=verbose, explain_skipevent=explain_skipevent,
#                     smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
#                     run=run, lumi=lumi, event=event, entry=evt_num
#                     )
#             if len(ls_zzcand) == 0:
#                 evt_info_d["n_quartets_zerogoodZZcands"] += 1
#                 # No good ZZ candidate found.
#                 continue

#             # Good 2P2F or 3P1F subevent!
#             # For now, the function above only picks out a single ZZ cand.
#             zzcand = ls_zzcand[0]

#             if match_lep_Hindex:
#                 # Make sure mass4l vars in TTree come from same leps
#                 # as the leps that built the ZZ candidate I selected.
#                 lep_Hindex_ls = list(tree.lep_Hindex)
#                 myleps_ls_ptorder = zzcand.z_fir.get_mylep_idcs_pTorder() + \
#                                     zzcand.z_sec.get_mylep_idcs_pTorder()
#                 if lep_Hindex_ls != myleps_ls_ptorder:
#                     evt_info_d["n_quartets_skip_lep_Hindex_mismatch"] += 1
#                     continue
                
#             subevt_passes_sel_2p2f = evt_is_2p2plusf
#             subevt_passes_sel_3p1f = evt_is_3p1plusf

#             if subevt_passes_sel_2p2f:
#                 nZXCRFailedLeptons = 2
#                 n_quartets_2p2f += 1
#                 evt_info_d["n_tot_2p2f_quartets"] += 1
#             elif subevt_passes_sel_3p1f:
#                 nZXCRFailedLeptons = 1
#                 n_quartets_3p1f += 1
#                 evt_info_d["n_tot_3p1f_quartets"] += 1
#             else:
#                 raise ValueError("SHOULD NEVER TRIGGER.")

#             # Event weight calculation.
#             n_dataset_tot = float(genwgts_dct[name])
#             evt_weight_calcd = get_evt_weight(
#                 dct_xs=dct_xs, Nickname=name, lumi=int_lumi, event=tree,
#                 n_dataset_tot=n_dataset_tot, orig_evt_weight=tree.eventWeight
#                 )
            
#             # See which leptons from Z2 failed.
#             n_fail_code = check_which_Z2_leps_failed(zzcand)

#             mylep1_fromz1 = zzcand.z_fir.mylep1
#             mylep2_fromz1 = zzcand.z_fir.mylep2
#             mylep1_fromz2 = zzcand.z_sec.mylep1
#             mylep2_fromz2 = zzcand.z_sec.mylep2
#             #=== 3P1F subevent. ===#
#             if n_fail_code == 2:
#                 # First lep from Z2 failed.
#                 # NOTE: Turns out this will never trigger!
#                 # This is due to the way that I build the 3P1F quartets.
#                 # I always place the 1 failing lepton as the 4th lepton.
#                 # Therefore, fr3 (the 4th lepton) will always be != 0.
#                 assert subevt_passes_sel_3p1f
#                 assert mylep1_fromz2.is_loose
#                 fr2, fr2_err = get_fakerate_and_error_mylep(
#                     mylep1_fromz2,
#                     h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
#                     verbose=verbose
#                     )
#                 fr2_down = calc_fakerate_down(fr2, fr2_err)  # Scale down.
#                 fr2_up = calc_fakerate_up(fr2, fr2_err)  # Scale up.
#                 fr3 = 0
#                 fr3_err = 0
#                 fr3_down = 0
#                 fr3_up = 0
#                 # Use fake rates to calculate new event weight.
#                 new_weight_down = (fr2_down / (1-fr2_down)) * evt_weight_calcd
#                 new_weight = (fr2 / (1-fr2)) * evt_weight_calcd
#                 new_weight_up = (fr2_up / (1-fr2_up)) * evt_weight_calcd
#             elif n_fail_code == 3:
#                 # Second lep from Z2 failed.
#                 assert subevt_passes_sel_3p1f
#                 assert mylep2_fromz2.is_loose
#                 fr2 = 0
#                 fr2_err = 0
#                 fr2_down = 0
#                 fr2_up = 0
#                 fr3, fr3_err = get_fakerate_and_error_mylep(
#                     mylep2_fromz2,
#                     h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
#                     verbose=verbose
#                     )
#                 fr3_down = calc_fakerate_down(fr3, fr3_err)  # Scale down.
#                 fr3_up = calc_fakerate_up(fr3, fr3_err)  # Scale up.
#                 # Use fake rates to calculate new event weight.
#                 new_weight_down = (fr3_down / (1-fr3_down)) * evt_weight_calcd
#                 new_weight = (fr3 / (1-fr3)) * evt_weight_calcd
#                 new_weight_up = (fr3_up / (1-fr3_up)) * evt_weight_calcd
#             #=== 2P2F subevent. ===#
#             elif n_fail_code == 5:
#                 # Both leps failed.
#                 assert subevt_passes_sel_2p2f
#                 fr2, fr2_err = get_fakerate_and_error_mylep(
#                     mylep1_fromz2,
#                     h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
#                     verbose=verbose
#                     )
#                 fr3, fr3_err = get_fakerate_and_error_mylep(
#                     mylep2_fromz2,
#                     h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
#                     verbose=verbose
#                     )
#                 fr2_down = calc_fakerate_down(fr2, fr2_err)  # Scale down.
#                 fr2_up = calc_fakerate_up(fr2, fr2_err)  # Scale up.
#                 fr3_down = calc_fakerate_down(fr3, fr3_err)  # Scale down.
#                 fr3_up = calc_fakerate_up(fr3, fr3_err)  # Scale up.
#                 # Use fake rates to calculate new event weight.
#                 new_weight_down = (fr2_down / (1-fr2_down)) * (fr3_down / (1-fr3_down)) * evt_weight_calcd
#                 new_weight = (fr2 / (1-fr2)) * (fr3 / (1-fr3)) * evt_weight_calcd
#                 new_weight_up = (fr2_up / (1-fr2_up)) * (fr3_up / (1-fr3_up)) * evt_weight_calcd

#             if verbose:
#                 print(
#                     f"Subevent is:\n"
#                     f"  2P2F={subevt_passes_sel_2p2f}, "
#                     f"3P1F={subevt_passes_sel_3p1f}\n"
#                     f"  This fail code: {n_fail_code}\n"
#                     f"  Z2 lep codes FOR DEBUGGING:\n"
#                     f"  ===========================\n"
#                     f"  0, if neither lep from Z2 failed\n"
#                     f"  2, if first lep from Z2 failed\n"
#                     f"  3, if second lep from Z2 failed\n"
#                     f"  5, if both leps from Z2 failed\n"
#                     f"  ===========================\n"
#                     f"  fr2_down={fr2_down:.6f}, fr3_down={fr3_down:.6f}\n"
#                     f"       fr2={fr2:.6f},      fr3={fr3:.6f}\n"
#                     f"    fr2_up={fr2_up:.6f},   fr3_up={fr3_up:.6f}\n"
#                     # f"eventWeight(from NTuple) = {tree.eventWeight:.6f}\n"
#                     f"    tree.eventWeight = {tree.eventWeight:.6f}\n"
#                     f"    evt_weight_calcd = {evt_weight_calcd:.6f}\n"
#                     f"          new_weight_down = {new_weight_down:.6f}\n"
#                     f"               new_weight = {new_weight:.6f}\n"
#                     f"            new_weight_up = {new_weight_up:.6f}"
#                 )
#                 zzcand.print_info(name="SELECTED")

#             # Save this subevent in TTree. Fill branches.
#             lep_idcs = [
#                 mylep1_fromz1.ndx_lepvec,
#                 mylep2_fromz1.ndx_lepvec,
#                 mylep1_fromz2.ndx_lepvec,
#                 mylep2_fromz2.ndx_lepvec,
#                 ]
#             ptr_finalState[0] = dct_finalstates_str2int[zzcand.get_finalstate()]
#             ptr_nZXCRFailedLeptons[0] = nZXCRFailedLeptons
#             ptr_is2P2F[0] = subevt_passes_sel_2p2f
#             ptr_is3P1F[0] = subevt_passes_sel_3p1f
#             ptr_isData[0] = isData
#             ptr_isMCzz[0] = isMCzz
#             ptr_fr2_down[0] = fr2_down
#             ptr_fr2[0] = fr2
#             ptr_fr2_up[0] = fr2_up
#             ptr_fr3_down[0] = fr3_down
#             ptr_fr3[0] = fr3
#             ptr_fr3_up[0] = fr3_up
#             ptr_eventWeightFR_down[0] = new_weight_down
#             ptr_eventWeightFR[0] = new_weight
#             ptr_eventWeightFR_up[0] = new_weight_up
#             ptr_lep_RedBkgindex[0] = lep_idcs[0]
#             ptr_lep_RedBkgindex[1] = lep_idcs[1]
#             ptr_lep_RedBkgindex[2] = lep_idcs[2]
#             ptr_lep_RedBkgindex[3] = lep_idcs[3]

#             if recalc_mass4l_vals:
#                 # Getting an IndexError since there is a discrepancy in the length
#                 # of vectors, like `lep_pt` and `vtxLepFSR_BS_pt`.
#                 ptr_massZ1[0] = zzcand.z_fir.get_mass()
#                 ptr_massZ2[0] = zzcand.z_sec.get_mass()
#                 ptr_mass4l[0] = zzcand.get_m4l()
#                 # ptr_mass4l[0] = calc_mass4l_from_idcs(
#                 #     tree, lep_idcs, kind="lepFSR"
#                 #     )
#                 # ptr_mass4l_vtxFSR_BS[0] = calc_mass4l_from_idcs(
#                 #     tree, lep_idcs, kind="vtxLepFSR_BS"
#                 #     )
#             if outfile_root is not None:
#                 new_tree.Fill()
#         # End loop over subevents.

#         #=== Some sanity checks. ===#
#         # Make sure at least 1 subevent from main event passed selection.
#         if (n_quartets_2p2f == 0) and (n_quartets_3p1f == 0):
#             evt_info_d["n_evts_nosubevtspassingsel"] += 1
#             if explain_skipevent:
#                 msg = "No subevents pass OS Method selection."
#                 print_skipevent_msg(msg, evt_num, run, lumi, event)
#             continue

#         # Recall that we should have either ONLY 3P1F or ONLY 2P2F subevents.
#         evt_info_d["n_good_redbkg_evts"] += 1
#         if evt_is_2p2plusf:
#             evt_type_msg = "2P2+F"
#             cr = "2p2f"
#             n_combos = n_quartets_2p2f
#             evt_info_d["n_good_2p2f_evts"] += 1
#             assert n_quartets_3p1f == 0
#         if evt_is_3p1plusf:
#             evt_type_msg = "3P1+F"
#             cr = "3p1f"
#             n_combos = n_quartets_3p1f
#             evt_info_d["n_good_3p1f_evts"] += 1
#             assert n_quartets_2p2f == 0

#         if verbose:
#             print(
#                 f"** Event passed CJLST OS Method Selections: **\n"
#                 f"     Event type {evt_type_msg}, {evt_id}, (entry {evt_num})"
#                 )
        
#         evt_info_2p2f_3p1f_d[evt_id] = {
#             "num_combos_2p2f" : n_quartets_2p2f,
#             "num_combos_3p1f" : n_quartets_3p1f,
#             }

#         if fill_hists:
#             d_hists[name][cr]["mass4l"].Fill(tree.mass4l, new_weight)
#             d_hists[name][cr]["combos"].Fill(n_combos, 1)
#             h2_n3p1fcombos_n2p2fcombos.Fill(n_quartets_2p2f, n_quartets_3p1f, 1)
#     print("End loop over events.")

#     print("Event info:")
#     pretty_print_dict(evt_info_d)

#     if outfile_root is not None:
#         print(f"Writing tree to root file:\n{outfile_root}")
#         new_tree.Write()

#         if fill_hists:
#             print(f"Writing hists to root file:\n{outfile_root}")
#             for d_name in d_hists.values():
#                 for d_cr in d_name.values():
#                     for h in d_cr.values():
#                         h.Write()
#             h2_n3p1fcombos_n2p2fcombos.Write()

#         new_file.Close()

#     if outfile_json is not None:
#         save_to_json(evt_info_2p2f_3p1f_d, outfile_json, overwrite=overwrite,
#                     sort_keys=False)
    
def fillhists_osmethod_cjlstntuple(
    t,
    infile_fakerates,
    m4l_window=(70, 870),
    start_at=0, break_at=-1,
    print_every=10000,
    use_first_quartet=False
    ):
    """Select OS Method events in CJLST NTuple and fill hists.
    
    Args:
        m4l_window (2-tup, optional):
            (m4l_min, m4l_max) in GeV.
            Default is (70, 870).
        use_first_quartet (bool, optional):
            Doesn't do anything but needed since sister function
            (fillhists_osmethod_bbfntuple) has it has an argument.
            Default is False.

    TODO:
        [ ] Combine this function and the sister bbf function.
            Factor out the code before and after event loop.
    """
    d_2p2f_fs_hists, d_3p1f_fs_hists, d_2p2fpred_fs_hists, d_3p1fpred_fs_hists, d_2p2fin3p1f_fs_hists = make_dct_hists_all_crs(
        h1_data_2p2f_m4l,
        h1_data_3p1f_m4l,
        h1_data_2p2fpred_m4l,
        h1_data_3p1fpred_m4l,
        h1_data_2p2fin3p1f_m4l
        )

    h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE = retrieve_FR_hists(
        infile_fakerates
        )

    n_tot = t.GetEntries()
    for evt_num in range(start_at, n_tot):
        print_periodic_evtnum(evt_num, n_tot, print_every)
        if evt_num == break_at:
            break
        t.GetEntry(evt_num)

        is_3p1f = (t.CRflag == CjlstFlag['CR3P1F'].value)
        is_2p2f = (t.CRflag == CjlstFlag['CR2P2F'].value)
        # Only want 2P2F or 3P1F events.
        if not (is_3p1f or is_2p2f):
            continue

        m4l = t.ZZMass
        m4l_min = m4l_window[0]
        m4l_max = m4l_window[1]
        if (m4l < m4l_min) or (m4l > m4l_max):
            continue

        # Determine final state.
        fs = convert_to_bbf_fs(t.Z1Flav, t.Z2Flav)

        # Get info on which leptons are fakes.
        ls_isfakelep = []
        for idx in range(4):
            lep_pdgID = t.LepLepId[idx]
            lep_is_tightID = bool(t.LepisID[idx])
            lep_iso = t.LepCombRelIsoPF[idx]
            is_tightlep = is_tight_cjlst_lep(lep_pdgID, lep_is_tightID, lep_iso)
            ls_isfakelep.append(not is_tightlep)

        # Lepton numbering: 0, 1, 2, 3
        if is_3p1f:
            # Make sure only 1 of the leptons is a fake.
            assert (ls_isfakelep[2] ^ ls_isfakelep[3])  # xor.
            assert sum(ls_isfakelep) == 1
            # Get index of fake lep.
            idx_of_fake = ls_isfakelep.index(True)
            fakelep_id = t.LepLepId[idx_of_fake]
            fakelep_pt = t.LepPt[idx_of_fake]  # No FSR.
            fakelep_eta = t.LepEta[idx_of_fake]  # No FSR.

            wgt_fr = calc_wgt_3p1f_cr(
                fakelep_id, fakelep_pt, fakelep_eta,
                h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
                )
            d_3p1f_fs_hists[fs].Fill(m4l, 1)
            d_3p1fpred_fs_hists[fs].Fill(m4l, wgt_fr)
            # Inclusive.
            h1_data_3p1f_m4l.Fill(m4l, 1)
            h1_data_3p1fpred_m4l.Fill(m4l, wgt_fr)
        elif is_2p2f:
            # Make sure that leps 2 and 3 are fake.
            assert ls_isfakelep[2] and ls_isfakelep[3]
            assert sum(ls_isfakelep) == 2
            fakelep_id1, fakelep_id2 = t.LepLepId[2:]
            fakelep_pt1, fakelep_pt2 = t.LepPt[2:]  # No FSR.
            fakelep_eta1, fakelep_eta2 = t.LepEta[2:]  # No FSR.

            wgt_fr = calc_wgt_2p2f_cr(
                fakelep_id1, fakelep_pt1, fakelep_eta1,
                fakelep_id2, fakelep_pt2, fakelep_eta2,
                h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
                in_3P1F=False,
            )
            d_2p2f_fs_hists[fs].Fill(m4l, 1)
            d_2p2fpred_fs_hists[fs].Fill(m4l, wgt_fr)
            # Inclusive.
            h1_data_2p2f_m4l.Fill(m4l, 1)
            h1_data_2p2fpred_m4l.Fill(m4l, wgt_fr)

            # Evaluate the contribution of 2P2F in the 3P1F CR.
            wgt_2p2f_in_3p1f = calc_wgt_2p2f_cr(
                fakelep_id1, fakelep_pt1, fakelep_eta1,
                fakelep_id2, fakelep_pt2, fakelep_eta2,
                h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
                in_3P1F=True,
            )
            d_2p2fin3p1f_fs_hists[fs].Fill(m4l, wgt_2p2f_in_3p1f)
            h1_data_2p2fin3p1f_m4l.Fill(m4l, wgt_2p2f_in_3p1f)
    # End loop over events.
    print(f"Mass window: {m4l_min} < ZZMass < {m4l_max}")
    return (
        h1_data_2p2f_m4l,
        h1_data_3p1f_m4l,
        h1_data_2p2fpred_m4l,
        h1_data_3p1fpred_m4l,
        h1_data_2p2fin3p1f_m4l,
        d_2p2f_fs_hists,
        d_3p1f_fs_hists,
        d_2p2fpred_fs_hists,
        d_3p1fpred_fs_hists,
        d_2p2fin3p1f_fs_hists,
        )

def fillhists_osmethod_bbfntuple(
    t,
    name,
    infile_fakerates,
    m4l_window=(70, 870),
    start_at=0, break_at=-1,
    print_every=10000,
    use_first_quartet=False
    ):
    """Fill histograms and dicts of hists with OS Method info.

    Args:
        name (str):
            Nickname of sample.
            Options: "Data", "ZZ", "DY", "TT", "WZ".
        infile_path (str):
        infile_fakerates (str): File path to fake rates in TH1.
        start_at (int, optional): Starting event. Defaults to 0.
        break_at (int, optional): Break before processing this event. Defaults to -1.
        print_every (int, optional): Print processing output per this many events. Defaults to 10000.
        use_first_quartet (bool, optional): 
            There can be multiple lepton quartets per event.
            CJLST typically keeps only one quartet per event.
            Set this bool to True to keep only the first quartet per event.
            Default is False.

    Raises:
        ValueError: [description]
    """
    d_data_2p2f_fs_hists, d_data_3p1f_fs_hists, d_data_2p2fpred_fs_hists, d_data_3p1fpred_fs_hists, d_data_2p2fin3p1f_fs_hists = make_dct_hists_all_crs_data(
        h1_data_2p2f_m4l,
        h1_data_3p1f_m4l,
        h1_data_2p2fpred_m4l,
        h1_data_3p1fpred_m4l,
        h1_data_2p2fin3p1f_m4l
        )

    d_zz_2p2f_fs_hists, d_zz_3p1f_fs_hists, d_zz_2p2fpred_fs_hists, d_zz_3p1fpred_fs_hists = make_dct_hists_all_crs(
        h1_zz_2p2f_m4l,
        h1_zz_3p1f_m4l,
        h1_zz_2p2fpred_m4l,
        h1_zz_3p1fpred_m4l,
        )

    if use_first_quartet:
        set_evtid_proc = set()

    n_tot = t.GetEntries()
    for ct in range(n_tot):

        # Loop control.
        t.GetEntry(ct)
        if ct == break_at:
            break
        print_periodic_evtnum(ct, n_tot, print_every=print_every)

        m4l = t.mass4l
        m4l_min = m4l_window[0]
        m4l_max = m4l_window[1]
        if (m4l < m4l_min) or (m4l > m4l_max):
            continue

        evtid = f"{t.Run} : {t.LumiSect} : {t.Event}"
        if use_first_quartet:
            # Skip event if we have already seen this evtID.
            if evtid in set_evtid_proc:
                continue
        # New event so add it to set.
        set_evtid_proc.add(evtid)

        fs = t.finalState
        wgt_fr = t.eventWeightFR

        if t.is3P1F:
            if t.isData:
                d_data_3p1f_fs_hists[fs].Fill(m4l, 1)
                d_data_3p1fpred_fs_hists[fs].Fill(m4l, wgt_fr)
                # Inclusive.
                h1_data_3p1f_m4l.Fill(m4l, 1)
                h1_data_3p1fpred_m4l.Fill(m4l, wgt_fr)
            elif t.isMCzz:
                # n_dataset_tot = float(n_sumgenweights_dataset_dct_jake[name])
                # evt_weight_calcd = get_evt_weight(
                #     dct_xs=dct_xs_jake, Nickname=name, lumi=int_lumi, event=tree,
                #     n_dataset_tot=n_dataset_tot, orig_evt_weight=t.eventWeight
                #     )

                # By final state.
                d_zz_3p1fpred_fs_hists[fs].Fill(m4l, wgt_fr)
                # Inclusive.
                h1_zz_3p1fpred_m4l.Fill(m4l, wgt_fr)

        elif t.is2P2F:
            if t.isData:
                d_data_2p2f_fs_hists[fs].Fill(m4l, 1)
                d_data_2p2fpred_fs_hists[fs].Fill(m4l, wgt_fr)
                # Inclusive.
                h1_data_2p2f_m4l.Fill(m4l, 1)
                h1_data_2p2fpred_m4l.Fill(m4l, wgt_fr)

                # Contribution of 2P2F in the 3P1F CR.
                wgt_2p2f_in_3p1f = (t.fr2 / (1 - t.fr2)) + (t.fr3 / (1 - t.fr3))
                d_data_2p2fin3p1f_fs_hists[fs].Fill(m4l, wgt_2p2f_in_3p1f)
                h1_data_2p2fin3p1f_m4l.Fill(m4l, wgt_2p2f_in_3p1f)
            elif t.isMCzz:
                d_zz_2p2fpred_fs_hists[fs].Fill(m4l, wgt_fr)
                # Inclusive.
                h1_zz_2p2fpred_m4l.Fill(m4l, wgt_fr)
        else:
            raise ValueError(f"Event was neither 3P1F nor 2P2F.")
    # End loop over events.
    print(f"Mass window: {m4l_min} < mass4l < {m4l_max}")
    return (
        h1_data_2p2f_m4l,
        h1_data_3p1f_m4l,
        h1_data_2p2fpred_m4l,
        h1_data_3p1fpred_m4l,
        h1_data_2p2fin3p1f_m4l,
        d_data_2p2f_fs_hists,
        d_data_3p1f_fs_hists,
        d_data_2p2fpred_fs_hists,
        d_data_3p1fpred_fs_hists,
        d_data_2p2fin3p1f_fs_hists,
        h1_zz_2p2fpred_m4l,
        h1_zz_3p1fpred_m4l,
        d_zz_3p1fpred_fs_hists,
        d_zz_2p2fpred_fs_hists,
        )

def make_ls_evtIDs_OSmethod(
    tree, framework,
    m4l_lim=(70, 1000),
    keep_2P2F=0,
    keep_3P1F=0,
    fs=1,
    print_every=5000,
    ):
    """Return a list of 3-tuples of event IDs that pass OS Method selection.

    Args:
        framework (str, optional):
            'jake' uses `is3P1F` and `isData`. Defaults to "jake".
        m4l_lim (2-tuple, optional):
            Select events with mass4l in this range. Defaults to (70, 1000).
        keep_2P2F (bool, optional):
            Select 2P2F-type events. Both this and keep_3P1F can be True.
            Defaults to False.
        keep_3P1F (bool, optional):
            Select 3P1F-type events. Both this and keep_2P2F can be True.
            Defaults to False.
        fs (int, optional):
            Final state to select.
            1=4mu, 2=4e, 3=2e2mu, 4=2mu2e, 5=all.
            Defaults to 5.
        print_every (int, optional):
            How often to print event info.
            Defaults to 500000.
    """
    ls_tup_evtID = []
    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    n_tot = tree.GetEntries()
    for ct, evt in enumerate(tree):
        print_periodic_evtnum(ct, n_tot, print_every=print_every)
        
        m4l = evt.mass4l
        if evt.finalState not in (1, 2, 3, 4):
            continue
        if (m4l < m4l_min) or (m4l > m4l_max):
            continue
        good_fs = True if fs == evt.finalState or fs == 5 else False
        if not good_fs:
            continue

        keep_evt = False
        if framework.lower() == "jake":
            if keep_2P2F and evt.is2P2F:
                keep_evt = True
            elif keep_3P1F and evt.is3P1F:
                keep_evt = True
        elif framework.lower() == "bbf":
            if not evt.passedZXCRSelection:
                continue
            if keep_2P2F and (evt.nZXCRFailedLeptons == 2):
                keep_evt = True
            elif keep_3P1F and (evt.nZXCRFailedLeptons == 1):
                keep_evt = True

        if keep_evt:
            tup_evtID = (evt.Run, evt.LumiSect, evt.Event,)
            ls_tup_evtID.append(tup_evtID)

    return ls_tup_evtID
