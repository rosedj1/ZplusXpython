import ROOT
from Utils_Python.Utils_Files import check_overwrite

overwrite = 0

infile_Data = "/blue/avery/rosedj1/ZplusXpython/data/20210802_alljake/Hist_Data.root"
infile_WZ   = "/blue/avery/rosedj1/ZplusXpython/data/20210802_alljake/Hist_MC_WZ-ext1-v2.root"

file_data = ROOT.TFile(infile_Data, "READ")
print(f"Data file opened.")
    
n_EB = file_data.Get("Data_FRel_EB_n")
n_EE = file_data.Get("Data_FRel_EE_n")
n_MB = file_data.Get("Data_FRmu_EB_n")
n_ME = file_data.Get("Data_FRmu_EE_n")


d_EB = file_data.Get("Data_FRel_EB_d")
d_EE = file_data.Get("Data_FRel_EE_d")
d_MB = file_data.Get("Data_FRmu_EB_d")
d_ME = file_data.Get("Data_FRmu_EE_d")


# file_MC = ROOT.TFile ("../data/Hist_MC_ptl3_WZ.root", "READ")
file_MC = ROOT.TFile (infile_WZ, "READ")
# file_MC = ROOT.TFile ("../data/Hist_MC_ptl3_WZ-ext1-v2_xs4p9.root", "READ")
print("MC (WZ) file opened.")
file_MC.cd()

# WZ removal from FRs.
n_EB.Add(file_MC.Get("Data_FRel_EB_n"), -1)
d_EB.Add(file_MC.Get("Data_FRel_EB_d"), -1)
n_EB.Divide(d_EB)

n_EE.Add(file_MC.Get("Data_FRel_EE_n"), -1)
d_EE.Add(file_MC.Get("Data_FRel_EE_d"), -1)
n_EE.Divide(d_EE)

n_MB.Add(file_MC.Get("Data_FRmu_EB_n"), -1)
d_MB.Add(file_MC.Get("Data_FRmu_EB_d"), -1)
n_MB.Divide(d_MB)

n_ME.Add(file_MC.Get("Data_FRmu_EE_n"), -1)
d_ME.Add(file_MC.Get("Data_FRmu_EE_d"), -1)
n_ME.Divide(d_ME)

# file1 = ROOT.TFile ("Hist_Data_ptl3_WZremoved.root", "RECREATE")
newfile = infile_Data.replace('.root', '_WZremoved.root')
check_overwrite(newfile, overwrite=overwrite)
file1 = ROOT.TFile(newfile, "RECREATE")
file1.cd()

print(f"Saving new ROOT file:\n{newfile}")
n_EB.SetName("Data_FRel_EB")
n_EB.Write()
n_EE.SetName("Data_FRel_EE") 
n_EE.Write()
n_MB.SetName("Data_FRmu_EB") 
n_MB.Write()
n_ME.SetName("Data_FRmu_EE")
n_ME.Write()

file_data.Close()
file_MC.Close()
file1.Close()