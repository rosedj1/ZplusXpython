from ROOT import TFile
import numpy as np
from array import array
# Local imports.
from Utils_Python.Utils_Physics import perc_diff, calc_mass4l_from_idcs
from Utils_Python.printing import (
    print_periodic_evtnum,
    print_skipevent_msg, pretty_print_dict
    )
from Utils_Python.Utils_Files import save_to_json, check_overwrite
from classes.zzpair import (
    myleps_pass_cjlst_osmethod_selection,
    get_ZZcands_from_myleps_OSmethod
    )
from classes.mylepton import (
    make_filled_mylep_ls,
    get_n_tight_myleps, get_n_loose_myleps, has_2p2f_leps, has_3p1f_leps
    )
from sidequests.containers.hists_th1 import (
    h1_data_2p2f_m4l,
    h1_data_3p1f_m4l,
    h1_data_n2p2f_combos,
    h1_data_n3p1f_combos,
    h1_zz_2p2f_m4l,
    h1_zz_3p1f_m4l,
    h1_zz_n2p2f_combos,
    h1_zz_n3p1f_combos,
    )
from sidequests.containers.hists_th2 import h2_n3p1fcombos_n2p2fcombos
from scripts.helpers.analyzeZX import (
    get_evt_weight, check_which_Z2_leps_failed,
    retrieve_FR_hists, get_fakerate_and_error,
    calc_fakerate_up, calc_fakerate_down
    )
from constants.analysis_params import (
    xs_dct_jake, n_sumgenweights_dataset_dct_jake
    )
# from scipy.special import binom

def find_combos_2tight2loose(mylep_ls):
    """Return a list of all possible 4-tuples of 2tight2loose MyLeptons.
    
    Example:
        Suppose you have 5 leptons:
            mu-    mu+    e-     e+     e2+
            pass   pass   fail   fail   fail
        There are 2 different 4l combinations that MAY give a 2P2F event:
            2P2Fa = mu-  mu+  e-   e+
            2P2Fb = mu-  mu+  e-   e2+
        So this ONE event has 2 different 2P2F combinations.
        
    Will return (each object is a MyLepton):
    [
        (mu-, mu+, e-, e+),
        (mu-, mu+, e-, e2+),
        ...
    ]
        
    NOTE:
    - The MyLeptons in `mylep_ls` have already been indexed according to
      original order in "lep_kinematic" vectors.
    - Tight and loose leptons are not in any particular order in the tuple.
    """
    fourlep_combos_2tight2loose = []
    pair_ls_tight = find_all_pairs_leps_tight(mylep_ls)
    pair_ls_loose = find_all_pairs_leps_loose(mylep_ls)
    for tpair in pair_ls_tight:
        for lpair in pair_ls_loose:
            fourlep_tup = tuple(tpair + lpair)
            fourlep_combos_2tight2loose.append(fourlep_tup)
    return fourlep_combos_2tight2loose

def find_combos_3tight1loose(mylep_ls):
    """Return a list of all possible 4-tuples of 3tight1loose MyLeptons.
    
    Args:
        mylep_ls (list): Contains MyLepton objects.
    """
    assert len(mylep_ls) >= 4
    myleps_combos_3tight1loose = []
    # Make all possible triplets of tight leptons:
    triple_tight_leps = find_all_triplets_leps_tight(mylep_ls)
    # Join each triplet with each loose lepton:
    for triplet in triple_tight_leps:
        for lep in mylep_ls:
            if not lep.is_loose:
                continue
            fourlep_tup = triplet + tuple([lep])
            myleps_combos_3tight1loose.append(fourlep_tup)
    return myleps_combos_3tight1loose

def find_all_triplets_leps_tight(mylep_ls, debug=False):
    """Return a list of all possible 3-tup of tight MyLeptons."""
    tight_leps = [tlep for tlep in mylep_ls if tlep.is_tight]
    triple_ls_tight = []
    for ndx1, mylep1 in enumerate(tight_leps[:-2]):
        if debug: print(f"For loop 1: ndx1={ndx1}")
        start_i2 = ndx1 + 1
        for ndx2, mylep2 in enumerate(tight_leps[start_i2:-1], start_i2):
            if debug: print(f"For loop 2: ndx2={ndx2}")
            start_i3 = ndx2 + 1
            for ndx3, mylep3 in enumerate(tight_leps[start_i3:], start_i3):
                if debug: print(f"For loop 3: ndx3={ndx3}")
                lep_tup = (mylep1, mylep2, mylep3)
                if debug: print(f"Found good triple: ({ndx1, ndx2, ndx3})")
                triple_ls_tight.append(lep_tup)
    n_tight_leps = len(tight_leps)
    try:
        assert len(triple_ls_tight) == int(binom(n_tight_leps, 3))
    except ModuleNotFoundError:
        pass
    except NameError:
        pass
    return triple_ls_tight

def find_all_pairs_leps_tight(mylep_ls):
    """Return a list of all possible 2-tup of tight MyLeptons."""
    pair_ls_tight = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.is_tight:
            continue
        start_i2 = ndx1 + 1
        for mylep2 in mylep_ls[start_i2:]:
            if not mylep2.is_tight:
                continue
            # Found 2 tight leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_tight.append(lep_tup)
    return pair_ls_tight

def find_all_pairs_leps_loose(mylep_ls):
    """Return a list of all possible 2-tup of tight MyLeptons."""
    pair_ls_loose = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.is_loose:
            continue
        start_i2 = ndx1 + 1
        for mylep2 in mylep_ls[start_i2:]:
            if not mylep2.is_loose:
                continue
            # Found 2 loose leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_loose.append(lep_tup)
    return pair_ls_loose

def make_evt_info_d():
    """Return a dict of counters for info in event loop.
    
    key (str): String of information about event loop.
    val (int): Starts at 0. Gets incremented when necessary in event loop.
    """
    tup = (
        # These will be dict keys whose values start at 0 and then increment.
        # "n_evts_eq4_leps",
        # "n_evts_ne4_leps",
        "n_evts_lt4_leps",
        "n_evts_not2or3tightleps",
        "n_evts_nosubevtspassingsel",
        "n_evts_fail_zzcand",
        # "n_evts_ge4_leps",
        # "n_evts_passedFullSelection",
        # "n_evts_passedZXCRSelection",
        # "n_evts_lt2tightleps",
        # "n_evts_lt1looselep",
        # "n_evts_lt2_zcand",
        # "n_evts_ne2_zcand",
        # "n_evts_lt4tightpluslooseleps",
        # "n_evts_no4lep_combos",
        # "n_combos_4tightleps",
        "n_good_redbkg_evts",
        "n_good_2p2f_evts",
        "n_good_3p1f_evts",
        "n_tot_good_2p2f_combos",
        "n_tot_good_3p1f_combos",
        "n_quartets_skip_mass4l_le0",
        "n_quartets_skip_lep_Hindex_mismatch"
    )
    return {s : 0 for s in tup}

def evt_loop_evtselcjlst_atleast4leps(tree, outfile_root=None, outfile_json=None,
                                      start_at_evt=0, break_at_evt=-1, fill_hists=True,
                                      explain_skipevent=False, verbose=False, print_every=50000,
                                      smartcut_ZapassesZ1sel=False):
    """Apply CJLST's RedBkg event selection to all events in tree.
    
    NOTE:
        - Asks for AT LEAST 4 leptons per event.
        - When an event has >4 leptons, then multiple combinations
        of 2P2F/3P1F are possible.
        - Does NOT select the BEST ZZ candidate per event.
        If there are >1 ZZ candidates that pass ZZ selections,
        then it takes all possible valid 4-lepton combinations
        and analyzes each individually.

    New reducible background analyzer to bypass nZXCRFailedLeptons.
    # ============================================================================
    # Author: Jake Rosenzweig
    # Created: 2021-11-16
    # Updated: 2021-12-02
    # ============================================================================

    Args:
        smartcut_ZapassesZ1sel (bool, optional):
            In the smart cut, the literature essentially says that if a Za
            looks like a more on-shell Z boson than the Z1 AND if the Zb is a
            low mass di-lep resonance, then veto the whole ZZ candidate.
            However, literature doesn't check for Za passing Z1 selections!
            Set this to True if you require Za to pass Z1 selections.
            Default is False.
    """
    evt_info_d = make_evt_info_d()
    evt_info_2p2f_3p1f_d = {}

    if outfile_root is not None:
        new_file = TFile.Open(outfile_root, "recreate")
    # new_tree = 
    n_tot = tree.GetEntries()
    if verbose:
        print(f"Total number of events: {n_tot}")
    print("Looking for AT LEAST 4 leptons per event.")
    for evt_num in range(start_at_evt, n_tot):

        if evt_num == break_at_evt:
            break

        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        tree.GetEntry(evt_num)
        run = tree.Run
        lumi = tree.LumiSect
        event = tree.Event

        # EVENTUALLY REMOVE THIS AND MAKE SURE RESULTS ARE THE SAME.
        # Don't want signal region events:
        # if tree.passedFullSelection:
        #     if verbose: print_skipevent_msg("SR", evt_num, run, lumi, event)
        #     evt_info_d["n_evts_passedFullSelection"] += 1
        #     continue

        # Check the number of leptons in this event.
        n_tot_leps = len(tree.lepFSR_pt)

        # Ensure at least 4 leptons in event:
        if n_tot_leps < 4:
            if verbose: print_skipevent_msg("n_leps < 4", evt_num, run, lumi, event)
            evt_info_d["n_evts_lt4_leps"] += 1
            continue
            
        # Initialize ALL leptons (there can be more than 4 leptons).
        mylep_ls = make_filled_mylep_ls(tree)
        n_tight_leps = get_n_tight_myleps(mylep_ls)
        n_loose_leps = get_n_loose_myleps(mylep_ls)

        # Preliminary checks.
        if n_tight_leps < 2:
            evt_info_d["n_evts_lt2tightleps"] += 1
            if explain_skipevent:
                msg = f"Number of tight leptons ({n_tight_leps}) < 2"
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            continue
        if n_loose_leps < 1:
            evt_info_d["n_evts_lt1looselep"] += 1
            if explain_skipevent:
                msg = f"Number of loose leptons ({n_loose_leps}) < 1"
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            continue
     
        # Check if any four-lep combos have 2P2F or 3P1F leptons.
        # NOTE: This does not mean they pass selection yet!
        fourlep_combos = []
        fourlep_combos.extend(find_combos_2tight2loose(mylep_ls))
        fourlep_combos.extend(find_combos_3tight1loose(mylep_ls))
        if len(fourlep_combos) == 0:
            evt_info_d["n_evts_no4lep_combos"] += 1
            if explain_skipevent:
                msg = (
                    f"Found 0 four-lep combos of type 2P2F or 3P1F."
                    f"  n_tight_leps={n_tight_leps}, "
                    f"  n_loose_leps={n_loose_leps}"
                )
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            continue

        print(f"WHAT THE HELL ARE YOU?")
        print(f"len(fourlep_combos) = {len(fourlep_combos)}")
        _ = [lep.print_info() for lep in fourlep_combos[0]]

        # Check which four-lep combos pass ZZ selections.
        n_tot_good_2p2f_combos_this_event = 0
        n_tot_good_3p1f_combos_this_event = 0
        for fourlep_tup in fourlep_combos:
            if not myleps_pass_cjlst_osmethod_selection(
                    fourlep_tup, verbose=verbose, explain_skipevent=explain_skipevent,
                    smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                    run=run, lumi=lumi, event=event, entry=evt_num):
                continue
            # Make sure it's not a SR event:
            if get_n_tight_myleps(fourlep_tup) == 4:
                evt_info_d["n_combos_4tightleps"] += 1
                if explain_skipevent:
                    print("Skipping 4-lep combo: 4 tight leptons.")
                continue

            # Good RedBkg event!
            if has_2p2f_leps(fourlep_tup):
                n_tot_good_2p2f_combos_this_event += 1
            elif has_3p1f_leps(fourlep_tup):
                n_tot_good_3p1f_combos_this_event += 1
            else:
                raise ValueError("Something is wrong with event selection.")
        # End loop over all possible four-lepton combinations.
        evt_id = f"{run} : {lumi} : {event}"
        if verbose:
            print(
                f"Event passed CJLST OS Method Selections:\n"
                f"{evt_id} (entry {evt_num})"
                )
        
        has_good_2p2f_combos = (n_tot_good_2p2f_combos_this_event > 0)
        has_good_3p1f_combos = (n_tot_good_3p1f_combos_this_event > 0)

        evt_info_d["n_good_redbkg_evts"] += 1
        if has_good_2p2f_combos:
            evt_info_d["n_good_2p2f_evts"] += 1
        if has_good_3p1f_combos:
            evt_info_d["n_good_3p1f_evts"] += 1
        
        if fill_hists:
            if has_good_2p2f_combos or has_good_3p1f_combos:
                h1_n2p2f_combos.Fill(n_tot_good_2p2f_combos_this_event, 1)
                h1_n3p1f_combos.Fill(n_tot_good_3p1f_combos_this_event, 1)
                h2_n3p1fcombos_n2p2fcombos.Fill(
                    n_tot_good_2p2f_combos_this_event,
                    n_tot_good_3p1f_combos_this_event,
                    1)
            
                evt_info_2p2f_3p1f_d[evt_id] = {
                    "num_combos_2p2f" : n_tot_good_2p2f_combos_this_event,
                    "num_combos_3p1f" : n_tot_good_3p1f_combos_this_event,
                }
    print("End loop over events.")

    pretty_print_dict(evt_info_d)
    if outfile_root is not None:
        h1_n2p2f_combos.Write()
        h1_n3p1f_combos.Write()
        h2_n3p1fcombos_n2p2fcombos.Write()
        new_file.Close()
        print(f"Hists stored in root file:\n{outfile_root}")

    if outfile_json is not None:
        save_to_json(evt_info_2p2f_3p1f_d, outfile_json, overwrite=True,
                    sort_keys=False)

def evt_loop_evtsel_2p2plusf3p1plusf_subevents(
    tree,
    infile_FR_wz_removed,
    outfile_root=None, outfile_json=None,
    name="", int_lumi=59830,
    start_at_evt=0, break_at_evt=-1, fill_hists=True,
    explain_skipevent=False, verbose=False, print_every=50000,
    smartcut_ZapassesZ1sel=False, overwrite=False,
    keep_only_mass4lgt0=False
    ):
    """Apply RedBkg "subevent" event selection to all events in tree.

    NOTE:
    A "subevent" is a 4-lepton combination (so a "quartet" of leptons).

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
        then it takes all possible valid 4-lepton combinations ("quartets")
        and analyzes each individually.
    
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
    """
    if fill_hists:
        # Prepare histograms
        d_hists = {
            "Data" : {
                "2p2f" : {
                    "mass4l" : h1_data_2p2f_m4l,
                    "combos" : h1_data_n2p2f_combos,
                },
                "3p1f" : {
                    "mass4l" : h1_data_3p1f_m4l,
                    "combos" : h1_data_n3p1f_combos,
                }
            },
            "ZZ" : {
                "2p2f" : {
                    "mass4l" : h1_zz_2p2f_m4l,
                    "combos" : h1_zz_n2p2f_combos,
                },
                "3p1f" : {
                    "mass4l" : h1_zz_3p1f_m4l,
                    "combos" : h1_zz_n3p1f_combos,
                }
            },
        }
    
    evt_info_d = make_evt_info_d()  # Info for printing.
    evt_info_2p2f_3p1f_d = {}  # Info for json file.

    assert infile_FR_wz_removed is not None
    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end = retrieve_FR_hists(
                                                    infile_FR_wz_removed
                                                    )

    if outfile_json is not None:
        check_overwrite(outfile_json, overwrite=overwrite)
    
    # Make pointers to store new values. 
    ptr_is2P2F = np.array([0], dtype=int)  # Close enough to bool lol.
    ptr_is3P1F = np.array([0], dtype=int)
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
    ptr_mass4l_vtxFSR_BS = array('f', [0.])
    # ptr_eventWeight = array('f', [0.])

    if outfile_root is not None:
        check_overwrite(outfile_root, overwrite=overwrite)
        new_file = TFile.Open(outfile_root, "recreate")
        print("Cloning TTree.")
        new_tree = tree.CloneTree(0)  # Clone 0 events.

        # Modify existing values of branches.
        new_tree.SetBranchAddress("mass4l", ptr_mass4l)
        new_tree.SetBranchAddress("mass4l_vtxFSR_BS", ptr_mass4l_vtxFSR_BS)

        # Make new corresponding branches in the TTree.
        new_tree.Branch("is2P2F", ptr_is2P2F, "is2P2F/I")
        new_tree.Branch("is3P1F", ptr_is3P1F, "is3P1F/I")
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
        # new_tree.Branch("eventWeight", ptr_eventWeight, "eventWeight/F")

    n_tot = tree.GetEntries()
    print(
        f"Total number of events: {n_tot}\n"
        f"Looking for AT LEAST 4 leptons per event."
        )
    
    ####################
    #=== Event Loop ===#
    ####################
    isMCzz = 1 if name in "ZZ" else 0
    for evt_num in range(start_at_evt, n_tot):
        if evt_num == break_at_evt:
            break

        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        tree.GetEntry(evt_num)
        run = tree.Run
        lumi = tree.LumiSect
        event = tree.Event
        evt_id = f"{run} : {lumi} : {event}"

        # Check the number of leptons in this event.
        n_tot_leps = len(tree.lepFSR_pt)
        if verbose: print(f"  Total number of leptons found: {n_tot_leps}")

        # Ensure at least 4 leptons in event:
        if n_tot_leps < 4:
            if verbose: print_skipevent_msg("n_leps < 4", evt_num, run, lumi, event)
            evt_info_d["n_evts_lt4_leps"] += 1
            continue
            
        # Initialize ALL leptons (possibly >=4 leptons).
        mylep_ls = make_filled_mylep_ls(tree)
        n_tight_leps = get_n_tight_myleps(mylep_ls)
        n_loose_leps = get_n_loose_myleps(mylep_ls)

        # Require exactly 2 or 3 leptons passing tight selection.
        if (n_tight_leps < 2) or (n_tight_leps > 3):
            evt_info_d["n_evts_not2or3tightleps"] += 1
            if explain_skipevent:
                msg = (
                    f"Doesn't contain 2 or 3 tight leps "
                    f"(contains {n_tight_leps} tight leps)."
                    )
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            if verbose:
                for lep in mylep_ls:
                    lep.print_info()
            continue
        # Guaranteed to have at least 4-leps per event
        # of which exactly 2 or 3 pass tight selection.
        # The remaining leptons must be loose.

        # Make all lepton quartets (i.e. make all subevents).
        evt_is_2p2plusf = False
        evt_is_3p1plusf = False
        err_msg = (
            f"  Should not get here. Correct the logic!\n"
            f"    n_loose_leps={n_loose_leps}, n_tight_leps={n_tight_leps}\n"
            f"    entry {evt_num}"
            )
        if n_tight_leps == 2:
            if n_loose_leps < 2:
                print(err_msg)
                for lep in mylep_ls:
                    lep.print_info()
                raise RuntimeError
            evt_is_2p2plusf = True
            fourlep_combos = find_combos_2tight2loose(mylep_ls)
        elif n_tight_leps == 3:
            if n_loose_leps < 1:
                print(err_msg)
                for lep in mylep_ls:
                    lep.print_info()
                raise RuntimeError
            evt_is_3p1plusf = True
            fourlep_combos = find_combos_3tight1loose(mylep_ls)
        else:
            raise ValueError(err_msg)
     
        # The event has EITHER 2 tight leps OR 3 tight leps, and loose leps.
        # Now analyze each lepton quartet (subevent).
        n_subevts_2p2f = 0
        n_subevts_3p1f = 0
        for fourlep_tup in fourlep_combos:
            # Check which four-lep combos pass ZZ selections.
            # Get the better ZZ cand from a single lepton quartet.
            ls_zzcand = get_ZZcands_from_myleps_OSmethod(
                    fourlep_tup,
                    verbose=verbose, explain_skipevent=explain_skipevent,
                    smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                    run=run, lumi=lumi, event=event, entry=evt_num
                    )
            if len(ls_zzcand) == 0:
                # No good ZZ candidate found.
                continue
            # Good 2P2F or 3P1F subevent!
            # For now, the function above only picks out a single ZZ cand.
            zzcand = ls_zzcand[0]
            subevt_passes_sel_2p2f = evt_is_2p2plusf
            subevt_passes_sel_3p1f = evt_is_3p1plusf
            # if zzcand.z_sec.mylep1.is_loose and evt_is_3p1plusf:
            #     msg = f"  Found 3P1F quartet where Z2 lep1 is loose: {evt_id}"
            #     raise RuntimeError(msg)

            if subevt_passes_sel_2p2f:
                n_subevts_2p2f += 1
                evt_info_d["n_tot_good_2p2f_combos"] += 1
            elif subevt_passes_sel_3p1f:
                n_subevts_3p1f += 1
                evt_info_d["n_tot_good_3p1f_combos"] += 1
            else:
                raise ValueError("SHOULD NEVER TRIGGER.")
            #--- TODO: Will need to update event weight here using FRs.
            # Since there may be multiple subevents in a single event,
            # then the SAME EVENT will be stored multiple times in the TTree.
            # The difference for each entry (subevent) will be the weight.

            n_dataset_tot = float(n_sumgenweights_dataset_dct_jake[name])
            evt_weight_calcd = get_evt_weight(
                xs_dct=xs_dct_jake, Nickname=name, lumi=int_lumi, event=tree,
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
                assert subevt_passes_sel_3p1f
                assert mylep1_fromz2.is_loose
                fr2, fr2_err = get_fakerate_and_error(
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
                assert subevt_passes_sel_3p1f
                assert mylep2_fromz2.is_loose
                fr2 = 0
                fr2_err = 0
                fr2_down = 0
                fr2_up = 0
                fr3, fr3_err = get_fakerate_and_error(
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
                assert subevt_passes_sel_2p2f
                fr2, fr2_err = get_fakerate_and_error(
                    mylep1_fromz2,
                    h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end,
                    verbose=verbose
                    )
                fr3, fr3_err = get_fakerate_and_error(
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
            if verbose:
                print(
                    f"Subevent is:\n"
                    f"  2P2F={subevt_passes_sel_2p2f}, "
                    f"3P1F={subevt_passes_sel_3p1f}\n"
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
                    # f"eventWeight(from NTuple) = {tree.eventWeight:.6f}\n"
                    f"    tree.eventWeight = {tree.eventWeight:.6f}\n"
                    f"    evt_weight_calcd = {evt_weight_calcd:.6f}\n"
                    f"          new_weight_down = {new_weight_down:.6f}\n"
                    f"               new_weight = {new_weight:.6f}\n"
                    f"            new_weight_up = {new_weight_up:.6f}"
                )
                zzcand.print_info()

            if keep_only_mass4lgt0:
                if tree.mass4l <= 0:
                    evt_info_d["n_quartets_skip_mass4l_le0"] += 1
                    continue

                # TESTING:
                # Make sure mass4l vars in TTree come from same leps
                # as the leps that built the ZZ candidate I selected.
                lep_Hindex_ls = list(tree.lep_Hindex)
                myleps_ls_ptorder = zzcand.z_fir.get_mylep_idcs_pTorder() + \
                                    zzcand.z_sec.get_mylep_idcs_pTorder()
                if lep_Hindex_ls != myleps_ls_ptorder:
                    evt_info_d["n_quartets_skip_lep_Hindex_mismatch"] += 1
                    continue

            # Save this subevent in TTree. Fill branches.
            lep_idcs = [
                mylep1_fromz1.ndx_lepvec,
                mylep2_fromz1.ndx_lepvec,
                mylep1_fromz2.ndx_lepvec,
                mylep2_fromz2.ndx_lepvec,
                ]
            ptr_is2P2F[0] = subevt_passes_sel_2p2f
            ptr_is3P1F[0] = subevt_passes_sel_3p1f
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
            # Getting an IndexError since there is a discrepancy in the length
            # of vectors, like `lep_pt` and `vtxLepFSR_BS_pt`.
            # WARNING!!! UNCOMMENT THIS BLOCK TO PROPERLY SAVE UPDATED DATA!
            # ptr_mass4l[0] = calc_mass4l_from_idcs(
            #     tree, lep_idcs, kind="lepFSR"
            #     )
            # ptr_mass4l_vtxFSR_BS[0] = calc_mass4l_from_idcs(
            #     tree, lep_idcs, kind="vtxLepFSR_BS"
            #     )
            if outfile_root is not None:
                new_tree.Fill()
        # End loop over subevents.

        #=== Some sanity checks. ===#
        # Make sure at least 1 subevent from main event passed selection.
        if (n_subevts_2p2f == 0) and (n_subevts_3p1f == 0):
            evt_info_d["n_evts_nosubevtspassingsel"] += 1
            if explain_skipevent:
                msg = "No subevents pass OS Method selection."
                print_skipevent_msg(msg, evt_num, run, lumi, event)
            continue

        # Recall that we should have either ONLY 3P1F or ONLY 2P2F subevents.
        evt_info_d["n_good_redbkg_evts"] += 1
        if evt_is_2p2plusf:
            evt_type_msg = "2P2+F"
            cr = "2p2f"
            n_combos = n_subevts_2p2f
            evt_info_d["n_good_2p2f_evts"] += 1
            assert n_subevts_3p1f == 0

        if evt_is_3p1plusf:
            evt_type_msg = "3P1+F"
            cr = "3p1f"
            n_combos = n_subevts_3p1f
            evt_info_d["n_good_3p1f_evts"] += 1
            assert n_subevts_2p2f == 0
        #===========================#

        if verbose:
            print(
                f"** Event passed CJLST OS Method Selections: **\n"
                f"     Event type {evt_type_msg}, {evt_id}, (entry {evt_num})"
                )
        
        evt_info_2p2f_3p1f_d[evt_id] = {
            "num_combos_2p2f" : n_subevts_2p2f,
            "num_combos_3p1f" : n_subevts_3p1f,
            }

        if fill_hists:
            d_hists[name][cr]["mass4l"].Fill(tree.mass4l, new_weight)
            d_hists[name][cr]["combos"].Fill(n_combos, 1)
            h2_n3p1fcombos_n2p2fcombos.Fill(n_subevts_2p2f, n_subevts_3p1f, 1)
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
    