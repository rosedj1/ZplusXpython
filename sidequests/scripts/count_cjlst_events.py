import sys
import ROOT

from sidequests.data.filepaths import infile_matteo_data2018_fromhpg
from sidequests.classes.cjlstflag import CjlstFlag
from Utils_Python.printing import print_periodic_evtnum
from Utils_Python.printing import pretty_print_dict

start_at = 0
break_at = -1
print_every = 10000

m4l_min = 105
m4l_max = 140

def convert_to_bbf_fs(Z1Flav, Z2Flav):
    """Return the finalState in BBF FW based on CJLST Z flavors.
    
    1 : 4mu
    2 : 4e
    3 : 2e2mu
    4 : 2mu2e
    """
    Z1Flav = -1 * abs(Z1Flav)
    Z2Flav = -1 * abs(Z2Flav)
    if (Z1Flav == -169) and (Z2Flav == -169):
        # 4mu.
        return 1
    elif (Z1Flav == -169) and (Z2Flav == -121):
        # 2mu2e.
        return 4
    elif (Z1Flav == -121) and (Z2Flav == -169):
        # 2e2mu.
        return 3
    elif (Z1Flav == -121) and (Z2Flav == -121):
        # 4e.
        return 2
    else:
        raise ValueError(
            f"Flavors unknown: Z1Flav={Z1Flav}, Z2Flav={Z2Flav}"
            )

if __name__ == '__main__':
    f = ROOT.TFile.Open(infile_matteo_data2018_fromhpg, "read")
    t = f.Get("CRZLLTree/candTree")

    d_fs_counts = {}
    for cr in ('2P2F', '3P1F'):
        d_fs_counts[cr] = {}
        for fs in (1, 2, 3, 4):
            d_fs_counts[cr][fs] = 0

    n_tot = t.GetEntries()
    for evt_num in range(start_at, n_tot):
        t.GetEntry(evt_num)

        if evt_num == break_at:
            break

        print_periodic_evtnum(evt_num, n_tot, print_every=print_every)

        if (t.ZZMass < m4l_min) or (t.ZZMass > m4l_max):
            continue

        bbf_fs = convert_to_bbf_fs(t.Z1Flav, t.Z2Flav)

        # if (bbf_fs != 1) and (bbf_fs != 3) and (bbf_fs != 4):
        #     print(bbf_fs)
        #     break
        if t.CRflag == CjlstFlag.CR3P1F.value:
            # print(f"3P1F Event: {evt_num}")
            # print(f"Z1Flav: {t.Z1Flav}")
            # print(f"Z2Flav: {t.Z2Flav}")
            # break
            d_fs_counts['3P1F'][bbf_fs] += 1
        elif t.CRflag == CjlstFlag.CR2P2F.value:
            d_fs_counts['2P2F'][bbf_fs] += 1

    print(f"Mass window: {m4l_min} < massZZ < {m4l_max}")
    pretty_print_dict(d_fs_counts)
    print(f"sum of 3P1F: {sum(d_fs_counts['3P1F'].values())}")
    print(f"sum of 2P2F: {sum(d_fs_counts['2P2F'].values())}")
