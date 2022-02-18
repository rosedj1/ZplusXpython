"""`hadd` NTuples (produced by xBF Analyzer) on SLURM.
==============================================================================
Syntax: python <this_script>.py
Notes:
    * Outfile gets placed in same dir as infiles.
    * Put the data set names to be hadded into `datasets`.
    * Names should NOT contain the year.
        E.g., just put 'MuonEG'
        The year will be appended.
    * Combines the "AllRun" data sets together:
        E.g., `hadd new.root EGamma_2017.root DoubleMuon_2017.root MuonEG_2017.root`
Author: Jake Rosenzweig
Created: 2021-Oct-ish
Updated: 2022-02-15
==============================================================================
"""
import sys
import os
sys.path.append('/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement')
from Utils_Python.SlurmManager import SLURMSubmitter

indir = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2017/fullstats/skimmedbranches/fewbranches"
outfile_name = "Data_2017_UL_MiniAODv2_skim2L.root"
mem = 64  # RAM in GB.

#################
#=== 2017 UL ===#
#################
ls_infiles = [
    "DoubleEG_2017_MiniAODv2.root",
    "DoubleMuon_2017_MiniAODv2_missing2LumiSect.root",
    "MuonEG_2017_MiniAODv2.root",
    "SingleElectron_2017_MiniAODv2.root",
    "SingleMuon_2017_MiniAODv2_missing1LumiSect.root",
]

# Hadd full-stat data sets into single file.
outfile = os.path.join(indir, outfile_name)

def hadd_on_slurm(indir, outfile, ls_infiles):
    """Submit a single job to SLURM that hadds data sets."""

    slurm_script = os.path.join(
        indir, outfile_name.replace(".root", ".sbatch")
        )

    slurm = SLURMSubmitter(verbose=True)
    job_name = f"hadd_{outfile_name.rstrip('.root')}"
    slurm.prep_directives(job_name=job_name,
                        output_txt=os.path.join(indir, f"{job_name}.out"),
                        email="rosedj1@ufl.edu",
                        time="08:00:00",
                        acct="avery",
                        burst=False,
                        mem=(mem, "gb"),
                        partition="bigmem", #"hpg2-compute",
                        nodes=1)
                        
    ls_names_as_str = ' '.join(ls_infiles)
    cmdtup = (
        f"""cd {indir}""",
        f"""hadd {outfile} {ls_names_as_str}""",
        )
    
    slurm.make_slurm_script(
        slurm_outpath=slurm_script,
        cmdtup=cmdtup,
        )
    slurm.submit_script(slurm_script)

if __name__ == '__main__':
    hadd_on_slurm(indir, outfile, ls_infiles)