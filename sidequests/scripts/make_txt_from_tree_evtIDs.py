"""Write a txt file of 'Run : Lumi : Event' for events which pass selections.
# ============================================================================
# Syntax: `python <this_script>.py`
# Creator: Jake Rosenzweig
# Created: 2022-02-02
# Updated: 2022-02-03
# ============================================================================
"""
from sidequests.funcs.evt_comparison import write_tree_evtID_to_txt
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from constants.finalstates import dct_finalstates_int2str
from Utils_Python.printing import print_header_message

inroot = infile_filippo_data_2018_fromhpg
# inroot = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals_2018_Data.root"
#=== outfile_txt will get appended with info about final state, mass window, etc.
# outtxt = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals"
outtxt_basename = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_filippo_evtids_passedZXCRSelection"

overwrite = 0
framework = "bbf"  # Choose between: 'jake', 'bbf'
tup_finalstates = (1, 2, 3, 4)
m4l_lim = (105, 140)

if __name__ == '__main__':
    ls_str_fs = [dct_finalstates_int2str[k] for k in tup_finalstates]
    print(
        f"Using framework: {framework}\n"
        f"on final states: {ls_str_fs}\n"
        f"in mass window:  {m4l_lim[0]} < mass4l < {m4l_lim[1]}"
        )

    for fs in tup_finalstates:
        # for switch in (0, 1):
        for switch in (0,):
            # A goofy way to trigger 3P1F=True and 2P2F=False, then vice versa.
            str_fs = dct_finalstates_int2str[fs]
            print_header_message(
                f"Processing {'3P1F' if switch == 1 else '2P2F'}: {str_fs}"
                )
            write_tree_evtID_to_txt(
                infile=inroot,
                outtxt_basename=outtxt_basename,
                framework=framework,
                m4l_lim=m4l_lim,
                keep_2P2F=(1-switch),
                keep_3P1F=switch,
                fs=fs,
                path_to_tree="passedEvents",
                print_every=500000,
                overwrite=overwrite,
                )
