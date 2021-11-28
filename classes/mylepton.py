class MyLepton:
    
    def __init__(self,
                 lpt, leta, lphi, lmass,
                 lid, ltightId, lRelIsoNoFSR,
                 lpt_NoFSR=None, leta_NoFSR=None, lphi_NoFSR=None, lmass_NoFSR=None):
        """When built, this MyLepton will determine if it's tight or loose."""
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
        
        self.is_tight = None  # Will become a bool.
        self.is_loose = None  # Will become a bool.
        self.ndx_lepvec = None  # Index of lepton in vectors like lep_pt.
        
        if self.passes_tightlep_selection():
            self.is_tight = True
            self.is_loose = False
        elif self.passes_looselep_selection():
            self.is_tight = False
            self.is_loose = True
        else:
            self.is_tight = False
            self.is_loose = False
        
    def passes_looselep_selection(self):
        """Return True if MyLepton passes loose lepton selection.

        Selections:
        - pT > 7(5) GeV for electrons(muons)
        - abs(eta) < 2.5(2.4) for electrons(muons)
        - (The selections below are included in a previous skim step.)
        - dxy < 0.5 cm
        - dz < 1 cm
        - SIP_3D < 4
        """
        return pass_lepton_kinem_selection(self.lid, self.lpt, self.leta)

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
        """Return a Lorentz vector version of this lepton.
        
        """
        if include_FSR:
            return Math.PtEtaPhiMVector(self.lpt,
                                        self.leta,
                                        self.lphi,
                                        self.lmass)
        return Math.PtEtaPhiMVector(self.lpt_NoFSR,
                                        self.leta_NoFSR,
                                        self.lphi_NoFSR,
                                        self.lmass_NoFSR)
    
    def print_info(self):
        """Print info about this MyLepton."""
        print(
            f"#--- lepton info at vector index={self.ndx_lepvec} ---#\n"
            f"Kinematics:\n"
            f"(FSR)    pt={self.lpt:.6f}, "
            f"eta={self.leta:.6f}, "
            f"phi={self.lphi:.6f}, "
            f"mass={self.lmass:.6f}\n"
            f"(no FSR) pt={self.lpt_NoFSR:.6f}, "
            f"eta={self.leta_NoFSR:.6f}, "
            f"phi={self.lphi_NoFSR:.6f}, "
            f"mass={self.lmass_NoFSR:.6f}\n"
            f"(more info) id={self.lid}, tightId={self.ltightId}, "
            f"RelIsoNoFSR={self.lRelIsoNoFSR:.6f}\n"
            f"(more info) is_loose={self.is_loose}, is_tight={self.is_tight}"
        )
        
    def calc_DeltaR(self, mylep2):
        """Return the DeltaR value between this MyLepton and mylep2."""
        deta = self.leta - mylep2.leta
        dphi = calc_dphi(self.lphi, mylep2.lphi)
        return calc_dR(deta, dphi)