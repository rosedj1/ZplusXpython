from ROOT import TFile
import numpy as np
from funcs.printing import print_periodic_evtnum

from sidequests.classes.cjlstflag import CjlstFlag

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

def print_evt_info_bbf(tree):
    print(f"tree.passedFullSelection: {tree.passedFullSelection}")
    print(f"tree.passedZXCRSelection: {tree.passedZXCRSelection}")
    print(f"tree.nZXCRFailedLeptons: {tree.nZXCRFailedLeptons}")
    print(f"tree.lep_Hindex: {list(tree.lep_Hindex)}")
    print(f"tree.lepFSR_pt: {list(tree.lepFSR_pt)}")
    print(f"tree.lep_RelIso: {list(tree.lep_RelIso)}")
    print(f"tree.lep_id: {list(tree.lep_id)}")
    print(f"tree.lep_tightId: {list(tree.lep_tightId)}")
    print("#--- PRINT MORE Z AND H INFO HERE. ---#")

def print_evt_info_cjlst(tree):
    print(f"tree.LepPt: {list(tree.LepPt)}")
    print(f"tree.LepLepId: {list(tree.LepLepId)}")
    print(f"tree.LepisID (tight lep): {list(np.array(tree.LepisID, dtype=bool))}")
    print(f"tree.LepisID (tight lep): {list(np.array(tree.LepisID, dtype=bool))}")
    print(f"tree.CRflag: {tree.CRflag} -> {CjlstFlag(tree.CRflag).name}")
    print(f"tree.Z1Mass: {tree.Z1Mass}")
    print(f"tree.Z2Mass: {tree.Z2Mass}")
    print(f"tree.ZZMass: {tree.ZZMass}")
    print()

def analyze_single_evt(tree, run, lumi, event, fw="bbf", which="all", evt_start=0, print_every=10000):
    """Print out event info (`run`:`lumi`:`event`) found in `tree`.
    
    Parameters
    ----------
    fw : str
        Which framework to use: "bbf", "cjlst"
    which : str
        Which instance of the event you want to select.
        Options: "first", anything else prints all such events.
    evt_start : int
    """
    print(f"Searching for event ID {run}:{lumi}:{event} in {fw.upper()} framework")

    n_tot = tree.GetEntries()
    for evt_num in range(evt_start, n_tot):
        tree.GetEntry(evt_num)
        if (evt_num % print_every) == 0:
            print(f"Event {evt_num}/{n_tot}")

        if fw in "bbf":
            if tree.Run != run:
                continue
            if tree.LumiSect != lumi:
                continue
            if tree.Event != event:
                continue
            if not tree.passedZXCRSelection:
                print(f"[WARNING] Event has passedZXCRSelection == 0.")
            print(f"Event {run}:{lumi}:{event} found. Index: {evt_num}")
            print_evt_info_bbf(tree)

        elif fw in "cjlst":
            if tree.RunNumber != run:
                continue
            if tree.LumiNumber != lumi:
                continue
            if tree.EventNumber != event:
                continue
            print(f"Event {run}:{lumi}:{event} found. Index: {evt_num}")
            print_evt_info_cjlst(tree)

        if "first" in which:
            break
    print("Done.")

def get_control_region(evt):
    """Return str of control region based on `lep_Hindex` and `lep_tightId`.

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