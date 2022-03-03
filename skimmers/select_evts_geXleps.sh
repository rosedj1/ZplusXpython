#!/bin/bash
#=============================================================================
# Purpose: Run the Python script `select_evts_geXleps.py` on SLURM.
# Syntax: `./<this_script>.sh`
# Notes: Only used on 1 root file at a time, so 1 SLURM job per root file.
# Author: Jake Rosenzweig
# Created: 2022-02-26
# Updated: 2022-02-27
#=============================================================================
infile_root='root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshzz4l/xBF/Run2/UL/MC/20165/ZZTo4L_M125_20165_skimmed.root'
outfile_root='/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/MC/2016/skimge3leps/ZZTo4L_M125_20165_skimmed.root'
outdir_logs="/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output"

py_template='/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/select_evts_geXleps_template.py'
sbatch_template='/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/select_evts_geXleps_onslurm_template.sbatch'

tree_path='passedEvents'
n_leps_skim=3
break_at=-1
ovewrite=0
print_every=1000000

###############
#=== Main. ===#
###############
function make_new_dir {
    # If 
    # Arg1: New directory to be created.
    if [  ! -d ${1} ]; then
        mkdir ${1}
        echo "Created ${1}."
    fi
}

make_new_dir ${outdir_logs}
make_new_dir $( dirname ${outfile_root} )

echo "Storing new SLURM script and Python script in:"
echo "${outdir_logs}"

function make_filename_in_log_dir {
    # Return the full path of a file: logdir/filename.ext
    # Arg1: logdir
    # Arg2: path/to/file or just file name.
    filename=$( basename ${2} )
    echo ${1}/${filename}
}

echo "Using Python template..."
echo "${py_template}"
echo "...to create new Python script:"
new_pyscript=${py_template/".py"/"_copy.py"}
new_pyscript=$( make_filename_in_log_dir ${outdir_logs} ${new_pyscript} )
echo "${new_pyscript}"
cp ${py_template} ${new_pyscript}

echo "Replacing words in new Python script."
sed -i "s|INFILE|${infile_root}|" ${new_pyscript}
sed -i "s|OUTFILE|${outfile_root}|" ${new_pyscript}
sed -i "s|TREE_PATH|${tree_path}|" ${new_pyscript}
sed -i "s|N_LEPS_SKIM|${n_leps_skim}|" ${new_pyscript}
sed -i "s|BREAK_AT|${break_at}|" ${new_pyscript}
sed -i "s|OVERWRITE|${ovewrite}|" ${new_pyscript}
sed -i "s|PRINT_EVERY|${print_every}|" ${new_pyscript}

echo "Using SLURM template..."
echo "${sbatch_template}"
echo "...to create new SLURM script:"
new_sbatch=${sbatch_template/".sbatch"/"_copy.sbatch"}
new_sbatch=$( make_filename_in_log_dir ${outdir_logs} ${new_sbatch} )
echo "${new_sbatch}"
cp ${sbatch_template} ${new_sbatch}

echo "Replacing words in new SLURM script."
sample=$( basename -s '.root' ${infile_root} )
job_name="select_evts_ge${n_leps_skim}leps_${sample}"
echo "This job name: ${job_name}"
sed -i "s|NAME|${job_name}|g" ${new_sbatch}
sed -i "s|NEW_PYSCRIPT|${new_pyscript}|" ${new_sbatch}
sed -i "s|LOGDIR|${outdir_logs}|" ${new_sbatch}  # Output txt file.

sbatch ${new_sbatch}