# Reducible Background Studies

This repo contains scripts to:

- Skim NTuples.
- Retrieve Data and MC info.
- Calculate lepton fake rates.
- Remove the WZ contribution.
- Estimate the total non-ZZ background contribution.
- Plot the resulting distributions.

---

## Skim NTuples

1. Use the UFHZZ4LAnalyzer to skim the MiniAOD files (Data or MC).

1. Combine files (using `hadd`) of the same process (e.g., MuonEG runs A-D) with:
   - `scripts/hadders/haddfiles_on_slurm_step01_runstogether.py`
      - Submits `hadd` jobs to SLURM.
      - **NOTE:** If you get an error like the one below
   then first get rid of extraneous branches using
   `skimmers/skim_useless_branches.C`; then resume `hadd`ing.

   ```bash
   Error in <TBufferFile::WriteByteCount>: bytecount too large (more than 1073741822)
   ```
   
1. Skim any extraneous branches to reduce file size:
   - `skimmers/skim_useless_branches_onslurm.py`
   - **NOTE:** Make sure you keep the branches you want in the skimmer template:
      - `skimmers/skim_useless_branches_template.C`

1. Now `hadd` together the "AllRun" files with:
   - `scripts/hadders/haddfiles_on_slurm_step02_datasetstogether.py`
      - Submits the one `hadd` job to SLURM.

1. Remove duplicate events (same `Run:Lumi:Event`) with one of:
   - `skimmers/remove_duplicates.py`
   - `skimmers/remove_duplicates_Filippo.C`
   - **NOTE:** The Python script may be faster than the C++ one:

      | Script | user time | sys time |  TOTAL time |
      | ---    | ---       | ---      | --- |
      | Python | 19m50.211s | 0m30.203s | **20m20.413s** |
      | C++    | 21m22.529s | 0m21.924s | 21m44.453s | 
   
1. Combine Data files into a single file (e.g. `Data2018_NoDuplicates.root`).
   - If you get the `'bytecount too large'` error, consider first trimming
   branches, then `hadd` together, and THEN remove duplicates.

---

## Retrieving Data and MC Info

### Cross Sections for MC

You will find many different values for cross section.
After some comparisons and asking the experts, it seems it is best to use the [values recommended](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns#DY_Z) by the Higgs MC working group.

For historical purposes, let it be noted that the CJLST group uses
[these values](https://github.com/CJLST/ZZAnalysis/blob/Run2_CutBased/AnalysisStep/test/prod/samples_2018_MC.csv).

You can also find cross sections associated with the generated samples, found on McM:

1. Go to https://cms-pdmv.cern.ch/mcm/ > Request > Output Dataset
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

### Retrieve Integrated Lumi (L_int) for Data

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

```python
h = f.Get('Ana/sumWeights')
h.GetBinContent(1)
```
   
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

<!-- 1. Select Z+L events with:
   - `skimmers/apply_redbkg_evt_selection_vxbs.C`
   - Apply the skimmer to multiple samples with:
      - `skimmers/skim_ZL_ZLL_4P_CR.sh` -->

---

## WZ Removal

Since the WZ process produces 3 prompt leptons,
we must subtract this from the Z+L CR:

```bash
python WZremoval_from_FR_comp.py
```

Plot the fake rate histograms (before and after WZ removal) with:

```bash
scripts/plotters/plot_fakerate_hists.py
```

---

## Estimate Reducible Background

<!-- ### Optional - Add New Branches

Add new branches like (`is2P2F`, `isMCzz`, `fr2`, etc.) with:

```bash
skimmers/skim_ZLL_addbranches.py
``` -->

Use Data and Monte Carlo ZZ->4l (irreducible background) to estimate the
RB.
Choose a framework to work with:

- Vukasin's Framework.
- Jake's Framework.

### Jake's Framework

Select "OS Method" events (2P2F and 3P1F) with:
   - `skimmers/select_evts_2P2plusF_3P1plusF.py`

### Vukasin's Framework

```bash
python main_estimateZX_ntuples.py
```

- Calls `estimateZX.py`.
- Produces final distributions.

Print out the estimates (integrals) within the histograms using:

```bash
python estimate_final_numbers_macro.py
```

#### Plot the 2P2F/3P1F distributions

```bash
python plotting_macros.py
```
