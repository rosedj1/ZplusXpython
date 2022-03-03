#!/bin/bash
#SBATCH --job-name=remove_duplicates_Data2016UL_preVFP
#SBATCH --output=/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/remove_duplicates_Data2016UL_preVFP.out
#SBATCH --error=/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/remove_duplicates_Data2016UL_preVFP.err
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
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/
conda activate my_root_env
source setup_hpg.sh
echo 'Packages loaded.'
echo 'Starting script...'

# time root -l /blue/avery/rosedj1/ZplusXpython/skimmers/remove_duplicates.C
python /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/remove_duplicates.py > /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/remove_duplicates_Data2016UL_preVFP.txt

echo 'Script finished!'