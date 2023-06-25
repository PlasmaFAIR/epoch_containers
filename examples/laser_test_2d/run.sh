#!/bin/bash
#SBATCH --job-name=singularity_epoch_laser_test_2d       # Job name
#SBATCH --mail-type=END,FAIL                             # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=<USERID>@york.ac.uk                  # Where to send mail
#SBATCH --ntasks=2                                       # Run n tasks...
#SBATCH --cpus-per-task=1                                # ...with one core each
#SBATCH --mem-per-cpu=600mb                              # Memory per processor
#SBATCH --time=00:01:00                                  # Time limit hrs:min:sec
#SBATCH --output=singularity_epoch_laser_test_2d_%j.log  # Standard output and error log
#SBATCH --account=<PROJECT>                              # Project account
 
module load mpi/OpenMPI tools/Singularity

# suppress OpenMPI warnings
export PMIX_MCA_psec=^munge  

echo "Running singularity epoch test on ${SLURM_NTASKS} CPU cores"

# Explanation of the run script
# -----------------------------
# echo . |
#     Epoch prompts the user to input the output directory after starting. This tells
#     it to use the current directory, and since it's automated it allows us to run on
#     the scheduler.
# mpiexec -n ${SLURM_NTASKS}
#     Run the container on ${SLURM_NTASKS} jobs.
# singularity exec library://liampattinson/epoch/epoch.sif:1.0
#     Download and run the container liampattinson/epoch/epoch.sif:1.0. This can be
#     found at https://cloud.sylabs.io/library/liampattinson/epoch/epoch.sif.
#     Note that this must be `singularity exec` and not `singularity run`, as that
#     would instead open a bash shell inside the container. 
# epoch2d
#     Run the `epoch2d` executable within the container. For a list of other
#     executables, try `singularity help library://liampattinson/epoch/epoch.sif:1.0`

# Note:
# You may want to pull the container first using:
#     $ singularity pull epoch.sif library://liampattinson/epoch/epoch.sif
# Then use `epoch.sif` in place of the `library://...` part below. 

echo . | mpiexec -n ${SLURM_NTASKS} singularity exec library://liampattinson/epoch/epoch.sif epoch2d
