"""New reducible background analyzer to bypass nZXCRFailedLeptons.
# ============================================================================
# Author: Jake Rosenzweig
# Created: 2021-11-30
# Updated: 2021-12-03
# Notes: This code makes a json file which stores the Run:Lumi:Event of all
#   events which pass 3T1L or 2T2L event selection. It also creates a TH2
#   of per-event 3T1L 4-lep combos vs. per-event 2T2L 4-lep combos and stores
#   the hist in a root file. You can draw the TH2 with:
#       `draw_th2_plots.py`
#   
# ============================================================================
"""
import os
from ROOT import TFile

from sidequests.funcs.evt_loops import evt_loop_evtselcjlst_atleast4leps
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from Utils_Python.Utils_Files import check_overwrite

verbose = 0
overwrite = 1
explain_skipevent = False
start_at_evt = 0
break_at_evt = -1  # Use -1 to run over all events.
print_every = 200000
smartcut_ZapassesZ1sel = False  # Literature sets this to False.

on_hpg = 1
on_lxplus = 0

outdir_hpg = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/"
outdir_lxp = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/"

outfile_base_root = "sidequests/rootfiles/h2_jakeimplem_cjlstOSmethodevtsel.root"
outfile_base_json = "sidequests/json/jakeimplem_cjlstOSmethodevtsel.json"

if __name__ == '__main__':
    if on_lxplus:
        outfile_json = os.path.join(outdir_lxp, outfile_base_json)
        outfile_root = os.path.join(outdir_lxp, outfile_base_root)
    elif on_hpg:
        outfile_json = os.path.join(outdir_hpg, outfile_base_json)
        outfile_root = os.path.join(outdir_hpg, outfile_base_root)
    
    check_overwrite(outfile_json, outfile_root, overwrite=overwrite)

    f_filippo_data2018 = TFile.Open(infile_filippo_data_2018_fromhpg)
    tree = f_filippo_data2018.Get("passedEvents")
    print(f"Successfully opened:\n{infile_filippo_data_2018_fromhpg}")

    evt_loop_evtselcjlst_atleast4leps(tree, outfile_root=outfile_root, outfile_json=outfile_json,
                                     start_at_evt=start_at_evt, break_at_evt=break_at_evt,
                                     fill_hists=True, explain_skipevent=explain_skipevent, verbose=verbose,
                                     print_every=print_every, smartcut_ZapassesZ1sel=smartcut_ZapassesZ1sel)
