import ROOT
import math

_fileData = ROOT.TFile ("estimateZXData.root", "READ")

h1D_m4l_SR_2P2F = _fileData.Get("h1D_m4l_SR_2P2F")
h1D_m4l_SR_2P2F_4e = _fileData.Get("h1D_m4l_SR_2P2F_4e")
h1D_m4l_SR_2P2F_4mu = _fileData.Get("h1D_m4l_SR_2P2F_4mu")
h1D_m4l_SR_2P2F_2e2mu = _fileData.Get("h1D_m4l_SR_2P2F_2e2mu")
h1D_m4l_SR_2P2F_2mu2e = _fileData.Get("h1D_m4l_SR_2P2F_2mu2e")

h1D_m4l_SR_3P1F = _fileData.Get("h1D_m4l_SR_3P1F")
h1D_m4l_SR_3P1F_4e = _fileData.Get("h1D_m4l_SR_3P1F_4e")
h1D_m4l_SR_3P1F_4mu = _fileData.Get("h1D_m4l_SR_3P1F_4mu")
h1D_m4l_SR_3P1F_2e2mu = _fileData.Get("h1D_m4l_SR_3P1F_2e2mu")
h1D_m4l_SR_3P1F_2mu2e = _fileData.Get("h1D_m4l_SR_3P1F_2mu2e")

print("------------3P1F Data-----------------")
print("h1D_m4l_SR_3P1F = " + str(h1D_m4l_SR_3P1F.Integral()))
print("h1D_m4l_SR_3P1F_4e = " + str(h1D_m4l_SR_3P1F_4e.Integral()))
print("h1D_m4l_SR_3P1F_4mu = " + str(h1D_m4l_SR_3P1F_4mu.Integral()))
print("h1D_m4l_SR_3P1F_2e2mu = " + str(h1D_m4l_SR_3P1F_2e2mu.Integral()))
print("h1D_m4l_SR_3P1F_2mu2e = " + str(h1D_m4l_SR_3P1F_2mu2e.Integral()))
print("--------------------------------")

#Just to initialize them with correct binning, will do a bin by bin estimate in the following lines
h1D_m4l_SR_tot = h1D_m4l_SR_2P2F.Clone()
h1D_m4l_SR_tot_4e = h1D_m4l_SR_2P2F_4e.Clone()
h1D_m4l_SR_tot_4mu = h1D_m4l_SR_2P2F_4mu.Clone()
h1D_m4l_SR_tot_2e2mu = h1D_m4l_SR_2P2F_2e2mu.Clone()
h1D_m4l_SR_tot_2mu2e = h1D_m4l_SR_2P2F_2mu2e.Clone()

_fileZZ = ROOT.TFile ("estimateZXZZ.root", "READ")

ZZ_4e = _fileZZ.Get("h1D_m4l_SR_3P1F_4e")
ZZ_4mu = _fileZZ.Get("h1D_m4l_SR_3P1F_4mu")
ZZ_2e2mu = _fileZZ.Get("h1D_m4l_SR_3P1F_2e2mu")
ZZ_2mu2e = _fileZZ.Get("h1D_m4l_SR_3P1F_2mu2e")
ZZ_tot = _fileZZ.Get("h1D_m4l_SR_3P1F")

print("------------3P1F ZZ-----------------")
print("ZZ_SR_3P1F = " + str(ZZ_tot.Integral()))
print("ZZ_SR_3P1F_4e = " + str(ZZ_4e.Integral()))
print("ZZ_SR_3P1F_4mu = " + str(ZZ_4mu.Integral()))
print("ZZ_SR_3P1F_2e2mu = " + str(ZZ_2e2mu.Integral()))
print("ZZ_SR_3P1F_2mu2e = " + str(ZZ_2mu2e.Integral()))
print("--------------------------------")

h1D_m4l_SR_3P1F.Add(ZZ_tot,-1)
h1D_m4l_SR_3P1F_4e.Add(ZZ_4e,-1)
h1D_m4l_SR_3P1F_4mu.Add(ZZ_4mu,-1)
h1D_m4l_SR_3P1F_2e2mu.Add(ZZ_2e2mu,-1)
h1D_m4l_SR_3P1F_2mu2e.Add(ZZ_2mu2e,-1)

var_nBins = h1D_m4l_SR_2P2F.GetNbinsX()

for c in range (1, var_nBins + 1):

    if (h1D_m4l_SR_3P1F_4e.GetBinContent(c) <= 2*h1D_m4l_SR_2P2F_4e.GetBinContent(c)):
        h1D_m4l_SR_tot_4e.SetBinContent(c,h1D_m4l_SR_2P2F_4e.GetBinContent(c))
        h1D_m4l_SR_tot_4e.SetBinError(c,h1D_m4l_SR_2P2F_4e.GetBinError(c))
    
    else:
        h1D_m4l_SR_tot_4e.SetBinContent(c,h1D_m4l_SR_3P1F_4e.GetBinContent(c)-h1D_m4l_SR_2P2F_4e.GetBinContent(c))
        h1D_m4l_SR_tot_4e.SetBinError(c,math.sqrt(h1D_m4l_SR_2P2F_4e.GetBinError(c)*h1D_m4l_SR_2P2F_4e.GetBinError(c)+h1D_m4l_SR_3P1F_4e.GetBinError(c)*h1D_m4l_SR_3P1F_4e.GetBinError(c)))


    if (h1D_m4l_SR_3P1F_4mu.GetBinContent(c) <= 2*h1D_m4l_SR_2P2F_4mu.GetBinContent(c)):
    
        h1D_m4l_SR_tot_4mu.SetBinContent(c,h1D_m4l_SR_2P2F_4mu.GetBinContent(c))
        h1D_m4l_SR_tot_4mu.SetBinError(c,h1D_m4l_SR_2P2F_4mu.GetBinError(c))

    else:
        h1D_m4l_SR_tot_4mu.SetBinContent(c,h1D_m4l_SR_3P1F_4mu.GetBinContent(c)-h1D_m4l_SR_2P2F_4mu.GetBinContent(c))
        h1D_m4l_SR_tot_4mu.SetBinError(c,math.sqrt(h1D_m4l_SR_2P2F_4mu.GetBinError(c)*h1D_m4l_SR_2P2F_4mu.GetBinError(c)+h1D_m4l_SR_3P1F_4mu.GetBinError(c)*h1D_m4l_SR_3P1F_4mu.GetBinError(c)))



    if (h1D_m4l_SR_3P1F_2e2mu.GetBinContent(c) <= 2*h1D_m4l_SR_2P2F_2e2mu.GetBinContent(c)):
        h1D_m4l_SR_tot_2e2mu.SetBinContent(c,h1D_m4l_SR_2P2F_2e2mu.GetBinContent(c))
        h1D_m4l_SR_tot_2e2mu.SetBinError(c,h1D_m4l_SR_2P2F_2e2mu.GetBinError(c))

    else:
        h1D_m4l_SR_tot_2e2mu.SetBinContent(c,h1D_m4l_SR_3P1F_2e2mu.GetBinContent(c)-h1D_m4l_SR_2P2F_2e2mu.GetBinContent(c))
        h1D_m4l_SR_tot_2e2mu.SetBinError(c,math.sqrt(h1D_m4l_SR_2P2F_2e2mu.GetBinError(c)*h1D_m4l_SR_2P2F_2e2mu.GetBinError(c)+h1D_m4l_SR_3P1F_2e2mu.GetBinError(c)*h1D_m4l_SR_3P1F_2e2mu.GetBinError(c)))


    if (h1D_m4l_SR_3P1F_2mu2e.GetBinContent(c) <= 2*h1D_m4l_SR_2P2F_2mu2e.GetBinContent(c)):
        h1D_m4l_SR_tot_2mu2e.SetBinContent(c,h1D_m4l_SR_2P2F_2mu2e.GetBinContent(c))
        h1D_m4l_SR_tot_2mu2e.SetBinError(c,h1D_m4l_SR_2P2F_2mu2e.GetBinError(c))
    
    else:
        h1D_m4l_SR_tot_2mu2e.SetBinContent(c,h1D_m4l_SR_3P1F_2mu2e.GetBinContent(c)-h1D_m4l_SR_2P2F_2mu2e.GetBinContent(c))
        h1D_m4l_SR_tot_2mu2e.SetBinError(c,math.sqrt(h1D_m4l_SR_2P2F_2mu2e.GetBinError(c)*h1D_m4l_SR_2P2F_2mu2e.GetBinError(c)+h1D_m4l_SR_3P1F_2mu2e.GetBinError(c)*h1D_m4l_SR_3P1F_2mu2e.GetBinError(c)))


print("--------Final Z+X estimates----------")
print("h1D_m4l_SR_2P2F = " + str(h1D_m4l_SR_2P2F.Integral()))
print("h1D_m4l_SR_2P2F_4e = " + str(h1D_m4l_SR_2P2F_4e.Integral()))
print("h1D_m4l_SR_2P2F_4mu = " + str(h1D_m4l_SR_2P2F_4mu.Integral()))
print("h1D_m4l_SR_2P2F_2e2mu = " + str(h1D_m4l_SR_2P2F_2e2mu.Integral()))
print("h1D_m4l_SR_2P2F_2mu2e = " + str(h1D_m4l_SR_2P2F_2mu2e.Integral()))
print("--------------------------------")

print("--------------------------------")
print("h1D_m4l_SR_3P1F = " + str(h1D_m4l_SR_3P1F.Integral()))
print("h1D_m4l_SR_3P1F_4e = " + str(h1D_m4l_SR_3P1F_4e.Integral()))
print("h1D_m4l_SR_3P1F_4mu = " + str(h1D_m4l_SR_3P1F_4mu.Integral()))
print("h1D_m4l_SR_3P1F_2e2mu = " + str(h1D_m4l_SR_3P1F_2e2mu.Integral()))
print("h1D_m4l_SR_3P1F_2mu2e = " + str(h1D_m4l_SR_3P1F_2mu2e.Integral()))
print("--------------------------------")

print("--------------------------------")
print("h1D_m4l_SR_tot = " + str(h1D_m4l_SR_tot.Integral()))
print("h1D_m4l_SR_tot_4e = " + str(h1D_m4l_SR_tot_4e.Integral()))
print("h1D_m4l_SR_tot_4mu = " + str(h1D_m4l_SR_tot_4mu.Integral()))
print("h1D_m4l_SR_tot_2e2mu = " + str(h1D_m4l_SR_tot_2e2mu.Integral()))
print("h1D_m4l_SR_tot_2mu2e = " + str(h1D_m4l_SR_tot_2mu2e.Integral()))
print("--------------------------------")