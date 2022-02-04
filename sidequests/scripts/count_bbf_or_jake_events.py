import sys
from glob import glob
from pprint import pprint
# Local imports.
from sidequests.classes.filecomparer import FileRunLumiEvent
from sidequests.funcs.evt_comparison import write_tree_evtID_to_txt
from sidequests.data.filepaths import infile_filippo_data_2018_fromhpg
from Utils_Python.printing import print_header_message

# intxt_evtIds_fili = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_filippo_evtids_3p1f_4mu_105masswindow140.txt"
# intxt_evtIDs_jake = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals_3P1F_4mu_105masswindow140.txt"

# ls_infiles_fili = glob("/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_filippo_evtids_*.txt")
ls_infiles_fili = glob("/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_filippo_evtids_passedZXCRSelection_*.txt")
ls_infiles_jake = glob("/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals*.txt")

tup_finalstates = ("2e2mu",)#("4e", "4mu", "2e2mu", "2mu2e",)
tup_cr = ("3p1f",)#, "2p2f")

print("Found files:")
pprint(ls_infiles_fili)
pprint(ls_infiles_jake)

for cr in tup_cr:
    for fs in tup_finalstates:

        print_header_message(f"{cr.upper()} {fs}")
        ls_fili = [name for name in ls_infiles_fili if fs in name.lower() and cr in name.lower()]
        ls_jake = [name for name in ls_infiles_jake if fs in name.lower() and cr in name.lower()]
        assert len(ls_fili) == len(ls_jake) == 1
        infile_fili = ls_fili[0]
        infile_jake = ls_jake[0]

        # assert all(isinstance(x, str), for x in (infile_fili, infile_jake))
        frle_fil = FileRunLumiEvent(txt=infile_fili)
        frle_jake_withquartets = FileRunLumiEvent(txt=infile_jake)

        # For counting Jake's file.
        _ = frle_fil.analyze_evtids(frle_jake_withquartets, event_type="common")
        _ = frle_fil.analyze_evtids(frle_jake_withquartets, event_type="unique")
        _ = frle_jake_withquartets.analyze_evtids(frle_fil, event_type="unique", print_evts=True)

# Jake's unique 3P1F 2e2mu events. Run fixed BBF Ana on them.
(316059, 14, 15898611),
(316219, 264, 409283510),
(316457, 94, 125536823),
(317340, 324, 426788720),
(317527, 1358, 1946914127),
(317661, 207, 269169251),
(322106, 92, 99772200),
(322322, 279, 526122160),
(323525, 527, 912578885),
(324021, 393, 670180256),
(324021, 465, 809016366),
(324980, 2052, 3682667760),
(325022, 951, 1439539354)


# # For collecting 3P1F/2P2F events in Filippo's file.
# finalState = 3
# study_3p1f = True
# study_2p2f = False

# m4l_min = m4l_lim[0]
# m4l_max = m4l_lim[1]

# if study_3p1f:
#     nZXCRFailedLeptons = 1
# elif study_2p2f:
#     nZXCRFailedLeptons = 2

# if framework == "bbf":
#     for evt in t: 
#         if evt.nZXCRFailedLeptons == nZXCRFailedLeptons:
#             if evt.finalState == finalstate: 
#                 if evt.passedZXCRSelection: 
#                     m4l = evt.mass4l
#                     if (m4l_min < m4l) and (m4l < m4l_max): 
#                         run = evt.Run 
#                         lumisect = evt.LumiSect 
#                         event = evt.Event 
#                         ls_tup_fil.extend([(run, lumisect, event,)])
# # JAKE! Check for a txt file in: .../sidequests/txt/ with the evtIDs.
# elif framework == "jake":
#     for evt in t: 
#         m4l = evt.mass4l
#         if (m4l_min < m4l) and (m4l < m4l_max):
#             if evt.is3P1F:
#                 if evt.finalState == finalstate:
#                     if evt.isData:
#                         run = evt.Run
#                         lumisect = evt.LumiSect 
#                         event = evt.Event 
#                         ls_tup_fil.extend([(run, lumisect, event,)])
