"""Count the 2P2F and 3P1F events in each final state. Print out results.
#=============================================================================
# Syntax: `python <script>.py -i infile -n ntuple`
#   infile (file path)
#   ntuple ('jake', 'xbf')
# Author: Jake Rosenzweig
# Created: 2022-02-23
# Updated: 2022-03-08
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

# def make_cr_fs_dct():
#     d = {}
#     for n_fail_leps in (1, 2):
#         key = f"nZXCRFailedLeptons={n_fail_leps}"
#         d[key] = {f"finalState={n}": 0 for n in (1, 2, 3, 4)}
#     return d

def count_xbf_events(t, m4l_lim):
    """Count 2P2F/3P1F events in xBF-type NTuple.
    
    Uses branches:
        - passedZXCRSelection
        - nZXCRFailedLeptons
    """
    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    for n_fail in (1, 2): 
        for fs in (1, 2, 3, 4):
            cuts = (
                f"passedZXCRSelection && "
                f"{m4l_min} < mass4l && mass4l < {m4l_max} && "
                f"nZXCRFailedLeptons == {n_fail} && finalState == {fs}"
                )
            print(f"{cuts}: {t.GetEntries(cuts)}")

    # dct_cr_fs = make_cr_fs_dct()
    # dct_cr_fs_m4l_window = make_cr_fs_dct()
    # dct_cr_fs_m4lgt70 = make_cr_fs_dct()

    # f = TFile.Open(infile, "read")
    # t = f.Get(tree_path)
    # n_tot = t.GetEntries()

    # print(
    #     f"Counting the number of events in the 2P2F and 3P1F CRs in file:\n"
    #     f"{infile}"
    #     )
    # for evt_num in range(n_tot):
    #     # if evt_num == 100000:
    #     #     break
    #     print_periodic_evtnum(evt_num, n_tot, print_every=500000)

    #     t.GetEntry(evt_num)

    #     if not t.passedZXCRSelection:
    #         continue

    #     in_m4l_window = ((m4l_min < t.mass4l) and (t.mass4l < m4l_max))
    #     is_m4lgt70 = (t.mass4l > 70)

    #     # Prep keys.
    #     fs = t.finalState
    #     key1 = f"nZXCRFailedLeptons={t.nZXCRFailedLeptons}"
    #     key2 = f"finalState={t.finalState}"

    #     dct_cr_fs[key1][key2] += 1
    #     if in_m4l_window:
    #         dct_cr_fs_m4l_window[key1][key2] += 1
    #     if is_m4lgt70:
    #         dct_cr_fs_m4lgt70[key1][key2] += 1

    # print("All events that passedZXCRSelection:")
    # pretty_print_dict(dct_cr_fs)

    # print(f"Just events with mass4l > 70 GeV:")
    # pretty_print_dict(dct_cr_fs_m4lgt70)

    # print(f"Just events within mass4l window: {m4l_lim}")
    # pretty_print_dict(dct_cr_fs_m4l_window)

def count_multiquart_events(t, m4l_lim):
    """Count 2P2F/3P1F events in Multi-quartet-type NTuple.
    
    Uses branches:
        - is2P2F / is3P1F
    """
    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    for cr in ('is3P1F', 'is2P2F'): 
        for fs in (1, 2, 3, 4):
            cuts = (
                f'{m4l_min} < mass4l && mass4l < {m4l_max} && '
                f'{cr} && finalState == {fs}'
                )
            print(f"{cuts}: {t.GetEntries(cuts)}")

def count_events(tree_path, m4l_lim):
    """Print info about 2P2F/3P1F (OS Method) events."""
    argpar = ArgumentParser()
    argpar.add_argument('-i', dest='infile')
    argpar.add_argument('-n', dest='ntuple')
    args = argpar.parse_args()
    ntup = args.ntuple.lower()
    infile = args.infile

    f = TFile.Open(infile, "read")
    t = f.Get(tree_path)
    if ntup == 'jake':
        count_multiquart_events(t, m4l_lim)
    elif ntup in ('xbf', 'bbf'):
        count_xbf_events(t, m4l_lim)

if __name__ == '__main__':
    count_events(tree_path, m4l_lim)
