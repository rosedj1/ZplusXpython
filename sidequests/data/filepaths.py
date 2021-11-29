import os

main_dir = "/blue/avery/rosedj1/ZplusXpython/sidequests/findmissingevents_comparetoelisa/jakes_new2018data/"

# infile_jake_tree = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/Data_2018_NoDuplicates_RunEventLumi.root"
infile_jake_tree = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/new_data2018/cr_ZLL.root"
# ^Contains all the passedZXCRSelection events as in:
# /fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates.root
infile_filippo_data_2018 = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/fullstats/filippo/rootfiles/Data_2018_03Nov.root"

#####################
#--- CJLST files ---#
#####################
dir_cjlst = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/data/"
infile_elisa       = os.path.join(dir_cjlst, "CRLLos_listOfEvents.txt")
infile_elisa_2p2f  = os.path.join(dir_cjlst, "CRLLos_2P2F_listOfEvents.txt")
infile_elisa_3p1f  = os.path.join(dir_cjlst, "CRLLos_3P1F_listOfEvents.txt")
infile_cjlst_sr    = os.path.join(dir_cjlst, "2018_CJLST_finalSelectedEvents_SR.txt")
infile_matteo_data2018 = "/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200430_LegacyRun2/Data_2018/AllData/ZZ4lAnalysis.root"

# elisa_3p1f_unique_evtid_dct_json = "/blue/avery/rosedj1/ZplusXpython/sidequests/findmissingevents_comparetoelisa/elisa_3p1f_unique_evtID_CR_dct.json"
elisa_3p1f_unique_evtid_dct_json = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/data/json/elisa_3p1f_unique_evtID_CR_dct.json"

infile_jake      = os.path.join(main_dir, "CRLLos_listOfEvents_jake.txt")
infile_jake_2p2f = os.path.join(main_dir, "CRLLos_listOfEvents_jake_2P2F.txt")
infile_jake_3p1f = os.path.join(main_dir, "CRLLos_listOfEvents_jake_3P1F.txt")
# infile_elisa_unique_353 = "/blue/avery/rosedj1/ZplusXpython/sidequests/rootfiles/elisa_unique_353events.root"
infile_elisa_unique_353 = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/rootfiles/elisa_unique_353events.root"

outfile_elisa_2p2f_unique  = os.path.join(main_dir, "CRLLos_2P2F_listOfEvents_unique.txt")
outfile_elisa_3p1f_unique  = os.path.join(main_dir, "CRLLos_3P1F_listOfEvents_unique.txt")
outfile_jake_2p2f_unique = os.path.join(main_dir, "CRLLos_listOfEvents_jake_2P2F_unique.txt")
outfile_jake_3p1f_unique = os.path.join(main_dir, "CRLLos_listOfEvents_jake_3P1F_unique.txt")
outfile_LLR_data2018 = "/blue/avery/rosedj1/ZplusXpython/sidequests/findmissingevents_comparetoelisa/"

outfile_2p2f_common = os.path.join(main_dir, "CRLLos_listOfEvents_2P2F_common.txt")
outfile_3p1f_common = os.path.join(main_dir, "CRLLos_listOfEvents_3P1F_common.txt")
# write_tree_info_to_txt(infile_jake_tree, infile_jake)