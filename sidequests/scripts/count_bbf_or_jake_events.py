"""Count the 2P2F and 3P1F events in each final state. Print out results.
#=============================================================================
# Syntax: `python <script>.py`
# Notes: Specialized for xBF NTuples, made with the UFHZZAnalyzer.
# Author: Jake Rosenzweig
# Created: 2022-02-23
#=============================================================================
"""
from argparse import ArgumentParser
from ROOT import TFile
# Local imports.
from Utils_Python.printing import (
    print_header_message, print_periodic_evtnum,
    pretty_print_dict
    )

# For collecting 3P1F/2P2F events in Filippo's file.
tree_path = 'passedEvents'
m4l_lim = (105, 140)

def make_cr_fs_dct():
    d = {}
    for n_fail_leps in (1, 2):
        key = f"nZXCRFailedLeptons={n_fail_leps}"
        d[key] = {f"finalState={n}": 0 for n in (1, 2, 3, 4)}
    return d

def count_xbf_events(infile, tree_path, m4l_lim):

    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    dct_cr_fs = make_cr_fs_dct()
    dct_cr_fs_m4l_window = make_cr_fs_dct()
    dct_cr_fs_m4lgt70 = make_cr_fs_dct()

    f = TFile.Open(infile, "read")
    t = f.Get(tree_path)
    n_tot = t.GetEntries()

    print(
        f"Counting the number of events in the 2P2F and 3P1F CRs in file:\n"
        f"{infile}"
        )
    for evt_num in range(n_tot):
        # if evt_num == 100000:
        #     break
        print_periodic_evtnum(evt_num, n_tot, print_every=500000)

        t.GetEntry(evt_num)

        if not t.passedZXCRSelection:
            continue

        in_m4l_window = ((m4l_min < t.mass4l) and (t.mass4l < m4l_max))
        is_m4lgt70 = (t.mass4l > 70)

        # Prep keys.
        fs = t.finalState
        key1 = f"nZXCRFailedLeptons={t.nZXCRFailedLeptons}"
        key2 = f"finalState={t.finalState}"

        dct_cr_fs[key1][key2] += 1
        if in_m4l_window:
            dct_cr_fs_m4l_window[key1][key2] += 1
        if is_m4lgt70:
            dct_cr_fs_m4lgt70[key1][key2] += 1

    print("All events that passedZXCRSelection:")
    pretty_print_dict(dct_cr_fs)

    print(f"Just the events with mass4l > 70 GeV:")
    pretty_print_dict(dct_cr_fs_m4lgt70)

    print(f"Just the events within mass4l window: {m4l_lim}")
    pretty_print_dict(dct_cr_fs_m4l_window)

if __name__ == '__main__':
    argpar = ArgumentParser()
    argpar.add_argument('-i', dest='infile')
    args = argpar.parse_args()
    
    count_xbf_events(args.infile, tree_path, m4l_lim)
