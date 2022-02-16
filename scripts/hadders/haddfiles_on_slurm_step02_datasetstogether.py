"""`hadd` NTuples (produced by xBF Analyzer) on SLURM.
==============================================================================
Syntax: python <this_script>.py
Notes: Put the data set names to be hadded into `datasets`.
    * Names should NOT contain the year.
        E.g., just put 'MuonEG'
        The year will be appended.
    * Combines combined-run data sets together:
        `hadd new.root EGamma_2017.root DoubleMuon_2017.root MuonEG_2017.root`
Author: Jake Rosenzweig
Created: 2021-Oct-ish
Updated: 2022-02-15
==============================================================================
"""
import sys
import os
sys.path.append('/cmsuf/data/store/user/t2/users/rosedj1/')
from HiggsMassMeasurement.Utils_Python.SlurmManager import SLURMSubmitter

indir_t2 = "/cmsuf/data/store/user/drosenzw/UFHZZAnalysisRun2/UL/Data2017/skim2L/"
outdir = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2017/fullstats/"
# Use empty string if you don't want suffix:
suffix_to_outfile = "-UL2017_MiniAODv2_skiperffunc_err"

year = 2017

#################
#=== 2017 UL ===#
#################
datasets = [
    # "DoubleEG",
    # "MuonEG",
    # "SingleElectron",
    #=== The below are missing a few jobs.
    "SingleMuon",
    "DoubleMuon",
]

##############
#=== 2018 ===#
##############
# datasets = (
#     "EGamma",
#     "DoubleMuon",
#     "MuonEG",
#     "SingleMuon"
# )

# Hadd full-stat data sets into single file.

outdir = os.path.join(indir, "noduplicates/")
outfile_name = "Data2018_NoDuplicates.root"
outfile = os.path.join(outdir, outfile_name)

infile_suffix = "_Duplicates"
datasets = (
    f"EGamma{infile_suffix}",
    f"DoubleMuon{infile_suffix}",
    f"MuonEG{infile_suffix}",
    f"SingleMuon{infile_suffix}"
)

dset_str = """"""
for dataset in datasets:
    dset_str += os.path.join(indir, f"{dataset}.root ")

slurm_script = os.path.join(indir, outfile_name.replace(".root", ".sbatch"))

slurm = SLURMSubmitter(verbose=True)
job_name = f"hadd_ZL_ZLL_4P_CR_{outfile_name.rstrip('.root')}"
slurm.prep_directives(job_name=job_name,
                    output_txt=os.path.join(indir, f"{job_name}.out"),
                    email="rosedj1@ufl.edu",
                    time="08:00:00",
                    acct="avery",
                    burst=False,
                    mem=(64, "gb"),
                    partition="bigmem", #"hpg2-compute",
                    nodes=1)
slurm.make_slurm_script(
    slurm_outpath=slurm_script,
    cmdtup=(f"""hadd {outfile} {dset_str}""", )
    )
slurm.submit_script(slurm_script)
