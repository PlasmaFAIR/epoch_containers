#!/bin/bash
#SBATCH --job-name=singularity_epoch2d_test       # Job name
#SBATCH --mail-type=END,FAIL                      # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=ltp511@york.ac.uk             # Where to send mail
#SBATCH --ntasks=2                                # Run n tasks...
#SBATCH --cpus-per-task=1                         # ...with one core each
#SBATCH --mem-per-cpu=600mb                       # Memory per processor
#SBATCH --time=00:01:00                           # Time limit hrs:min:sec
#SBATCH --output=singularity_epoch2d_test_%j.log  # Standard output and error log
#SBATCH --account=phys-ypirse-2019                # Project account
 
module purge
module load mpi/OpenMPI tools/Singularity
export PMIX_MCA_psec=^munge

echo "Running singularity epoch test on ${SLURM_NTASKS} CPU cores"
  
mpirun -n ${SLURM_NTASKS} singularity exec library://liampattinson/epoch/epoch.sif:latest run_epoch -d 2 -o .
