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

ls_infiles_fili = glob("/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_filippo_evtids_*.txt")
ls_infiles_jake = glob("/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/txt/data2018_2P2plusF_3P1plusF_syncwithfilippo_updatedmZvals*.txt")

tup_finalstates = ("4e", "4mu", "2e2mu", "2mu2e",)
tup_cr = ("2p2f", "3p1f")

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
        _ = frle_jake_withquartets.analyze_evtids(frle_fil, event_type="unique")

# framework = "bbf"
# tup_finalstates = (1,)# 2, 3, 4)
# write_tree_only = 1  # After writing the txt files, exit.
# m4l_lim = (105, 140)

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

# BBF Ana with RedBkg fix selects these events (and possibly more).
# addto = [
#     (321887, 450, 722204060),
#     (315689, 342, 398232246),
#     (319991, 777, 1213672625),
#     (322599, 224, 359072495),
#     (316766, 179, 208365005),
#     (319524, 885, 1310553109),
#     (317291, 636, 878537435),
#     (322348, 827, 1498597313),
#     (321434, 39, 65055154),
#     ]

# Jake's Ana can look into events with >=4 tight leptons and selects these:
# check_jake_has_these = [
#     (322492, 778, 1346201480),
#     (321961, 189, 343183869),
#     (321909, 32, 57978416),
#     (321396, 930, 1447135355),
#     (325022, 162, 228256467),
#     (317320, 504, 706020777),
#     (315689, 604, 672709805),
#     (315713, 819, 996429494),
#     (316758, 674, 941538912),
#     (325022, 1263, 1789168728),
#     (316766, 1907, 2626778761),
#     (317661, 556, 813675880),
#     (319449, 364, 498050124),
#     ]
