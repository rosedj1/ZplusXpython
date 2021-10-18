# Reducible Background Studies

This repo contains scripts to:

- Skim NTuples.
- Retrieving Data and MC info.
- Calculate lepton fake rates.
- Remove the WZ contribution.
- Estimate the total non-ZZ background contribution.
- Plot the resulting distributions.

---

## Skim NTuples

1. Use the UFHZZ4LAnalyzer to skim the MiniAOD files (Data or MC).
1. Combine files (using `hadd`) of the same process (e.g., MuonEG runs A-D) with:
   - `hadders/haddfiles_on_slurm.ipynb` (submits `hadd` jobs to SLURM)
1. Skim only the important branches with:
   - `skimmers/apply_redbkg_evt_selection_vxbs`.
   - Apply the skimmer to multiple samples with:
      - `skimmers/skim_ZL_ZLL_4P_CR.sh`
1. Combine data files into a single file (e.g. `Data2018_Duplicates.root`) using `hadd`.
   - You can probably do it locally, but if the files are still large, use:
      - `hadders/haddfiles_on_slurm.ipynb`
1. Remove duplicate events with:
   - `skimmers/remove_duplicates.py`
<!-- 1. [OPTIONAL] Combine Data files into a single file (e.g. `Data_*_NoDuplicates.root`).
   - May not be possible due to memory issues! May get `'bytecount too large'` error. 
   - Work around: skim these big files, hadd together, and THEN remove duplicates. -->

---

## Retrieving Data and MC Info

### Cross Sections for MC

You will find many different values for cross section.
After some comparisons and asking the experts, it seems it is best to use the [values recommended](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns#DY_Z) by the Higgs MC working group.

For historical purposes, let it be noted that the CJLST group uses
[these values](https://github.com/CJLST/ZZAnalysis/blob/Run2_CutBased/AnalysisStep/test/prod/samples_2018_MC.csv).

You can also find cross sections associated with the generated samples, found on McM:

1. Going to https://cms-pdmv.cern.ch/mcm/ > Request > Output Dataset
1. Search for your data set by providing the data set name.
2. Under 'PrepId' column, copy the name of the file.
3. Under 'Dataset name' column, click on the icon to the right of the name
of the data set (it looks like a file explorer).
4. Show all results (bottom-righthand corner).
1. Search (Ctrl-F) for the PrepId.
Even if a few options are found, they should all have the same LHEGS
file. Click this LHEGS file name.
1. Then Select View > Generator parameters.
The cross section is in the 'Generator Parameters' column to the right.

Put cross sections in `constants/analysis_params.py`.

### L_int for Data

Go to `lxplus` and do:

```bash
crab report -d <crab_dir>
```

This produces the file `<crabdir>/results/processedLumis.json`.
Then do:

```bash
brilcalc lumi -c web -i <crabdir>/results/processedLumis.json
```

Add up the **L_int** for all data sets of a _single kind_ (e.g. only SingleMuon).
Each data set should give a similar value as the other data sets.
Take the average or the min and put this number in
`constants/analysis_params.py`

### Sum GenWeights for MC

Get the effective number of MC events (the sum of gen weights) with:
   - `scripts/helpers/print_sumWeights.py`
   
Put the number of events in `constants/analysis_params.py`.

---

## Calculate Fake Rates

Use the Z+L background control region (CR) to calculate how often a non-prompt
lepton passes tight selection:

```bash
python scripts/main_FR_CR.py
```

- Produces a `.root` file which contains histograms of the total number of
leptons which passed tight selection, total number of loose leptons, and their
ratio (fake rate) in bins of pT(lep3).
- Calls `analyzeZX.py`.
- Uses `MC_composition.py` to call `PartOrigin()`.
   -  Checks the type of fake procedure (checking the ID of the parent).

---

## WZ Removal

Since the WZ process produces 3 prompt leptons,
we must subtract this from the Z+L CR:

```bash
python WZremoval_from_FR_comp.py
```

Plot the fake rate histograms (before and after WZ removal) with:

```bash
ZplusXpython/scripts/plotters/plot_fakerate_hists.py
```

### Optional - Add New Branches

Add new branches like (`is2P2F`, `isMCzz`, `fr2`, etc.) with:

```bash
skimmers/skim_ZLL_addbranches.py
```

---

## Estimate Non-ZZ Contribution

Use Data and Monte Carlo ZZ->4l (irreducible background) to estimate the
non-ZZ contribution:

```bash
python main_estimateZX_ntuples.py
```

- Calls `estimateZX.py`.
- Produces final distributions.

Print out the estimates (integrals) within the histograms using:

```bash
python estimate_final_numbers_macro.py
```

---

## Plot the 2P2F/3P1F distributions

```bash
python plotting_macros.py
```
