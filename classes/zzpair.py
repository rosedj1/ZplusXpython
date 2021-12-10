from classes.mylepton import (check_leps_separated_in_DeltaR,
                              check_leps_pass_leadsublead_pTcuts,
                              leps_pass_lowmass_dilep_res,
                              has_2p2f_leps,has_3p1f_leps)
from classes.myzboson import MyZboson, make_all_zcands

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
        self.ndx_in_zzpair_ls = None  # Will be assigned when forming ZZPairs.
        self.smartcut_ZapassesZ1sel = smartcut_ZapassesZ1sel

    def get_m4l(self):
        """Return the m(4l) of this ZZPair."""
        return self.get_LorentzVector().M()

    def passes_cjlst_sel(self):
        """Return True if this ZZ pair forms a CJLST ZZ candidate.
        
        Step 1: Check that Z_fir and Z_sec have no overlapping leptons.
        
        Step 2: See if Z_fir is a valid Z1 candidate.
        - Z1 must be built from 2 tight leptons.
        - m(Z1) > 40 GeV.
        - If Z_fir and Z_sec both have only tight leptons, then whichever is
          closer to m(Z_PDG) is Z1.
        
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
              and if m(Zb) > 12 GeV, then this whole ZZ pair FAILS smart cut.
        - m(4l) > 70 GeV.
        """
        # NOTE: Doing m(4l) cut first since it is an efficient cut.
        if self.get_m4l() < 70:
            if self.explain_skipevent:
                print(f"Invalid ZZ cand. Failed m(4l) > 70 GeV.")
                self.print_info()
            return False
        
        # Step 1. Should already be taken into account, but just in case.
        if self.z_fir.has_overlapping_leps(self.z_sec):
            if self.explain_skipevent:
                print(f"Invalid ZZ cand. Has overlapping leptons.")
                self.print_info()
            return False
        
        # Step 2.
        if not self.z_fir.passes_z1_kinematic_selec():
            if self.explain_skipevent:
                print(
                    f"Invalid ZZ cand. z_fir does not pass Z1 selections."
                )
                self.print_info()
            return False
        # Check if Z2 also comes from tight leptons.
        # If so, make sure m(Z1) is closer to PDG mass.
        if self.z_sec.made_from_tight_leps:
            z_dist_fir = self.z_fir.get_distance_from_PDG_mass()
            z_dist_sec = self.z_sec.get_distance_from_PDG_mass()
            if abs(z_dist_sec) < abs(z_dist_fir):
                if self.explain_skipevent:
                    print(f"Invalid ZZ cand. m(Z2) closer to PDG than m(Z1) is.")
                    self.print_info()
                return False
        
        # Step 3.
        mylep_ls = self.get_mylep_ls()
        if not check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
            if self.explain_skipevent:
                print(f"Invalid ZZ cand. Leptons not separated in dR.")
                self.print_info()
            return False
        if not check_leps_pass_leadsublead_pTcuts(mylep_ls):
            if self.explain_skipevent:
                print(
                    f"Invalid ZZ cand. Leptons don't pass lead/sublead cuts."
                    )
                self.print_info()
            return False
        if not leps_pass_lowmass_dilep_res(mylep_ls, min_mass=4):
            if self.explain_skipevent:
                print(f"Invalid ZZ cand. Low-mass dilep resonance found.")
                self.print_info()
            return False
        if not self.passes_smart_cut():
            if self.explain_skipevent:
                print(f"Invalid ZZ cand. Failed smart cut.")
                self.print_info()
            return False
        return True
        
    def get_mylep_ls(self):
        """Return a list of all myleps that built this ZZPair."""
        return self.z_fir.get_mylep_ls() + self.z_sec.get_mylep_ls()

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
        if fs in ("4e", "4mu"):
            if self.verbose:
                print(f"{fs} final state found. Checking smart cut (ZaZb).")
            zazb = self.build_zazb_pair()
            # Is m(Za) closer to m(Z_PDG) than m(Z1) is?
            # NOTE: BBF doesn't check if Za has tight leptons!
            # TODO: Check if CJLST looks for Za built with tight leptons.
            # Now back up check Z1 check and lepton kinematics.
            # ...lepton kinematics have already been checked.
            pdg_dist_za = zazb.z_fir.get_distance_from_PDG_mass()
            pdg_dist_z1 = self.z_fir.get_distance_from_PDG_mass()
            za_more_onshell_than_z1 = (abs(pdg_dist_za) < abs(pdg_dist_z1))
            
            # Low mass di-lep cut should never trigger since all Z
            # candidates have already been checked for 12 < mZ < 120 GeV.
            zb_is_lowmass_dilep_res = (zazb.z_sec.mass < 12)
            if za_more_onshell_than_z1 and zb_is_lowmass_dilep_res:
                # ABOUT TO FAIL SMART CUT! Za looks like a good Z1.
                if self.smartcut_ZapassesZ1sel:
                    # Is Za a valid Z1 candidate?
                    if not zazb.z_fir.passes_z1_kinematic_selec():
                        # RAISE ALL HELL.
                        print(
                            f"CJLST goofed, y'all!\n"
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
                        f"  m(Za)={zazb.z_fir.mass:.4f} is closer to PDG "
                        f"value than m(Z1)={self.z_fir.mass:.4f}\n"
                        f"  m(Zb)={zazb.z_sec.mass:.4f} "
                        f"  m(Z2)={self.z_sec.mass:.4f}\n"
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

    def print_info(self):
        """Print info about both Z bosons in this ZZ candidate."""
        header = "@" * 67
        print(
            f"{header}\n"
            f"Info about ZZ candidate #{self.ndx_in_zzpair_ls}\n"
            f"{header}\n"
            f"  m(4l): {self.get_m4l():.9f}\n"
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
# End of ZZPair.
    
def make_all_zz_pairs(zcand_ls, explain_skipevent=False, smartcut_ZapassesZ1sel=False):
    """Return a list of all possible ZZPair objects.
    
    Notes:
    - Skip pairing a Z with itself.
    - Skip pairing two Z's if they share common leptons.
    - This accounts for ALL possible ZZ candidates, even swapping Z1 <-> Z2.
    - This function does not impose any selections on ZZ candidates.

    Args:
        smartcut_ZapassesZ1sel (bool, optional):
            In the smart cut, the literature essentially says that if a Za
            looks like a more on-shell Z boson than the Z1 AND if the Zb is a
            low mass di-lep resonance, then veto the whole ZZ candidate.
            However, literature doesn't check for Za passing Z1 selections!
            Set this to True if you require Za to pass Z1 selections.
            Default is False.
    """
    zz_pair_ndx = 0
    zz_pair_ls = []
    for ndx1, z1 in enumerate(zcand_ls):
        for ndx2, z2 in enumerate(zcand_ls):
            if ndx1 == ndx2:
                # Skip if they are the same Z.
                continue
            if z1.has_overlapping_leps(z2):
                if explain_skipevent:
                    print(
                        f"Z's contain overlapping leptons:\n"
                        f"z #{z1.ndx_zcand_ls}: {z1.get_mylep_indices()}\n"
                        f"z #{z2.ndx_zcand_ls}: {z2.get_mylep_indices()}"
                        )
                # Skip if they share common leptons.
                continue
            # Build ZZPair with no selections imposed.
            zz_pair = ZZPair(
                z_fir=z1, z_sec=z2,
                kin_discrim=None, explain_skipevent=explain_skipevent)
            zz_pair.ndx_in_zzpair_ls = zz_pair_ndx
            zz_pair_ls.extend((zz_pair,))
            zz_pair_ndx += 1
    return zz_pair_ls

def make_zz_pairs(zcand_ls):
    """Return a list of ALL possible non-overlapping ZZPair objects.

    Notes:
    - A non-overlapping ZZ pair means that they share no common leptons.
    - This function does not impose any selections on ZZ candidates.
    """
    zz_pair_ls = []
    for ndx1, z1 in enumerate(zcand_ls[:-1]):
        start_ndx2 = ndx1 + 1
        for ndx2, z2 in enumerate(zcand_ls[start_ndx2:]):
            if z1.has_overlapping_leps(z2):
                continue
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

def get_ZZcands_from_myleps_OSmethod(
    mylep_ls, verbose=False, explain_skipevent=False,
    smartcut_ZapassesZ1sel=False,
    run=None, lumi=None, event=None, entry=None):
    """Return list of all valid ZZ candidates from `mylep_ls`.
    
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
    assert len(mylep_ls) == 4, "`mylep_ls` must have only 4 leptons."
    empty_ls = []
    # Need 2 tight + 2 loose leps (2P2F) or 3 tight + 1 loose leps (3P1F).
    # This checks that leptons pass basic kinematic criteria (at least loose).
    if verbose: print("Checking for 2P2F or 3P1F leptons.")
    if (not has_2p2f_leps(mylep_ls)) and (not has_3p1f_leps(mylep_ls)):
        if verbose or explain_skipevent:
            print("Leptons are not 2P2F or 3P1F.")
        return empty_ls
    
    # Build all general Z candidates:
    # 12 < mll < 120 GeV.
    # OSSF leptons.
    # Leptons at least loose.
    if verbose: print("Making all Z candidates.")
    zcand_ls = make_all_zcands(mylep_ls, explain_skipevent=explain_skipevent)
    n_zcands = len(zcand_ls)
    if verbose: print(f"Number of Z candidates: {n_zcands}")
    if n_zcands < 2:
        if verbose or explain_skipevent:
            print(f"Found fewer than two Z candidates ({n_zcands}).")
        return empty_ls
    
    # Build all ZZ candidates.
    if verbose: print("Making all ZZ candidates.")
    zz_pair_ls = make_all_zz_pairs(zcand_ls,
                     explain_skipevent=explain_skipevent,
                     smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel)  # Does not implement ZZ cuts.
    if verbose: print(f"Made {len(zz_pair_ls)} ZZ pairs (pair != candidate)")
    ls_all_passing_zz = get_all_ZZcands_passing_cjlst(zz_pair_ls)
    if len(ls_all_passing_zz) > 1:
        print("MULTIPLE passing ZZ candidates found in this subevent!")
        for zz in ls_all_passing_zz:
            zz.print_info()
        # raise ValueError("Jake, choose a best ZZ among this quartet.")
    return ls_all_passing_zz

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
    all_passing_zzcands = get_ZZcands_from_myleps_OSmethod(
        mylep_ls=mylep_ls, verbose=verbose,
        explain_skipevent=explain_skipevent,
        smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
        run=run, lumi=lumi, event=event, entry=entry
        )
    n_zzcands = len(all_passing_zzcands)
    if n_zzcands == 0:
        if verbose or explain_skipevent:
            print(f"No ZZ candidates formed! ({n_zzcands} candidates)")
        return False
    # Should each 4-lep combo provide ONLY 1 valid ZZ candidate?
    if n_zzcands > 1:
        print(
            f"[WARNING] Found more than one ZZ candidate (found {n_zzcands}) "
            f"in event {run} : {lumi} : {event} (entry {entry})"
            )
        # for zzcand in all_passing_ZZcands_cjlst_ls:
        #     zzcand.print_info()
        # return False
    # According to CJLST, these 4 leptons should form exactly one valid
    # ZZ candidate! Must decide which ZZ is the best.
    # If the two ZZs have the same leptons, choose the cand whose m(Z1) is
    # closer to the m(Z_PDG) --- WARNING though! Should check that winning Z1
    # still passes Z1 selections!!!
    # If two ZZs do NOT have same leptons, then choose the ZZ with higher Kd.
    return True