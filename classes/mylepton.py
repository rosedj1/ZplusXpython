from ROOT import Math
from Utils_Python.Utils_Physics import calc_dphi, calc_dR
class MyLepton:
    
    def __init__(self,
                 lpt, leta, lphi, lmass,
                 lid, ltightId, lRelIsoNoFSR,
                 lpt_NoFSR, leta_NoFSR, lphi_NoFSR, lmass_NoFSR,
                 ndx_lepvec=None):
        """When built, this MyLepton will determine if it's tight or loose.
        
        NOTE:
            Here, "tight" and "loose" are EXclusive!
            So in this code, either a lepton is tight OR it's loose.
            Compare this to previous literature which says that if a lepton is
            tight, then it also satisfies loose selections!
            Not the case here.
        """
        self.lpt = lpt
        self.leta = leta
        self.lphi = lphi
        self.lmass = lmass
        self.lid = lid
        self.ltightId = ltightId
        self.lRelIsoNoFSR = lRelIsoNoFSR
        
        self.lpt_NoFSR = lpt_NoFSR
        self.leta_NoFSR = leta_NoFSR
        self.lphi_NoFSR = lphi_NoFSR
        self.lmass_NoFSR = lmass_NoFSR

        self.ndx_lepvec = ndx_lepvec  # Index of lepton in vectors like lep_pt.
        
        self.is_loose = False
        self.is_tight = False
        if self.passes_tightlep_selection():
            self.is_tight = True
            # self.is_loose remains False.
        elif self.passes_looselep_selection():
            self.is_loose = True
        
    def passes_looselep_selection(self):
        """Return True if MyLepton passes loose lepton selection.

        Selections:
        - pT_NoFSR > 7(5) GeV for electrons(muons)
        - abs(eta_NoFSR) < 2.5(2.4) for electrons(muons)
        The selections below are included in a previous skim step:
        - dxy < 0.5 cm
        - dz < 1 cm
        - SIP_3D < 4
        """
        return pass_lepton_kinem_selection(
            self.lid, self.lpt_NoFSR, self.leta_NoFSR
            )

    def passes_tightlep_selection(self):
        """Return True if MyLepton passes tight lepton selection.

        Selections:
        - All loose selections.
        - tightID = True
        - Relative Isolation < 0.35 for muons (electrons are accounted for in BDT)
        """
        if not self.ltightId:
            return False
        if (abs(self.lid) == 13) and (self.lRelIsoNoFSR > 0.35):
            return False
        if not self.passes_looselep_selection():
            return False
        return True
        
    def get_LorentzVector(self, include_FSR=True):
        """Return a Lorentz vector version of this lepton."""
        if include_FSR:
            return Math.PtEtaPhiMVector(
                    self.lpt,
                    self.leta,
                    self.lphi,
                    self.lmass
                    )
        return Math.PtEtaPhiMVector(
            self.lpt_NoFSR,
            self.leta_NoFSR,
            self.lphi_NoFSR,
            self.lmass_NoFSR
            )
    
    def print_info(self, oneline=True):
        """Print info about this MyLepton."""
        info = f"#-- lep at index {self.ndx_lepvec}:\n"
        if self.lpt_NoFSR is not None:
            info += (
                f" pt={self.lpt_NoFSR:.6f},"
                f" eta={self.leta_NoFSR:.6f},"
                f" phi={self.lphi_NoFSR:.6f},"
                f" mass={self.lmass_NoFSR:.6f}\n"
                )
        info += (
            f" pt_FSR={self.lpt:.6f},"
            f" eta_FSR={self.leta:.6f},"
            f" phi_FSR={self.lphi:.6f},"
            f" mass_FSR={self.lmass:.6f}\n"
            f" id={self.lid},  tightId={self.ltightId},"
            f" RelIsoNoFSR={self.lRelIsoNoFSR:.6f}\n"
            f" is_tight={self.is_tight}, is_loose={self.is_loose}\n"
        )
        if oneline:
            info = info.replace('\n', ', ').rstrip(', ')
        print(info)

    def calc_DeltaR(self, mylep2):
        """Return the DeltaR value between this MyLepton and mylep2."""
        deta = self.leta_NoFSR - mylep2.leta_NoFSR
        dphi = calc_dphi(self.lphi_NoFSR, mylep2.lphi_NoFSR)
        return calc_dR(deta, dphi)

def make_filled_mylep_ls(tree):
    """Return list of MyLepton objs filled with lep info from this event."""
    assert len(tree.lepFSR_pt) == \
            len(tree.lepFSR_eta) == \
            len(tree.lepFSR_phi) == \
            len(tree.lepFSR_mass) == \
            len(tree.lep_id) == \
            len(tree.lep_tightId) == \
            len(tree.lep_RelIsoNoFSR) == \
            len(tree.lep_pt) == \
            len(tree.lep_eta) == \
            len(tree.lep_phi) == \
            len(tree.lep_mass)
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

def pass_lepton_kinem_selection(lid, lpt_NoFSR, leta_NoFSR):
    """Return True if muon or electron and passes kinematic selections.

    NOTE:
        - Need to use lepton kinematics BEFORE FSR reconstruction!
        - Also checks if lepton is either a muon or electron. 
    Args:
        lid (int): Lepton ID (11 for e-, -13 for mu+)
        lpt_NoFSR (float): Lepton pT before FSR (GeV).
        leta_NoFSR (float): Lepton pseudorapidity before FSR.

    Returns:
        bool: True if these kinematics pass selections.
    """
    if abs(lid) == 11:
        # Electron selections.
        if lpt_NoFSR < 7:
            return False
        if abs(leta_NoFSR) > 2.5:
            return False
        # Passed.
        return True
    elif abs(lid) == 13:
        # Muon selections.
        if lpt_NoFSR < 5:
            return False
        if abs(leta_NoFSR) > 2.4:
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
    n_leps_pTgt10 = sum(lep.lpt_NoFSR > 10 for lep in mylep_ls)
    n_leps_pTgt20 = sum(lep.lpt_NoFSR > 20 for lep in mylep_ls)
    if n_leps_pTgt10 < 2:
        return False
    if n_leps_pTgt20 < 1:
        return False
    return True
    
def check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
    """Return True if all leps are DeltaR separated by at least `min_sep`."""
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        start_ndx2 = ndx1 + 1
        for mylep2 in mylep_ls[start_ndx2:]:
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

def get_n_myleps_failing(mylep_ls):
    """Return the number (int) of loose MyLeptons."""
    return sum(lep.is_loose for lep in mylep_ls)

def get_n_myleps_passing(mylep_ls):
    """Return the number (int) of tight MyLeptons."""
    return sum(lep.is_tight for lep in mylep_ls)

def has_2p2f_leps(mylep_ls):
    """Return True if exactly 2 leps are tight and 2 are loose."""
    if get_n_myleps_passing(mylep_ls) != 2:
        return False
    if get_n_myleps_failing(mylep_ls) != 2:
        return False
    return True

def has_3p1f_leps(mylep_ls):
    """Return True if exactly 3 leps are tight and 1 is loose."""
    if get_n_myleps_passing(mylep_ls) != 3:
        return False
    if get_n_myleps_failing(mylep_ls) != 1:
        return False
    return True

def has_atleastone_2p2f_comb(mylep_ls):
    """Return True if AT LEAST 2 leps are tight and AT LEAST 2 are loose."""
    if get_n_myleps_passing(mylep_ls) < 2:
        return False
    if get_n_myleps_failing(mylep_ls) < 2:
        return False
    return True

def has_atleastone_3p1f_comb(mylep_ls):
    """Return True if AT LEAST 3 leps are tight and AT LEAST 1 is loose."""
    if get_n_myleps_passing(mylep_ls) < 3:
        return False
    if get_n_myleps_failing(mylep_ls) < 1:
        return False
    return True

def find_quartets_2pass2fail(mylep_ls):
    """Return a list of all possible 4-tuples of 2pass2fail MyLeptons.
    
    Example:
        Suppose you have 5 leptons:
            mu-    mu+    e-     e+     e2+
            pass   pass   fail   fail   fail (tight selection)
        Then this ONE event can yield 2 different 2P2F quartets:
            2P2Fa = mu-  mu+  e-   e+
            2P2Fb = mu-  mu+  e-   e2+
        
    Returns:
        list of 4-tuples:
            Each 4-tuple contains 2 leps passing tight sel and 2 failing.
            Returns an empty list if no 2P2F quartets are found.

    Will return (each object is a MyLepton):
    [
        (mu-, mu+, e-, e+),
        (mu-, mu+, e-, e2+),
        ...
    ]
        
    NOTE:
    - The MyLeptons in `mylep_ls` have already been indexed according to
        original order in "lep_kinematic" vectors.
    - Leptons passing tight selection are in the first 2 elements.
        Failing leptons are in the last 2 elements.
    """
    fourlep_combos_2pass2fail = []
    pair_ls_tight = find_all_pairs_leps_tight(mylep_ls)
    pair_ls_loose = find_all_pairs_leps_loose(mylep_ls)
    for tpair in pair_ls_tight:
        for lpair in pair_ls_loose:
            fourlep_tup = tuple(tpair + lpair)
            # After appending to list: [(2P2F_a), (2P2F_b), ... ].
            fourlep_combos_2pass2fail.append(fourlep_tup)
    return fourlep_combos_2pass2fail

def find_quartets_3pass1fail(mylep_ls):
    """Return a list of all possible 4-tuples of 3pass1fail MyLeptons.
    
    Args:
        mylep_ls (list): Contains MyLepton objects.
    Returns:
        list of 4-tuples:
            Each 4-tuple contains 3 leps passing tight sel and 1 failing.
            Returns an empty list if no 3P1F quartets are found.
    """
    assert len(mylep_ls) >= 4
    myleps_combos_3pass1fail = []
    # Make all possible triplets of tight leptons:
    triple_tight_leps = find_all_triplets_leps_tight(mylep_ls)
    # Join each triplet with each loose lepton:
    for triplet in triple_tight_leps:
        # NOTE: if triple_tight_leps is empty, then for loop is skipped.
        for lep in mylep_ls:
            if not lep.is_loose:
                continue
            fourlep_tup = triplet + tuple([lep])
            myleps_combos_3pass1fail.append(fourlep_tup)
    return myleps_combos_3pass1fail

def find_combos_4tight(mylep_ls):
    """Return a list of all possible 4-tuples of 4tight MyLeptons.
    
    FIXME: Finish function.

    Args:
        mylep_ls (list): Contains MyLepton objects.
    """
    raise RuntimeError("Finish this function!")
    assert len(mylep_ls) >= 4
    myleps_combos_4loose = []
    # Make all possible triplets of tight leptons:
    triple_tight_leps = find_all_triplets_leps_tight(mylep_ls)
    # Join each triplet with each loose lepton:
    for triplet in triple_tight_leps:
        for lep in mylep_ls:
            if not lep.is_loose:
                continue
            fourlep_tup = triplet + tuple([lep])
            myleps_combos_4loose.append(fourlep_tup)
    return myleps_combos_4loose

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
    n_leps_passing = len(tight_leps)
    try:
        assert len(triple_ls_tight) == int(binom(n_leps_passing, 3))
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
