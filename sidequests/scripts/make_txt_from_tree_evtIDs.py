from sidequests.funcs.evt_comparison import write_tree_evtID_to_txt
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg

# infile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/data2018_2P2plusF_3P1plusF_syncwithfilippo_ge4tightleps_skippassfullsel_2018_Data.root"
inroot = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals_2018_Data.root"
#=== outfile_txt will get appended with info about final state, mass window, etc.
outtxt = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals"
# outfile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_ge4tightleps_skippassfullsel"

framework = "jake"  # Choose between: 'jake', 'bbf'
tup_finalstates = (1, 2, 3, 4)
m4l_lim = (105, 140)

if __name__ == '__main__':
    print(
        f"Using framework: {framework}\n"
        f"on final states: {tup_finalstates}\n"
        f"in mass window:  {m4l_lim[0]} < mass4l < {m4l_lim[1]}"
        )

    for fs in tup_finalstates:
        for switch in (0, 1):
            # A goofy way to trigger 3P1F=True and 2P2F=False, then vice versa.
            write_tree_evtID_to_txt(
                infile=inroot,
                outtxt=outtxt,
                framework=framework,
                m4l_lim=m4l_lim,
                keep_2P2F=(1-switch),
                keep_3P1F=switch,
                fs=fs,
                path_to_tree="passedEvents",
                print_every=500000
                )
