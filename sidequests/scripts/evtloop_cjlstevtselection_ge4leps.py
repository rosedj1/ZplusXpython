"""New reducible background analyzer to bypass nZXCRFailedLeptons.
# ============================================================================
# Author: Jake Rosenzweig
# Created: 2021-11-16
# Updated: 2021-11-28
# ============================================================================
"""
from ROOT import TFile
from sidequests.data.filepaths import infile_filippo_data_2018
from sidequests.containers.h2_tightlooselepcounts import h2_nlooseleps_vs_ntightleps_evtsel_cjlst
from classes.mylepton import MyLepton, make_filled_mylep_ls, get_n_tight_myleps, get_n_loose_myleps
from classes.zzpair import myleps_pass_cjlst_osmethod_selection
from funcs.printing import print_skipevent_msg, print_periodic_evtnum

verbose = 0
explain_why_skipevent = False
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 500000

outfile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/rootfiles/h2_cjlstevtsel_ge4leps_3p1f.root"

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
    
    NOTE:
      - Assumes that there are EXACTLY 3 tight leptons in the event
        (no restriction on the number of loose leptons).
    """
    myleps_combos_3tight1loose = []
    # Identify the 3 tight leptons:
    tight_myleps = [lep for lep in mylep_ls if lep.is_tight]
    # Pair these 3 up with all each of the loose leptons:
    for lep in mylep_ls:
        if not lep.is_loose:
            continue
        fourlep_tup = tuple(tight_myleps + [lep])
        myleps_combos_3tight1loose.append(fourlep_tup)
    return myleps_combos_3tight1loose

def find_all_pairs_leps_tight(mylep_ls):
    """Return a list of 2-tup of all pairs of tight MyLeptons."""
    pair_ls_tight = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.is_tight:
            continue
        start_ndx2 = ndx1 + 1
        for ndx2, mylep2 in enumerate(mylep_ls[start_ndx2:]):
            if not mylep2.is_tight:
                continue
            # Found 2 tight leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_tight.append(lep_tup)
    return pair_ls_tight

def find_all_pairs_leps_loose(mylep_ls):
    """Return a list of 2-tup of all pairs of tight MyLeptons."""
    pair_ls_loose = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.is_loose:
            continue
        start_ndx2 = ndx1 + 1
        for ndx2, mylep2 in enumerate(mylep_ls[start_ndx2:]):
            if not mylep2.is_loose:
                continue
            # Found 2 loose leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_loose.append(lep_tup)
    return pair_ls_loose

def evt_loop_evtselcjlst_atleast4leps(tree, outfile):
    """Apply CJLST's RedBkg event selection to all events in for loop.
    
    NOTE:
      - Asks for AT LEAST 4 leptons per event.
      - When an event has >4 leptons, then multiple combinations of 2P2F/3P1F
        are possible.
    """
    new_file = TFile.Open(outfile, "recreate")
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
        # myleps_combos_3tight1loose = find_combos_3tight1loose(mylep_ls)

        n_tight_leps = get_n_tight_myleps(mylep_ls)
        n_loose_leps = get_n_loose_myleps(mylep_ls)
        if n_tight_leps <= 1:
            if explain_why_skipevent:
                msg = f"Number of tight leptons ({n_tight_leps}) <= 1"
                print_skipevent_msg(msg, evt_num)
            continue
     
        # if (n_tight_leps == 2) and (n_loose_leps >= 2):
        #     # ONLY 2P2F is possible.
        #     fourlep_combo = find_combos_2tight2loose(mylep_ls)
        if (n_tight_leps == 3) and (n_loose_leps >= 1):
            # FIXME: It is possible to find 2P2F events cooped up in here.
            fourlep_combo = find_combos_3tight1loose(mylep_ls)
        else:
            # if explain_why_skipevent:
            #     msg = f"Number of tight leptons ({n_tight_leps}) <= 1"
            #     print_skipevent_msg(msg, evt_num)
            continue
    
        # if n_tight_leps == 3:???
        #     EVENTUALLY ACCOUNT FOR FINDING 2P2F EVENTS HERE!!!
        #     EXAMPLE: l1P l2P l3P l4F l5F l6F
        #     There are quite a few 2P2F combinations possible here!
        #     myleps_combos_3tight1loose = find_combos_3tight1loose(mylep_ls)
            
        for fourlep_tup in fourlep_combo:
            if not myleps_pass_cjlst_osmethod_selection(fourlep_tup, verbose=verbose):
                continue
            # NOW we have a good RedBkg event!
            # if verbose: print(f"FOUND GOOD EVENT {evt_num}!")
            h2_nlooseleps_vs_ntightleps_evtsel_cjlst.Fill(n_tight_leps, n_loose_leps, 1)
            # new_tree.Fill()

    # End loop over events.
    # new_tree.Write()
    h2_nlooseleps_vs_ntightleps_evtsel_cjlst.Write()
    new_file.Close()
    print(f"Root file created:\n{outfile}")
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

    f_filippo_data2018 = TFile.Open(infile_filippo_data_2018)
    # t_filippo_data2018 = f_filippo_data2018.Get("passedEvents")
    tree = f_filippo_data2018.Get("passedEvents")
    print(f"Successfully opened:\n{infile_filippo_data_2018}")

    evt_loop_evtselcjlst_atleast4leps(tree, outfile)
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