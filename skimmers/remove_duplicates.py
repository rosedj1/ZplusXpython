import sys
from ROOT import TFile
# sys.path.append("/blue/avery/rosedj1/")
from Utils_Python.Utils_Files import check_overwrite

infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/Data2018_Duplicates.root"
outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates_comparesetwithstrandtup_deleteme.root"
path_to_tree = "passedEvents"
overwrite = 1
verbose = 1

def eliminate_duplicates(old_tree, verbose=False):
    """Return a new TTree that contains no duplicates within `old_tree`.

    A duplicate is any entry with exactly the same Run, Lumi, Event number.
    
    Args:
        old_tree (ROOT.TTree): Tree to be cloned and trimmed.
    """
    newtree = old_tree.CloneTree(0)  # Clone 0 entries.
    print(f"TTree cloned. Filled with {newtree.GetEntries()} entries.")

    n_tot = old_tree.GetEntries()
    num_duplicates = 0
    event_set = set()
    for ct, evt in enumerate(old_tree):
        if verbose:
            if (ct % 100000) == 0:
                print(
                    f"Event {ct}/{n_tot}, (progress: {(ct/n_tot * 100):.1f}%). "
                    f"Duplicates found = {num_duplicates}"
                    )

        key = (evt.Run, evt.LumiSect, evt.Event, )

        if key in event_set:
            num_duplicates += 1
            continue
        else:
            newtree.Fill()
            event_set.add(key)
    if verbose:
        print(
            f"Number of duplicates found: {num_duplicates}, "
            f"({num_duplicates/n_tot * 100:.1f}% of original entries)"
            )
    return newtree

def main(infile, path_to_tree, outfile, overwrite=False):
    """Write a new root file with a cloned TTree, but with no duplicates.
    
    The duplicates are indexed by: (Run, LumiSect, Event).
    
    Args:
        infile (str): Absolute path of input root file.
        path_to_tree (str): Path inside root file to `Get()` the TTree.
        outfile (str): Absolute path of output root file.
        overwrite (bool, optional): Overwrite new file. Defaults to False.
    """
    f = TFile(infile)
    old_tree = f.Get(path_to_tree)
    print(f"File opened:\n{infile}")

    check_overwrite(outfile, overwrite=overwrite)
    newfile = TFile(outfile, "recreate")

    newtree = eliminate_duplicates(old_tree, verbose=verbose)

    newtree.Write()
    print(f"New TTree written to file:\n{outfile}")
    newfile.Close()

if __name__ == '__main__':
    main(infile, path_to_tree, outfile, overwrite=overwrite)