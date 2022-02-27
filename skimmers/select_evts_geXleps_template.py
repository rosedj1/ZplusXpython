#=============================================================================
import sys
from ROOT import TFile
#=== Local imports. ===#
from Utils_Python.Utils_Files import check_overwrite
from Utils_Python.printing import print_periodic_evtnum

infile = 'INFILE'
outfile = 'OUTFILE'
tree_path = 'TREE_PATH'

keep_ge_leps = N_LEPS_SKIM  # Save events with at least this many leptons per event.
break_at = BREAK_AT
overwrite = OVERWRITE
print_every = PRINT_EVERY

def make_newtree(tree, n_keep, break_at=-1, print_every=500000):
    """Return a TTree selecting events with `n_keep` or more leptons."""

    n_tot = tree.GetEntries()
    print(f"number of entries in original TTree: {n_tot}")

    new_tree = tree.CloneTree(0, 'fast')

    print(f"Selecting events with len(lep_pt) >= {n_keep}.")
    for evt_num in range(n_tot):

        if evt_num == break_at:
            break
        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        tree.GetEntry(evt_num)

        # Event selection.
        if len(tree.lep_pt) >= n_keep:
            new_tree.Fill()

    return new_tree

def select_evts_ge3leps(
    infile, tree_path, outfile,
    keep_ge_leps=3, break_at=-1, print_every=500000,
    overwrite=False
    ):

    check_overwrite(outfile, overwrite=overwrite)

    f = TFile.Open(infile, 'read')
    tree = f.Get(tree_path)

    print(f"Creating new file:\n{outfile}")
    new_tf = TFile.Open(outfile, 'recreate')
    new_tree = make_newtree(
        tree, n_keep=keep_ge_leps, break_at=break_at,
        print_every=print_every
        )

    n_tot = tree.GetEntries()
    n_new_evts = new_tree.GetEntries()
    perc = (n_new_evts / float(n_tot)) * 100.0
    print(
        f"Number of events selected with >= {keep_ge_leps} leptons: "
        f"{n_new_evts} ({perc:.2f}%)"
        )
    print("Saving TTree to new file.")
    new_tree.Write()

if __name__ == '__main__':

    select_evts_ge3leps(
        infile=infile, tree_path=tree_path, outfile=outfile, 
        keep_ge_leps=keep_ge_leps, break_at=break_at, print_every=print_every,
        overwrite=overwrite
        )