import os
import numpy as np
from ROOT import TFile

from Utils_Python.printing import print_periodic_evtnum, print_header_message
from Utils_Python.Utils_Files import check_overwrite
from sidequests.classes.cjlstflag import CjlstFlag
from sidequests.funcs.evt_loops import (
    evt_loop_evtsel_2p2plusf3p1plusf_subevents
    )
from constants.finalstates import dct_finalstates_int2str

def print_evt_info_bbf(evt):
    """A goofy way to print branch info for `evt` in TTree.
    
    TODO:
    - [ ] Print only up to 6 decimals for all floats.
    """
    print_header_message("Analyzer: BBF")
    d_branch = {
        "passedFullSelection" : "",
        "passedZXCRSelection" : "",
        "nZXCRFailedLeptons" : "",
        "lep_Hindex" : "list",
        "lep_RedBkgindex" : "list",
        "lep_id" : "list",
        "lep_pt" : "list",
        "lep_eta" : "list",
        "lep_phi" : "list",
        "lep_mass" : "list",
        "lepFSR_pt" : "list",
        "lepFSR_eta" : "list",
        "lepFSR_phi" : "list",
        "lepFSR_mass" : "list",
        "vtxLepFSR_BS_pt" : "list",
        # "lep_RelIso" : "list",
        "lep_RelIsoNoFSR" : "list",
        "lep_tightId" : "list",
        "is2P2F" : "",
        "is3P1F" : "",
    }
    for branch, express_as in d_branch.items():
        if express_as == "":
            try:
                print(f"evt.{branch}: {getattr(evt, branch)}")
            except AttributeError:
                # Branch doesn't exist.
                pass
        elif express_as == "list":
            try:
                print(f"evt.{branch}: {list(getattr(evt, branch))}")
            except AttributeError:
                # Branch doesn't exist.
                pass
    print()

def find_entries_using_runlumievent(
    tree, run, lumi, event,
    evt_start=0, evt_end=-1, print_every=10000,
    which="all", fw="bbf"
    ):
    """Return list of entries of NTuple that correspond to run, lumi, event.

    Args:
        which (str):
            If "all", will find all entries with run, lumi, event.
            If "first", break after first entry is found.
    """
    ls_entries = []
    for evt_num in range(evt_start, evt_end):
        print_periodic_evtnum(evt_num, evt_end, print_every=print_every)
        tree.GetEntry(evt_num)
        if (fw == "bbf") or (fw == "jake"):
            if tree.Run != run:
                continue
            if tree.LumiSect != lumi:
                continue
            if tree.Event != event:
                continue
        elif fw == "cjlst":
            if tree.RunNumber != run:
                continue
            if tree.LumiNumber != lumi:
                continue
            if tree.EventNumber != event:
                continue
        else:
            raise ValueError(f"`fw` must be 'bbf', 'jake', or 'cjlst'.")
        # Found entry.
        ls_entries.extend([evt_num])
        if which == "first":
            break

    num_entries = len(ls_entries)
    if num_entries == 0:
        print(f"  WARNING: No entry found for {run} : {lumi} : {event}.")
    print(
        f"  Number of entries for event {run}:{lumi}:{event} found:"
        f"  {num_entries}"
        )
    for entry in ls_entries:
        print(f"  Index: {entry}")
    return ls_entries

def find_runlumievent_using_entry(tree, entry, fw="bbf"):
    """Return the 3-tuple of run, lumi, event corresponding to `entry`."""
    tree.GetEntry(entry)
    if (fw == "bbf") or (fw == "jake"):
        tup_evt_id = (tree.Run, tree.LumiSect, tree.Event,)
    elif fw == "cjlst":
        tup_evt_id = (tree.RunNumber, tree.LumiNumber, tree.EventNumber,)
    else:
        raise ValueError(f"`fw` must be 'bbf', 'jake', or 'cjlst'.")
    # print(
    #     f"  Entry {entry} found in framework={fw.upper()}:\n"
    #     f"    Run, Lumi, Event = {tup_evt_id}"
    #     )
    return tup_evt_id

def analyze_single_evt(
    tree, run=None, lumi=None, event=None, entry=None,
    fw="bbf", which="all",
    evt_start=0, evt_end=-1, print_every=10000,
    infile_fakerates=None,
    genwgts_dct=None,
    xs_dct=None,
    allow_ge4tightleps=False,
    explain_skipevent=True,
    verbose=True
    ):
    """Return list of event numbers that correspond to run, lumi, event.

    Event number in this case refers to its entry (row index) in `tree`.
    
    Also prints out event info (`run`:`lumi`:`event`) found in `tree`.
    
    Args:
        entry (int):
            Row in TTree.
        fw (str):
            Which framework to use: "bbf", "cjlst", "jake"
        which (str):
            Which instance of the event you want to select.
            Options: "first", anything else collects all such events.
        evt_start (int):
        allow_ge4tightleps (bool):
            If True, then Jake's Analyzer will look for 3P1F quartets even
            when an event has >=4 tight leptons.
            NOTE:
                Filippo made the good point that we may be killing events too
                quickly if we throw events away with >=4 tight leptons!
                For example, what if we have:
                    mu+     mu-     mu+T    mu-L    e+T
                    (tight) (tight) (tight) (loose) (tight)
                There are 4 tight leptons, but they can't make a signal
                candidate. Therefore the 4 tight selection is made too early.
    """
    know_evtid = all(x is not None for x in (run, lumi, event))
    know_entry = entry is not None
    if (not know_entry) and know_evtid:
        # Specific entry (row in TTree) was not specified.
        # Use Run, Lumi, Event to find all, entries.
        assert all(x is not None for x in (run, lumi, event))
        if evt_end == -1:
            evt_end = tree.GetEntries()
        ls_entries = find_entries_using_runlumievent(
                tree, run, lumi, event,
                evt_start=evt_start,
                evt_end=evt_end,
                print_every=print_every,
                which=which, fw=fw
                )
    elif know_entry and (not know_evtid):
        # We know the entry, but not the Run, Lumi, Event.
        run, lumi, event = find_runlumievent_using_entry(
            tree=tree, entry=entry, fw=fw
            )
        ls_entries = [entry]
    elif know_entry and know_evtid:
        ls_entries = [entry]
    else:
        raise ValueError(f"Must specify either `entry` or `run, lumi, event`")

    for entry in ls_entries:
        print(
            f"Analyzing event #{entry} in {fw.upper()} framework"
            f" (event ID {run}:{lumi}:{event})."
            )

        tree.GetEntry(entry)
        if fw == "bbf":
            print_evt_info_bbf(tree)
        elif fw == "jake":
            print_header_message("ANALYZER: Jake")
            evt_loop_evtsel_2p2plusf3p1plusf_subevents(
                tree,
                infile_fakerates=infile_fakerates,
                genwgts_dct=genwgts_dct,
                xs_dct=xs_dct,
                outfile_root=None, outfile_json=None,
                name="Data", int_lumi=59830,
                start_at_evt=entry, break_at_evt=entry+1,
                fill_hists=False,
                explain_skipevent=explain_skipevent,
                verbose=verbose,
                print_every=1, smartcut_ZapassesZ1sel=False,
                overwrite=False, keep_only_mass4lgt0=False,
                recalc_mass4l_vals=False,
                allow_ge4tightleps=allow_ge4tightleps,
                )
            # store_evt = True
        elif fw == "cjlst":
            print_evt_info_cjlst(tree)

    # End loop over collected ls_entries.
    return ls_entries

def get_control_region(evt):
    """Return str of control region based on `lep_Hindex` and `lep_tightId`.

    FIXME: Logic may be incorrect. Review it.

    Only works for BBF root files.
    """
    l_Hindex_ls = list(evt.lep_Hindex)
    assert -1 not in l_Hindex_ls
    l_tightId_arr = np.array(evt.lep_tightId)[l_Hindex_ls]

    # 3P1F is defined as 3 leptons passing tight and ISO criteria:
    l_RelIsoNoFSR_arr = np.array(evt.lep_RelIsoNoFSR)[l_Hindex_ls]
    # muons_arr = 
    # l_RelIsoNoFSR_arr
    s = l_tightId_arr.sum()

    if s == 4:
        return "SR"
    elif s == 3:
        return "3P1F"
    elif s == 2:
        return "2P2F"
    else:
        return f"[WARNING] Could not assign number of tight leps ({s}) to a CR!"

def write_tree_evtID_to_txt(
    infile,
    outtxt_basename,
    framework="jake",
    m4l_lim=(70, 1000),
    keep_2P2F=True,
    keep_3P1F=True,
    fs=5,
    path_to_tree="passedEvents",
    print_every=500000,
    overwrite=False,
    ):
    """Write evtIDs from TTree 'passedEvents' in TFile `infile` to `outtxt`.

    Info which gets written:
    Run : LumiSect : Event

    NOTE:
        - Select events passed on 2P2F/3P1F control regions, final state, and
        mass4l cuts.
        - If framework == "bbf", also requires passedZXCRSelection == 1.

    Args:
        fs (int): 4-lep final state (branch = finalState).
            1 = 4mu
            2 = 4e
            3 = 2e2mu
            4 = 2mu2e
            5 = all
    """
    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    tfile = TFile.Open(infile)
    tree = tfile.Get(path_to_tree)
    n_tot = tree.GetEntries()

    outtxt_dir = os.path.dirname(outtxt_basename)
    outtxt_basename_noext = os.path.basename(outtxt_basename).split(".")[0]

    if keep_2P2F:
        outtxt_basename_noext += "_2P2F"
    if keep_3P1F:
        outtxt_basename_noext += "_3P1F"
    outtxt_basename_noext += f"_{dct_finalstates_int2str[fs]}"
    outtxt_basename_noext += f"_{m4l_min}masswindow{m4l_max}.txt"

    outtxt_fullname = os.path.join(
        outtxt_dir,
        outtxt_basename_noext
        )
    check_overwrite(outtxt_fullname, overwrite=overwrite)

    with open(outtxt_fullname, "w") as f:
        f.write("# Run : LumiSect : Event\n")
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
                f.write(f"{evt.Run} : {evt.LumiSect} : {evt.Event}\n")
    print(f"TTree info written to:\n{outtxt_fullname}")