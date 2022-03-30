from itertools import combinations
from constants.particleprops import ZMASS_PDG
from Utils_Python.printing import announce

class MyZboson:
    
    def __init__(
        self, mylep1, mylep2,
        zleps_in_pT_order=True,
        allow_z1_failing_leps=True,
        explain_skipevent=False
        ):
        self.mylep1 = mylep1
        self.mylep2 = mylep2
        self.allow_z1_failing_leps = allow_z1_failing_leps
        self.made_from_tight_leps = \
            mylep1.pass_tight_sel() * mylep2.pass_tight_sel()
        self.ndx_zcand_ls = None  # Index of this Z in list of Z candidates.
        self.explain_skipevent = explain_skipevent

        lep2pt_gt_lep1pt = (mylep2.lpt > mylep1.lpt)
        if zleps_in_pT_order and lep2pt_gt_lep1pt:
            self.mylep1 = mylep2
            self.mylep2 = mylep1
        
    def get_chargeflav(self):
        """Return str comparing charge and flavor of composite MyLeptons.

        Returns one of:
            * 'SSSF'
            * 'SSDF'
            * 'OSSF'
            * 'OSDF'
        """
        return self.mylep1.compare_chargeflavor(self.mylep2)

    def get_LorentzVector(self):
        """Return a Lorentz vector version of this Z boson."""
        return self.mylep1.get_LorentzVector(include_FSR=True) + \
                self.mylep2.get_LorentzVector(include_FSR=True)

    def passes_generic_zcand_sel(
        self, mass_min=12, mass_max=120, verbose=False
        ):
        """Return True if `self` makes a valid generic Z candidate.
        
        SELECTIONS:
        - Lepton pair must be one of:
            * OSSF
            * SSSF
            * OSDF
            But not SSDF since this is JUST crazy. :-)
        - mass_min < mZ(including FSR) < mass_max GeV.
        
        NOTE:
        - This is NOT necessarily a valid Z1 or Z2 candidate, as Z1 and Z2 can
        have their own selections.
        - Leptons comprising Z DO NOT NEED TO pass tight selection!
        (loose+tightID+RelIso)
        This will be checked for when forming the Z1.

        Args:
            z (MyZboson): Z candidate to consider.
        """
        # Must pass one of: OSSF, SSSF, OSDF.
        # Thus, it just can't be same-sign, different-flavor.
        if self.get_chargeflav() == 'SSDF':
            if verbose:
                print("  Z NOT BUILT: Leptons form same-sign, diff-flav pair")
                for lep in self.get_mylep_ls:
                    lep.print_info()
            return False
        # Check invariant mass cut:
        m = self.get_mass()
        if (m < mass_min):
            if verbose:
                print(f"  Z NOT BUILT: Zmass ({m:.6f}) < {mass_min} GeV.")
            return False
        if (m > mass_max):
            if verbose:
                print(f"  Z NOT BUILT: Zmass ({m:.6f}) > {mass_max} GeV.")
            return False
        return True

    def passes_z1_kinematic_sel(self, min_mass=40):
        """Return True if this Z boson COULD pass as a Z1 candidate.
        
        Checks for:
        * Zmass > 40 GeV
        * Whether it's OK to build the Z from passing/failing leptons.
        * That leptons are OSSF (this should be true even for WCF method)!

        Doesn't mean that it has been SELECTED AS the Z1 candidate!
        """
        msg = (
            f"Z (from leps {self.get_mylep_indices()}) "
            f"failed Z1 cut"
            )
        if not self.has_leps_OSSF():
            if self.explain_skipevent:
                print(f"{msg}: lepton pair is not OSSF.")
            return False
        mass = self.get_mass()
        if (mass < min_mass):
            if self.explain_skipevent:
                print(f"{msg}: mass ({mass:.6f}) < {min_mass} GeV.")
            return False
        can_fail = self.allow_z1_failing_leps
        all_leps_pass = self.made_from_tight_leps
        if (not can_fail) and (not all_leps_pass):
            if self.explain_skipevent:
                print(
                    f"  Z (from leps {self.get_mylep_indices()}) "
                    f"failed Z1 cut: not built from leps passing tight sel\n"
                    f"  (allow_z1_failing_leps={can_fail}, "
                    f"num_fail_leps={self.get_num_failing_leps()})"
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
        lep_info = (
            f"Made from: {n_pass} passing leptons, "
            f"{n_fail} failing leptons."
            )
        if n_pass == 1:
            lep_info = lep_info.replace("leptons,", "lepton,")
        if n_fail == 1:
            lep_info = lep_info.replace("leptons.", "lepton.")
        print(
            f"{header_footer}\n"
            f"# Z INFO{name}\n"
            f"Z made from pT-ordered leptons at indices: "
            f"{self.get_mylep_indices(in_pT_order=True)}\n"
            f"Z_pt={zvec.Pt():.6f}, Z_eta={zvec.Eta():.6f}, "
            f"Z_phi={zvec.Phi():.6f}, Z_mass={zvec.M():.6f}\n"
            f"Passes Z1 selections (mZ > 40 GeV and tightness check): "
            f"{self.passes_z1_kinematic_sel(min_mass=40)}\n"
            f"{lep_info}\n"
            f"{header_footer.replace('#', '-')}"
        )
        # self.mylep1.print_info()
        # self.mylep2.print_info()
        print()
        
    def get_distance_from_PDG_mass(self):
        """Return distance (float) this Z boson is from PDG Z mass value."""
        return self.get_mass() - ZMASS_PDG
    
    def get_num_passing_leps(self):
        """Return the number of passing leptons in this Z boson.
        
        Note: "Passing" means passing tight selection.
        """
        return sum([lep.pass_tight_sel() for lep in self.get_mylep_ls()])

    def get_num_failing_leps(self):
        """Return the number of failing leptons in this Z boson.
        
        Note: "Failing" means failing tight selection.

        In retrospect, I probably could have just done:
            return (2 - self.get_num_passing_leps())
        lol
        """
        return sum([lep.fail_tight_sel() for lep in self.get_mylep_ls()])

    def get_mylep_ls(self, in_pT_order=False):
        """Return a list of mylep1 and mylep2."""
        lep1 = self.mylep1
        lep2 = self.mylep2
        leps_1then2 = [lep1, lep2]
        if in_pT_order and (lep2.lpt > lep1.lpt):
            return leps_1then2[::-1]  # Reverse the order.
        return leps_1then2

    def get_mylep_indices(self, in_pT_order=False):
        """Return a list of the indices of mylep1 and mylep2.
        
        Args:
            in_pT_order (bool, optional):
                If True, first index is lep with higher pT.
                Default is False.
        """
        return [
            lep.ndx_lepvec for lep in \
            self.get_mylep_ls(in_pT_order=in_pT_order)
            ]
    
    def get_finalstate(self):
        """Return flavor (as str) of two leptons that built this Z.

        One of: '2e', '2mu', 'emu'

        'emu' can be returned in the case of wrong flavor studies.
        """
        str_fs = self.mylep1.get_flavor() + self.mylep2.get_flavor()
        str_fs = str_fs.replace('ee', '2e')
        str_fs = str_fs.replace('mumu', '2mu')
        str_fs = str_fs.replace('mue', 'emu')
        return str_fs

    def has_leps_same_flavor(self):
        """Return True if the two MyLeptons are same flavor (e.g. mu+mu-)."""
        return True if "2" in self.get_finalstate() else False

    def has_leps_opposite_charge(self):
        """Return True if the two MyLeptons are oppositely charged."""
        return (self.mylep1.get_charge() * self.mylep2.get_charge()) < 0 

    def has_leps_OSSF(self):
        """Return True if the two MyLeptons are opposite-sign same flavor."""
        return self.has_leps_opposite_charge() and self.has_leps_same_flavor()

    def has_leps_WCF(self):
        """Return True if the two MyLeptons are wrong charge or flavor."""
        wrong_char = (not self.has_leps_opposite_charge())
        wrong_flav = (not self.has_leps_same_flavor())
        return (wrong_char or wrong_flav)

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
# End of MyZboson.

def make_all_zcands(
    mylep_ls,
    method,
    zleps_in_pT_order=True,
    explain_skipevent=False, verbose=False
    ):
    """Return list of valid MyZboson obj (Z candidates) based on `method`.
    
    NOTE:
    - Also stores indices of Z as it appears in list of Z.
    - Go through all combinations (not permutations) of mylep_ls to make all
    valid Z candidates. This function DOES apply cuts to each Z!

    SELECTIONS:
    - 12 < m(ll, including FSR) < 120 GeV.
    - Leptons DO NOT HAVE TO pass tight selection! (loose+tightID+RelIso)
        - This will be accounted for in forming the Z1.
    Additionally, a valid Z candidate depends on `method` chosen:
        * method == 'OS'
            - Leptons necessarily must be OSSF.
        * method == 'WCF'
            - Z MAY have wrong charge/flavor (WCF) combo, but not required!
            Can accept OSSF, or wrong charge (e.g. e+e+, mu-mu-, etc.),
            or wrong flavor (e+mu- or e-mu+).
            The final 4l quartet must have one OSSF Z and a WCF Z.
            This will be handled in another function.

    Args:
        mylep_ls (list):
        method (str): Can be 'OS', 'WCF'
    """
    raise RuntimeError("Function deprecated. Use QuartetMaker.")
    zcand_ls = []
    # Make all dilepton combinations to find eligible Z candidates.
    ls_dileps = list(combinations(mylep_ls, 2))
    if verbose:
        print(f"  Found {len(ls_dileps)} lepton pairs.")
    # Validate each pair.
    for ndx_zvec, (mylep1, mylep2) in enumerate(ls_dileps):
        if not passes_generic_zcand_sel(
            mylep1, mylep2, method=method, verbose=verbose
            ):
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