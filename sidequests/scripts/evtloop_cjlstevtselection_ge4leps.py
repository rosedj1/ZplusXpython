"""New reducible background analyzer to bypass nZXCRFailedLeptons.
# ============================================================================
# Author: Jake Rosenzweig
# Created: 2021-11-30
# Updated: 2021-12-01
# ============================================================================
"""
import os
from ROOT import TFile

from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
from sidequests.data.filepaths import infile_filippo_data_2018_fromlxp

verbose = 0
explain_skipevent = False
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 200000
usetightZa_smartcut = True  # Literature sets this to False.

on_hpg = 0
on_lxplus = 1

outdir_hpg = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/"
outdir_lxp = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/"

outfile_base_root = "sidequests/rootfiles/h2_cjlstevtsel_2p2f_3p1f_widebins_includepassfullsel.root"
outfile_base_json = "sidequests/json/cjlstevtsel_2p2f_3p1f_widebins_includepassfullsel.json"

if __name__ == '__main__':
    if on_lxplus:
        outfile_json = os.path.join(outdir_lxp, outfile_base_json)
        outfile_root = os.path.join(outdir_lxp, outfile_base_root)
    elif on_hpg:
        outfile_json = os.path.join(outdir_hpg, outfile_base_json)
        outfile_root = os.path.join(outdir_hpg, outfile_base_root)

    f_filippo_data2018 = TFile.Open(infile_filippo_data_2018_fromlxp)
    tree = f_filippo_data2018.Get("passedEvents")
    print(f"Successfully opened:\n{infile_filippo_data_2018_fromlxp}")

    evt_loop_evtselcjlst_atleast4leps(tree, outfile_root=outfile_root, outfile_json=outfile_json,
                                     start_at_evt=start_at_evt, break_at_evt=break_at_evt,
                                     fill_hists=True, explain_skipevent=explain_skipevent, verbose=verbose,
                                     print_every=print_every, usetightZa_smartcut=usetightZa_smartcut)
