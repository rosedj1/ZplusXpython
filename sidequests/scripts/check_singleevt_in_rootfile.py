"""Identify root files which only contain 1 event. Also hadd files.
------------------------------------------------------------------------------
SYNTAX:  python2 this_script.py
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-21
------------------------------------------------------------------------------
"""
import ROOT
import os
from glob import glob
from pprint import pprint
import sys
sys.path.append("/afs/cern.ch/work/d/drosenzw/HiggsMassMeasurement/")
sys.path.append("/afs/cern.ch/work/d/drosenzw/zplusx/")

indir_rootfiles = "../rootfiles/"
rootfile_ls = [
    "elisa_unique_event_3p1f_315267_72_71643124.root",
    "elisa_unique_event_3p1f_315259_11_6691550.root",
    "elisa_unique_event_3p1f_315257_58_40785294.root",
    # "elisa_unique_event_3p1f_315357_120_90263024.root", # Does not have 1 event.
    "elisa_unique_event_3p1f_315270_147_126267922.root",
    "elisa_unique_event_3p1f_315357_137_106622216.root",
    # "elisa_unique_event_3p1f_315361_81_50003576.root", # Does not have 1 event.
    "elisa_unique_event_3p1f_315366_132_80193773.root",
    "elisa_unique_event_3p1f_315357_582_474271871.root",
    # "elisa_unique_event_3p1f_315420_147_111359074.root", # Does not have 1 event.
    "elisa_unique_event_3p1f_315366_213_126700025.root",
    "elisa_unique_event_3p1f_315420_1017_671153361.root",
    # "elisa_unique_event_3p1f_315420_36_19703356.root", # Does not have 1 event.
    "elisa_unique_event_3p1f_315488_543_515166528.root",
    "elisa_unique_event_3p1f_315488_152_135937874.root",
    # "elisa_unique_event_3p1f_315488_564_533098650.root", # Does not have 1 event.
    # "elisa_unique_event_3p1f_315489_346_198881489.root", # Does not have 1 event.
    "elisa_unique_event_3p1f_315489_693_374300687.root",
]

# rootfile_ls = glob(indir_rootfiles)

def check_rootfile_has_evt(new_root, tree_name="Ana/passedEvents"):
    """Return True if newly-produced root file has exactly 1 event."""
    f = ROOT.TFile(new_root)
    t = f.Get(tree_name)
    return True if t.GetEntries() == 1 else False

def print_rootfiles_with_single_evt():
    n_files = len(rootfile_ls)
    print("Checking {} root files for any with exactly 1 event.".format(n_files))

    empty_rootfiles = []
    for ct, rootfile_name in enumerate(rootfile_ls, 1):
        rootfile_path = os.path.join(indir_rootfiles, rootfile_name)
        if (ct % 5) == 0:
            print("Checking file {}/{}: {}".format(ct, n_files, rootfile_name))
        if not check_rootfile_has_evt(rootfile_path):
            empty_rootfiles.append(rootfile_name)

    if len(empty_rootfiles) > 0:
        print("The following root files do not contain 1 event:")
        pprint(empty_rootfiles)

rootfile_relpath_ls = [os.path.join(indir_rootfiles, f) for f in rootfile_ls]

if __name__ == '__main__':
    print_rootfiles_with_single_evt()
