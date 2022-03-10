"""Print info comparing the 3P1F/2P2F events between 2 NTuples.
#=============================================================================
# Recommended syntax (to store output in txt file):
#   `python this_script.py > some_output.txt`
# Author: Jake Rosenzweig
# Created: 2022-02-28
# Updated: 2022-03-09
#=============================================================================
"""
from ROOT import TFile
#=== Local imports. ===#
from Utils_Python.printing import announce, print_periodic_evtnum
from constants.finalstates import dct_finalstates_int2str
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_comparison import make_ls_evtIDs_OSmethod
from sidequests.data.filepaths import (
    rb_skim_UL2017_data, rb_skim_UL2018_data,
    rb_skim_UL2017_data_zz, rb_skim_UL2018_data_zz,
    data_2017_UL_ge3lepskim, data_2018_UL_ge3lepskim,
    data_2017_UL_ge4lepskim, data_2018_UL_ge4lepskim
    )

input_info1 = (
    "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_Data.root",
    "passedEvents",
    "jake"
    )
input_info2 = (
    # "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/osmethod_UL_nomatchlepHindex_2016_Data.root",
    "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/osmethod_UL_nomatchlepHindex_analyzemass4llt0_2016_Data.root",
    # "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/osmethod_UL_nomatchlepHindex_multiquartets_2016_Data.root",
    "passedEvents",
    "jake"
    )

year = 2016
ls_finalstates = [1, 2, 3, 4]  # Use `[5]` to get all final states in one go.
m4l_lim = (105, 140)
keep_2P2F = 1   # Only select 2P2F-type events.
keep_3P1F = 0  # Only 3P1F.
print_every = 10_000

def print_commonanduniqueevts_jakvsbbf(
    input_info1, input_info2,
    keep_2P2F, keep_3P1F,
    year,
    m4l_lim=(70, 1000),
    ls_finalstates=[5],
    print_every=500000
    ):
    """Print common and unique event info between files 1 and 2.
    
    input_info (3-tuple of str):
        ('file_path', 'tree_path', 'framework')

        'framework' can be one of: 'jake', 'bbf'
    """
    infile1, tree_path1, fw1 = input_info1
    infile2, tree_path2, fw2 = input_info2

    assert all(str(year) in x for x in (infile1, infile2))

    if ls_finalstates == [5]:
        fs_str = "4mu, 4e, 2e2mu, 2mu2e"
    else:
        fs_str = ', '.join(
            [dct_finalstates_int2str[fs] for fs in ls_finalstates]
            )
    
    if keep_2P2F and keep_3P1F:
        cr_str = '2P2F and 3P1F'
    elif keep_2P2F:
        cr_str = '2P2F'
    elif keep_3P1F:
        cr_str = '3P1F'

    print(
        f"Comparing events in files [1] and [2]:\n"
        f"  [1] {infile1}\n"
        f"  [2] {infile2}\n"
        f"  Analyzing year: {year}\n"
        f"  Analyzing final states: {fs_str}\n"
        f"  Analyzing CR{'s' if 'and' in cr_str else ''}: {cr_str}"
    )

    tf1 = TFile.Open(infile1, 'read')
    tree1 = tf1.Get(tree_path1)
    tf2 = TFile.Open(infile2, 'read')
    tree2 = tf2.Get(tree_path2)

    print(f"Looping over final states and comparing events...")
    for fs in ls_finalstates:

        ls_collection = []
        for t, fw in zip(
            [tree1, tree2],
            [fw1, fw2]
            ):

            msg = (
                f"Framework = {fw}, "
                f"fs = {dct_finalstates_int2str[fs]}, "
                f"CR = {cr_str}, "
                f"{m4l_lim[0]} < mass4l < {m4l_lim[1]} GeV"
                )
            announce(msg=msg, pad_char="-", n_center_pad_chars=3)

            ls_evtID = make_ls_evtIDs_OSmethod(
                tree=t,
                framework=fw,
                m4l_lim=m4l_lim,
                keep_2P2F=keep_2P2F,
                keep_3P1F=keep_3P1F,
                fs=fs,
                print_every=print_every,
                )

            ls_collection.extend(
                (ls_evtID,)
                )

        # Unpack each list.
        ls_tup_evtIDs_1, ls_tup_evtIDs_2 = ls_collection

        # Load FileRunLumiEvent comparers.
        frle_1 = FileRunLumiEvent(ls_tup_evtid=ls_tup_evtIDs_1, name='File 1')
        frle_2 = FileRunLumiEvent(ls_tup_evtid=ls_tup_evtIDs_2, name='File 2')

        # Do event comparisons.
        frle_1.analyze_evtids(frle_2, event_type="common", print_evts=False)
        frle_1.analyze_evtids(frle_2, event_type="unique", print_evts=True)
        frle_2.analyze_evtids(frle_1, event_type="unique", print_evts=True)
        frle_1.show_duplicates()
        frle_2.show_duplicates()

if __name__ == '__main__':

    print_commonanduniqueevts_jakvsbbf(
        input_info1=input_info1,
        input_info2=input_info2,
        keep_2P2F=keep_2P2F,
        keep_3P1F=keep_3P1F,
        year=year,
        m4l_lim=m4l_lim,
        ls_finalstates=ls_finalstates,
        print_every=print_every,
        )