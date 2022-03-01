from ROOT import TFile
#=== Local imports. ===#
from Utils_Python.printing import print_header_message, print_periodic_evtnum
from constants.finalstates import dct_finalstates_int2str
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_comparison import make_ls_evtIDs_OSmethod
from sidequests.data.filepaths import (
    rb_skim_UL2017_data, rb_skim_UL2018_data,
    rb_skim_UL2017_data_zz, rb_skim_UL2018_data_zz,
    data_2017_UL_ge3lepskim, data_2018_UL_ge3lepskim,
    data_2017_UL_ge4lepskim, data_2018_UL_ge4lepskim
    )

infile_jak = rb_skim_UL2017_data
infile_bbf = data_2017_UL_ge4lepskim

tree_path_jak = 'passedEvents'
tree_path_bbf = 'passedEvents'

ls_finalstates = [1, 2, 3, 4]
m4l_lim = (105, 140)
keep_2P2F = False
keep_3P1F = True
print_every = 20000

def print_commonanduniqueevts_jakvsbbf(
    infile_jak, tree_path_jak,
    infile_bbf, tree_path_bbf,
    keep_2P2F, keep_3P1F,
    m4l_lim=(70, 1000),
    ls_finalstates=[5],
    print_every=500000
    ):
    """Print common and unique event info between Jake and xBF Ntuples."""

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
        f"  [1] {infile_jak}\n"
        f"  [2] {infile_bbf}\n"
        f"  Will analyze final states: {fs_str}\n"
        f"  Will analyze CR{'s' if 'and' in cr_str else ''}: {cr_str}"
    )

    tf_jak = TFile.Open(infile_jak, 'read')
    tree_jak = tf_jak.Get(tree_path_jak)
    tf_bbf = TFile.Open(infile_bbf, 'read')
    tree_bbf = tf_bbf.Get(tree_path_bbf)

    print(f"Looping over final states and comparing events...")
    for fs in ls_finalstates:

        ls_collection = []
        for t, fw in zip(
            [tree_jak, tree_bbf],
            ["jake", "bbf"]
            ):

            msg = (
                f"Framework = {fw}, "
                f"fs = {dct_finalstates_int2str[fs]}, "
                f"CR = {cr_str}, "
                f"{m4l_lim[0]} < mass4l < {m4l_lim[1]} GeV"
                )
            print_header_message(msg=msg, pad_char="-", n_center_pad_chars=3)

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
        ls_tup_evtIDs_jak, ls_tup_evtIDs_bbf = ls_collection

        # Load FileRunLumiEvent comparers.
        frle_jak = FileRunLumiEvent(ls_tup_evtid=ls_tup_evtIDs_jak)
        frle_bbf = FileRunLumiEvent(ls_tup_evtid=ls_tup_evtIDs_bbf)

        # Do event comparisons.
        frle_jak.analyze_evtids(frle_bbf, event_type="common", print_evts=False)
        frle_jak.analyze_evtids(frle_bbf, event_type="unique", print_evts=True)
        frle_bbf.analyze_evtids(frle_jak, event_type="unique", print_evts=True)

if __name__ == '__main__':

    print_commonanduniqueevts_jakvsbbf(
        infile_jak=infile_jak,
        tree_path_jak=tree_path_jak,
        infile_bbf=infile_bbf,
        tree_path_bbf=tree_path_bbf,
        keep_2P2F=keep_2P2F,
        keep_3P1F=keep_3P1F,
        m4l_lim=m4l_lim,
        ls_finalstates=ls_finalstates,
        print_every=print_every,
        )