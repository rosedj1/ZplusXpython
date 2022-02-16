#!/bin/bash
#SBATCH --job-name=DoubleEG_skimbranches
#SBATCH --output=DoubleEG_skimbranches.out
#SBATCH --error=DoubleEG_skimbranches.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=08:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=8gb
#SBATCH --partition=bigmem
#SBATCH --nodes=1

pwd; hostname; date
source ~/.bash_profile
conda activate my_root_env
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/
source setup_hpg.sh
echo 'Packages loaded.'

echo 'Starting script...'
time root -l /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/skim_useless_branches.C

echo 'Script finished!'