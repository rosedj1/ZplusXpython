"""Make pickles of evtID lists for 3P1F and 2P2F events (DATA ONLY)."""
import os
from ROOT import TFile
from argparse import ArgumentParser
# Local imports.
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from Utils_Python.Utils_Files import (
    save_to_pkl, open_pkl, check_overwrite
    )
from Utils_Python.printing import print_periodic_evtnum

ntuple_style_bbf = 0

infile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_mass4lgt0_2018_Data.root"
# infile = infile_filippo_data_2018_fromhpg
outfile_basename = "jake_evtids"
outdir = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/test/"

def make_evtid_lists(tree, print_every, break_at_evt, ntuple_style_bbf):
    """Return 2 filled lists of event IDs: 2P2F and 3P1F"""

    ls_evtids_2p2f = []
    ls_evtids_3p1f = []

    n_2p2f = 0
    n_3p1f = 0
    n_tot = tree.GetEntries()
    print(f"Starting event loop: n_tot = {n_tot}")
    for evt_num in range(n_tot):
        if evt_num == break_at_evt:
            break

        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        tree.GetEntry(evt_num)
        run = tree.Run
        lumi = tree.LumiSect
        event = tree.Event

        evt_id = (run, lumi, event,)

        if ntuple_style_bbf:
            n_failed_leps = tree.nZXCRFailedLeptons
            if n_failed_leps == 2:
                # Get 2P2F evt IDs.
                ls_evtids_2p2f.extend((evt_id,))
                n_2p2f += 1
            elif n_failed_leps == 1:
                # Get 3P1F evt IDs.
                ls_evtids_3p1f.extend((evt_id,))
                n_3p1f += 1
        else:
            # Jake-style NTuple. Contains branches like is3P1F.
            if tree.isMCzz:
                continue
            if tree.is2P2F:
                ls_evtids_2p2f.extend((evt_id,))
                n_2p2f += 1
            elif tree.is3P1F:
                ls_evtids_3p1f.extend((evt_id,))
                n_3p1f += 1
    print(f"n_2p2f={n_2p2f}, n_3p1f={n_3p1f}")
    return (ls_evtids_2p2f, ls_evtids_3p1f)

def make_pkls():
    """Write a pickle of 2P2F event IDs and another of 3P1F event IDs."""
    parser = ArgumentParser()
    parser.add_argument(
        '-x', '--overwrite',
        dest="killthefile", action="store_true",
        help="Overwrite output file. Default is False."
        )
    parser.add_argument(
        '-p', '--printevery',
        dest="printevery", type=int,
        help="Print event info every `printevery` number of events."
        )
    parser.add_argument(
        '-b', '--breakat',
        dest="breakat", type=int,
        help="Break before running over event number `breakat`."
        )
    args = parser.parse_args()
    overwrite = args.killthefile
    print_every = args.printevery
    break_at_evt = args.breakat
    outpkl_2p2f = os.path.join(outdir, f"{outfile_basename}_2p2f.pkl")
    outpkl_3p1f = outpkl_2p2f.replace("2p2f", "3p1f")
    check_overwrite(outpkl_2p2f, outpkl_3p1f, overwrite=overwrite)

    tf = TFile.Open(infile, "read")
    tree = tf.Get("passedEvents")

    ls_evtids_2p2f, ls_evtids_3p1f = make_evtid_lists(
        tree,
        print_every,
        break_at_evt,
        ntuple_style_bbf
        )

    save_to_pkl(ls_evtids_2p2f, outpkl_2p2f, overwrite=overwrite)
    save_to_pkl(ls_evtids_3p1f, outpkl_3p1f, overwrite=overwrite)

if __name__ == '__main__':
    make_pkls()
