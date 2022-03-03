"""Use xBF Ana and Jake RedBkg Ana's on events and print selection info.
#=============================================================================
# Execute: `python this_script.py > some_output.txt`
# Comment:
# Creator: Jake Rosenzweig
# Created: 2021-12-16
# Updated: 2022-03-01
#=============================================================================
"""
from ROOT import TFile
# Local imports.
# from sidequests.classes.filecomparer import (
#     FileRunLumiEvent, get_list_of_entries,
#     )
from Utils_Python.printing import print_periodic_evtnum
from sidequests.funcs.evt_comparison import (
    # print_evt_info_bbf,
    analyze_single_evt,
    find_runlumievent_using_entry
    )
from sidequests.data.filepaths import (
    rb_skim_UL2017_data, rb_skim_UL2018_data,
    data_2017_UL_ge4lepskim, data_2018_UL_ge4lepskim,
    # infile_filippo_data_2018_fromhpg,
    fakerates_WZremoved_2017_UL_woFSR,
    fakerates_WZremoved_2018_UL_woFSR,
    )
from constants.analysis_params import (
    dct_sumgenweights_2017_UL, dct_sumgenweights_2018_UL,
    dct_xs_jake,
    LUMI_INT_2017_UL, LUMI_INT_2018_UL
    )

year = 2017
lumi_int = LUMI_INT_2017_UL
infile_root = data_2017_UL_ge4lepskim
genwgts_dct = dct_sumgenweights_2017_UL
infile_fakerates = fakerates_WZremoved_2017_UL_woFSR  # Required for 'jake'.
tree_path = "passedEvents"

analyze_using = "jake"  # Choose between: "jake" or "bbf".

start_at = 0
end_at = -1  #start_at + 1
print_every = 50000

allow_ge4tightleps = True
keep_only_mass4lgt0 = True
match_lep_Hindex = True
recalc_mass4l_vals = False

# Either use `run_lumi_evt_row` or fill in `ls_tup_unique`:
run_lumi_evt_row = None #(304366, 1117, 1809338116, 270236)

ls_tup_unique = [
    ######################
    #=== DATA 2018 UL ===#
    ######################
#     # Data 2018 UL, 4mu unique in xBF:
#     (316218, 967, 1341095734),
#     (317640, 312, 422234534),
#     (317392, 1222, 1734755160),
#     (324293, 463, 847164031),
#     (315689, 72, 65832774),
#     # Data 2018 UL, 4e unique in xBF:
#     (316114, 1293, 1312567745),
#     (324245, 1199, 2225759472),
#     (319579, 238, 295829669),
#     (324980, 154, 221810851),
#     (317435, 1136, 1638637503),
#     (324897, 66, 73197820),
#     (316718, 293, 435036170),
#     (324201, 456, 892509259),
#     (322625, 239, 379085701),
#     (320674, 307, 170248938),
#     # Data 2018 UL, 2e2mu unique in xBF:
#     (320920, 71, 94504378),
#     (323525, 527, 912578885),
#     # Data 2018 UL, 2mu2e unique in xBF:
#     (321415, 95, 154493574),
#     (319756, 1190, 1918222741),
#     (320006, 55, 91339111),
#     (315840, 973, 1072588622),
#     (323488, 359, 656231860),
#     (324841, 370, 695850712),
#     (322252, 1314, 2277052934),
#     (320822, 316, 525998426),
#     (317291, 519, 691007747),
#     (324201, 102, 162862016),
#     (315420, 1017, 671153361),
#     (316199, 860, 1188017841),
#     (324878, 761, 1379305225),
#     (317663, 672, 1022304522),
#     (319657, 2, 2834035)
# ]

# ls_tup_unique = [
#     ######################
#     #=== DATA 2017 UL ===#
#     ######################
#     # Data 2017 UL, 4mu unique in xBF:
#     (304366, 1117, 1809338116),
#     (297178, 716, 891914663)  #--- Jake tagged as valid 3P1F quartet,
#     # (304625, 298, 425714862) --- Jake tagged as valid 3P1F quartet,
#     (300517, 258, 314860251),
#     (305314, 48, 56936615),
#     (305081, 55, 11862118),
#     (306125, 480, 843196636),
#     # (305636, 1142, 2053996960) --- Jake tagged as valid 3P1F quartet,
#     # (300122, 409, 561022370) --- Jake tagged as valid 3P1F quartet,

#     # # Data 2017 UL, 4e unique in xBF:,
#     # (297219, 1957, 2885608175) --- Jake tagged as valid 3P1F quartet,
#     (297603, 241, 433745367),
#     (299370, 371, 471174005),
#     (306138, 1158, 1507073799),
#     (302448, 345, 411406556),
#     (297296, 333, 477343383),
#     # (302393, 106, 125394268) --- Jake tagged as valid 3P1F quartet,
#     (300785, 975, 1153338559),
      (304616, 603, 1002279386),  # --- Jake tagged as valid 3P1F quartet,
]
#     (304062, 1481, 1947677889),
#     (305112, 1334, 2220608605),
#     (300123, 254, 294498299),
#     (297293, 134, 208229640),
#     (297656, 288, 472775383),
#     (300155, 919, 1242579761),
#     (299096, 51, 84760341),
#     # (300517, 339, 408325107) --- Jake tagged as valid 3P1F quartet,
#     # (305204, 321, 543469667) --- Jake tagged as valid 3P1F quartet,
#     (304144, 959, 1659587081),
#     # (299184, 409, 680767941) --- Jake tagged as valid 3P1F quartet,
#     # (303948, 572, 921521958) --- Jake tagged as valid 3P1F quartet,
#     (304506, 46, 80595885),

#     # # Data 2017 UL, 2e2mu unique in xBF:,
#     (305282, 95, 66742053),
#     (301627, 244, 210214709),
#     (305112, 1449, 2365634557),

#     # # Data 2017 UL, 2mu2e unique in xBF:,
#     # (300516, 54, 67369043) --- Jake tagged as valid 3P1F quartet,
#     # (303832, 167, 171552872) --- Jake tagged as valid 3P1F quartet,
#     # (305064, 171, 275285910) --- Jake tagged as valid 3P1F quartet,
#     (305207, 666, 1039685283),
#     # (304062, 306, 452386132) --- Jake tagged as valid 3P1F quartet,
#     (304144, 2176, 2993221045),
#     # (305586, 249, 397773940) --- Jake tagged as valid 3P1F quartet,
#     (300284, 56, 81830714),
#     (300157, 776, 786459853),
#     (304144, 254, 379612237),
#     # (303832, 137, 126397351) --- Jake tagged as valid 3P1F quartet,
#     # (300464, 250, 362770303) --- Jake tagged as valid 3P1F quartet,
#     (305406, 1400, 2223006930),
#     (302029, 17, 21904470),
#     # (301986, 113, 102785248) --- Jake tagged as valid 3P1F quartet,
#     (304209, 387, 664130533),
#     # (297562, 198, 323224932) --- Jake tagged as valid 3P1F quartet,
#     (304144, 137, 145237539),
#     # (302476, 135, 102855717) --- Jake tagged as valid 3P1F quartet,
#     (301472, 472, 454742452),
#     (297487, 369, 482491182),
#     (300462, 91, 138044248),
#     # (304333, 1100, 1755439890) --- Jake tagged as valid 3P1F quartet,
#     (305045, 260, 458138209),
#     (300636, 253, 348785005),
#     (297292, 722, 1288623271),
#     # (300785, 649, 812374663) --- Jake tagged as valid 3P1F quartet,
#     (302344, 178, 163157463),
#     # (301998, 1335, 1086736376) --- Jake tagged as valid 3P1F quartet,
#     (301323, 354, 349857504),
#     (300514, 65, 58754413),
#     (305636, 1578, 2746712922),
#     (302343, 10, 9296697),
# ]

# Use Jake's analyzer on Filippo's unique events to see why Jake's FW failed.
f = TFile.Open(infile_root, "read")
tree = f.Get(tree_path)

# Run over root file and compare each event to event of interest.
# Pro: only 1 for loop over entire root file.
# Con: events of interest are analyzed in the order as found in NTuple.
if run_lumi_evt_row is not None:
    run = run_lumi_evt_row[0]
    lumi = run_lumi_evt_row[1]
    event = run_lumi_evt_row[2] 
    entry = run_lumi_evt_row[3]
    analyze_single_evt(
        tree, run=run, lumi=lumi, event=event, entry=entry,
        fw=analyze_using, which="first",
        evt_start=0, evt_end=-1, print_every=print_every,
        infile_fakerates=infile_fakerates,
        genwgts_dct=genwgts_dct,
        dct_xs=dct_xs_jake,
        LUMI_INT=lumi_int,
        smartcut_ZapassesZ1sel=False,
        overwrite=False,
        keep_only_mass4lgt0=False,
        match_lep_Hindex=False,
        recalc_mass4l_vals=False,
        allow_ge4tightleps=allow_ge4tightleps,
        skip_passedFullSelection=True,
        explain_skipevent=True,
        verbose=True,
        )
else:
    # Use list of provided evtIDs.
    if end_at == -1:
        end_at = tree.GetEntries()
    for evt_num in range(start_at, end_at):
        print_periodic_evtnum(evt_num, end_at, print_every=print_every)

        tree.GetEntry(evt_num)
        tup_evtid = find_runlumievent_using_entry(tree, evt_num, fw="bbf")

        if tup_evtid in ls_tup_unique:
            run, lumi, event = tup_evtid
            # We know the exact row. Grab the event.
            analyze_single_evt(
                tree, run=run, lumi=lumi, event=event, entry=evt_num,
                fw=analyze_using, which="first",
                evt_start=0, evt_end=-1, print_every=print_every,
                infile_fakerates=infile_fakerates,
                genwgts_dct=genwgts_dct,
                dct_xs=dct_xs_jake,
                LUMI_INT=lumi_int,
                smartcut_ZapassesZ1sel=False,
                overwrite=False,
                keep_only_mass4lgt0=False,
                match_lep_Hindex=False,
                recalc_mass4l_vals=False,
                allow_ge4tightleps=allow_ge4tightleps,
                skip_passedFullSelection=True,
                explain_skipevent=True,
                verbose=True,
                )


# tf = TFile.Open(infile_filippo_data_2018_fromhpg)
# tree_bbf = tf.Get("passedEvents")

# if use_exact_entry:
#     ls_uniq_entries = get_list_of_entries(infile_exact_entries)
#     for entry in ls_uniq_entries:
#         analyze_single_evt(
#             tree_bbf,
#             run=None, lumi=None, event=None,
#             entry=entry,
#             fw="bbf", which="first"
#             )
#         analyze_single_evt(
#             tree_bbf,
#             run=None, lumi=None, event=None,
#             entry=entry,
#             fw="jake", which="first",
#             infile_FR_wz_removed=infile_FR_wz_removed,
#             explain_skipevent=explain_skipevent,
#             verbose=verbose
#             )
#         print("=#" * 39)
#         print("=#" * 39)
#         print("=#" * 39)
# else:
#     # Not sure which entry to use. Find using exactly run, lumi, event.
#     for ct, tup_fili_uniq_evtid in enumerate(fili_unique_evts):
#         # if ct == 1:
#         #     break
#         run, lumi, event = tup_fili_uniq_evtid
#         ls_bbf_evt_ndx = analyze_entry(
#             tree_bbf, entry=None, run=run, lumi=lumi, event=event,
#             fw="bbf", which="first"

#             tree, run, lumi, event, entry=None, fw="bbf", which="all",
#             evt_start=0, evt_end=-1, print_every=10000,
#             infile_FR_wz_removed=infile_FR_wz_removed,
#             explain_skipevent=True,
#             verbose=False
#             )
#         print()



# Filippo's unique 3P1F 4mu events.
# They all have at least 4 tight leptons!
# ls_tup_unique_fili = [
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

# ls_tup_unique_jake = [
#     # Jake's unique 3P1F 4mu events.
#     # (321887, 450, 722204060),
#     # (315689, 342, 398232246),
#     # (319991, 777, 1213672625),
#     # (322599, 224, 359072495),
#     # (316766, 179, 208365005),
#     # (319524, 885, 1310553109),
#     # (317291, 636, 878537435),
#     # (322348, 827, 1498597313),
#     # (321434, 39, 65055154)

#     (321010, 33, 54826308),
#     (316218, 760, 1057128632),
#     (324980, 1481, 2730022725),
#     ]



# # inpkl_bbf_2p2f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_2p2f.pkl"
# # inpkl_bbf_3p1f  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/bbf_evtids_3p1f.pkl"
# # inpkl_jake_2p2f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_2p2f.pkl"
# # inpkl_jake_3p1f = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/pkls/jake_evtids_3p1f.pkl"
# # infile_root_jake = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root"

# intxt_jake_3p1f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_3p1f.txt"
# intxt_jake_2p2f = "../txt/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data_2p2f.txt"
# intxt_fili_3p1f = "../txt/data2018_filippo_evtids_3p1f.txt"

