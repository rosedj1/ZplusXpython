from ROOT import TFile
import numpy as np

from Utils_Python.printing import print_periodic_evtnum, print_header_message
from sidequests.classes.cjlstflag import CjlstFlag
from sidequests.funcs.evt_loops import (
    evt_loop_evtsel_2p2plusf3p1plusf_subevents
    )

def write_tree_info_to_txt(infile, outtxt,
                           keep_2P2F=True, keep_3P1F=True, keep_all=False,
                           path_to_tree="passedEvents", print_every=500000):
    """Write info from TFile `infile` from TTree 'passedEvents' to `outtxt`.

    Info which gets written:
    Run : LumiSect : Event
    """
    tfile = TFile.Open(infile)
    tree = tfile.Get(path_to_tree)
    n_tot = tree.GetEntries()
    with open(outtxt, "w") as f:
        f.write("# Run : LumiSect : Event\n")
        for ct, evt in enumerate(tree):
            print_periodic_evtnum(ct, n_tot, print_every=print_every)
            keep_evt = False
            if keep_all:
                keep_evt = True
            elif keep_2P2F and evt.getis2P2F:
                keep_evt = True
            elif keep_3P1F and evt.is3P1F:
                keep_evt = True
            if keep_evt:
                f.write(f"{evt.Run} : {evt.LumiSect} : {evt.Event}\n")
    print(f"TTree info written to:\n{outtxt}")

def get_list_of_lines(evt_ls_txt):
    """Return a list of the lines from `evt_ls_txt` with comments removed.
    
    The lines are checked to start with a digit to avoid comments (#).
    Trailing newlines ('\\n') and whitespaces on both ends are stripped.
    """
    ls_lines = []
    with open(evt_ls_txt, "r") as f:
        for line in f.readlines():
            clean_line = line.rstrip('\n').rstrip().lstrip()
            if not clean_line[0].isdigit():
                continue
            ls_lines.extend([clean_line])
    return ls_lines
        # return [line.rstrip('\n').rstrip() for line in f.readlines() if line[0].isdigit()]

def get_list_of_tuples(evt_ls):
    """
    Return a list of 3-tuples from a list of strings `evt_ls`:

    [
        (Run1, LumiSect1, Event1),
        (Run2, LumiSect2, Event2),
        ...
    ]

    NOTE: Elements of tuples are int.
    """
    new_evt_ls = []
    for line in evt_ls:
        # Grab the first three entries: Run, Lumi, Event.
        tup = tuple([int(num) for num in line.split(":")[:3]])
        new_evt_ls.extend([tup])
    return new_evt_ls

def get_runlumievent_ls_tup(txt):
    """Return a list of tuples of (Run, Lumi, Event) from a txt.

    Args:
        txt (str): Path to txt file that contains Run, Lumi Event like:
                   'Run : Lumi : Event'
                   NOTE: Will strip newlines and whitespace from the ends.

    NOTE: Tuple elements are int.
    """
    return get_list_of_tuples(get_list_of_lines(txt))

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
        "lepFSR_pt" : "list",
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

def print_evt_info_cjlst(tree):
    """A goofy way to print branch info for `evt` in TTree.
    
    TODO:
    - [ ] Print only up to 6 decimals for all floats.
    """
    # d_branch = {
    #     "LepPt" : "list",
    #     "LepEta" : "list",
    #     "LepLepId" : "list",
    #     "LepisID" : "array",
    #     "LepCombRelIsoPF" : "list",
    #     "CRflag" : "list",
    #     "Z1Mass" : "list",
    #     "Z2Mass" : "list",
    #     "ZZMass" : "list",
    # }
    # for branch, express_as in d_branch.items():
    #     if express_as == "":
    #         try:
    #             print(f"{branch}: {getattr(evt, branch)}")
    #         except AttributeError:
    #             # Branch doesn't exist.
    #             pass
    #     elif express_as == "list":
    #         try:
    #             print(f"{branch}: {list(getattr(evt, branch))}")
    #         except AttributeError:
    #             # Branch doesn't exist.
    #             pass
    print_header_message("Analyzer: CJLST")

    print(
        f"tree.LepPt: {list(tree.LepPt)}\n"
        f"tree.fsrPt: {list(tree.fsrPt)}\n"
        f"tree.LepEta: {list(tree.LepEta)}\n"
        f"tree.LepLepId: {list(tree.LepLepId)}\n"
        f"tree.LepisLoose: {list(np.array(tree.LepisLoose, dtype=bool))}\n"
        f"tree.LepisID (tight lep): {list(np.array(tree.LepisID, dtype=bool))}\n"
        f"tree.LepCombRelIsoPF: {list(tree.LepCombRelIsoPF)}\n"
        f"tree.CRflag: {tree.CRflag} -> {CjlstFlag(tree.CRflag).name}\n"
        f"tree.Z1Mass: {tree.Z1Mass}\n"
        f"tree.Z2Mass: {tree.Z2Mass}\n"
        f"tree.ZZMass: {tree.ZZMass}\n"
        )

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
    tree, run, lumi, event, entry=None, fw="bbf", which="all",
    evt_start=0, evt_end=-1, print_every=10000,
    infile_FR_wz_removed=None,
    explain_skipevent=True,
    verbose=True
    ):
    """Return list of event numbers that correspond to run, lumi, event.

    Event number in this case refers to its entry (row index) in `tree`.
    
    Also prints out event info (`run`:`lumi`:`event`) found in `tree`.
    
    Args:
        entry (int):
            Row in TTree.
        fw : str
            Which framework to use: "bbf", "cjlst", "jake"
        which : str
            Which instance of the event you want to select.
            Options: "first", anything else collects all such events.
        evt_start : int
    """
    if entry is None:
        # Specific entry (row in TTree) was not specified.
        # Use Run, Lumi, Event to find all, entries.
        ls_entries = find_entries_using_runlumievent(
                tree, run, lumi, event,
                evt_start=evt_start,
                evt_end=evt_end,
                print_every=print_every,
                which=which, fw=fw
                )
    else:
        # We know the entry, but not the Run, Lumi, Event.
        run, lumi, event = find_runlumievent_using_entry(
            tree=tree, entry=entry, fw=fw
            )
        ls_entries = [entry]

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
                infile_FR_wz_removed=infile_FR_wz_removed,
                outfile_root=None, outfile_json=None,
                name="Data", int_lumi=59830,
                start_at_evt=entry, break_at_evt=entry+1,
                fill_hists=False,
                explain_skipevent=explain_skipevent,
                verbose=verbose,
                print_every=1, smartcut_ZapassesZ1sel=False,
                overwrite=False, keep_only_mass4lgt0=False
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