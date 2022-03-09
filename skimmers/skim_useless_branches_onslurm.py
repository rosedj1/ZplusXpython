"""Submit SLURM jobs which remove TTree branches from xBF NTuples.
==============================================================================
Syntax: python <this_script>.py
Notes:
    * Check the "User Parameters" section.
    * Check the branches to be saved in your `cpp_skim_template`.
    * One SLURM job is submitted per root file.
Author: Jake Rosenzweig
Created: 2022-02-15
Updated: 
==============================================================================
"""
import sys
import os
sys.path.append('/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/')
from sidequests.classes.templatemanager import TemplateManager
from Utils_Python.SlurmManager import SLURMSubmitter
from Utils_Python.Utils_Files import replace_value

#=== Begin User Parameters. ===#
cpp_skim_template = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/skim_useless_branches_template.C"

indir = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2017/fullstats"
ls_rootfiles = [
    # "DoubleEG_2017_MiniAODv2.root",
    "DoubleMuon_2017_MiniAODv2_missing2LumiSect.root",
    "MuonEG_2017_MiniAODv2.root",
    "SingleElectron_2017_MiniAODv2.root",
    "SingleMuon_2017_MiniAODv2_missing1LumiSect.root",
]
path_to_tree = "Ana/passedEvents"
n_evts = -1  # Use -1 to process all events.
mem = 8  # GB to request on SLURM.

outdir = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2017/fullstats/skimmedbranches/fewbranches"
#=== End User Parameters. ===#

def skim_on_slurm():
    for rf in ls_rootfiles:
        infile = os.path.join(indir, rf)
        outfile = os.path.join(outdir, rf)
        basename = rf.rstrip(".root")

        tm = TemplateManager(input_template=cpp_skim_template)
        cpp_skim_name, ext = cpp_skim_template.split(".")
        assert all("." not in x for x in [cpp_skim_name, ext])
        new_skim_file = f"{cpp_skim_name}_{basename}.{ext}"
        tm.duplicate_template(output_template=new_skim_file)

        replace_value("INFILE", infile, new_skim_file)
        replace_value("OUTFILE", outfile, new_skim_file)
        replace_value("PATH_TO_TREE", path_to_tree, new_skim_file)
        replace_value("N_EVENTS", n_evts, new_skim_file)

        slurm = SLURMSubmitter(verbose=True)
        slurm.prep_directives(job_name=f"skimbranches_{basename}",
                            output_txt=outfile.replace(".root", ".out"),
                            email="rosedj1@ufl.edu",
                            time="08:00:00",
                            acct="avery",
                            burst=False,
                            mem=(mem, "gb"),
                            partition="bigmem", #"hpg2-compute",
                            nodes=1)
        new_skim_file_funcname = os.path.basename(new_skim_file).split(".")[0]
        replace_value("FUNC_NAME", new_skim_file_funcname, new_skim_file)

        cmdtup = (f"""root -l {new_skim_file}""",)
        slurm_script = outfile.replace(".root", ".sbatch")
        slurm.make_slurm_script(slurm_outpath=slurm_script, cmdtup=cmdtup)
        slurm.submit_script(slurm_script)

if __name__ == '__main__':
    skim_on_slurm()