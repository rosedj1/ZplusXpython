from Utils_Python.printing import announce
from classes.zzpair import (
    get_best_zzcand_single_quartet
    )
from classes.mylepton import (
    # find_quartets_2pass2fail,
    # find_quartets_3pass1fail,
    make_all_quartets_3p1f,
    make_all_quartets_2p2f,
    make_all_quartets_wcf
)

class QuartetCategorizer:
    """Per event, sort MyLeptons into 2P2F and 3P1F quartets.
    
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
        # Categorize mylep_ls into OS Method 3P1F and 2P2F quartets.
        self.ls_valid_ZZcands_OS_3p1f = \
            self.get_best_zzcands_all_quartets(
                mylep_ls, cr='3P1F',
                allow_z1_failing_leps=allow_z1_failing_leps,
                zleps_in_pT_order=zleps_in_pT_order,
                verbose=verbose,
                explain_skipevent=explain_skipevent,
                smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                run=run, lumi=lumi, event=event, entry=entry
                )
        self.n_valid_ZZcands_OS_3p1f = len(self.ls_valid_ZZcands_OS_3p1f)
        self.has_valid_ZZcand_OS_3p1f = (self.n_valid_ZZcands_OS_3p1f > 0)
        
        if self.has_valid_ZZcand_OS_3p1f and stop_when_found_3p1f:
            self.ls_valid_ZZcands_OS_2p2f = []
        else:
            self.ls_valid_ZZcands_OS_2p2f = \
                self.get_best_zzcands_all_quartets(
                    mylep_ls, cr='2P2F',
                    allow_z1_failing_leps=allow_z1_failing_leps,
                    zleps_in_pT_order=zleps_in_pT_order,
                    verbose=verbose,
                    explain_skipevent=explain_skipevent,
                    smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                    run=run, lumi=lumi, event=event, entry=entry
                    )

        self.ls_valid_ZZcands_WCF = \
            self.get_best_zzcands_all_quartets(
                mylep_ls, cr='WCF',
                allow_z1_failing_leps=allow_z1_failing_leps,
                zleps_in_pT_order=zleps_in_pT_order,
                verbose=verbose,
                explain_skipevent=explain_skipevent,
                smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                run=run, lumi=lumi, event=event, entry=entry
                )
        self.n_valid_ZZcands_OS_2p2f = len(self.ls_valid_ZZcands_OS_2p2f)
        self.has_valid_ZZcand_OS_2p2f = (self.n_valid_ZZcands_OS_2p2f > 0)

    def get_best_zzcands_all_quartets(
        self,
        mylep_ls, cr,
        allow_z1_failing_leps=True,
        zleps_in_pT_order=True,
        verbose=False, explain_skipevent=False,
        smartcut_ZapassesZ1sel=False,
        run=None, lumi=None, event=None, entry=None
        ):
        """Return a list of all best ZZ cands that pass `cr` selections.
        
        Each valid quartet has an associated ZZ cand returned in the list:

            ls_all_valid_zzcands = [
                best_ZZ_quart1,
                best_ZZ_quart2,
                ...
                ]

        Leptons are sorted into quartets based on given control region `cr`.

        TODO: Add wrong charge/flavor functionality.

        Args:
            mylep_ls (list of MyLeptons):
                Leptons from only 1 event. Not limited to just 4 leptons.
                Will be sorted into different quartets based on methods
                (OS, WCF) and CRs (3P1F, 2P2F).
            cr (str): Control region ('3P1F', '2P2F', 'WCF').

        Returns:
            list: Valid ZZ candidates that pass OS Method selections.
        """
        cr = cr.upper()
        if cr == '3P1F':
            ls_quartets = make_all_quartets_3p1f(mylep_ls)
        elif cr == '2P2F':
            ls_quartets = make_all_quartets_2p2f(mylep_ls)
        elif cr == 'WCF':
            ls_quartets = make_all_quartets_wcf(mylep_ls)

        n_tot_quart = len(ls_quartets)
        if n_tot_quart == 0:
            # No chance to make quartets.
            return []
            
        if verbose:
            print(f"  Num of {cr} quartets to analyze: {n_tot_quart}")
        # List to hold valid ZZ cands that pass selections.
        ls_all_valid_zzcands = []
        for n_quart, quart in enumerate(ls_quartets, 1):
            if verbose:
                announce(f"Analyzing {cr} quartet #{n_quart}/{n_tot_quart}")
                lep_ndcs = [mylep.ndx_lepvec for mylep in quart]
                print(f"  Lepton indices: {lep_ndcs}")
            # For this quartet, pick best ZZ cand using either
            # OS Method or WC/F logic.
            ls_zzcand = get_best_zzcand_single_quartet(
                    quart, cr,
                    allow_z1_failing_leps=allow_z1_failing_leps,
                    zleps_in_pT_order=zleps_in_pT_order,
                    verbose=verbose, explain_skipevent=explain_skipevent,
                    smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                    run=run, lumi=lumi, event=event, entry=entry
                    )

            if len(ls_zzcand) == 0:
                # No good ZZ candidate found.
                continue

            # Save the best ZZ cand.
            ls_all_valid_zzcands.append(ls_zzcand[0])

        return ls_all_valid_zzcands