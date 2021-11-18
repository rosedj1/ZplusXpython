"""New reducible background analyzer to bypass nZXCRFailedLeptons.
# ============================================================================
# Author: Jake Rosenzweig
# Created: 2021-11-16
# Updated: 2021-11-17
# ============================================================================

# TODO:
- [ ] Include RelIsoNoFSR vector in for loops.
- [ ] Implement new bools (force_z1_leps_reliso, etc.).
- [ ] Keep thinking about what plots you need to make:
    - Frequency of 2P2F/3P1F per event.
- [ ] Keep thinking about what events you need to save:
    - Events with 2 loose leps from Z1 and >=2 other loose leps (2P2+F).
    - Events with 2 loose leps from Z1, 1 tight lep (in which sense?), and >=1 other loose leps (3P1+F).
    - Events with 2 loose leps from Z1, 2 tight leps (in which sense?) (4P0+F).
"""
from Particles import MyParticle#, MyMuon, MyElectron
from pprint import pprint
from ROOT import TFile, Math
import numpy as np

verbose = 1
start_at_evt = 27
break_at_evt = 28
force_z1_leps_tightID = True
force_z1_leps_reliso = False

# NOTE: All leptons in Filippo's root file already pass SIP3D, dxy, and dz cuts.
# This is typical of root files produced with the HZZ4L Analyzer.
infile = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/fullstats/filippo/rootfiles/Data_2018_03Nov.root"
f_filippo_data2018 = TFile.Open(infile)
tree = f_filippo_data2018.Get("passedEvents")
print(f"Successfully opened:\n{infile}")

# def make_valid_z1_candidate(lep1, lep2):
#     """Return True if lep1 and lep2 form a valid Z1 candidate.
    
#     NOTE:
#     - Leptons must be OSSF.
#     - 12 < m(ll, including FSR) < 120 GeV.

#     Args:
#         lep1 (MyMuon): Combined with lep2 to make Z cand.
#         lep2 (MyMuon): Combined with lep1 to make Z cand.
#     """
#     # Check OSSF:
#     if lep1.charge == (-1 * lep2.charge):
#         # Check m(ll):
#         lorentz_lep1 = lep1.get_LorentzVector(kind="withFSR")
#         lorentz_lep2 = lep2.get_LorentzVector(kind="withFSR")
#         zmass = (lorentz_lep1 + lorentz_lep2).M()
#         if (12 < zmass) and (zmass < 120):
#             return True
#     return False

def pass_lepton_kinem_selection(lid, lpt, leta):
    """Return True if muon or electron and passes kinematic selections.

    Args:
        lid (int): Lepton ID (11 for e-, -13 for mu+)
        lpt (float): Lepton pT (GeV).
        leta (float): Lepton pseudorapidity.

    Returns:
        bool: True if these kinematics pass selections.
    """
    if abs(lid) == 11:
        if lpt < 7:
            return False
        if abs(leta) > 2.5:
            return False
        # Electron passed selections.
        return True
    elif abs(lid) == 13:
        if lpt < 5:
            return False
        if abs(leta) > 2.4:
            return False
        # Muon passed selections.
        return True
    else:
        return False

# def get_all_z1_candidates(lepFSR_pt, lepFSR_eta, lepFSR_phi, lepFSR_mass):

#     return z1_cand_ls

evt_info_tup = (
    # These will be dict keys whose values start at 0 and then increment.
    "n_evts_eq4_leps",
    "n_evts_ne4_leps",
    "n_evts_lt4_leps",
    "n_evts_ge4_passing_leps",
    "n_evts_passedFullSelection",
    "n_evts_passedZXCRSelection",
)
evt_info_d = {s : 0 for s in evt_info_tup}

n_tot = tree.GetEntries()
for evt_num in range(start_at_evt, n_tot):
    if evt_num == break_at_evt:
        break
    tree.GetEntry(evt_num)

    # We are only interested events that are NOT SR, ZXCRSelection, etc.:
    if tree.passedFullSelection:
        evt_info_d["n_evts_passedFullSelection"] += 1
        continue
    if tree.passedZXCRSelection:
        evt_info_d["n_evts_passedZXCRSelection"] += 1
        continue

    # # Ensure at least 4 leptons in event:
    # n_tot_leps = len(tree.lepFSR_pt)
    # if n_tot_leps < 4:
    #     evt_info_d["n_evts_lt4_leps"] += 1
    #     continue

    # Ensure EXACTLY 4 leptons in event:
    n_tot_leps = len(tree.lepFSR_pt)
    if n_tot_leps != 4:
        evt_info_d["n_evts_ne4_leps"] += 1
        continue

    z_cand_lep_ndcs = []
    if verbose:
        print(f"Looking at event {evt_num}:")
    # Loop over pairs of leptons to find all Z candidates.
    # Don't iterate over the final entry since lep2 will get there.
    for ndx1, (lpt1, leta1, lphi1, lmass1, lid1, ltightId1) in enumerate(
        zip(tree.lepFSR_pt[:-1],
            tree.lepFSR_eta[:-1],
            tree.lepFSR_phi[:-1],
            tree.lepFSR_mass[:-1],
            tree.lep_id[:-1],
            tree.lep_tightId[:-1]
            )
        ):

        # Check kinematics and ID (electron/muon) of this lepton:
        if not pass_lepton_kinem_selection(lid1, lpt1, leta1):
            if verbose:
                print(f"Event {evt_num} lep1 failed kinem selections.")
            continue

        # Compare lep1 to the next lepton over:
        start_ndx2 = ndx1 + 1
        for ndx2, (lpt2, leta2, lphi2, lmass2, lid2, ltightId2) in enumerate(
            zip(
                tree.lepFSR_pt[start_ndx2:],
                tree.lepFSR_eta[start_ndx2:],
                tree.lepFSR_phi[start_ndx2:],
                tree.lepFSR_mass[start_ndx2:],
                tree.lep_id[start_ndx2:],
                tree.lep_tightId[start_ndx2:]
                ), start_ndx2
            ):

            if force_z1_leps_tightID:
                if not ltightId1

            # Check kinematics and ID (electron/muon) of this lepton:
            if not pass_lepton_kinem_selection(lid2, lpt2, leta2):
                if verbose:
                    print(f"Event {evt_num} lep2 failed kinem selections.")
                continue

# def pass_lepton_tightID(lid, ltightId):
#     """Return True if lepton passes tightID.

#     Args:
#         lid (int): Lepton ID.
#         ltightId (bool): Tight ID.
#     """
#     if abs(lid) == 11:
#         return ltightId
#     elif abs(lid) == 13:
#         if ltightId < 
#         return True if 
#     else:
#         return False

def pass_lepton_RelIso(lid, ltightId):
    """Return True if lepton passes tightID.

    Args:
        lid (int): Lepton ID.
        ltightId (bool): Tight ID.
    """
    if abs(lid) == 11:
        return ltightId
    elif abs(lid) == 13:
        if ltightId < 
        return True if 
    else:
        return False

            # We have 2 good (loose) leptons which MAY form a Z candidate.
            loose_lep_arr = []
            # Do an OSSF check:
            if (lid1 + lid2) != 0:
                if verbose:
                    print(f"Event {evt_num} failed OSSF check.")
                continue
            
            # Do we want tight Z1 leptons?
            if force_z1_leps_tightID:
                if (not ltightId1) or (not ltightId2):
                    continue
            
            lorvec_lep1 = Math.PtEtaPhiMVector(lpt1, leta1, lphi1, lmass1)
            lorvec_lep2 = Math.PtEtaPhiMVector(lpt2, leta2, lphi2, lmass2)
            z_cand = lorvec_lep1 + lorvec_lep2
            
            if (z_cand.M() < 12) or (z_cand.M() > 120):
                print(f"Event {evt_num} failed m(Z1) window.")
                continue

            # Good Z candidate! Save these lepton indices.
            z_cand_lep_ndcs.append((ndx1, ndx2))

            #  Need to check lepton kinematics (dxy, dz, SIP3D)
            # if make_valid_z1_candidate(lep1, lep2):

    # All Z1 candidates found!

    # my_lep_ls = 
    # z1_cand_ls = get_all_z1_candidates()

    # If the event made it this far, the leptons are good!
    evt_info_d["n_evts_ge4_passing_leps"] += 1

pprint(evt_info_d)