from itertools import combinations
# Package imports.
from Utils_Python.printing import announce
from classes.myzboson import MyZboson
from classes.zzpair import (
    get_best_zzcand_single_quartet,
    make_all_zz_pairs
    )
from classes.mylepton import (
    # find_quartets_2pass2fail,
    # find_quartets_3pass1fail,
    make_all_quartets_3p1f,
    make_all_quartets_2p2f,
    # make_all_quartets_wcf
)

# t.GetEntry(61)
# from classes.quartetmaker import QuartetMaker
# from classes.mylepton import *
# lep_ls = make_filled_mylep_ls(t)
# qm = QuartetMaker(lep_ls)
# qm.ls_valid_z


allow_z1_failing_leps=True,
stop_when_found_3p1f=True,
run=None, lumi=None, event=None, entry=None,
smartcut_ZapassesZ1sel = False,
        
class QuartetMaker:
    """Per event, sort MyLeptons into quartets in different control regions.
    
    Select quartets that fall into one of eight orthogonal control regions:
        1. OS 2P2F
        2. OS 3P1F
        3. SS 2P2F
        4. SS 3P1F
        5. SS 4P
        6. DF 2P2F
        7. DF 3P1F
        8. DF 4P
        
    Abbreviations:
        * OS = Quartet made up of opposite-sign, same-flavor leptons.
        * SS = Quartet made up of same-sign, same-flavor leptons.
        * DF = Quartet made up of opposite-sign, different-flavor leptons.
        
    A "quartet" is a combination of 4-leptons.
    Each event may have multiple leptons quartets.
    If an event has both a 3P1F quartet and a 2P2F quartet,
    then the 3P1F will take priority when `stop_when_found_3p1f` is True.
    In this case, the 2P2F quartets will not be saved.

    In the literature, one will see "WCF" (wrong charge/flavor).
    WCF is the same as SS + DF.

    Selected events must also pass corresponding OS, SS, DF selections.

    Applies ZZ candidate selection criteria to determine "valid" ZZ cands.

    NOTE:
        By default, if a 3P1F ZZ cand is found, then 2P2F cands will NOT
        be searched for. To also search for 2P2F, then set:
            `stop_when_found_3p1f = False`
    """

    def __init__(
        self, mylep_ls,
        verbose=False, explain_skipevent=False,
        smartcut_ZapassesZ1sel=False,
        run=None, lumi=None, event=None, entry=None,
        stop_when_found_3p1f=True,
        allow_z1_failing_leps=True,
        zleps_in_pT_order=True
        ):
        """Make categorizer with sorted MyLepton quartets for one event.

        There are two main steps to forming a valid quartet (ZZ cand):
        1. Z Formation: Form all dilepton COMBINATIONS that pass selections.
        2. Z Pairing: Form all Z pair PERMUTATIONS that pass selections.
            - If both ZxZy and ZyZx pass selections, the better is chosen.
            - TODO: What makes one better?

        Args:
            mylep_ls (list):
                This event's list of MyLeptons.
            verbose (bool, optional):
                Verbose output. Defaults to False.
            explain_skipevent (bool, optional):
                Print details on why the ZZ candidate was not built.
                Defaults to False.
            smartcut_ZapassesZ1sel (bool, optional):
                Deprecated.
                Defaults to False.
            run (int, optional):
                Run number. Useful for selecting a specific event.
                Defaults to None.
            lumi (int, optional):
                Lumi section number. Useful for selecting a specific event.
                Defaults to None.
            event (int, optional):
                Event number. Useful for selecting a specific event.
                Defaults to None.
            entry (int, optional):
                Row in TTree. Defaults to None.
            stop_when_found_3p1f (bool, optional):
                If True, if at least one valid 3P1F ZZ candidate was found,
                do not look for any 2P2F candidates. Defaults to True.
            allow_z1_failing_leps (bool, optional):
                If True,
            zleps_in_pT_order (bool, optional):
                Build Z's with leading lepton at index 0 and subleading at 1.
                Default is True.
        """
        ls_valid_z = self.form_valid_Zs(
            mylep_ls,
            verbose=verbose,
            explain_skipevent=explain_skipevent,
            zleps_in_pT_order=zleps_in_pT_order,
            mz_min=12, mz_max=120,
            )

        self.ls_valid_zzcands = self.pair_Zs(
            ls_valid_z,
            verbose=False, explain_skipevent=False,
            smartcut_ZapassesZ1sel=False,
            run=None, lumi=None, event=None, entry=None,
            stop_when_found_3p1f=True,
            allow_z1_failing_leps=True,
            zleps_in_pT_order=True
            )
    
    def form_valid_Zs(
        self,
        mylep_ls,
        verbose=False, explain_skipevent=False,
        zleps_in_pT_order=True,
        mz_min=12, mz_max=120,
        ):
        """Return list of MyZboson objects that pass selections.

        Dilepton selections:
        * mz_min < mZ < mz_max GeV.
        Lepton pair satisfies only ONE of the following:
            * OS (opposite-sign, same-flavor)
            * SS (same-sign, same-flavor)
            * DF (opposite-sign, different-flavor)

        NOTE:
            Forms COMBINATIONS of lepton pairs, not permutations.
        """
        zcand_ls = []
        # Make all dilepton combinations to find eligible Z candidates.
        ls_dileps = list(combinations(mylep_ls, 2))
        if verbose:
            print(f"  Found {len(ls_dileps)} lepton pairs.")
        # Make each Z and check if it passes basic Z cand selections.
        for ndx_zvec, (mylep1, mylep2) in enumerate(ls_dileps):
            zcand = MyZboson(
                mylep1, mylep2,
                zleps_in_pT_order=zleps_in_pT_order,
                explain_skipevent=explain_skipevent
                )
            if not zcand.passes_generic_zcand_sel(
                    mass_min=mz_min, mass_max=mz_max, verbose=verbose
                    ):
                continue
            # Z is good.
            zcand.ndx_zcand_ls = ndx_zvec
            if verbose:
                print(
                    f"    Made valid Z cand using leptons: "
                    f"{zcand.get_mylep_indices()}."
                    )
            zcand_ls.extend(
                (zcand,)
                )
        if verbose:
            print(f"  Number of valid Z candidates: {len(zcand_ls)}")
        return zcand_ls

    def pair_Zs(
        self, ls_zcand, method, allow_z1_failing_leps=True
        ):
        """Return list of all ZZ candidates that pass OS or WCF selections.
        
        OS Method:
            Z1 and Z2 are both OSSF.
        WCF Method:
            Z1 must be OSSF but Z2 is either SSSF or OSDF.

        Args:
            ls_zcand (list):
                List of Z candidates passing general Z sel.
            method (str):
                RedBkg event selection method.
                Can be: 'any', 'OS', 'WCF'
            allow_z1_failing_leps (bool):
                Default is True.
        """
        for ndx1, z1 in enumerate(ls_zcand):
            for ndx2, z2 in enumerate(ls_zcand):
                if ndx1 == ndx2:
                    # Skip pairing identical Z's.
                    continue
                if z1.has_overlapping_leps(z2):
                    # Skip if they share common leptons.
                    if explain_skipevent:
                        print(
                            f"  Z's contain overlapping leptons:"
                            f" z#{z1.ndx_zcand_ls}{z1.get_mylep_indices()}, "
                            f" z#{z2.ndx_zcand_ls}{z2.get_mylep_indices()}"
                            )
                    continue
                # Build ZxZy. If both Z's are OSSF, then compare to ZyZx.
                zz = build_better_zzcand(
                    z1, z2,
                    )
                if zz is not None:
                    ls_zz_cands.extend(
                        [zz]
                        )


def build_better_zzcand():
    """Return the better ZZPair object that passes RedBkg Selections."""



                # Build ZZPair with no selections imposed.
                zz = ZZPair(
                    z_fir=z1, z_sec=z2,
                    kin_discrim=None, explain_skipevent=explain_skipevent
                    )
                # Check ZxZy pairing.
                if zz.check_passes_redbkg_sel(
                    method=method,
                    allow_z1_failing_leps=allow_z1_failing_leps
                    ):
                # Check ZyZx pairing (other permutation). 
                zz_pair.ndx_zzpair_ls = ndx




            zz = choose_better_zz(
                z1, z2,
                verbose=self.verbose,
                explain_skipevent=False,
                smartcut_ZapassesZ1sel=False,
                )
            # Check ZyZx .
            zz_alt = 
            ls_zz_cands.extend(
                (zz,)
            )

        # Implement ZZ cuts.
        ls_zz_cands = [
            zz for zz in ls_zz_pairs \

            ]
            





        
        n_zzpairs = len(ls_zz_pairs)
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



    # def get_passing_quartets(self, cr, method):
    #     """Return list of valid ZZPairs that fall into `cr` and pass `method`.
        
    #     Args:
    #         cr (str): '2P2F', '3P1F', '4P'
    #         method (str): 'OS', 'WCF'
    #     """
    #     assert cr in ('2P2F', '3P1F', '4P')
    #     assert method in ('OS', 'WCF')
    #     n_pass_leps = int(cr.split('P')[0])
    #     return [zz for zz in self.ls_valid_zzcands \
    #         if zz.get_num_passing_leps() == n_pass_leps and zz.]
        



    #     # Categorize mylep_ls into OS Method 3P1F and 2P2F quartets.
    #     self.ls_valid_ZZcands_OS_3p1f = \
    #         self.get_best_zzcands_all_quartets(
    #             mylep_ls, cr='3P1F',
    #             allow_z1_failing_leps=allow_z1_failing_leps,
    #             zleps_in_pT_order=zleps_in_pT_order,
    #             verbose=verbose,
    #             explain_skipevent=explain_skipevent,
    #             smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
    #             run=run, lumi=lumi, event=event, entry=entry
    #             )
    #     self.n_valid_ZZcands_OS_3p1f = len(self.ls_valid_ZZcands_OS_3p1f)
    #     self.has_valid_ZZcand_OS_3p1f = (self.n_valid_ZZcands_OS_3p1f > 0)
        
    #     if self.has_valid_ZZcand_OS_3p1f and stop_when_found_3p1f:
    #         self.ls_valid_ZZcands_OS_2p2f = []
    #     else:
    #         self.ls_valid_ZZcands_OS_2p2f = \
    #             self.get_best_zzcands_all_quartets(
    #                 mylep_ls, cr='2P2F',
    #                 allow_z1_failing_leps=allow_z1_failing_leps,
    #                 zleps_in_pT_order=zleps_in_pT_order,
    #                 verbose=verbose,
    #                 explain_skipevent=explain_skipevent,
    #                 smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
    #                 run=run, lumi=lumi, event=event, entry=entry
    #                 )

    #     self.ls_valid_ZZcands_WCF = \
    #         self.get_best_zzcands_all_quartets(
    #             mylep_ls, cr='WCF',
    #             allow_z1_failing_leps=allow_z1_failing_leps,
    #             zleps_in_pT_order=zleps_in_pT_order,
    #             verbose=verbose,
    #             explain_skipevent=explain_skipevent,
    #             smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
    #             run=run, lumi=lumi, event=event, entry=entry
    #             )
    #     self.n_valid_ZZcands_OS_2p2f = len(self.ls_valid_ZZcands_OS_2p2f)
    #     self.has_valid_ZZcand_OS_2p2f = (self.n_valid_ZZcands_OS_2p2f > 0)

    # def get_best_zzcands_all_quartets(
    #     self,
    #     mylep_ls, cr,
    #     allow_z1_failing_leps=True,
    #     zleps_in_pT_order=True,
    #     verbose=False, explain_skipevent=False,
    #     smartcut_ZapassesZ1sel=False,
    #     run=None, lumi=None, event=None, entry=None
    #     ):
    #     """Return a list of all best ZZ cands that pass `cr` selections.
        
    #     Each valid quartet has an associated ZZ cand returned in the list:

    #         ls_all_valid_zzcands = [
    #             best_ZZ_quart1,
    #             best_ZZ_quart2,
    #             ...
    #             ]

    #     Leptons are sorted into quartets based on given control region `cr`.

    #     TODO: Add wrong charge/flavor functionality.

    #     Args:
    #         mylep_ls (list of MyLeptons):
    #             Leptons from only 1 event. Not limited to just 4 leptons.
    #             Will be sorted into different quartets based on methods
    #             (OS, WCF) and CRs (3P1F, 2P2F).
    #         cr (str): Control region ('3P1F', '2P2F', 'WCF').

    #     Returns:
    #         list: Valid ZZ candidates that pass OS Method selections.
    #     """
    #     cr = cr.upper()
    #     if cr == '3P1F':
    #         ls_quartets = make_all_quartets_3p1f(mylep_ls)
    #     elif cr == '2P2F':
    #         ls_quartets = make_all_quartets_2p2f(mylep_ls)
    #     elif cr == 'WCF':
    #         ls_quartets = make_all_quartets_wcf(mylep_ls)

    #     n_tot_quart = len(ls_quartets)
    #     if n_tot_quart == 0:
    #         # No chance to make quartets.
    #         return []
            
    #     if verbose:
    #         print(f"  Num of {cr} quartets to analyze: {n_tot_quart}")
    #     # List to hold valid ZZ cands that pass selections.
    #     ls_all_valid_zzcands = []
    #     for n_quart, quart in enumerate(ls_quartets, 1):
    #         if verbose:
    #             announce(f"Analyzing {cr} quartet #{n_quart}/{n_tot_quart}")
    #             lep_ndcs = [mylep.ndx_lepvec for mylep in quart]
    #             print(f"  Lepton indices: {lep_ndcs}")
    #         # For this quartet, pick best ZZ cand using either
    #         # OS Method or WC/F logic.
    #         ls_zzcand = get_best_zzcand_single_quartet(
    #                 quart, cr,
    #                 allow_z1_failing_leps=allow_z1_failing_leps,
    #                 zleps_in_pT_order=zleps_in_pT_order,
    #                 verbose=verbose, explain_skipevent=explain_skipevent,
    #                 smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
    #                 run=run, lumi=lumi, event=event, entry=entry
    #                 )

    #         if len(ls_zzcand) == 0:
    #             # No good ZZ candidate found.
    #             continue

    #         # Save the best ZZ cand.
    #         ls_all_valid_zzcands.append(ls_zzcand[0])

    #     return ls_all_valid_zzcands
