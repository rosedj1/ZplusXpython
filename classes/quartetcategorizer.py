from Utils_Python.printing import print_header_message
from classes.zzpair import (
    get_ZZcands_from_myleps_OSmethod
    )
from classes.mylepton import (
    find_combos_2tight2loose,
    find_combos_3tight1loose,
)

class QuartetCategorizer:

    def __init__(
        self, mylep_ls,
        verbose=False, explain_skipevent=False,
        smartcut_ZapassesZ1sel=False,
        run=None, lumi=None, event=None, entry=None
        ):
        # Categorize mylep_ls into OS Method 3P1F and 2P2F quartets.
        self.ls_valid_ZZcands_OS_3p1f = \
            self.get_best_ZZcand_per_quart(
                mylep_ls, cr='3P1F',
                verbose=verbose,
                explain_skipevent=explain_skipevent,
                smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                run=run, lumi=lumi, event=event, entry=entry
                )
        self.ls_valid_ZZcands_OS_2p2f = \
            self.get_best_ZZcand_per_quart(
                mylep_ls, cr='2P2F',
                verbose=verbose,
                explain_skipevent=explain_skipevent,
                smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                run=run, lumi=lumi, event=event, entry=entry
                )

        self.n_valid_ZZcands_OS_3p1f = len(self.ls_valid_ZZcands_OS_3p1f)
        self.n_valid_ZZcands_OS_2p2f = len(self.ls_valid_ZZcands_OS_2p2f)

        self.has_valid_ZZcand_OS_3p1f = (self.n_valid_ZZcands_OS_3p1f > 0)
        self.has_valid_ZZcand_OS_2p2f = (self.n_valid_ZZcands_OS_2p2f > 0)

    def get_best_ZZcand_per_quart(
        self,
        mylep_ls, cr,
        verbose=False, explain_skipevent=False,
        smartcut_ZapassesZ1sel=False,
        run=None, lumi=None, event=None, entry=None
        ):
        """Return a list of best ZZ cands that pass OS method selections.
        
        In the returned list:
            ls_valid_zz_cand_OS = [
                best_ZZ_quart1, best_ZZ_quart2, ...
                ]

        Leptons are sorted into quartets based on given control region `cr`.

        TODO: Add wrong charge/flavor functionality.

        Args:
            mylep_ls (list of MyLeptons):
                Leptons from only 1 event. Not limited to just 4 leptons.
                Will be sorted into different quartets based on methods
                (OS, WCF) and CRs (3P1F, 2P2F).
            cr (str): Control region ('3P1F' or '2P2F').

        Returns:
            list: Valid ZZ candidates that pass OS Method selections.
        """
        cr = cr.upper()
        if cr == '3P1F':
            fourlep_combos = find_combos_3tight1loose(mylep_ls)
        elif cr == '2P2F':
            fourlep_combos = find_combos_2tight2loose(mylep_ls)

        n_tot_combos = len(fourlep_combos)
        if n_tot_combos == 0:
            # No chance to make quartets.
            return []
            
        if verbose:
            print(f"  Num of {cr} quartets to analyze: {n_tot_combos}")
        # List to hold valid ZZ cands that pass OS Method sel.
        ls_valid_zz_cand_OS = []
        for n_quartet, quart in enumerate(fourlep_combos):
            if verbose:
                print_header_message(f"Analyzing quartet #{n_quartet}")
                lep_ndcs = [mylep.ndx_lepvec for mylep in quart]
                print(f"  Lepton indices: {lep_ndcs}")
            # For this quartet, use OS Method logic to pick best ZZ cand.
            ls_zzcand = get_ZZcands_from_myleps_OSmethod(
                    quart,
                    verbose=verbose, explain_skipevent=explain_skipevent,
                    smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel,
                    run=run, lumi=lumi, event=event, entry=entry
                    )

            if len(ls_zzcand) == 0:
                # No good ZZ candidate found.
                continue

            ls_valid_zz_cand_OS.append(
                ls_zzcand[0]  # Best ZZ cand.
                )
        return ls_valid_zz_cand_OS