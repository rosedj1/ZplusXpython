"""Make hists for redbkg studies using CJLST NTuples.
==============================================================================
Author: Jake Rosenzweig
Created: 2022-01-19
Updated:
Notes:  Need to do `voms-proxy-init` in shell before running this script.
==============================================================================
"""
from sidequests.funcs.evt_loops import (
    analyze_cjlstntuple_osmethod
    )
from sidequests.data.filepaths import (
    infile_matteo_data2018_fromhpg,
    fakerates_WZremoved
    )

analyze_cjlstntuple_osmethod(
    infile_path=infile_matteo_data2018_fromhpg,
    infile_fakerates=fakerates_WZremoved,
    start_at=0, break_at=-1,
    print_every=10000,
    outfile_root=None,
    # int_lumi=59830,
    # fill_hists=True,
    verbose=False,
    overwrite=False
    )