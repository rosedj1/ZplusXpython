from ROOT import TFile
from enum import IntEnum

infile_matteo_data2018 = "/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200430_LegacyRun2/Data_2018/AllData/ZZ4lAnalysis.root"
f = TFile.Open(infile_matteo_data2018)
t = f.Get("CRZLLTree/candTree")

class CjlstFlag(IntEnum):
    CR3P1F = 8388608
    CR2P2F = 4194304
    CRLLss = 2097152
    
def analyze_single_evt(tree, run, lumi, event, fw="bbf", which="all",
                       evt_start=0, print_every=10000):
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
    
if __name__ == '__main__':
    analyze_single_evt(t, 321305, 1003, 1613586694, fw="cjlst")
    print_evt_info_cjlst(t, 32366)