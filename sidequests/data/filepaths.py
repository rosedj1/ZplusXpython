import os

####################
#--- Fake Rates ---#
####################
fakerates_WZremoved_2017_UL = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/fakerates/Hist_Data_ptl3_WZremoved_2017UL_WZxs5p26pb.root"
fakerates_WZremoved_2018_UL = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/fakerates/Hist_Data_ptl3_WZremoved_2018UL_WZxs5p26pb.root"
fakerates_WZremoved_2017_UL_woFSR = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/fakerates/Hist_Data_ptl3_WZremoved_2017UL_WZxs5p26pb_woFSR_versVukasin.root"
fakerates_WZremoved_2018_UL_woFSR = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/fakerates/Hist_Data_ptl3_WZremoved_2018UL_WZxs5p26pb_woFSR_versVukasin.root"
fakerates_WZremoved_2018_rereco = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/uselepFSRtocalc_mZ1/Hist_Data_ptl3_WZremoved.root"

##############################
#--- RedBkg Skimmed Trees ---#
##############################
rb_skim_UL2017 = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/redbkgest_UL_WZxs5p26pb_ge3lepskim_2017_Data_ZZ.root"
rb_skim_UL2018 = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/redbkgest_UL_WZxs5p26pb_ge3lepskim_2018_Data_ZZ.root"

#################
#=== 2017 UL ===#
#################
data_2017_UL = "root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshzz4l/xBF/Run2/UL/Data/2017/Data_2017_UL_MiniAODv2_skim2L_noDuplicates.root"
data_2017_UL_ge3lepskim = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2017/skimge3leps/Data_2017_UL_MiniAODv2_skim2L_noDuplicates.root"
dir_mc_2017_UL = "root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshzz4l/xBF/Run2/UL/MC/2017/"
mc_2017_UL_DY = os.path.join(dir_mc_2017_UL, "DYJetsToLL_M-50_M125_2017_skimmed.root")
mc_2017_UL_TT = os.path.join(dir_mc_2017_UL, "TTTo2L2Nu_M125_2017_skimmed.root")
mc_2017_UL_WZ = os.path.join(dir_mc_2017_UL, "WZTo3LNu_M125_2017_skimmed.root")
mc_2017_UL_ZZ = os.path.join(dir_mc_2017_UL, "ZZTo4L_M125_2017_skimmed.root")
mc_2017_UL_ZZ_ge3lepskim = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/MC/2017/skimge3leps/ZZTo4L_M125_2017_skimmed.root"

#################
#=== 2018 UL ===#
#################
data_2018_UL = "root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshzz4l/xBF/Run2/UL/Data/2018/2018DATA_noDuplicates.root"
data_2018_UL_ge3lepskim = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2018/skimge3leps/2018DATA_noDuplicates.root"
dir_mc_2018_UL = "root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshzz4l/xBF/Run2/UL/MC/2018/"
mc_2018_UL_DY = os.path.join(dir_mc_2018_UL, "DYJetsToLL_M-50_M125_2018_skimmed.root")
mc_2018_UL_TT = os.path.join(dir_mc_2018_UL, "TTTo2L2Nu_M125_2018_skimmed.root")
mc_2018_UL_WZ = os.path.join(dir_mc_2018_UL, "WZTo3LNu_M125_2018_skimmed.root")
mc_2018_UL_ZZ = os.path.join(dir_mc_2018_UL, "ZZTo4L_M125_2018_skimmed.root")
mc_2018_UL_ZZ_ge3lepskim = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/MC/2018/skimge3leps/ZZTo4L_M125_2018_skimmed.root"

#####################
#=== 2018 RERECO ===#
#####################
main_dir = "/blue/avery/rosedj1/ZplusXpython/sidequests/findmissingevents_comparetoelisa/jakes_new2018data/"

# infile_jake_tree = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/Data_2018_NoDuplicates_RunEventLumi.root"
infile_jake_tree = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/new_data2018/cr_ZLL.root"
# ^Contains all the passedZXCRSelection events as in:
# /fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates.root
# infile_filippo_data_2018_fromlxp = f"root://gator.rc.ufl.edu//{filippo_file}"    # Doesn't work.
# infile_filippo_data_2018_fromlxp = f"root://cmsxrootd.fnal.gov//{filippo_file}"  # Doesn't work.
infile_filippo_data_2018_fromlxp = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/data_from_HPG/Data_2018_03Nov.root"
infile_filippo_data_2018_fromhpg = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/fullstats/filippo/Data_2018_03Nov.root"
infile_filippo_zz_2018_fromlxp = "/eos/user/f/ferrico/www/Jake/ZZTo4L_M125_2018_skimmed.root"
infile_filippo_zz_2018_fromhpg = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/filippo/skimmedbranches/ZZTo4L_M125_2018_skimmed.root"

mc_2018_basedir = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/skimmedbranches/"
mc_2018_dy_hpg = os.path.join(mc_2018_basedir, "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root")
mc_2018_tt_hpg = os.path.join(mc_2018_basedir, "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root")
mc_2018_wz_hpg = os.path.join(mc_2018_basedir, "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root")
mc_2018_zz_hpg = os.path.join(mc_2018_basedir, "ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root")

dir_redbkgskim = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/redbkgskim"
data_2018_jakeredbkgskim = os.path.join(dir_redbkgskim, "cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root")

#####################
#--- CJLST files ---#
#####################
dir_cjlst = "../../sidequests/data/"
infile_elisa       = os.path.join(dir_cjlst, "CRLLos_listOfEvents.txt")
infile_elisa_2p2f  = os.path.join(dir_cjlst, "CRLLos_2P2F_listOfEvents.txt")
infile_elisa_3p1f  = os.path.join(dir_cjlst, "CRLLos_3P1F_listOfEvents.txt")
infile_cjlst_sr    = os.path.join(dir_cjlst, "2018_CJLST_finalSelectedEvents_SR.txt")
infile_matteo_data2018_fromlxp = "/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200430_LegacyRun2/Data_2018/AllData/ZZ4lAnalysis.root"
infile_matteo_data2018_fromhpg = f"root://eoscms.cern.ch/{infile_matteo_data2018_fromlxp}"

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
