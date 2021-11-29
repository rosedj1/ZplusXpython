"""New reducible background analyzer to bypass nZXCRFailedLeptons.
# ============================================================================
# Author: Jake Rosenzweig
# Created: 2021-11-16
# Updated: 2021-11-28
# ============================================================================
"""
from ROOT import TFile
from scipy.special import binom

from sidequests.data.filepaths import infile_filippo_data_2018
from sidequests.containers.h2_tightlooselepcounts import (
    h2_nlooseleps_vs_ntightleps_evtsel_cjlst, h1_n2p2f_combos, h1_n3p1f_combos,
    h2_n3p1fcombos_n2p2fcombos
    )
from classes.mylepton import (MyLepton, make_filled_mylep_ls,
    get_n_tight_myleps, get_n_loose_myleps, has_2p2f_leps, has_3p1f_leps,
    has_atleastone_2p2f_comb, has_atleastone_3p1f_comb
    )
from classes.zzpair import myleps_pass_cjlst_osmethod_selection
from funcs.printing import print_skipevent_msg, print_periodic_evtnum
from Utils_Python.Utils_Files import save_to_json

verbose = 0
explain_why_skipevent = False
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 500000

outfile_root = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/rootfiles/h2_cjlstevtsel_ge4leps_2p2f_3p1f.root"
outfile_json = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/json/cjlstevtsel_ge4leps_2p2f_3p1f.json"

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
    """Return a list of all possible 4-tuples of 3tight1loose MyLeptons."""
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
    assert len(triple_ls_tight) == int(binom(n_tight_leps, 3))
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

def evt_loop_evtselcjlst_atleast4leps(tree, outfile_root):
    """Apply CJLST's RedBkg event selection to all events in for loop.
    
    NOTE:
      - Asks for AT LEAST 4 leptons per event.
      - When an event has >4 leptons, then multiple combinations of 2P2F/3P1F
        are possible.
    """
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

        # EVENTUALLY REMOVE THIS AND MAKE SURE RESULTS ARE THE SAME.
        # Don't want signal region events:
        if tree.passedFullSelection:
            if verbose: print_skipevent_msg("SR", evt_num)
            evt_info_d["n_evts_passedFullSelection"] += 1
            continue

        # Check the number of leptons in this event.
        n_tot_leps = len(tree.lepFSR_pt)
        # h1_nleps_perevent.Fill(n_tot_leps, 1)

        # Ensure at least 4 leptons in event:
        if n_tot_leps < 4:
            if verbose: print_skipevent_msg("n_leps < 4", evt_num)
            evt_info_d["n_evts_lt4_leps"] += 1
            continue
            
        # Initialize ALL leptons (there can be more than 4 leptons).
        mylep_ls = make_filled_mylep_ls(tree)
        n_tight_leps = get_n_tight_myleps(mylep_ls)
        n_loose_leps = get_n_loose_myleps(mylep_ls)

        # Preliminary checks.
        if n_tight_leps < 2:
            if explain_why_skipevent:
                msg = f"Number of tight leptons ({n_tight_leps}) < 2"
                print_skipevent_msg(msg, evt_num)
            continue
        if n_loose_leps < 1:
            if explain_why_skipevent:
                msg = f"Number of loose leptons ({n_loose_leps}) < 1"
                print_skipevent_msg(msg, evt_num)
            continue
     
        # Check if any four-lep combos have 2P2F or 3P1F leptons.
        # NOTE: This does not mean they pass selection yet!
        fourlep_combos = []
        fourlep_combos.extend(find_combos_2tight2loose(mylep_ls))
        fourlep_combos.extend(find_combos_3tight1loose(mylep_ls))
        if len(fourlep_combos) == 0:
            if explain_why_skipevent:
                msg = (
                    f"Found 0 four-lep combos of type 2P2F or 3P1F."
                    f"  n_tight_leps={n_tight_leps}, "
                    f"  n_loose_leps={n_loose_leps}"
                )
                print_skipevent_msg(msg, evt_num)
            continue

        # Check which four-lep combos pass ZZ selections.
        n_tot_good_2p2f_combos_this_event = 0
        n_tot_good_3p1f_combos_this_event = 0
        for fourlep_tup in fourlep_combos:
            if not myleps_pass_cjlst_osmethod_selection(fourlep_tup, verbose=verbose):
                if explain_why_skipevent:
                    msg = "Did not pass CJLST OS Method Event Selection"
                    print_skipevent_msg(msg, evt_num)
                continue
            # Good RedBkg event!
            if has_2p2f_leps(fourlep_tup):
                n_tot_good_2p2f_combos_this_event += 1
            elif has_3p1f_leps(fourlep_tup):
                n_tot_good_3p1f_combos_this_event += 1
            else:
                raise ValueError
        # End loop over all possible four-lepton combinations.
        
        has_good_2p2f_entries = n_tot_good_2p2f_combos_this_event > 0
        has_good_3p1f_entries = n_tot_good_3p1f_combos_this_event > 0

        if has_good_2p2f_entries or has_good_3p1f_entries:
            h1_n2p2f_combos.Fill(n_tot_good_2p2f_combos_this_event, 1)
            h1_n3p1f_combos.Fill(n_tot_good_3p1f_combos_this_event, 1)
            h2_n3p1fcombos_n2p2fcombos.Fill(
                n_tot_good_2p2f_combos_this_event,
                n_tot_good_3p1f_combos_this_event,
                1)
        
            key = f"{tree.Run} : {tree.LumiSect} : {tree.Event}"
            evt_info_2p2f_3p1f_d[key] = {
                "num_combos_2p2f" : n_tot_good_2p2f_combos_this_event,
                "num_combos_3p1f" : n_tot_good_3p1f_combos_this_event,
            }

        # new_tree.Fill()

    # End loop over events.
    # new_tree.Write()
    h1_n2p2f_combos.Write()
    h1_n3p1f_combos.Write()
    h2_n3p1fcombos_n2p2fcombos.Write()
    new_file.Close()
    print(f"Root file created:\n{outfile_root}")

    save_to_json(evt_info_2p2f_3p1f_d, outfile_json, overwrite=True,
                 sort_keys=False)
    # h1_n2p2f_combos.Fill(?, 1)

    # Save it to the new tree:
    
    #     newtree.Fill()    
    # Make new TTree with new branches.

if __name__ == '__main__':
    evt_info_tup = (
        # These will be dict keys whose values start at 0 and then increment.
        "n_evts_eq4_leps",
        "n_evts_ne4_leps",
        "n_evts_lt4_leps",
        "n_evts_ge4_leps",
        "n_evts_passedFullSelection",
        "n_evts_passedZXCRSelection",
        "n_evts_lt2tightleps",
        "n_evts_lt2_zcand",
        "n_evts_ne2_zcand",
        "n_evts_fail_zzcand",
        "n_evts_lt4tightpluslooseleps",
        "n_za_hastightleps_whenfailsmartcut",
        "n_za_haslooseleps_whenfailsmartcut"
    )
    evt_info_d = {s : 0 for s in evt_info_tup}

    evt_info_2p2f_3p1f_d = {}

    f_filippo_data2018 = TFile.Open(infile_filippo_data_2018)
    # t_filippo_data2018 = f_filippo_data2018.Get("passedEvents")
    tree = f_filippo_data2018.Get("passedEvents")
    print(f"Successfully opened:\n{infile_filippo_data_2018}")

    evt_loop_evtselcjlst_atleast4leps(tree, outfile_root)
    # FOR DEBUGGING:
    # myprac_lep_ls = [
    #     MyLepton(lpt=25, leta=1, lphi=1, lmass=1, lid=13, ltightId=1, lRelIsoNoFSR=0.01, ndx_lepvec=0),
    #     MyLepton(lpt=25, leta=1, lphi=1, lmass=1, lid=-13, ltightId=1, lRelIsoNoFSR=0, ndx_lepvec=1),
    #     MyLepton(lpt=25, leta=1, lphi=1, lmass=1, lid=11, ltightId=0, lRelIsoNoFSR=0.01, ndx_lepvec=2),
    #     MyLepton(lpt=25, leta=1, lphi=1, lmass=1, lid=-11, ltightId=0, lRelIsoNoFSR=1, ndx_lepvec=3),
    #     MyLepton(lpt=25, leta=1, lphi=1, lmass=1, lid=-11, ltightId=1, lRelIsoNoFSR=1, ndx_lepvec=4),
    # ]
    # fourlep_ls_2p2f = find_combos_2tight2loose(myprac_lep_ls)
    # for tup in fourlep_ls_2p2f:
    #     print(f"NEW TUP with 2 tight and 2 loose leps:")
    #     for lep in tup:
    #         lep.print_info()
    #     print()



        # # Get 2P2F combinations.
        # fourlep_combos_tup_2p2f = find_combos_2tight2loose(mylep_ls)
        # n_combos_2p2f_noZZcand = len(fourlep_combos_tup_2p2f)

        # # Get 3P1F combinations.
        # fourlep_combos_tup_3p1f = find_combos_3tight1loose(mylep_ls)
        # n_combos_3p1f_noZZcand = len(fourlep_combos_tup_3p1f)

        #--- If above code is slow, then below code may speed things up.
        # already_found_2p2f_comb = False
        # if has_atleastone_2p2f_comb(mylep_ls):
        #     fourlep_combo.append(find_combos_2tight2loose(mylep_ls))
        #     already_found_2p2f_comb = True
        # if has_atleastone_3p1f_comb(mylep_ls):
        #     fourlep_combo.append(find_combos_3tight1loose(mylep_ls))
        #     if not already_found_2p2f_comb:
        #         fourlep_combo.append(find_combos_2tight2loose(mylep_ls))
        # if n_combos_2p2f_noZZcand == n_combos_3p1f_noZZcand == 0:
        #     continue

        # if (n_tight_leps == 2) and (n_loose_leps >= 2):
        # #     # ONLY 2P2F is possible.
        #     fourlep_combo = find_combos_2tight2loose(mylep_ls)
        # elif (n_tight_leps >= 3) and (n_loose_leps >= 1):
        #     # FIXME: It is possible to find 2P2F events cooped up in here.
        #     fourlep_combo = find_combos_3tight1loose(mylep_ls)
        # else:
        #     # if explain_why_skipevent:
        #     #     msg = f"Number of tight leptons ({n_tight_leps}) <= 1"
        #     #     print_skipevent_msg(msg, evt_num)
        #     continue
    
        # if n_tight_leps == 3:???
        #     EVENTUALLY ACCOUNT FOR FINDING 2P2F EVENTS HERE!!!
        #     EXAMPLE: l1P l2P l3P l4F l5F l6F
        #     There are quite a few 2P2F combinations possible here!
        #     myleps_combos_3tight1loose = find_combos_3tight1loose(mylep_ls)
        
        # if (n_combos_2p2f_noZZcand > 0) and (n_combos_3p1f_noZZcand == 0):
        #     # Now check to see if these 2P2F combos pass ZZ selections.
        #     n_tot_good_2p2f_combos_this_event = 0
        #     for fourlep_tup in fourlep_combos_tup_2p2f:
        #         if not myleps_pass_cjlst_osmethod_selection(fourlep_tup, verbose=verbose):
        #             continue
        #         # Good RedBkg event!
        #         n_tot_good_2p2f_combos_this_event += 1
        #     h1_n2p2f_combos.Fill(n_tot_good_2p2f_combos_this_event, 1)

        # if (n_combos_3p1f_noZZcand > 0) and (n_combos_2p2f_noZZcand == 0)::
        #     # Now check to see if these 3P1F combos pass ZZ selections.
        #     n_tot_good_3p1f_combos_this_event = 0
        #     for fourlep_tup in fourlep_combos_tup_3p1f:
        #         if not myleps_pass_cjlst_osmethod_selection(fourlep_tup, verbose=verbose):
        #             continue
        #         # Good RedBkg event!
        #         n_tot_good_3p1f_combos_this_event += 1
        #     h1_n3p1f_combos.Fill(n_tot_good_3p1f_combos_this_event, 1)