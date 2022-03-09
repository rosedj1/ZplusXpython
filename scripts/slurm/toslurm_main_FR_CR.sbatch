#!/bin/bash
#SBATCH --job-name=WZ_skim
#SBATCH --output=WZ_skim
#SBATCH --error=WZ_skim
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=08:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=64gb
#SBATCH --partition=bigmem
#SBATCH --nodes=1

pwd; hostname; date
source ~/.bash_profile
#cd /cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/
conda activate my_root_env
source setup_hpg.sh
echo 'Packages loaded.'
echo 'Starting script...'

# Code here.
python /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/scripts/main_FR_CR.py

echo 'Script finished!'
