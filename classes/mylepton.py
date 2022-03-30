from ROOT import Math
from itertools import combinations
from Utils_Python.Utils_Physics import calc_dphi, calc_dR
class MyLepton:
    
    def __init__(self,
                 lpt, leta, lphi, lmass,
                 lptFSR, letaFSR, lphiFSR, lmassFSR,
                 lid, ltightId, lRelIsoNoFSR,
                 ndx_lepvec=None):
        """Initialize a lepton."""
        # Kinematics (no FSR).
        self.lpt = lpt
        self.leta = leta
        self.lphi = lphi
        self.lmass = lmass
        # Kinematics (with FSR).
        self.lptFSR = lptFSR
        self.letaFSR = letaFSR
        self.lphiFSR = lphiFSR
        self.lmassFSR = lmassFSR
        # Other important variables.
        self.lid = lid
        self.ltightId = ltightId
        self.lRelIsoNoFSR = lRelIsoNoFSR
        # Index of lepton in vectors like lep_pt.
        self.ndx_lepvec = ndx_lepvec
        
    def pass_loose_sel(self):
        """Return True if MyLepton passes loose lepton selection.

        NOTE:
            This is not the same as failing tight selection!

        Selections:
        - pT_NoFSR > 7(5) GeV for electrons(muons)
        - abs(eta_NoFSR) < 2.5(2.4) for electrons(muons)
        The selections below are included in a previous skim step:
        - dxy < 0.5 cm
        - dz < 1 cm
        - SIP_3D < 4
        """
        return pass_lepton_kinem_selection(
            self.lid, self.lpt, self.leta
            )

    def pass_tight_sel(self):
        """Return True if MyLepton passes tight lepton selection.

        NOTE:
            A lepton can pass BOTH loose and tight selections.

        Selections:
        - All loose selections.
        - tightID = True
        - Relative Isolation < 0.35 for muons (electrons are accounted for in BDT)
        """
        if not self.ltightId:
            return False
        if (abs(self.lid) == 13) and (self.lRelIsoNoFSR > 0.35):
            return False
        if not self.pass_loose_sel():
            return False
        return True

    def fail_tight_sel(self):
        """Return True if this MyLepton fails tight selection.
        
        NOTE:
            Lepton could still pass loose selections!
        """
        return not self.pass_tight_sel()

    def get_LorentzVector(self, include_FSR=True):
        """Return a Lorentz vector version of this lepton."""
        if include_FSR:
            return Math.PtEtaPhiMVector(
                self.lptFSR,
                self.letaFSR,
                self.lphiFSR,
                self.lmassFSR
                )
        return Math.PtEtaPhiMVector(
            self.lpt,
            self.leta,
            self.lphi,
            self.lmass
            )
    
    def print_info(self, oneline=True):
        """Print info about this MyLepton."""
        info = f"#-- lep at index {self.ndx_lepvec}:\n"
        if self.lpt is not None:
            info += (
                f" pt={self.lpt:.6f},"
                f" eta={self.leta:.6f},"
                f" phi={self.lphi:.6f},"
                f" mass={self.lmass:.6f}\n"
                )
        info += (
            f" pt_FSR={self.lptFSR:.6f},"
            f" eta_FSR={self.letaFSR:.6f},"
            f" phi_FSR={self.lphiFSR:.6f},"
            f" mass_FSR={self.lmassFSR:.6f}\n"
            f" id={self.lid},  tightId={self.ltightId},"
            f" RelIsoNoFSR={self.lRelIsoNoFSR:.6f}\n"
            f" pass_tight_sel={self.pass_tight_sel()}\n"
        )
        if oneline:
            info = info.replace('\n', ', ').rstrip(', ')
        print(info)

    def calc_DeltaR(self, mylep2):
        """Return the DeltaR value between this MyLepton and mylep2."""
        deta = self.leta - mylep2.leta
        dphi = calc_dphi(self.lphi, mylep2.lphi)
        return calc_dR(deta, dphi)

    def get_flavor(self):
        """Return lepton flavor as str: 'e', 'mu'"""
        abs_id = abs(self.lid)
        if abs_id == 11:
            return 'e'
        elif abs_id == 13:
            return 'mu'
        elif abs_id == 15:
            return 'tau'
        else:
            raise ValueError(f'Unknown flavor (abs(ID) = {abs_id})')
        
    def get_charge(self):
        """Return charge (int) of lepton."""
        assert self.get_flavor() in ('e', 'mu')
        return (-1 * self.lid / abs(self.lid))
        
    def same_charge_as(self, other):
        """Return True if this MyLepton has same charge as `other`."""
        return (self.get_charge() == other.get_charge())

    def same_flavor_as(self, other):
        """Return True if this MyLepton has same flavor as `other`."""
        return (self.get_flavor() == other.get_flavor())

    def compare_chargeflavor(self, other):
        """Return str comparing charge and flavor of MyLepton to `other`.

        Returns one of:
            * 'SSSF' (leptons are same sign, same flavor)
            * 'SSDF' (leptons are same sign, diff flavor)
            * 'OSSF' (leptons are opposite sign, same flavor)
            * 'OSDF' (leptons are opposite sign, diff flavor)
        """
        q = 'SS' if self.same_charge_as(other) else 'OS'
        f = 'SF' if self.same_flavor_as(other) else 'DF'
        return q + f

def make_filled_mylep_ls(tree):
    """Return list of MyLepton objs filled with lep info from this event."""
    assert len(tree.lep_pt) == \
            len(tree.lep_eta) == \
            len(tree.lep_phi) == \
            len(tree.lep_mass) == \
            len(tree.lepFSR_pt) == \
            len(tree.lepFSR_eta) == \
            len(tree.lepFSR_phi) == \
            len(tree.lepFSR_mass) == \
            len(tree.lep_id) == \
            len(tree.lep_tightId) == \
            len(tree.lep_RelIsoNoFSR)
    mylep_ls = []
    for ndx, (
        lpt, leta, lphi, lmass,
        lptFSR, letaFSR, lphiFSR, lmassFSR,
        lid, ltightId, lRelIsoNoFSR,
        ) in enumerate(
                zip(
                    tree.lep_pt,
                    tree.lep_eta,
                    tree.lep_phi,
                    tree.lep_mass,
                    tree.lepFSR_pt,
                    tree.lepFSR_eta,
                    tree.lepFSR_phi,
                    tree.lepFSR_mass,
                    tree.lep_id,
                    tree.lep_tightId,
                    tree.lep_RelIsoNoFSR,
                    )
            ):
        
        mylep = MyLepton(
                    lpt, leta, lphi, lmass,
                    lptFSR, letaFSR, lphiFSR, lmassFSR,
                    lid, ltightId, lRelIsoNoFSR,
                    )
        # Record the index of the lepton as it appears in the kinem vector.
        mylep.ndx_lepvec = ndx
        mylep_ls.extend(
            (mylep,)  # extend is be faster than append.
            )
    return mylep_ls

def pass_lepton_kinem_selection(
    lid, lpt, leta,
    absid_elec=11, min_pt_elec=7, max_abseta_elec=2.5,
    absid_muon=13, min_pt_muon=5, max_abseta_muon=2.4,
    ):
    """Return True if lepton kinematics pass selections.

    NOTE:
        - Need to use lepton kinematics WITHOUT FSR reconstruction!
        - Also checks if lepton is either a muon or electron. 
    Args:
        lid (int): Lepton ID (11 for e-, -13 for mu+)
        lpt (float): Lepton pT without FSR (GeV).
        leta (float): Lepton pseudorapidity without FSR.

    Returns:
        bool: True if these kinematics pass selections.
    """
    if abs(lid) == absid_elec:
        # Electron selections.
        if lpt < min_pt_elec:
            return False
        if abs(leta) > max_abseta_elec:
            return False
        # Passed.
        return True
    elif abs(lid) == absid_muon:
        # Muon selections.
        if lpt < min_pt_muon:
            return False
        if abs(leta) > max_abseta_muon:
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

def get_n_myleps_failtightsel(mylep_ls):
    """Return the number (int) of MyLeptons failing tight selection."""
    return sum(lep.fail_tight_sel() for lep in mylep_ls)

def get_n_myleps_passtightsel(mylep_ls):
    """Return the number (int) of MyLeptons passing tight selection."""
    return sum(lep.pass_tight_sel() for lep in mylep_ls)

def has_2p2f_leps(mylep_ls):
    """Return True if exactly 2 leps pass tight selection and 2 fail."""
    if get_n_myleps_passtightsel(mylep_ls) != 2:
        return False
    if get_n_myleps_failtightsel(mylep_ls) != 2:
        return False
    return True

def has_3p1f_leps(mylep_ls):
    """Return True if exactly 3 leps pass tight selection and 1 fails."""
    if get_n_myleps_passtightsel(mylep_ls) != 3:
        return False
    if get_n_myleps_failtightsel(mylep_ls) != 1:
        return False
    return True

def make_all_quartets_3p1f(mylep_ls):
    """Return a list of all 4-tuple combinations of 3P1F MyLeptons.
    
    NOTE:
        - Does not consider any Z or ZZ selections.
        - Not permutations!

    Args:
        mylep_ls (list): Contains MyLepton objects.
    Returns:
        list of 4-tuples:
            Each 4-tuple contains 3 leps passing tight sel and 1 failing.
            Returns an empty list if no 3P1F quartets are found.
    """
    if len(mylep_ls) < 4:
        return []
    combos = list(combinations(mylep_ls, r=4))
    return [tup for tup in combos if has_3p1f_leps(tup)]

def make_all_quartets_2p2f(mylep_ls):
    """Return a list of all 4-tuple combinations of 2P2F MyLeptons.
    
    NOTE:
        - Does not consider any Z or ZZ selections.
        - Not permutations!

    Args:
        mylep_ls (list): Contains MyLepton objects.
    Returns:
        list of 4-tuples:
            Each 4-tuple contains 2 leps passing tight sel and 2 failing.
            Returns an empty list if no 2P2F quartets are found.
    """
    if len(mylep_ls) < 4:
        return []
    combos = list(combinations(mylep_ls, r=4))
    return [tup for tup in combos if has_2p2f_leps(tup)]

def find_all_leptriplets_passtightsel(mylep_ls, debug=False):
    """Return a list of all possible 3-tup of tight MyLeptons."""
    tight_leps = [tlep for tlep in mylep_ls if tlep.pass_tight_sel()]
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

def find_all_leppairs_passtightsel(mylep_ls):
    """Return a list of all possible 2-tup of MyLeptons passing tight sel."""
    pair_ls_passing = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.pass_tight_sel():
            continue
        start_i2 = ndx1 + 1
        for mylep2 in mylep_ls[start_i2:]:
            if not mylep2.pass_tight_sel():
                continue
            # Found 2 tight leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_passing.append(lep_tup)
    return pair_ls_passing

def find_all_leppairs_failtightsel(mylep_ls):
    """Return a list of all possible 2-tup of MyLeptons failing tight sel."""
    pair_ls_failing = []
    for ndx1, mylep1 in enumerate(mylep_ls[:-1]):
        if not mylep1.fail_tight_sel():
            continue
        start_i2 = ndx1 + 1
        for mylep2 in mylep_ls[start_i2:]:
            if not mylep2.fail_tight_sel():
                continue
            # Found 2 failing leptons.
            lep_tup = (mylep1, mylep2)
            pair_ls_failing.append(lep_tup)
    return pair_ls_failing

# def has_atleastone_2p2f_comb(mylep_ls):
#     """Return True if AT LEAST 2 leps are tight and AT LEAST 2 are loose."""
#     if get_n_myleps_passtightsel(mylep_ls) < 2:
#         return False
#     if get_n_myleps_failtightsel(mylep_ls) < 2:
#         return False
#     return True

# def has_atleastone_3p1f_comb(mylep_ls):
#     """Return True if AT LEAST 3 leps are tight and AT LEAST 1 is loose."""
#     if get_n_myleps_passtightsel(mylep_ls) < 3:
#         return False
#     if get_n_myleps_failtightsel(mylep_ls) < 1:
#         return False
#     return True

# def find_quartets_2pass2fail(mylep_ls):
#     """Return a list of all possible 4-tuples of 2pass2fail MyLeptons.
    
#     Example:
#         Suppose you have 5 leptons:
#             mu-    mu+    e-     e+     e2+
#             pass   pass   fail   fail   fail (tight selection)
#         Then this ONE event can yield 2 different 2P2F quartets:
#             2P2Fa = mu-  mu+  e-   e+
#             2P2Fb = mu-  mu+  e-   e2+
        
#     Returns:
#         list of 4-tuples:
#             Each 4-tuple contains 2 leps passing tight sel and 2 failing.
#             Returns an empty list if no 2P2F quartets are found.

#     Will return (each object is a MyLepton):
#     [
#         (mu-, mu+, e-, e+),
#         (mu-, mu+, e-, e2+),
#         ...
#     ]
        
#     NOTE:
#     - The MyLeptons in `mylep_ls` have already been indexed according to
#         original order in "lep_kinematic" vectors.
#     - Leptons passing tight selection are in the first 2 elements.
#         Failing leptons are in the last 2 elements.
#     """
#     raise RuntimeError(
#         f"Function has been superceded by make_all_quartets_2p2f."
#         )
#     fourlep_combos_2pass2fail = []
#     pair_ls_tight = find_all_leppairs_passtightsel(mylep_ls)
#     pair_ls_loose = find_all_leppairs_failtightsel(mylep_ls)
#     for tpair in pair_ls_tight:
#         for lpair in pair_ls_loose:
#             fourlep_tup = tuple(tpair + lpair)
#             # After appending to list: [(2P2F_a), (2P2F_b), ... ].
#             fourlep_combos_2pass2fail.append(fourlep_tup)
#     return fourlep_combos_2pass2fail

# def find_quartets_3pass1fail(mylep_ls):
#     """Return a list of all possible 4-tuples of 3pass1fail MyLeptons.
    
#     Args:
#         mylep_ls (list): Contains MyLepton objects.
#     Returns:
#         list of 4-tuples:
#             Each 4-tuple contains 3 leps passing tight sel and 1 failing.
#             Returns an empty list if no 3P1F quartets are found.
#     """
#     raise RuntimeError(
#         f"Function has been superceded by make_all_quartets_3p1f."
#         )
#     myleps_combos_3pass1fail = []
#     if len(mylep_ls) < 4:
#         return myleps_combos_3pass1fail
#     # Make all possible triplets of tight leptons:
#     triple_tight_leps = find_all_leptriplets_passtightsel(mylep_ls)
#     # Join each triplet with each loose lepton:
#     for triplet in triple_tight_leps:
#         # NOTE: if triple_tight_leps is empty, then for loop is skipped.
#         for lep in mylep_ls:
#             if not lep.is_loose:
#                 continue
#             fourlep_tup = triplet + tuple([lep])
#             myleps_combos_3pass1fail.append(fourlep_tup)
#     return myleps_combos_3pass1fail

# def find_combos_4tight(mylep_ls):
#     """Return a list of all possible 4-tuples of 4tight MyLeptons.
    
#     FIXME: Finish function.

#     Args:
#         mylep_ls (list): Contains MyLepton objects.
#     """
#     raise RuntimeError("Finish this function!")
#     assert len(mylep_ls) >= 4
#     myleps_combos_4loose = []
#     # Make all possible triplets of tight leptons:
#     triple_tight_leps = find_all_leptriplets_passtightsel(mylep_ls)
#     # Join each triplet with each loose lepton:
#     for triplet in triple_tight_leps:
#         for lep in mylep_ls:
#             if not lep.is_loose:
#                 continue
#             fourlep_tup = triplet + tuple([lep])
#             myleps_combos_4loose.append(fourlep_tup)
#     return myleps_combos_4loose