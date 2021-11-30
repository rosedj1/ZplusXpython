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
        verbose=False):
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
        """
        self.z_fir = z_fir
        self.z_sec = z_sec
        self.kin_discrim = kin_discrim
        self.verbose = verbose
        
    def get_m4l(self):
        """Return the m(4l) of this ZZPair."""
        return self.get_LorentzVector().M()

    def passes_cjlst_sel(self):
        """Return True if this ZZ pair forms a CJLST ZZ candidate.
        
        Step 1: Check that Z_fir and Z_sec have no overlapping leptons.
        
        Step 2: See if Z_fir is a valid Z1 candidate.
        - Z1 must be built from 2 tight leptons.
        - m(Z1) > 40 GeV.
        - If Z_fir and Z_sec are both from tight leptons, then whichever is
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
            return False
        
        # Step 1.
        if self.z_fir.has_overlapping_leps(self.z_sec):
            return False
        
        # Step 2.
        if not self.z_fir.passes_z1_kinematic_selec():
            return False
        z_dist_fir = self.z_fir.get_distance_from_PDG_mass()
        z_dist_sec = self.z_sec.get_distance_from_PDG_mass()
        if abs(z_dist_sec) < abs(z_dist_fir):
            return False
        
        # Step 3.
        mylep_ls = self.get_mylep_ls()
        if not check_leps_separated_in_DeltaR(mylep_ls, min_sep=0.02):
            return False
        if not check_leps_pass_leadsublead_pTcuts(mylep_ls):
            return False
        if not leps_pass_lowmass_dilep_res(mylep_ls, min_mass=4):
            return False
        if not self.passes_smart_cut():
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
            za_more_onshell_than_z1 = abs(pdg_dist_za) < abs(pdg_dist_z1)
            zb_is_lowmass_dilep_res = zazb.z_sec.mass < 12
            if za_more_onshell_than_z1:# and zb_is_lowmass_dilep_res:
                if self.verbose:
                    print(
                        f"FAILED SMART CUT:\n"
                        f"  m(Za)={zazb.z_fir.mass:.4f} is closer to PDG "
                        f"value than m(Z1)={self.z_fir.mass:.4f}\n"
                        f"  m(Zb)={zazb.z_sec.mass:.4f} "
                        f"  m(Z2)={self.z_sec.mass:.4f}\n"
                    )
                return False
        return True
    
    def build_zazb_pair(self):
        """Return a new ZZPair object using other OSSF lep pair.
        
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

    
#     def get_num_valid_z1cand(self, z_first, z_second):
#         """Return the number of valid Z1 candidates. Either 0, 1, or 2.

#         To be a valid Z1 candidate:
#         - Must be built from 2 tight leptons.
#         - Must have m(Z1) > 40 GeV.
#         """
#         return sum(z.passes_z1cand_selec for z in (z_first, z_second))

#     def print_info(self):
#         FIXME: Needs to be cleaned up!
#         """Print info about both Z bosons in this ZZ candidate."""
#         header = "@" * 67
#         print(
#             f"{header}\n"
#             f"Info about ZZ candidate\n"
#             f"{header}\n"
#             f" ZaZb cand: {self.is_zazb_cand}, "
#             f" ZaZb preferred: {self.zazb_is_preferred}\n"
#             f" Number of valid Z1 cands: {self.num_valid_z1cand}, "
#             f" Found best Z1: {self.found_best_z1}\n"
#             f" Z cand swap required to build Z1: {self.zcands_swapped}\n"
#             f" Bkg kinematic discriminant: {self.kin_discrim}\n"
#             f"Individual Z info:\n"
#         )
# #         if self.is_zazb_cand and :
# #             # This ZZ has already 
# #             # Name Z1 as Za and Z2 as Zb.
# #             name1 = "Za"
# #             name2 = "Zb"
#         self.z1.print_info()
#         self.z2.print_info()

#         self.found_best_z1 = self.
#         self.zazb_is_preferred = None  # True: ZaZb cand is better than Z1Z2.
#         self.num_valid_z1cand = self.get_num_valid_z1cand(z_first, z_second)
        
#         # Figure out which Z should be Z1, if any.
#         if self.num_valid_z1cand > 0:
#             self.z1, self.z2 = self.assign_z1_and_z2(z_first, z_second)
#             self.found_best_z1 = True
#         else:
#             self.found_best_z1 = False

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