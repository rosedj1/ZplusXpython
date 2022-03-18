from itertools import combinations
from constants.particleprops import ZMASS_PDG
from Utils_Python.printing import announce

class MyZboson:
    
    def __init__(
        self, mylep1, mylep2,
        zleps_in_pT_order=True,
        explain_skipevent=False
        ):
        self.mylep1 = mylep1
        self.mylep2 = mylep2
        self.made_from_tight_leps = mylep1.is_tight * mylep2.is_tight
        self.ndx_zcand_ls = None  # Index of this Z in list of Z candidates.
        self.explain_skipevent = explain_skipevent

        lep2pt_gt_lep1pt = (mylep2.lpt_NoFSR > mylep1.lpt_NoFSR)
        if zleps_in_pT_order and lep2pt_gt_lep1pt:
            self.mylep1 = mylep2
            self.mylep2 = mylep1
        
    def get_LorentzVector(self):
        """Return a Lorentz vector version of this Z boson."""
        return self.mylep1.get_LorentzVector(include_FSR=True) + \
                self.mylep2.get_LorentzVector(include_FSR=True)
        
    def passes_z1_kinematic_selec(self, allow_z1_failing_leps=True):
        """Return True if this Z boson COULD pass as a Z1 candidate.
        
        Doesn't mean that it has been SELECTED AS the Z1 candidate!
        """
        mass = self.get_mass()
        if (mass < 40):
            if self.explain_skipevent:
                print(
                    f"  Z (from leps {self.get_mylep_indices()}) "
                    f"failed Z1 cut: mass ({mass:.6f}) < 40 GeV."
                    )
            return False
        if (not allow_z1_failing_leps) and (not self.made_from_tight_leps):
            if self.explain_skipevent:
                print(
                    f"  Z (from leps {self.get_mylep_indices()}) "
                    f"failed Z1 cut: not built from leps passing tight sel."
                    )
            return False
        return True
    
    def get_mass(self):
        """Return the mass of this Z boson from its LorentzVector.
        
        NOTE: By default uses lep_FSR kinematics.
        """
        return self.get_LorentzVector().M()

    def print_info(self, name=None):
        """Print info about this Z boson.
        
        Args:
            name (str): Name for this Z: "Z1", "Za".
        """
        header_footer = '#' * 67
        name = "" if name is None else f": name={name}"
        zvec = self.get_LorentzVector()
        n_pass = self.get_num_passing_leps()
        n_fail = self.get_num_failing_leps()
        lep_info = f"Made from: {n_pass} passing lepton, {n_fail} failing lepton."
        if n_pass > 1:
            lep_info = lep_info.replace("lepton,", "leptons,")
        if n_fail > 1:
            lep_info = lep_info.replace("lepton.", "leptons.")
        print(
            f"{header_footer}\n"
            f"# Z CANDIDATE INFO{name}\n"
            f"Z_pt={zvec.Pt():.6f}, Z_eta={zvec.Eta():.6f}, "
            f"Z_phi={zvec.Phi():.6f}, Z_mass={zvec.M():.6f}\n"
            f"Z made from pT-ordered leptons at indices: "
            f"{self.get_mylep_indices(in_pT_order=True)}\n"
            f"Passes Z1 selections: {self.passes_z1_kinematic_selec()}\n"
            f"{lep_info}\n"
            f"{header_footer.replace('#', '-')}"
        )
        # self.mylep1.print_info()
        # self.mylep2.print_info()
        print()
        
    def get_distance_from_PDG_mass(self):
        """Return distance (float) this Z boson is from PDG Z mass value."""
        return self.get_mass() - ZMASS_PDG
    
    def get_mylep_ls(self):
        """Return a list of mylep1 and mylep2."""
        return [self.mylep1, self.mylep2]

    def get_mylep_indices(self, in_pT_order=False):
        """Return a list of the indices of mylep1 and mylep2.
        
        Args:
            in_pT_order (bool, optional):
                If True, first index is lep with higher pT.
                Default is False.
        """
        lep1 = self.mylep1
        lep2 = self.mylep2
        idcs_1then2 = [lep1.ndx_lepvec, lep2.ndx_lepvec]
        if in_pT_order and (lep2.lpt > lep1.lpt):
            return idcs_1then2[::-1]  # Reverse the order.
        else:
            return idcs_1then2
    
    def get_finalstate(self):
        """Return flavor (as str) of two leptons that built this Z.

        One of: '2e', '2mu'
        
        NOTE:
        - Only looks at first lepton flavor, thus won't work for
          the SS Method.
        """
        if abs(self.mylep1.lid) == 11:
            return "2e"
        elif abs(self.mylep1.lid) == 13:
            return "2mu"
        
    def has_overlapping_leps(self, other_z):
        """Return True if `self` and `other_z` have common leptons."""
        ndx_ls = self.get_mylep_indices() + other_z.get_mylep_indices()
        if len(ndx_ls) != len(set(ndx_ls)):
            # Contains duplicates (overlaps)! Sets kill duplicates.
            return True
        return False

    def has_closer_mass_to_ZPDG(self, other_z):
        """Return True if mass of `self` is closer to PDG than other_z is."""
        my_abs_dist = abs(self.get_distance_from_PDG_mass())
        their_abs_dist = abs(other_z.get_distance_from_PDG_mass())
        i_am_closer = ((my_abs_dist - their_abs_dist) < 0)
        return True if i_am_closer else False

    def get_num_passing_leps(self):
        """Return the number of passing leptons in this Z boson.
        
        Note: "Passing" means passing tight selection.
        """
        return sum([lep.is_tight for lep in self.get_mylep_ls()])

    def get_num_failing_leps(self):
        """Return the number of failing leptons in this Z boson.
        
        Note: "Failing" means failing tight selection.
        """
        return sum([lep.is_loose for lep in self.get_mylep_ls()])
# End of MyZboson.

def makes_valid_zcand(lep1, lep2, wcf_ok=False, verbose=False):
    """Return True if lep1 and lep2 will form a valid Z candidate.
    
    NOTE:
    - This is NOT necessarily a valid Z1 or Z2 candidate.
    
    To form a valid Z candidate:
    - Leptons DO NOT HAVE TO pass tight selection! (loose +tightID +RelIso)
        - This will be accounted for in forming the Z1.
    - Leptons must be OSSF.
    - 12 < m(ll, including FSR) < 120 GeV.

    Args:
        lep1 (MyLepton): Combines with lep2 to make Z cand.
        lep2 (MyLepton): Combines with lep1 to make Z cand.
        wcf_ok (bool, optional):
            If True, then a valid Z can have wrong charge/flavor (wcf) combo.
            Either wrong charge (e.g. e+e+, mu-mu-, etc.)
            or wrong flavor (e+mu- or e-mu+).
    """
    # Check OSSF:
    if not wcf_ok:
        if (lep1.lid + lep2.lid) != 0:
            if verbose:
                print("  PAIRING FAILED: Leptons are not OSSF")
                for lep in (lep1, lep2):
                    lep.print_info()
            return False
    if (lep1.lid == 0) or (lep2.lid == 0):
        if verbose:
            print("  PAIRING FAILED: Lepton ID is 0.")
        return False
    # Check invariant mass cut:
    zcand = lep1.get_LorentzVector(include_FSR=True) + \
            lep2.get_LorentzVector(include_FSR=True)
    z_mass = zcand.M()
    if (z_mass < 12):
        if verbose:
            print(f"  PAIRING FAILED: Zmass ({z_mass:.6f}) < 12 GeV.")
        return False
    if (z_mass > 120):
        if verbose:
            print(f"  PAIRING FAILED: Zmass ({z_mass:.6f}) > 120 GeV.")
        return False
    return True
    
def make_all_zcands(
    mylep_ls,
    zleps_in_pT_order=True,
    explain_skipevent=False, verbose=False
    ):
    """Return list of valid Z candidates as MyZboson objects.
    
    Go through all combinations (not permutations) of mylep_ls to make all
    valid Z candidates. This function DOES apply cuts to each Z!

    To form a valid Z candidate:
    - Leptons DO NOT HAVE TO pass tight selection! (loose + tightID + RelIso)
    - Leptons must be OSSF.
    - 12 < m(ll, including FSR) < 120 GeV.

    NOTE: Also stores indices of Z as it appears in list of Z.
    """
    zcand_ls = []
    # Make all dilepton combinations to find eligible Z candidates.
    ls_dileps = list(combinations(mylep_ls, 2))
    if verbose:
        print(f"  Found {len(ls_dileps)} dilepton pairs.")
    # Validate each pair.
    for ndx_zvec, (mylep1, mylep2) in enumerate(ls_dileps):
        if not makes_valid_zcand(mylep1, mylep2, verbose=verbose):
            continue
        # Found valid Z candidate.
        zcand = MyZboson(
            mylep1, mylep2,
            zleps_in_pT_order=zleps_in_pT_order,
            explain_skipevent=explain_skipevent
            )
        zcand.ndx_zcand_ls = ndx_zvec
        if verbose:
            print(
                f"    Made valid Z cand using leptons: "
                f"{zcand.get_mylep_indices()}."
                )
        zcand_ls.extend((zcand,))
    if verbose:
        print(f"  Number of valid Z candidates: {len(zcand_ls)}")
    return zcand_ls