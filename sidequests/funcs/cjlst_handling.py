import numpy as np
# Local imports.
from Utils_Python.printing import print_header_message
from sidequests.classes.cjlstflag import CjlstFlag

def is_tight_cjlst_lep(lep_pdgID, lep_is_tightID, lep_iso):
    """Return True if lepton kinematics pass tight selection."""
    if abs(lep_pdgID) == 11:
        if lep_is_tightID:
            return True
    elif abs(lep_pdgID) == 13:
        if lep_is_tightID and (lep_iso < 0.35):
            return True
    return False

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

    raise RuntimeWarning(
        f"Modify this func to include proper handling of tight CJLST lep\n"
        f"Proper way:\n"
        f"  lep_pdgID = t.LepLepId[idx]\n"
        f"  lep_is_tightID = bool(t.LepisID[idx])\n"
        f"  lep_iso = t.LepCombRelIsoPF[idx]\n"
        f"  For electrons, only require: lep_is_tightID=True\n"
        f"  For muons, require: lep_is_tightID=True AND lep_iso < 0.35"
        )
    print(
        f"tree.LepPt: {list(tree.LepPt)}\n"
        # f"tree.fsrPt: {list(tree.fsrPt)}\n"  # pT of FSR photons.
        f"tree.LepEta: {list(tree.LepEta)}\n"
        f"tree.LepLepId: {list(tree.LepLepId)}\n"
        f"tree.LepisLoose: {list(np.array(tree.LepisLoose, dtype=bool))}\n"
        f"tree.LepisID (tight ID): {list(np.array(tree.LepisID, dtype=bool))}\n"
        f"tree.LepCombRelIsoPF: {list(tree.LepCombRelIsoPF)}\n"
        f"tree.CRflag: {tree.CRflag} -> {CjlstFlag(tree.CRflag).name}\n"
        f"tree.Z1Mass: {tree.Z1Mass}\n"
        f"tree.Z2Mass: {tree.Z2Mass}\n"
        f"tree.ZZMass: {tree.ZZMass}\n"
        )

def convert_to_bbf_fs(Z1Flav, Z2Flav):
    """Return the finalState in BBF FW based on CJLST Z flavors.
    
    1 : 4mu
    2 : 4e
    3 : 2e2mu
    4 : 2mu2e
    """
    Z1Flav = -1 * abs(Z1Flav)
    Z2Flav = -1 * abs(Z2Flav)
    if (Z1Flav == -169) and (Z2Flav == -169):
        # 4mu.
        return 1
    elif (Z1Flav == -169) and (Z2Flav == -121):
        # 2mu2e.
        return 4
    elif (Z1Flav == -121) and (Z2Flav == -169):
        # 2e2mu.
        return 3
    elif (Z1Flav == -121) and (Z2Flav == -121):
        # 4e.
        return 2
    else:
        raise ValueError(
            f"Flavors unknown: Z1Flav={Z1Flav}, Z2Flav={Z2Flav}"
            )