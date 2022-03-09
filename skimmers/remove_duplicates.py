"""Write a new root file with a copy of a TTree without duplicates.
# ==============================================================================
# Syntax:  python this_script.py [-x] [-v]
#   -x (overwrite)
#   -v (verbose)
# Author:  Jake Rosenzweig
# Created: 2021-Oct
# Updated: 2022-03-02
# Comment:
#   This script is faster than the C++ version!
#   Can submit to SLURM using: skimmers/remove_duplicates.sbatch
# ==============================================================================
"""
from argparse import ArgumentParser
from ROOT import TFile
from Utils_Python.Utils_Files import check_overwrite
from sidequests.data.filepaths import data_2016_UL_preVFP

infile = data_2016_UL_preVFP
outfile = infile.replace(".root", "_noDuplicates.root") #"/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates_comparesetwithstrandtup_deleteme.root"
path_to_tree = "passedEvents"
start_at = 0  # First event is indexed at 0.
end_at = -1  # Use -1 to process all events.

def make_prefilled_event_set(tree, start_at, verbose=False):
    """Return a set of 3-tuples from entry0 -> `start_at` (exclusive).

    Args:
        tree (ROOT.TTree): Contains events indexed by (Run, Lumi, Event).
        start_at (int): Which entry of TTree to begin checking for
            duplicates.
        verbose (bool, optional): Print debug info. Defaults to False.

    Returns:
        set: A set of 3-tuples.
    """
    end_at = start_at - 1
    if verbose:
        print(
            f"Prefilling eventID set within entry range:\n"
            f"0 -> {end_at} (inclusive)"
            )
    prefilled_set = set()
    for ct in range(0, start_at):
        print_every = round(end_at / 10.0)
        if (ct % print_every) == 0:
            if verbose:
                print(f"{ct}/{(end_at)}, (progress: {(ct/end_at * 100):.1f}%).")
        tree.GetEntry(ct)
        key = (tree.Run, tree.LumiSect, tree.Event, )
        prefilled_set.add(key)
    if verbose:
        print(f"Prefilling set done.")
    err_msg = f"Duplicate found before entry=`start_at`={start_at}!"
    assert len(prefilled_set) == start_at, err_msg
    return prefilled_set

def eliminate_duplicates(tree, start_at=0, end_at=-1, verbose=False):
    """Return a new TTree that contains no duplicates within `tree`.

    A duplicate is any entry with exactly the same Run, Lumi, Event number.
    
    NOTE:
      - You must open up a new TFile BEFORE calling this function.
        This function creates a new TTree which must live in a new TFile.
      - You can start looking for duplicates at entry `start_at`.
        In this case, the TTree is cloned from event 0 up to `start_at`
        without looking for duplicates. However, these eventIDs
        (Run, LumiSect, Event) are stored in `unique_event_set`.

    Args:
        tree (ROOT.TTree): Tree to be cloned and trimmed.
    """
    if end_at > 0:
        assert end_at > start_at

    if start_at == 0:
        unique_event_set = set()
        newtree = tree.CloneTree(0)  # Clone 0 entries.
    else:
        unique_event_set = make_prefilled_event_set(tree, start_at=start_at, verbose=verbose)
        newtree = tree.CloneTree(start_at)
    print(f"TTree cloned with {newtree.GetEntries()} entries.")

    n_tot = tree.GetEntries()
    num_duplicates = 0
    ct = start_at
    if end_at == -1:
        end_at = tree.GetEntries()
    for ct in range(start_at, end_at):
        if verbose:
            if (ct % 100000) == 0:
                print(
                    f"Event {ct}/{n_tot}, (progress: {(ct/n_tot * 100):.1f}%). "
                    f"Duplicates found = {num_duplicates}"
                    )

        tree.GetEntry(ct)
        key = (tree.Run, tree.LumiSect, tree.Event, )

        if key in unique_event_set:
            num_duplicates += 1
            continue
        else:
            newtree.Fill()
            unique_event_set.add(key)
        ct += 1
        if ct == end_at:
            break
        
    print(
        f"Number of duplicates found: {num_duplicates}, "
        f"({num_duplicates/n_tot * 100:.1f}% of original entries)"
        )

    return newtree

def main(
    infile, path_to_tree, outfile,
    start_at=0, end_at=-1
    ):
    """Write a new root file with a cloned TTree, but with no duplicates.
    
    The duplicates are indexed by: (Run, LumiSect, Event).
    
    Args:
        infile (str): Absolute path of input root file.
        path_to_tree (str): Path inside root file to `Get()` the TTree.
        outfile (str): Absolute path of output root file.
    """
    argpar = ArgumentParser()
    argpar.add_argument(
        '-x', '--overwrite',
        dest="overwrite", action="store_true",
        help="Overwrite output file. Default is False."
        )
    argpar.add_argument(
        '-v', '--verbose',
        dest="verbose", action="store_true",
        help="Overwrite output file. Default is False."
        )
    args = argpar.parse_args()
    overwrite = args.overwrite
    verbose = args.verbose

    f = TFile(infile)
    old_tree = f.Get(path_to_tree)
    print(f"Input file opened:\n{infile}")

    check_overwrite(outfile, overwrite=overwrite)
    print(f"Creating new file:\n{outfile}")
    newfile = TFile(outfile, "recreate")

    newtree = eliminate_duplicates(
                old_tree, start_at=start_at, end_at=end_at, verbose=verbose
                )

    newtree.Write()
    print(f"New TTree written to file:\n{outfile}")
    newfile.Close()

if __name__ == '__main__':
    main(infile, path_to_tree, outfile, start_at=start_at, end_at=end_at)