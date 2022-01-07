#!/bin/bash
#SBATCH --job-name=remove_dup_cpp
#SBATCH --output=remove_dup_cpp.out
#SBATCH --error=remove_dup_cpp.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=12:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=64gb
#SBATCH --partition=bigmem
#SBATCH --nodes=2

pwd; hostname; date
source ~/.bash_profile
cd /blue/avery/rosedj1/ZplusXpython/
conda activate my_root_env
source setup.sh
echo 'Packages loaded.'
echo 'Starting script...'

time root -l /blue/avery/rosedj1/ZplusXpython/skimmers/remove_duplicates.C
# python /blue/avery/rosedj1/ZplusXpython/skimmers/remove_duplicates.py > /cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates.out

echo 'Script finished!'