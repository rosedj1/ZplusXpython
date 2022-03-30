from itertools import permutations
from classes.mylepton import (check_leps_separated_in_DeltaR,
                              check_leps_pass_leadsublead_pTcuts,
                              leps_pass_lowmass_dilep_res,
                              has_2p2f_leps, has_3p1f_leps)
from classes.myzboson import MyZboson, make_all_zcands
from Utils_Python.printing import announce

class ZZPair:
    """NOT the same thing as a 'ZZ Candidate' (which passes selections)."""
    
    def __init__(
        self,
        z_fir,
        z_sec,
        kin_discrim=None,
        verbose=False,
        explain_skipevent=False,
        smartcut_ZapassesZ1sel=False):
        """
        NOTE:
        - The literature is confusing with its notation.
          For instance, the "Z1" is often used to describe the best on-shell
          Z candidate and "Z2" is the other.
          Then there's "Za" and "Zb", when considering the alternate OSSF
          lepton pairing within this ZZ candidate.
          So instead of Z1Z2 and ZaZb, we'll use Z_fir, Z_sec to indicate:
            Z_fir = the first Z candidate given to this ZZPair.
            Z_sec = the second Z candidate given to this ZZPair.
          
        Args:
            z_fir (MyZboson):
            z_sec (MyZboson):
            kin_discrim (float): Kinematic Discriminant for background.
            ### ^Not yet implemented. Need to discuss this with Filippo.
            smartcut_ZapassesZ1sel (bool, optional):
                In the smart cut, the literature essentially says that if a Za
                looks like a more on-shell Z boson than the Z1 AND if the Zb is a
                low mass di-lep resonance, then veto the whole ZZ candidate.
                However, literature doesn't check for Za passing Z1 selections!
                Set this to True if you require Za to pass Z1 selections.
                Default is False.
        """
        self.z_fir = z_fir
        self.z_sec = z_sec
        self.kin_discrim = kin_discrim
        self.verbose = verbose
        self.explain_skipevent = explain_skipevent
        self.ndx_zzpair_ls = None  # Will be assigned when forming ZZPairs.
        self.smartcut_ZapassesZ1sel = smartcut_ZapassesZ1sel
        # Filled after self.passes_redbkg_sel():
        self.passed_method = None  # 'OS', 'WCF'.

    def get_m4l(self):
        """Return the m(4l) of this ZZPair."""
        return self.get_LorentzVector().M()

    def passes_redbkg_osmethod_sel(self, allow_z1_failing_leps=True):
        """Return True if this ZZ passes OS Method selections.

        NOTE: If ZZ does pass, then it is a valid OS Method ZZ cand.

        When `allow_z1_failing_leps = False`,
        then implements HIG-19-001 RedBkg event selection:
        - AN: AN-19-139v6, p.58.
        - PAS: HIG-19-001v9, p.12.
        - Paper: Eur. Phys. J. C (2021) 81:488, p.10.

        More notes:
        - The reducible background event selection mentioned in HIG-19-001 has
            a few suboptimal parts of its logic. This function implements the
            improvements as follows:
        - Considers Multiple Quartets:
            Different lepton quartets per event can contribute to the RBE.
            So if there are 3 leptons passing tight sel and 2 failing, then
            there are at least two 3P1F quartets that could be built.
            Both should contribute to the RBE.
        - All ZZ candidates considered:
            For each quartet in an event, a (possibly different) Z1 is
            selected, whereas in the current xBF analyzer the BEST Z1 is first
            chosen among ALL Z candidates and then it is paired with the other
            Z's one-by-one.
        - 3P1F priority over 2P2F:
            If an event has valid 3P1F and 2P2F candidates in an event, then
            only consider the 3P1F quartets to the RBE. Currently, the xBF
            analyzer selects the best ZZ candidate based on which has the
            highest D_kin_bkg. Thus, it sometimes selects a 2P2F quartet over
            a 3P1F one.
        - Relaxed Z1 requirement:
            Z1 can be built from failing leptons which should better estimate
            ttbar contribution.

        ======================================================================
        EVENT SELECTION
        Step 1: Check that Z_fir and Z_sec have no overlapping leptons.
        
        Step 2: See if Z_fir is a valid Z1 candidate.
        - Z1 MAY be built from 2 leptons passing tight selection,
            depending on the value of `allow_z1_failing_leps`.
        - m(Z1) > 40 GeV.
        - See which Z is closer to PDG mass value of Z boson.
        
        Step 3: Kinematic selections.
        - Ghost removal: All 4 leptons must have DeltaR > 0.02.
        - Lep pT cuts:
            - At least 2 leps must have pT > 10 GeV.
            - At least 1 lep must have pT > 20 GeV.
        - QCD Suppression:
            - m(ll) > 4 GeV for all OS leptons, neglect flavor and FSR.
        - Smart Cut:
            - If fs = 4mu/4e, check alternate ZaZb cand from other OSSF leps.
            - m(Za) is closer to m(Z_PDG) than m(Zb) is.
            - If Za (new possible Z1) is closer to PDG mass than old Z1,
              and if m(Zb) < 12 GeV, then this whole ZZ pair FAILS smart cut.
        - m(4l) > 70 GeV.
        ======================================================================

        Args:
            allow_z1_failing_leps (bool, optional):
                If True, allow Z1 to be built from 0, 1, or 2 leptons failing
                tight selection.
        """
        skip_msg_prefix = f"Invalid ZZ cand (#{self.ndx_zzpair_ls})"
        # NOTE: Doing m(4l) cut first since it is an efficient cut.
        if self.get_m4l() < 70:
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Failed m(4l) > 70 GeV.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        
        # Step 1. Should already be taken into account, but just in case.
        if self.z_fir.has_overlapping_leps(self.z_sec):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Z's have overlapping leptons.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        
        # Step 2.
        if not self.z_fir.passes_z1_kinematic_sel(
                allow_z1_failing_leps=allow_z1_failing_leps
                ):
            if self.explain_skipevent:
                print(
                    f"  {skip_msg_prefix}: z_fir does not pass Z1 selections."
                )
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        # If m(Z2) is closer to PDG mass, then it MAY supercede current Z1
        # (but only check if both Z's are built from passing leptons).
        if self.z_sec.has_closer_mass_to_ZPDG(self.z_fir):
            if allow_z1_failing_leps or self.z_sec.made_from_tight_leps:
                if self.explain_skipevent:
                    print(
                        f"  {skip_msg_prefix}: "
                        f"m(Z2) closer to PDG than m(Z1) is."
                        )
                    if self.verbose: self.print_info()
                self.valid_cand_osmethod = False
                return False
        
        # Step 3.
        mylep_ls = self.get_mylep_ls()
        if not check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Leptons not separated in dR.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        if not check_leps_pass_leadsublead_pTcuts(mylep_ls):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Leptons fail lead/sublead cuts.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        if not leps_pass_lowmass_dilep_res(mylep_ls, min_mass=4):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Low-mass dilep resonance found.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False
        if not self.passes_smart_cut():
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Failed smart cut.")
                if self.verbose: self.print_info()
            self.valid_cand_osmethod = False
            return False

        # Good redbkg ZZ candidate for OS Method!
        self.valid_cand_osmethod = True
        return True
        
    def passes_redbkg_sel(self, method, allow_z1_failing_leps=True):
        """Return True if this ZZ passes `method` selections.

        Arg:
            `method` (str): 'OS', 'WCF', 'any'

        - OS is "opposite sign".
        - WCF is "wrong charge/flavor".
        - If ZZ does pass, then it is a valid ZZ cand for that method and
        the str attribute `passed_method` gets filled with either 'OS' or 'WCF'.

        More notes:
        - The reducible background event selection mentioned in HIG-19-001 has
            a few suboptimal parts of its logic. This function implements the
            improvements as follows:
        - Considers Multiple Quartets:
            Different lepton quartets per event can contribute to the RBE.
            So if there are 3 leptons passing tight sel and 2 failing, then
            there are at least two 3P1F quartets that could be built.
            Both should contribute to the RBE.
        - All ZZ candidates considered:
            For each quartet in an event, a (possibly different) Z1 is
            selected, whereas in the current xBF analyzer the BEST Z1 is first
            chosen among ALL Z candidates and then it is paired with the other
            Z's one-by-one.
        - 3P1F priority over 2P2F:
            If an event has valid 3P1F and 2P2F candidates in an event, then
            only consider the 3P1F quartets to the RBE. Currently, the xBF
            analyzer selects the best ZZ candidate based on which has the
            highest D_kin_bkg. Thus, it sometimes selects a 2P2F quartet over
            a 3P1F one.
        - Relaxed Z1 requirement:
            Z1 can be built from failing leptons which should better estimate
            ttbar contribution.

        ======================================================================
        EVENT SELECTION
        Step 1: Check that Z_fir and Z_sec have no overlapping leptons.
        
        Step 2: See if Z_fir is a valid Z1 candidate.
        - Z1 MAY be built from 2 leptons passing tight selection,
            depending on the value of `allow_z1_failing_leps`.
        - m(Z1) > 40 GeV.
        - See which Z is closer to PDG mass value of Z boson.
        
        Step 3: Kinematic selections.
        - Ghost removal: All 4 leptons must have DeltaR > 0.02.
        - Lep pT cuts:
            - At least 2 leps must have pT > 10 GeV.
            - At least 1 lep must have pT > 20 GeV.
        - QCD Suppression:
            - m(ll) > 4 GeV for all OS leptons, neglect flavor and FSR.
        - Smart Cut:
            - If fs = 4mu/4e, check alternate ZaZb cand from other OSSF leps.
            - m(Za) is closer to m(Z_PDG) than m(Zb) is.
            - If Za (new possible Z1) is closer to PDG mass than old Z1,
              and if m(Zb) < 12 GeV, then this whole ZZ pair FAILS smart cut.
        - m(4l) > 70 GeV.
        ======================================================================

        Args:
            allow_z1_failing_leps (bool, optional):
                If True, allow Z1 to be built from 0, 1, or 2 leptons failing
                tight selection.
        """
        method = method.upper()
        skip_msg_prefix = f"Invalid ZZ cand (#{self.ndx_zzpair_ls})"

        # Check if ZZ agrees with specified method.
        zz_ossf = self.check_both_Zs_OSSF()
        zz_wcf = self.check_z2_WCF()
        if method == 'OS' and not zz_ossf:
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: not made from 2 OSSF Z's.")
                if self.verbose: self.print_info()
            return False
        elif method == 'WCF' and not zz_wcf:
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: z_sec is not WCF.")
                if self.verbose: self.print_info()
            return False
        elif method == 'any':
            if not zz_ossf and not zz_wcf:
                if self.explain_skipevent:
                    print(f"  {skip_msg_prefix}: neither OSSF nor WCF.")
                    if self.verbose: self.print_info()
                return False
            else:
                method = 'OS' if zz_ossf else 'WCF'

        # NOTE: Do m(4l) cut first since it is an efficient cut.
        if self.get_m4l() < 70:
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Failed m(4l) > 70 GeV.")
                if self.verbose: self.print_info()
            return False
        
        # Step 1. Should already be taken into account, but just in case.
        if self.z_fir.has_overlapping_leps(self.z_sec):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Z's have overlapping leptons.")
                if self.verbose: self.print_info()
            return False
        
        # Step 2.
        if not self.z_fir.passes_z1_kinematic_sel(
                min_mass=40,
                allow_z1_failing_leps=allow_z1_failing_leps
                ):
            if self.explain_skipevent:
                print(
                    f"  {skip_msg_prefix}: z_fir does not pass Z1 selections."
                    )
                if self.verbose: self.print_info()
            return False
        # If m(Z2) is closer to PDG mass, then it MAY supercede current Z1
        # (but only check if both Z's are built from passing leptons).
        if self.z_sec.has_closer_mass_to_ZPDG(self.z_fir):
            if allow_z1_failing_leps or self.z_sec.made_from_tight_leps:
                if self.explain_skipevent:
                    print(
                        f"  {skip_msg_prefix}: "
                        f"m(Z2) closer to PDG than m(Z1) is."
                        )
                    if self.verbose: self.print_info()
                return False
        
        # Step 3.
        mylep_ls = self.get_mylep_ls()
        if not check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Leptons not separated in dR.")
                if self.verbose: self.print_info()
            return False
        if not check_leps_pass_leadsublead_pTcuts(mylep_ls):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Leptons fail lead/sublead cuts.")
                if self.verbose: self.print_info()
            return False
        if not leps_pass_lowmass_dilep_res(mylep_ls, min_mass=4):
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Low-mass dilep resonance found.")
                if self.verbose: self.print_info()
            return False
        if not self.passes_smart_cut():
            if self.explain_skipevent:
                print(f"  {skip_msg_prefix}: Failed smart cut.")
                if self.verbose: self.print_info()
            return False

        # Good redbkg ZZ candidate!
        self.passed_method = method
        return True

    def check_valid_cand_os_3p1f(self):
        """Return True if ZZ cand passed OS Method sel and is 3P1F."""
        n_fail = self.get_num_failing_leps()
        return self.valid_cand_osmethod and (n_fail == 1)

    def check_valid_cand_os_2p2f(self):
        """Return True if ZZ cand passed OS Method sel and is 2P2F."""
        n_fail = self.get_num_failing_leps()
        return self.valid_cand_osmethod and (n_fail == 2)

    def check_both_Zs_OSSF(self):
        """Return True if `self.z_fir` and `self.z_sec` are OSSF."""
        return (self.z_fir.has_leps_OSSF() and self.z_sec.has_leps_OSSF())

    def check_z2_WCF(self):
        """Return True if `self.z_sec` has wrong charge/flavor leps."""
        return self.z_sec.has_leps_WCF()

    def get_mylep_ls(self, in_pT_order=False):
        """Return a list of all myleps that built this ZZPair.
        
        Args:
            in_pT_order (bool, optional):
                If True, then each Z will have its lepton pTs sorted.
                So the first 2 elements will still be Z1's leps
                and the last 2 elements will still be Z2's leps.
        """
        return self.z_fir.get_mylep_ls(in_pT_order=in_pT_order) + \
                self.z_sec.get_mylep_ls(in_pT_order=in_pT_order)

    def get_mylep_indices(self, in_pT_order=False):
        """Return a list of 4 indices: [z1_lep1, z1_lep2, z2_lep1, z2_lep2].

        Args:
            in_pT_order (bool, optional):
                If True, then each Z will have its lepton pTs sorted.
                So the first 2 elements will still be Z1's leps
                and the last 2 elements will still be Z2's leps.
        """
        return self.z_fir.get_mylep_indices(in_pT_order=in_pT_order) + \
                self.z_sec.get_mylep_indices(in_pT_order=in_pT_order)
        
    def get_LorentzVector(self):
        """Return a Lorentz vector version of this ZZ candidate."""
        return self.z_fir.get_LorentzVector() + self.z_sec.get_LorentzVector()

    def get_finalstate(self):
        """Return str of 4-lepton final state:

        One of: '4e', '4mu', '2e2mu', '2mu2e'
        """
        zz_fs_str = self.z_fir.get_finalstate() + self.z_sec.get_finalstate()
        zz_fs_str = zz_fs_str.replace("2e2e", "4e")
        zz_fs_str = zz_fs_str.replace("2mu2mu", "4mu")
        return zz_fs_str
    
    def passes_smart_cut(self):
        """Return True if this ZZPair is better than alternate pair ZaZb."""
        fs = self.get_finalstate()
        if fs in ("4e", "4mu") and self.check_both_Zs_OSSF()
            if self.verbose:
                print(
                    f"OSSF {fs} final state found. Checking smart cut (ZaZb)."
                    )
            zazb = self.build_zazb_pair()
            # Is m(Za) closer to m(Z_PDG) than m(Z1) is?
            # TODO: Check if HIG-19-001 looks for Za built with tight leptons.
            # Now back up check Z1 check and lepton kinematics.
            # ...lepton kinematics have already been checked.
            pdg_dist_za = zazb.z_fir.get_distance_from_PDG_mass()
            pdg_dist_z1 = self.z_fir.get_distance_from_PDG_mass()
            za_more_onshell_than_z1 = (abs(pdg_dist_za) < abs(pdg_dist_z1))
            
            zb_is_lowmass_dilep_res = (zazb.z_sec.get_mass() < 12)
            if za_more_onshell_than_z1 and zb_is_lowmass_dilep_res:
                # ABOUT TO FAIL SMART CUT! Za looks like a good Z1.
                if self.smartcut_ZapassesZ1sel:
                    # Is Za a valid Z1 candidate?
                    if not zazb.z_fir.passes_z1_kinematic_sel():
                        # RAISE ALL HELL.
                        print(
                            f"HIG-19-001 goofed, y'all!\n"
                            f"ZaZb DID look better than Z1Z2, except Za "
                            f"is not a valid Z1 candidate!"
                        )
                        print("ZaZb info:")
                        zazb.print_info()
                        print("Z1Z2 info:")
                        self.print_info()
                        raise RuntimeError
                if self.explain_skipevent:
                    print(
                        f"FAILED SMART CUT:\n"
                        f"  m(Za)={zazb.z_fir.get_mass():.4f} is closer to PDG "
                        f"value than m(Z1)={self.z_fir.get_mass():.4f}\n"
                        f"  m(Zb)={zazb.z_sec.get_mass():.4f} "
                        f"  m(Z2)={self.z_sec.get_mass():.4f}\n"
                    )
                    self.print_info()
                return False
        return True
    
    def build_zazb_pair(self):
        """Return a new ZZPair object using other OSSF lep pair.
        
        So you have 4 leptons:
            L1  L2  L3  L4

        m(Za) is closer to m(Z_PDG) than m(Zb) is.
        """
        # Build new ZaZb candidate.
        new_zcand_ls = []
        for mylep1 in self.z_fir.get_mylep_ls():
            # Pair this guy with the lepton of OS from z2.
            for mylep2 in self.z_sec.get_mylep_ls():
                if (mylep1.lid + mylep2.lid) == 0:
                    # OSSF.
                    new_z = MyZboson(mylep1, mylep2)
                    new_zcand_ls.extend((new_z,))
        assert len(new_zcand_ls) == 2
        za = new_zcand_ls[0]
        zb = new_zcand_ls[1]
        pdg_dist_za = za.get_distance_from_PDG_mass()
        pdg_dist_zb = zb.get_distance_from_PDG_mass()
        if abs(pdg_dist_za) < abs(pdg_dist_zb):
            return ZZPair(za, zb, self.kin_discrim)
        else:
            return ZZPair(zb, za, self.kin_discrim)

    def print_info(self, name=""):
        """Print info about both Z bosons in this ZZ candidate."""
        header = "@" * 67
        print(
            f"{header}\n"
            f"Info about ZZ candidate #{self.ndx_zzpair_ls}: {name}\n"
            f"{header}\n"
            f"  m(4l): {self.get_m4l():.6f}\n"
            f"  final state: {self.get_finalstate()}\n"
            f"               | z_fir | z_sec |\n"
            f"  lep indices: | "
            f"{self.z_fir.mylep1.ndx_lepvec} , "
            f"{self.z_fir.mylep2.ndx_lepvec} | "
            f"{self.z_sec.mylep1.ndx_lepvec} , "
            f"{self.z_sec.mylep2.ndx_lepvec} |\n"
            f"Individual Z info:"
        )
        self.z_fir.print_info()
        self.z_sec.print_info()

    def has_same_4leps(self, other_zz):
        """Return True if other_zz contains same 4 lep indices as `self`.
        
        The beauty of using sets is that the order of indices doesn't matter.
        """
        my_lep_idxs = set(
                        self.z_fir.get_mylep_indices() +
                        self.z_sec.get_mylep_indices()
                        )
        other_lep_idxs = set(
                            other_zz.z_fir.get_mylep_indices() +
                            other_zz.z_sec.get_mylep_indices()
                            )
        # err_msg = "ZZ has overlapping leptons!"
        # assert len(my_lep_idxs) == 4, err_msg
        # assert len(other_lep_idxs) == 4, err_msg
        # overlapping_leps = (my_lep_idxs & other_lep_idxs)
        # return True if len(overlapping_leps) == 4 else False
        return (my_lep_idxs == other_lep_idxs)

    def has_same_z1z2(self, other_zz):
        """Return True if other_zz has the same Z1 and Z2 as this ZZ."""
        my_lep_idxs_z1 = set(self.z_fir.get_mylep_indices())
        my_lep_idxs_z2 = set(self.z_sec.get_mylep_indices())
        other_lep_idxs_z1 = set(other_zz.z_fir.get_mylep_indices())
        other_lep_idxs_z2 = set(other_zz.z_sec.get_mylep_indices())
        samez1 = (my_lep_idxs_z1 == other_lep_idxs_z1)
        samez2 = (my_lep_idxs_z2 == other_lep_idxs_z2)
        return (samez1 and samez2)
    
    def get_num_failing_leps(self):
        """Return the number of failing leptons in this ZZ pair.
        
        Note: "Failing" means failing tight selection.
        """
        return sum([lep.fail_tight_sel() for lep in self.get_mylep_ls()])

    def get_num_passing_leps(self):
        """Return the number of passing leptons in this ZZ pair.
        
        Note: "Passing" means passing tight selection.
        """
        return sum([lep.pass_tight_sel() for lep in self.get_mylep_ls()])

    def get_str_cr_os_method(self):
        """Return str corresponding to OS method control region.
        
        Returns either '3P1F' or '2P2F'.

        Assumes that ZZ pairing has passed OS Method selections,
        i.e. is a "valid" candidate.
        """
        if self.check_valid_cand_os_3p1f():
            return '3P1F'
        elif self.check_valid_cand_os_2p2f():
            return '2P2F'
        else:
            n_fail = self.get_num_failing_leps()
            raise ValueError(
                f"Valid OS Method ZZ cand has {n_fail} leptons "
                f"failing tight selection.\n  Is it truly valid?"
                )

    def get_bools_lepsfailtightsel(self, in_pT_order=True):
        """Return a list of bools of the leptons which fail tight selection.

        Returns:
            4-elem list:
                A `1` indicates that the lepton failed tight sel.
                The order of the list is:
                    [z1_lep1, z1_lep2, z2_lep1, z2_lep2]
                Example:
                    [0, 1, 1, 0]
                So here z1_lep2 and z2_lep1 failed tight selection.
        """
        return [
            lep.fail_tight_sel() for lep in \
                self.get_mylep_ls(in_pT_order=in_pT_order)
        ]
# End of ZZPair.
    
def make_all_zz_pairs(
    zcand_ls,
    verbose=False, explain_skipevent=False,
    smartcut_ZapassesZ1sel=False
    ):
    """Return a list of all ZZPair objects, skipping Z's with common leps.
    
    Notes:
    - Build all permutations of ZZ pairs:
        So if you had Z cands (Zx, Zy) then it would form:
            (Zx, Zy) AND (Zy, Zx).
    - Skip pairing two Z's if they share common leptons.
    - This function does not impose any selections on ZZPairs.
    - Stores index of ZZPair as `self.ndx_zzpair_ls`.

    NOTE: If code is slow, then this function could be slowing things down.
    More efficient way would be to use a different function which uses a
    double for loop over the list of Z's, skip the same Z, and implement ZZ
    selections right away.
    """
    if verbose:
        print("  Making all ZZ permutations.")
    zz_pair_ls = []
    # zcand_ls contains unique MyZbosons.
    ls_zz_permut = list(permutations(zcand_ls, 2))
    for ndx, (z1, z2) in enumerate(ls_zz_permut):
        if z1.has_overlapping_leps(z2):
            # Skip if they share common leptons.
            if explain_skipevent:
                print(
                    f"  Z's contain overlapping leptons:"
                    f" z#{z1.ndx_zcand_ls}{z1.get_mylep_indices()}, "
                    f" z#{z2.ndx_zcand_ls}{z2.get_mylep_indices()}"
                    )
            continue
        # Build ZZPair with no selections imposed.
        zz_pair = ZZPair(
            z_fir=z1, z_sec=z2,
            kin_discrim=None, explain_skipevent=explain_skipevent
            )
        zz_pair.ndx_zzpair_ls = ndx
        zz_pair_ls.extend(
            (zz_pair,)
            )
    if verbose:
        print(f"  Made {len(zz_pair_ls)} ZZ permutations.")
    return zz_pair_ls

def select_better_zzcand(
    zzcand1, zzcand2, allow_z1_failing_leps=True, verbose=False
    ):
    """Return better ZZPair (candidate) out of two.
    
    If the two ZZs share same leptons, choose the cand whose m(Z1) is
    closer to the m(Z_PDG). --- WARNING! Should check that winning Z1
    still passes Z1 selections!!! CJLST and xBF do not do this.
    UPDATE:
        After running over millions of events,
        The second ZZ candidate is sometimes selected over the first.
        Even after checking that the Z1 from this second ZZ passes
        Z1 candidate selections gives no errors.
        Conclusion:
            Perhaps there's something inherent in the smart cut that ensures
            the Z1 will pass tight selections.
    
    If two ZZs do NOT have same leptons, then choose the ZZ with higher Kd.
    Unfortunately, this code cannot yet recalculate Kd's per ZZ.
    """
    ndx_fir = zzcand1.ndx_zzpair_ls
    ndx_sec = zzcand2.ndx_zzpair_ls
    if zzcand1.has_same_4leps(zzcand2):
        if verbose:
            print(
                f"  ZZ cands (#{ndx_fir}, #{ndx_sec}) share same 4 leptons.\n"
                f"  Selecting the ZZ with m(Z1) closer to PDG value."
                )
        err_msg = (
            f"  Z1 from best ZZ doesn't pass tight selections!\n"
            f"  This could imply bad logic in literature smart cut!!!"
            )
        if zzcand1.z_fir.has_closer_mass_to_ZPDG(zzcand2.z_fir):
            # First ZZ cand is the better cand.
            assert zzcand1.z_fir.passes_z1_kinematic_sel(
                allow_z1_failing_leps=allow_z1_failing_leps
            ), err_msg
            winning_zz = zzcand1
            winning_zz_ndx = ndx_fir
        else:
            # Second ZZ cand is the better cand.
            assert zzcand2.z_fir.passes_z1_kinematic_sel(
                allow_z1_failing_leps=allow_z1_failing_leps
            ), err_msg
            winning_zz = zzcand2
            winning_zz_ndx = ndx_sec
    else:
        raise ValueError(
                f"  ZZ cands have different leptons.\n"
                f"  Choose cand with higher Kd. HOW???"
                )
    if verbose:
        print(
            f"  ZZ#{winning_zz_ndx} selected as better cand, "
            f"since its Z1 was closer to PDG."
            )
        zzcand1.print_info()
        zzcand2.print_info()
    return winning_zz

def get_zz_passing_redbkg_osmethod_sel(
    zz_pair_ls, allow_z1_failing_leps=True
    ):
    """Return a sub-list of `zz_pair_ls` with the ZZs passing OS Method cuts.
    
    If no ZZ pairs pass selections, then return an empty list.
    
    When `allow_z1_failing_leps = False`,
    then implements HIG-19-001 RedBkg event selection:

    NOTE:
        - Be sure that zz_pair_ls provides ALL permutations of ZZ pairings.
        E.g. If you have three Zs, then zz_pair_ls should have 6 ZZPair objs:
            (Z1, Z2),
            (Z1, Z3),
            (Z2, Z1),
            (Z2, Z3),
            (Z3, Z1),
            (Z3, Z2)

    Args:
        zz_pair_ls (list): Contains ZZPair objects to test.
        allow_z1_failing_leps (bool, optional):
            TODO: Get docstring entry from other function.
    """
    return [
        zz for zz in zz_pair_ls if zz.passes_redbkg_osmethod_sel(
            allow_z1_failing_leps=allow_z1_failing_leps
            )
        ]
    # Since ZZ permutations are considered, it is possible that
    # ZxZy passes and ZyZx passes selections - but these are the same ZZ!
    # So must eliminate any duplicates like this.
    # set_unique_zz = set()
    # for zz in ls_zzcands:
    #     if zz.has_same_z1z2()
    #     set_unique_zz.add()

def get_best_zzcand_single_quartet(
    mylep_ls, allow_z1_failing_leps=True,
    zleps_in_pT_order=True,
    verbose=False, explain_skipevent=False,
    smartcut_ZapassesZ1sel=False,
    run=None, lumi=None, event=None, entry=None):
    """Return a list of the single best ZZ candidate from a lepton quartet.
    
    NOTE:
    - Imposes Z1, Z2, and ZZ selection criteria.
    - `mylep_ls` should have exactly 4 leptons (a quartet).
    - Should just return ONE ZZ candidate (but inside a list).
    - Returns empty list if no ZZ candidates are found.

    Args:
        TODO: Update below.
        mylep_ls (list):
            Four MyLeptons that make up quartet.
            Will be combined into a ZZPair and analyzed for candidacy.
        allow_z1_failing_leps (bool, optional):
            If True, allow Z1 to be built from 0, 1, or 2 leptons failing
            tight selection.
        smartcut_ZapassesZ1sel (bool, optional):
            In the smart cut, the literature essentially says that if a Za
            looks like a more on-shell Z boson than the Z1 AND if the Zb is a
            low mass di-lep resonance, then veto the whole ZZ candidate.
            However, literature doesn't check for Za passing Z1 selections!
            Set this to True if you require Za to pass Z1 selections.
            Default is False.
        run (int): The run number, used for debugging.
        lumi (int): The lumi number, used for debugging.
        event (int): The event number, used for debugging.
        entry (int): The row of tree containing event, used for debugging.
    """
    assert len(mylep_ls) == 4, "`mylep_ls` must have only 4 leptons."
    empty_ls = []
    if verbose:
        print(f"Event {run}:{lumi}:{event} (entry = {entry})")
    # Need 2P2F or 3P1F.
    if (not has_2p2f_leps(mylep_ls)) and (not has_3p1f_leps(mylep_ls)):
        if verbose or explain_skipevent:
            print("  MyLep list does not fall into 2P2F or 3P1F CR.")
        return empty_ls
    
    # Build all general Z candidates:
    # 12 < mll < 120 GeV.
    # OSSF leptons.
    # Leptons at least loose.
    if verbose:
        print("  Building all Z candidates...")
    zcand_ls = make_all_zcands(
        mylep_ls,
        method=method,
        zleps_in_pT_order=zleps_in_pT_order,
        explain_skipevent=explain_skipevent, verbose=verbose
        )
    n_zcands = len(zcand_ls)
    if n_zcands < 2:
        if verbose or explain_skipevent:
            print(f"  Found fewer than two Z candidates ({n_zcands}).")
        return empty_ls
    
    # Build all permutations of ZZ candidates.
    zz_pair_ls = make_all_zz_pairs(
        zcand_ls,
        verbose=verbose,
        explain_skipevent=explain_skipevent,
        smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel
        )

    # Implement ZZ cuts.
    if cr in ("2P2F", "3P1F"):
        ls_all_passing_zz = get_zz_passing_redbkg_osmethod_sel(
            zz_pair_ls, allow_z1_failing_leps=allow_z1_failing_leps
            )
    elif cr == "WCF":
        ls_all_passing_zz = get_zz_passing_redbkg_wcf_sel(
            zz_pair_ls, allow_z1_failing_leps=allow_z1_failing_leps
            )
    
    n_zzpairs = len(zz_pair_ls)
    n_zzcands = len(ls_all_passing_zz)
    if verbose:
        print(f"  Made {n_zzcands} {cr} ZZ cands from {n_zzpairs} ZZ pairs.")
    if n_zzcands <= 1:
        # Return either empty list or the only ZZ cand made.
        return ls_all_passing_zz
    if not allow_z1_failing_leps:
        # Each lepton quartet can provide up to TWO ZZ cands: Z1Z2 and ZaZb.
        assert n_zzcands < 3, (
            f"  Houston, we have a problem...\n"
            f"  Quartet of leptons built {n_zzcands} ZZ cands."
            )
    # Found two ZZ cands. Must choose the better ZZ.
    zzcand1, zzcand2 = ls_all_passing_zz
    better_zz_cand = select_better_zzcand(
        zzcand1, zzcand2,
        allow_z1_failing_leps=allow_z1_failing_leps,
        verbose=verbose
        )
    return [better_zz_cand]

def myleps_pass_cjlst_osmethod_selection(
    mylep_ls, verbose=False, explain_skipevent=False,
    smartcut_ZapassesZ1sel=False,
    run=None, lumi=None, event=None, entry=None):
    """Return True if myleps form at least 1 valid ZZ candidate.
    
    NOTE:
    - Checks that they pass all Z1, Z2, and ZZ selection criteria.
    - `mylep_ls` should have exactly 4 leptons. 

    Args:
        smartcut_ZapassesZ1sel (bool, optional):
            In the smart cut, the literature essentially says that if a Za
            looks like a more on-shell Z boson than the Z1 AND if the Zb is a
            low mass di-lep resonance, then veto the whole ZZ candidate.
            However, literature doesn't check for Za passing Z1 selections!
            Set this to True if you require Za to pass Z1 selections.
            Default is False.
        run (int): The run number, used for debugging.
        lumi (int): The lumi number, used for debugging.
        event (int): The event number, used for debugging.
        entry (int): The row of tree containing event, used for debugging.
    """
    all_passing_zzcands = get_best_zzcand_single_quartet(
        mylep_ls=mylep_ls,
        zleps_in_pT_order=zleps_in_pT_order,
        verbose=verbose,
        explain_skipevent=explain_skipevent,
        smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
        run=run, lumi=lumi, event=event, entry=entry
        )
    n_zzcands = len(all_passing_zzcands)
    if n_zzcands == 0:
        if verbose or explain_skipevent:
            print(f"  No ZZ candidates formed! ({n_zzcands} candidates)")
        return False
    return True