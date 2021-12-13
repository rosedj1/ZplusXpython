from ROOT import Math
from Utils_Python.Utils_Physics import calc_dphi, calc_dR
class MyLepton:
    
    def __init__(self,
                 lpt, leta, lphi, lmass,
                 lid, ltightId, lRelIsoNoFSR,
                 lpt_NoFSR=None, leta_NoFSR=None, lphi_NoFSR=None, lmass_NoFSR=None,
                 ndx_lepvec=None):
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
        self.ndx_lepvec = ndx_lepvec  # Index of lepton in vectors like lep_pt.
        
        # NOTE: Here, "tight" and "loose" are exclusive!
        # Compare this to previous literature which says that if a lepton is
        # tight, then it also satisfies loose selections! Not the case here.
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
        """Return a Lorentz vector version of this lepton."""
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
            f"#- General Info -#\n"
            f"id={self.lid}, tightId={self.ltightId}, "
            f"RelIsoNoFSR={self.lRelIsoNoFSR:.6f}\n"
            f"is_loose={self.is_loose}, is_tight={self.is_tight}\n"
            f"#- Kinematics -#\n"
            f"(FSR)    pt={self.lpt:.6f}, "
            f"eta={self.leta:.6f}, "
            f"phi={self.lphi:.6f}, "
            f"mass={self.lmass:.6f}"
        )
        if self.lpt_NoFSR is not None:
            print(
                f"(no FSR) pt={self.lpt_NoFSR:.6f}, "
                f"eta={self.leta_NoFSR:.6f}, "
                f"phi={self.lphi_NoFSR:.6f}, "
                f"mass={self.lmass_NoFSR:.6f}\n"
            )

    def calc_DeltaR(self, mylep2):
        """Return the DeltaR value between this MyLepton and mylep2."""
        deta = self.leta - mylep2.leta
        dphi = calc_dphi(self.lphi, mylep2.lphi)
        return calc_dR(deta, dphi)

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

def has_atleastone_2p2f_comb(mylep_ls):
    """Return True if AT LEAST 2 leps are tight and AT LEAST 2 are loose."""
    if get_n_tight_myleps(mylep_ls) < 2:
        return False
    if get_n_loose_myleps(mylep_ls) < 2:
        return False
    return True

def has_atleastone_3p1f_comb(mylep_ls):
    """Return True if AT LEAST 3 leps are tight and AT LEAST 1 is loose."""
    if get_n_tight_myleps(mylep_ls) < 3:
        return False
    if get_n_loose_myleps(mylep_ls) < 1:
        return False
    return True
