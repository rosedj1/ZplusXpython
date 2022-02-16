"""`hadd` NTuples (produced by xBF Analyzer) on SLURM.
==============================================================================
Syntax: python <this_script>.py
Notes: Put the data set names to be hadded into `datasets`.
    * Names should NOT contain the year.
        E.g., just put 'MuonEG'
        The year will be appended.
    * 
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

#=== Hadd files of a common data set (e.g. MuonEG A-D) ===#
assert not isinstance(datasets, str)
for dataset in datasets:
    inglob = f"{os.path.join(indir_t2, dataset)}/crab_{dataset}*/*/*/{dataset}*.root"
    outfile = os.path.join(outdir, f"{dataset}_{year}.root")
    if len(suffix_to_outfile) > 0:
        outfile = outfile.replace(".root", f"{suffix_to_outfile}.root")

    slurm_script = os.path.join(outdir, f"{dataset}_{year}.sbatch")

    slurm = SLURMSubmitter(verbose=True)
    slurm.prep_directives(job_name=f"{dataset}_{year}",
                        output_txt=os.path.join(outdir, f"{dataset}_{year}.out"),
                        email="rosedj1@ufl.edu",
                        time="08:00:00",
                        acct="avery",
                        burst=False,
                        mem=(64, "gb"),
                        partition="bigmem", #"hpg2-compute",
                        nodes=1)
    cmdtup = (f"""hadd {outfile} {inglob}""", )
    slurm.make_slurm_script(slurm_outpath=slurm_script, cmdtup=cmdtup)
    slurm.submit_script(os.path.join(outdir, f"{dataset}_{year}.sbatch"))
