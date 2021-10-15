#!/bin/bash
#SBATCH --job-name=
#SBATCH --output=
#SBATCH --error=
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
cd /blue/avery/rosedj1/HiggsMassMeasurement/
conda activate my_root_env
source setup.sh
echo 'Packages loaded.'
echo 'Starting script...'

# Code here.

echo 'Script finished!'