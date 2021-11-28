class MyZboson:
    
    def __init__(self, mylep1, mylep2):
        self.mylep1 = mylep1
        self.mylep2 = mylep2
        self.mass = self.get_LorentzVector().M()
        self.made_from_tight_leps = mylep1.is_tight * mylep2.is_tight
        self.passes_z1cand_selec = self.passes_z1_kinematic_selec()
        self.ndx_zcand_ls = None
        
    def get_LorentzVector(self):
        """Return a Lorentz vector version of this Z boson."""
        return self.mylep1.get_LorentzVector() + self.mylep2.get_LorentzVector()
        
    def passes_z1_kinematic_selec(self):
        """Return True if this Z boson COULD pass as a Z1 candidate.
        
        Doesn't mean that it has been SELECTED AS the Z1 candidate!
        """
        if (self.mass < 40):
            return False
        if not self.made_from_tight_leps:
            return False
        return True
    
    def print_info(self, name=""):
        """Print info about this Z boson.
        
        Args:
            name (str): Name for this Z: "Z1", "Za".
        """
        header_footer = '#' * 67
        name = "" if name is None else f": name={name}"
        zvec = self.get_LorentzVector()
        if self.made_from_tight_leps:
            lep_tightness_info = "Made from 2 tight leptons."
        else:
            lep_tightness_info = "Made from at least 1 loose lepton."
        print(
            f"{header_footer}\n"
            f"# Z CANDIDATE INFO{name}\n"
            f"Z_pt={zvec.Pt():.6f}, Z_eta={zvec.Eta():.6f}, "
            f"Z_phi={zvec.Phi():.6f}, Z_mass={zvec.M():.6f}\n"
            f"Z boson made from leptons with vector indices: "
            f"{self.mylep1.ndx_lepvec}, {self.mylep2.ndx_lepvec}\n"
            f"{lep_tightness_info}\n"
            f"{header_footer.replace('#', '-')}"
        )
        self.mylep1.print_info()
        self.mylep2.print_info()
        print()
        
    def get_distance_from_PDG_mass(self):
        """Return distance (float) this Z boson is from PDG Z mass value."""
        return self.get_LorentzVector().M() - Zmass_pdg
    
    def get_mylep_ls(self):
        """Return a list of mylep1 and mylep2."""
        return [self.mylep1, self.mylep2]
    
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
        mylep_ls = self.get_mylep_ls() + other_z.get_mylep_ls()
        ndx_ls = [lep.ndx_lepvec for lep in mylep_ls]
        if len(ndx_ls) != set(ndx_ls):
            # The set will remove any duplicates.
            return False
        return True