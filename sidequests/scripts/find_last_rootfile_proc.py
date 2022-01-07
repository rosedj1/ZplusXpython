"""Scan a dir for missing root files when comparing to a master dict.
------------------------------------------------------------------------------
SYNTAX:  python3 this_script.py
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-21
UPDATED: 2021-10-27
------------------------------------------------------------------------------
"""
import sys
from glob import glob
from pprint import pprint
from Utils_Python.Utils_Files import open_json

all_rootfile_dct = open_json("../data/json/elisa_unique_2p2f_3p1f_commontobothCRs_evts_id_rootfile.json")
proc_rootfiles = glob("../rootfiles/elisa_unique_2p2f_3p1f_commontobothCRs*.root")

def get_evtid_from_rootfilename(name):
    name = name.rstrip(".root") 
    parts = name.split("_")
    # The last three parts of the name contain Run_Lumi_Event.
    # E.g. "elisa_unique_event_3p1f_315357_120_90263024.root"
    return ":".join(parts[-3::])

if __name__ == '__main__':
    proc_rootfiles_evtid_ls = [get_evtid_from_rootfilename(name) for name in proc_rootfiles]

    for ct, evt_id in enumerate(all_rootfile_dct.keys()): 
        if evt_id not in proc_rootfiles_evtid_ls:
            print(f"Couldn't find {evt_id} in ../rootfiles/")
            print(f"Last left off at index: {ct}")
            break
