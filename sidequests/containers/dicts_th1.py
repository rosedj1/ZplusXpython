# from sidequests.containers.hists_th1 import (
#     h1_data_2p2f_m4l,
#     h1_data_3p1f_m4l,
#     h1_data_2p2fpred_m4l,
#     h1_data_3p1fpred_m4l
# )
def make_fs_histdict_from_clone(h_to_clone):
    """Return a dict of hists for finalStates 1->4 made from a hist clone.
    
    Keys are finalState (int).
    """
    d = {}
    for fs in (1, 2, 3, 4):
        h = h_to_clone.Clone()
        name = f"{h.GetName()}_fs{fs}"
        h.SetName(name)
        d[fs] = h
    return d

def make_dct_hists_all_crs(
    h1_2p2f_m4l,
    h1_3p1f_m4l,
    h1_2p2fpred_m4l,
    h1_3p1fpred_m4l,
    ):
    """Return tuple of dicts, filled with empty hists for OS Method CRs.

    Args:
        h1_2p2f_m4l (ROOT.TH1): CR 2P2F to be filled with mass4l. Raw number of events.
        h1_3p1f_m4l (ROOT.TH1): CR 3P1F to be filled with mass4l. Raw number of events.
        h1_2p2fpred_m4l (ROOT.TH1): CR 2P2F to be filled with predicted estimation using FRs.
        h1_3p1fpred_m4l (ROOT.TH1): CR 2P2F to be filled with predicted estimation using FRs.
    """
    # Make dicts of hists to sort by final state.
    d_2p2f_fs_hists = make_fs_histdict_from_clone(h1_2p2f_m4l)  # Raw Data events.
    d_3p1f_fs_hists = make_fs_histdict_from_clone(h1_3p1f_m4l)  # Raw Data events.
    d_2p2fpred_fs_hists = make_fs_histdict_from_clone(h1_2p2fpred_m4l)  # Predicted using FRs.
    d_3p1fpred_fs_hists = make_fs_histdict_from_clone(h1_3p1fpred_m4l)  # Predicted using FRs.
    return (
        d_2p2f_fs_hists,
        d_3p1f_fs_hists,
        d_2p2fpred_fs_hists,
        d_3p1fpred_fs_hists,
        )

def make_dct_hists_all_crs_data(
    h1_data_2p2f_m4l,
    h1_data_3p1f_m4l,
    h1_data_2p2fpred_m4l,
    h1_data_3p1fpred_m4l,
    h1_data_2p2fin3p1f_m4l,
    ):
    """Return tuple of dicts, filled with empty hists for OS Method CRs.

    Args:
        h1_data_2p2f_m4l (ROOT.TH1): CR 2P2F to be filled with mass4l.
        h1_data_3p1f_m4l (ROOT.TH1): CR 3P1F to be filled with mass4l.
        h1_data_2p2fpred_m4l (ROOT.TH1): CR 2P2F to be filled with predicted estimation using FRs.
        h1_data_3p1fpred_m4l (ROOT.TH1): CR 2P2F to be filled with predicted estimation using FRs.
        h1_data_2p2fin3p1f_m4l (ROOT.TH1): Contribution of 2P2F to 3P1F using FRs.
    """
    # Make dicts of hists to sort by final state.
    tup_of_dcts_of_hists = make_dct_hists_all_crs(
        h1_data_2p2f_m4l,      # Raw Data events.
        h1_data_3p1f_m4l,      # Raw Data events.
        h1_data_2p2fpred_m4l,  # Predicted using FRs.
        h1_data_3p1fpred_m4l,  # Predicted using FRs.
        )
    ls = list(tup_of_dcts_of_hists)
    d = make_fs_histdict_from_clone(h1_data_2p2fin3p1f_m4l)
    ls.append(d)
    # Convert back to tuple.
    return tuple(ls)
