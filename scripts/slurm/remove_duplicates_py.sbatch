#!/bin/bash
#SBATCH --job-name=rmDups_Data2017UL_lep_matching_branches
#SBATCH --output=rmDups_Data2017UL_lep_matching_branches.out
#SBATCH --error=rmDups_Data2017UL_lep_matching_branches.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=03:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=40gb
#SBATCH --partition=bigmem
#SBATCH --nodes=1

pwd; hostname; date
source ~/.bash_profile
conda activate my_root_env
cd /cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/
source setup.sh
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/
source setup_hpg.sh
echo 'Packages loaded.'
echo 'Starting script...'

# Code here.
python /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/remove_duplicates.py

echo 'Script finished!'