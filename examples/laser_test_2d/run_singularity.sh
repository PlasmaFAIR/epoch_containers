#!/bin/bash

# To be run on HPC systems.
# Only run short tests on login nodes! Use the sbatch example for real runs.
# This example is aimed at the University of York Viking cluster. Modules names will
# differ on other systems.

module purge
module load mpi/OpenMPI tools/Singularity

mpirun -n 2 singularity exec library://liampattinson/epoch/epoch.sif:latest -d 2 -o .
