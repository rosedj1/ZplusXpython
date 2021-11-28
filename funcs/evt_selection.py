def make_filled_mylep_ls(tree):
    """Return list of MyLepton objs filled with lep info from this event."""
    mylep_ls = []
    for ndx, (lpt, leta, lphi, lmass, lid, ltightId, lRelIsoNoFSR,
              lpt_NoFSR, leta_NoFSR, lphi_NoFSR, lmass_NoFSR) in enumerate(
        zip(tree.lepFSR_pt,
            tree.lepFSR_eta,
            tree.lepFSR_phi,
            tree.lepFSR_mass,
            tree.lep_id,
            tree.lep_tightId,
            tree.lep_RelIsoNoFSR,
            tree.lep_pt,
            tree.lep_eta,
            tree.lep_phi,
            tree.lep_mass,
           )
        ):
        
        mylep = MyLepton(lpt, leta, lphi, lmass, lid, ltightId, lRelIsoNoFSR,
                         lpt_NoFSR, leta_NoFSR, lphi_NoFSR, lmass_NoFSR)
        mylep.ndx_lepvec = ndx
        mylep_ls.extend((mylep,))
    return mylep_ls

def makes_valid_zcand(lep1, lep2):
    """Return True if lep1 and lep2 will form a valid Z candidate.
    
    NOTE:
    - This is NOT necessarily a valid Z1 or Z2 candidate.
    
    To form a valid Z candidate:
    - Leptons DO NOT HAVE TO be tight (loose+tightID+RelIso)!
    - Leptons must be OSSF.
    - 12 < m(ll, including FSR) < 120 GeV.

    Args:
        lep1 (MyLepton): Combines with lep2 to make Z cand.
        lep2 (MyLepton): Combines with lep1 to make Z cand.
    """
#     if (not lep1.is_tight) or (not lep2.is_tight):
#         return False
    # Check OSSF:
    if (lep1.lid + lep2.lid) != 0:
        return False
    if (lep1.lid == 0) or (lep2.lid == 0):
        return False
    # Check invariant mass cut:
    zcand = lep1.get_LorentzVector() + lep2.get_LorentzVector()
    z_mass = zcand.M()
    if (z_mass < 12) or (z_mass > 120):
        return False
    return True

def make_all_zcands(mylep_ls):
    """Return list of valid Z candidates as MyZboson objects.
    
    To form a valid Z candidate:
    - Leptons DO NOT HAVE TO be tight (loose+tightID+RelIso)!
    - Leptons must be OSSF.
    - 12 < m(ll, including FSR) < 120 GeV.
    """
    zcand_ls = []
    # Make a lep-by-lep comparison to find eligible Z candidates.
    for ndx_lep1, mylep1 in enumerate(mylep_ls[:-1]):
        start_ndx_lep2 = ndx_lep1 + 1
        for ndx_lep2, mylep2 in enumerate(mylep_ls[start_ndx_lep2:]):
            if not makes_valid_zcand(mylep1, mylep2):
                continue
            # Found valid Z candidate.
            zcand = MyZboson(mylep1, mylep2)
            zcand_ls.extend((zcand,))
    return zcand_ls

def pass_lepton_kinem_selection(lid, lpt, leta):
    """Return True if muon or electron and passes kinematic selections.

    Note:
        Also checks if lepton is either a muon or electron. 
    Args:
        lid (int): Lepton ID (11 for e-, -13 for mu+)
        lpt (float): Lepton pT (GeV).
        leta (float): Lepton pseudorapidity.

    Returns:
        bool: True if these kinematics pass selections.
    """
    if abs(lid) == 11:
        # Electron selections.
        if lpt < 7:
            return False
        if abs(leta) > 2.5:
            return False
        # Passed.
        return True
    elif abs(lid) == 13:
        # Muon selections.
        if lpt < 5:
            return False
        if abs(leta) > 2.4:
            return False
        # Passed
        return True
    else:
        return False

def check_leps_pass_leadsublead_pTcuts(mylep_ls):
    """Return True if all leptons pass kinematic cuts for ZZ selection.
    
    Selection:
    - All leptons have DeltaR(l_i, l_j) > 0.02.
    - At least 2 leptons have pT > 10 GeV.
    - At least 1 lepton has pT > 20 GeV.
    """
    n_leps_pTgt10 = sum(lep.lpt > 10 for lep in mylep_ls)
    n_leps_pTgt20 = sum(lep.lpt > 20 for lep in mylep_ls)
    if n_leps_pTgt10 < 2:
        return False
    if n_leps_pTgt20 < 1:
        return False
    return True
    
def check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
    """Return True if all leps are DeltaR separated by at least `min_sep`."""
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        start_ndx2 = ndx1 + 1
        for ndx2, mylep2 in enumerate(mylep_ls[start_ndx2:]):
            dR = mylep1.calc_DeltaR(mylep2)
            if dR < min_sep:
                return False
    return True

def leps_pass_lowmass_dilep_res(mylep_ls, min_mass=4):
    """Return True if all di-lep OS pairs pass mass cut.

    m(ll) > 4 GeV for all OS leptons, irrespective of flavor.
        - Don't include FSR photons in this calculation.
    """
    for ndx1, lep1 in enumerate(mylep_ls[:-1]):
        start_ndx2 = ndx1 + 1
        for ndx2, lep2 in enumerate(mylep_ls[start_ndx2:]):
            # Identify OS leptons by taking the product of IDs.
            if (lep1.lid * lep2.lid) < 0:
                # Found OS pair.
                res = lep1.get_LorentzVector(include_FSR=False) + \
                      lep2.get_LorentzVector(include_FSR=False)
                if res.M() < min_mass:
                    return False
    return True
    
def make_all_zz_pairs(zcand_ls):
    """Return a list of all possible ZZPair objects.
    
    Notes:
    - Skip pairing a Z with itself.
    - This accounts for ALL possible ZZ candidates, even swapping Z1 <-> Z2.
    - This function does not impose any selections on ZZ candidates.
    """
    zz_pair_ls = []
    for ndx1, z1 in enumerate(zcand_ls):
        z1.ndx_zcand_ls = ndx1
        for ndx2, z2 in enumerate(zcand_ls):
            if ndx1 == ndx2:
                continue
            z2.ndx_zcand_ls = ndx2
            zz_cand = ZZPair(z1, z2, kin_discrim=None)  # No selections.
            zz_pair_ls.extend((zz_cand,))
    return zz_pair_ls

def make_zz_pairs(zcand_ls):
    """Return a list of ALL possible ZZCandidate objects.
    
    Notes:
    - This function does not impose any selections on ZZ candidates.
    """
    zz_pair_ls = []
    for ndx1, z1 in enumerate(zcand_ls[:-1]):
        start_ndx2 = ndx1 + 1
        for ndx2, z2 in enumerate(zcand_ls[start_ndx2:]):
            zz_cand = ZZCandidate(z1, z2, kin_discrim=None)  # No selections.
            zz_pair_ls.extend((zz_cand,))
    return zz_pair_ls

def get_all_ZZcands_passing_cjlst(zz_pair_ls):
    """Return a (sub)set list of zz_pair_ls of the ZZs passing CJLST cuts.
        
    Selects the ZZPair objects which pass CJLST selections.
    If no ZZ pairs pass selections, then return an empty list.
    Implements CJLST ZZ selection.
    
    zz_pair_ls contains ZZPair objects.
    
    NOTE:
    - Be sure that zz_pair_ls provides ALL combinations ZZ pairings.
        E.g. If you have three Zs, then zz_pair_ls should have 6 ZZPair objs:
        (Z1, Z2), (Z1, Z3),
        (Z2, Z1), (Z2, Z3),
        (Z3, Z1), (Z3, Z2)
    """
    return [zz for zz in zz_pair_ls if zz.passes_cjlst_sel()]

def get_n_loose_myleps(mylep_ls):
    """Return the number (int) of loose MyLeptons."""
    return sum(lep.is_loose for lep in mylep_ls)

def get_n_tight_myleps(mylep_ls):
    """Return the number (int) of tight MyLeptons."""
    return sum(lep.is_tight for lep in mylep_ls)

def has_2p2f_leps(mylep_ls):
    """Return True if exactly 2 leps are tight and 2 are loose."""
    if get_n_tight_myleps(mylep_ls) != 2:
        return False
    if get_n_loose_myleps(mylep_ls) != 2:
        return False
    return True

def has_3p1f_leps(mylep_ls):
    """Return True if exactly 3 leps are tight and 1 is loose."""
    if get_n_tight_myleps(mylep_ls) != 3:
        return False
    if get_n_loose_myleps(mylep_ls) != 1:
        return False
    return True

def myleps_pass_cjlst_osmethod_selection(mylep_ls, verbose=False):
    """Return True if myleps pass all Z1, Z2, and ZZ selection criteria.
    
    NOTE:
    - Checks for a 2P2F or 3P1F configuration.
    - `mylep_ls` should have exactly 4 leptons. 
    """
    # Need 2 tight + 2 loose leps (2P2F) or 3 tight + 1 loose leps (3P1F).
    # This checks that leptons pass basic kinematic criteria (at least loose).
    if verbose: print("Checking for 2P2F or 3P1F leptons.")
    if (not has_2p2f_leps(mylep_ls)) and (not has_3p1f_leps(mylep_ls)):
        if verbose: print("Leptons are not 2P2F or 3P1F.")
        return False
    
    # Build all Z candidates.
    if verbose: print("Making all Z candidates.")
    zcand_ls = make_all_zcands(mylep_ls)
    n_zcands = len(zcand_ls)
    if n_zcands < 2:
        if verbose: print(f"Found fewer than two Z cands (found {n_zcands}).")
        return False
    
    # Build all ZZ candidates.
    if verbose: print("Making all ZZ candidates.")
    zz_pair_ls = make_all_zz_pairs(zcand_ls)  # Does not implement ZZ cuts.
    all_passing_ZZcands_cjlst_ls = get_all_ZZcands_passing_cjlst(zz_pair_ls)
    # For RedBkg, each 4-lep combo should provide ONLY 1 valid ZZ candidate.
    if len(all_passing_ZZcands_cjlst_ls) != 1:
        return False
    # These 4 leptons form a valid ZZ candidate according to CJLST!
    return True