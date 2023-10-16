#!/bin/bash
#SBATCH --job-name=singularity_epoch2d_test       # Job name
#SBATCH --mail-type=END,FAIL                      # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=myemail@york.ac.uk            # Where to send mail
#SBATCH --ntasks=2                                # Run n tasks...
#SBATCH --cpus-per-task=1                         # ...with one core each
#SBATCH --mem-per-cpu=600mb                       # Memory per processor
#SBATCH --time=00:01:00                           # Time limit hrs:min:sec
#SBATCH --output=singularity_epoch2d_test_%j.log  # Standard output and error log
#SBATCH --account=my-proj-account                 # Project account
 
module purge
module load mpi/OpenMPI tools/Singularity
export PMIX_MCA_psec=^munge # Not sure what this does exactly, but it fixes some warnings!

# TODO Figure out proper linkage with MPI libraries

echo "Running singularity epoch test on ${SLURM_NTASKS} CPU cores"
  
./run_epoch.py singularity -d 2 -o ./output
# or...
mpirun -n ${SLURM_NTASKS} singularity exec --bind ./output:/output oras://ghcr.io/plasmafair/epoch.sif:latest run_epoch -d 2 -o /output

# TODO srun not working on Viking, not sure if this is a machine-specific problem
