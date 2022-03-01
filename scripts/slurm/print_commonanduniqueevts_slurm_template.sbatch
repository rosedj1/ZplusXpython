#!/bin/bash
#SBATCH --job-name=print_commonanduniqueevts_jakevsbbf
#SBATCH --output=print_commonanduniqueevts_jakevsbbf.out
#SBATCH --error=print_commonanduniqueevts_jakevsbbf.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=08:00:00
#SBATCH --account=avery
#SBATCH --qos=avery-b
#SBATCH --mem=16gb
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

echo 'Checking for valid GRID cert...'
export X509_USER_PROXY=/cmsuf/data/store/user/t2/users/rosedj1/myproxy
export X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/certificates

# Code here.
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/scripts
python print_commonanduniqueevts_jakevsbbf.py > print_commonanduniqueevts_jakevsbbf.txt

err_code=$?
if [ ${err_code} -eq 0 ]; then
    echo "Code ran successfully!"
else
    echo "Code did not run successfully (error ${err_code})."
fi
