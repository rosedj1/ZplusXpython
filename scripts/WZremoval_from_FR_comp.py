import ROOT

infile_Data = "../data/Hist_Data_ptl3_Data.root"
file0 = ROOT.TFile(infile_Data, "READ")
print(f"Data file opened.")
    
n_EB = file0.Get("Data_FRel_EB_n")
n_EE = file0.Get("Data_FRel_EE_n")
n_MB = file0.Get("Data_FRmu_EB_n")
n_ME = file0.Get("Data_FRmu_EE_n")


d_EB = file0.Get("Data_FRel_EB_d")
d_EE = file0.Get("Data_FRel_EE_d")
d_MB = file0.Get("Data_FRmu_EB_d")
d_ME = file0.Get("Data_FRmu_EE_d")


fileMC = ROOT.TFile ("../data/Hist_MC_ptl3_WZ.root", "READ")
print("MC file opened.")
fileMC.cd()

n_EB.Add(fileMC.Get("Data_FRel_EB_n"),-1)
d_EB.Add(fileMC.Get("Data_FRel_EB_d"),-1)

n_EB.Divide(d_EB)

n_EE.Add(fileMC.Get("Data_FRel_EE_n"),-1)
d_EE.Add(fileMC.Get("Data_FRel_EE_d"),-1)

n_EE.Divide(d_EE)

n_MB.Add(fileMC.Get("Data_FRmu_EB_n"),-1)
d_MB.Add(fileMC.Get("Data_FRmu_EB_d"),-1)

n_MB.Divide(d_MB)

n_ME.Add(fileMC.Get("Data_FRmu_EE_n"),-1)
d_ME.Add(fileMC.Get("Data_FRmu_EE_d"),-1)

n_ME.Divide(d_ME)

# file1 = ROOT.TFile ("Hist_Data_ptl3_WZremoved.root", "RECREATE")
newfile = infile_Data.replace('.root', '_WZremoved.root')
file1 = ROOT.TFile(newfile, "RECREATE")
file1.cd()

n_EB.SetName("Data_FRel_EB")
n_EB.Write()
n_EE.SetName("Data_FRel_EE") 
n_EE.Write()
n_MB.SetName("Data_FRmu_EB") 
n_MB.Write()
n_ME.SetName("Data_FRmu_EE")
print(f"Saving new ROOT file:\n{newfile}")
n_ME.Write()

file0.Close()
fileMC.Close()
file1.Close()