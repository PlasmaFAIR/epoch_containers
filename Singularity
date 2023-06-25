Bootstrap: docker
From: ubuntu:22.04

%help

    This is a Singularity container for running Epoch. It contains several
    Epoch installations for 1D, 2D, and 3D, and variations with different
    combinations of compiler flags switched on.

    Before running Epoch via this container, first load the Singularity and
    OpenMPI modules:

        module load tools/Singularity mpi/OpenMPI

    It can then be run using:

        echo <outdir> | mpirun -n <nprocs> singularity exec <img> <exe>

    The parts in <angle brackets> must be filled in by you:

        - <outdir>: Epoch prompts the user to input the output directory
          manually when running. As we need to be able to run Epoch in an
          automated fashion, we can get around this by piping the name of
          the output directory. If we want to write to the current
          directory, this can just be '.'. Your "input.deck" files should
          be located here.
        - <nprocs>: The number of MPI processes to run on. This should be
          set to "${SLURM_NTASKS}" in most cases.
        - <img>: The Singularity image file, or the URI of an uploaded
          image.
        - <exe>: The executable to run. These are defined inside the
          container, so won't be visible on your host system. The
          executables include:
            - epoch1d
            - epoch2d
            - epoch3d
            - epoch1d_qed
            - epoch2d_qed
            - epoch3d_qed
          The 'qed' executables have been compiled with the PHOTONS flag
          switched on. 

    To look around inside the container, try:

        singularity run <img>

    The Epoch repository can be located in the /epoch directory.

    An example sbatch script might look like:

        #!/bin/bash
        #SBATCH --job-name=singularity_epoch         # Job name
        #SBATCH --mail-type=END,FAIL                 # Mail events (NONE, BEGIN, END, FAIL, ALL)
        #SBATCH --mail-user=usr501@york.ac.uk        # Where to send mail
        #SBATCH --ntasks=2                           # Run n tasks...
        #SBATCH --cpus-per-task=1                    # ...with one core each
        #SBATCH --mem-per-cpu=1gb                    # Memory per processor
        #SBATCH --time=00:05:00                      # Time limit hrs:min:sec
        #SBATCH --output=singularity_epoch_%j.log    # Standard output and error log
        #SBATCH --account=my_proj_account            # Project account
         
        module purge
        module load mpi/OpenMPI tools/Singularity
        echo . | mpiexec -n ${SLURM_NTASKS} singularity exec epoch.simg epoch2d

    Make sure you have your deck in the output directory with the name "input.deck"
	    

%post

    # Install requirements 
    apt-get update -y
    apt-get upgrade -y
    apt-get install git make python3 libgtk2.0-dev gfortran \
        openmpi-bin openmpi-common libopenmpi-dev -y

    # Create symlink so calls to 'python' redirect to 'python3'.
    # Needed because a lot of the Epoch build processes rely on Python,
    # but don't differentiate python2 and python3.
    ln -s /usr/bin/python3 /usr/bin/python

    # Get epoch files. The --recursive is important to get the SDF submodule
    git clone --recursive https://github.com/Warwick-Plasma/epoch

    # Create common directory for all executables to live in
    cd epoch
    mkdir bin

    # Compile each version of Epoch in turn

    cd /epoch/epoch1d
    make -j COMPILER=gfortran
    mv bin/epoch1d /epoch/bin/epoch1d
    make clean

    cd /epoch/epoch2d
    make -j COMPILER=gfortran
    mv bin/epoch2d /epoch/bin/epoch2d
    make clean

    cd /epoch/epoch3d
    make -j COMPILER=gfortran
    mv bin/epoch3d /epoch/bin/epoch3d
    make clean

    # Versions with QED activated

    cd /epoch/epoch1d
    cp Makefile Makefile.original
    sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
    make -j COMPILER=gfortran
    mv bin/epoch1d /epoch/bin/epoch1d_qed
    make clean
    mv Makefile.original Makefile

    cd /epoch/epoch2d
    cp Makefile Makefile.original
    sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
    make -j COMPILER=gfortran
    mv bin/epoch2d /epoch/bin/epoch2d_qed
    make clean
    mv Makefile.original Makefile

    cd /epoch/epoch3d
    cp Makefile Makefile.original
    sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
    make -j COMPILER=gfortran
    mv bin/epoch3d /epoch/bin/epoch3d_qed
    make clean
    mv Makefile.original Makefile

%environment

    export PATH="$PATH:/epoch/bin"

%runscript

    /bin/bash
