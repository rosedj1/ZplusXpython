import numpy as np
from array import array
from ROOT import TFile, Math
# Local imports.
from classes.zzpair import ZZPair
from classes.myzboson import MyZboson
from classes.mylepton import make_filled_mylep_ls
from Utils_Python.printing import print_periodic_evtnum
from sidequests.funcs.evt_comparison import print_evt_info_bbf

break_at_evt = -1

infile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_2018_Data_ZZ.root"
tf = TFile.Open(infile, "read")
tree = tf.Get("passedEvents")

new_file = infile.replace(".root", "_updatedmass4lvals.root")
print(f"Opening new root file:\n{new_file}")
nf = TFile.Open(new_file, "recreate")

print("Cloning original tree.")
new_tree = tree.CloneTree(break_at_evt)  # All events.
print("Done.")

ptr_mass4l = array('f', [0.])
ptr_mass4l_vtxFSR_BS = array('f', [0.])

new_tree.SetBranchAddress("mass4l", ptr_mass4l)
new_tree.SetBranchAddress("mass4l_vtxFSR_BS", ptr_mass4l_vtxFSR_BS)

# tree.Show(4)
print(
    f"Number of weird events = "
    # f"{tree.GetEntries('(Sum$(lep_RedBkgindex) > 6) && (Length$(lep_pt) == 4)')}"
    f"{tree.GetEntries('(Sum$(lep_RedBkgindex) >= 0)')}"
    )

# DEBUGGING:
# for n in range(8):
#     num_evts = tree.GetEntries(f'(Sum$(lep_RedBkgindex) >= {n})')
#     print(f"Num events Sum$(lep_RedBkgindex) >= n... n = {n}, num_evts = {num_evts}")
n_indexerrors = 0
n_weird_evts = 0

n_tot = tree.GetEntries()
print(f"n_tot = {n_tot}")
for evt_num in range(n_tot):
    if evt_num == break_at_evt:
        break
    print_periodic_evtnum(evt_num, n_tot, print_every=50000)
    # if evt_num == 4:
    #     print(list(tree.lep_id))
    #     print(list(tree.lep_tightId))
    #     print(list(tree.lep_pt))
    #     print(list(tree.lepFSR_pt))
    #     print(list(tree.vtxLepFSR_BS_pt))

    # try:

    tree.GetEntry(evt_num)

    # ls_all_myleps = np.array(make_filled_mylep_ls(tree))
    # lep_RedBkgindex = list(tree.lep_RedBkgindex)
    # myleps = ls_all_myleps[lep_RedBkgindex]

    # zz = ZZPair(
    #     MyZboson(myleps[0], myleps[1]),
    #     MyZboson(myleps[2], myleps[3]),
    # )
    # # print(f"zz.get_m4l() = {zz.get_m4l()}")

    # ls_lepvec_lepFSR = []
    # ls_lepvec_vtxLepFSR_BS = []

    # zz_lepFSR = Math.PtEtaPhiMVector(0, 0, 0, 0)
    # zz_vtxLepFSR_BS = Math.PtEtaPhiMVector(0, 0, 0, 0)
    # for idx in tree.lep_RedBkgindex:
    #     # lepvec_lepFSR = Math.PtEtaPhiMVector(
    #     zz_lepFSR += Math.PtEtaPhiMVector(
    #         tree.lepFSR_pt[idx],
    #         tree.lepFSR_eta[idx],
    #         tree.lepFSR_phi[idx],
    #         tree.lepFSR_mass[idx]
    #         )
    #     # ls_lepvec_lepFSR.append(lepvec_lepFSR)

    #     # lepvec_vtxLepFSR_BS = Math.PtEtaPhiMVector(
    #     zz_vtxLepFSR_BS += Math.PtEtaPhiMVector(
    #         tree.vtxLepFSR_BS_pt[idx],
    #         tree.vtxLepFSR_BS_eta[idx],
    #         tree.vtxLepFSR_BS_phi[idx],
    #         tree.vtxLepFSR_BS_mass[idx]
    #         )
    #     # ls_lepvec_vtxLepFSR_BS.append(lepvec_vtxLepFSR_BS)
    # # End loop over RedBkg leptons from this quartet.
    # # print(f"zz_lepFSR.M() now = {zz_lepFSR.M()}")
    # # print(f"zz_vtxLepFSR_BS.M() now = {zz_vtxLepFSR_BS.M()}")
    # ptr_mass4l[0] = zz_lepFSR.M()
    # ptr_mass4l_vtxFSR_BS[0] = zz_vtxLepFSR_BS.M()

    # except IndexError:
        # try:
        #     assert tree.passedZXCRSelection
        #     assert (tree.mass4l > 0) and (tree.mass4l_vtxFSR_BS > 0)
        # except AssertionError:
        #     print_evt_info_bbf(tree)
        #     raise AssertionError
        # n_indexerrors += 1
# End loop over tree entries.
print(f"Events with at least a 4 in lep_Hindex but only 4 leps: {n_weird_evts}")
new_tree.Write()
nf.Close()
