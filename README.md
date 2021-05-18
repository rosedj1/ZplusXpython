# Reducible Background Studies

This repo contains scripts to:

- Calculate lepton fake rates.
- Remove the WZ contribution.
- Estimate the total non-ZZ background contribution.
- Plot the resulting distributions.

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
