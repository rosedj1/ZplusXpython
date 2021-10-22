"""Hadd a list of root files. Benefit: comment out which files you don't want!
------------------------------------------------------------------------------
SYNTAX:  python3 this_script.py
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-21
------------------------------------------------------------------------------
"""
import sys
sys.path.append("/afs/cern.ch/work/d/drosenzw/HiggsMassMeasurement/")
sys.path.append("/afs/cern.ch/work/d/drosenzw/zplusx/")
from Utils_Python.Commands import shell_cmd
from sidequests.scripts.check_singleevt_in_rootfile import rootfile_relpath_ls

hadd_out = "../test/test_hadd.root"

def hadd_rootfiles(infile_ls, hadd_out):
    """Take the root files in `infile_ls` and `hadd` them into `hadd_out`."""
    single_str_of_files = ' '.join(infile_ls)
    cmd = f"hadd {hadd_out} {single_str_of_files}"
    shell_cmd(cmd, verbose=True)

if __name__ == '__main__':
    hadd_rootfiles(rootfile_relpath_ls, hadd_out)