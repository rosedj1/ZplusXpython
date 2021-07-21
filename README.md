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
1. Combine files (using `hadd`) of the same process (e.g., MuonEG runs A-D).
1. Remove duplicate events from Data with:
`skimmers/removeDuplicatesH4l2018.py`.
1. Combine Data files into a single file (e.g. `Data_*_NoDuplicates.root`).
1. Select only the important branches with:
`skimmers/apply_preselections_vxbs.C`.

---

## Retrieving Data and MC Info

### Cross Sections for MC

MCM xs vals obtained by going to:
https://cms-pdmv.cern.ch/mcm/ > Request > Output Dataset >
Search for your data set by providing the data set name.
Under 'PrepId' column, copy the name of the file.
Under 'Dataset name' column, click on the icon to the right of the name
of the data set (it looks like a file explorer).
Show all results (bottom-righthand corner).
Search (Ctrl-F) for the PrepId.
Even if a few options are found, they should all have the same LHEGS
file. Click this LHEGS file name.
Then Select View > Generator parameters.
The cross section is in the 'Generator Parameters' column to the right.

Put the cross section into the dict in `physics.py`.

### L_int for Data

Go to `lxplus` and do:

```bash
crab report -d <crab_dir>
```

This produces the file `<crabdir>/results/processedLumis.json`.
It also tells you the 'Number of events read' which is needed for scaling MC.
Put this number of events in `physics.py`.
Now do:

```bash
brilcalc lumi -c web -i <crabdir>/results/processedLumis.json
```

Add up the L_int for all data sets of a _single kind_ (e.g. only SingleMuon).
Put this number in `physics.py`

---

## Calculate Fake Rates

Use the Z+L background control region (CR) to calculate how often a non-signal
lepton passes tight selection:

```bash
python main_FR_CR.py
```

- Produces a `.root` file which contains histograms of the total number of
leptons which passed tight selection, total number of loose leptons, and their
ratio (fake rate) in bins of pT(lep3).
- Calls `analyzeZX.py`.
- Uses `MC_composition.py` to call `PartOrigin()`.
   -  Checks the type of fake procedure (checking the ID of the parent).

Plot the histograms with:
`ZplusXpython/scripts/plotters/plot_fakerate_hists.py`.

---

## WZ Removal

Since the WZ process produces 3 prompt leptons,
we must subtract this from the Z+L CR:

```bash
python WZremoval_from_FR_comp.py
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

## Plot the Histograms

```bash
python plotting_macros.py
```
