# Epoch Containers

Tools and information for building/running [Epoch][epoch] using Docker/Singularity
containers.

## Introduction

Containers package up software and dependencies so that code compiled on one machine
can be reliably run on others. When used in conjunction with scientific software, they
allow researchers to run code without needing to build it themselves, and they make
it much easier to share reproducible workflows.

We provide support for two container platforms: [Docker][docker] and
[Singularity][singularity]. Docker is the most widely used platform, and has been used
here to build a 'base image' of Epoch on which other tools may be built. Singularity is
an alternative container platform that was designed from the ground up to be useable on
HPC systems, so unlike Docker it can be run on multi-node architectures using MPI
without issue.

## Usage

Users of this software do not need to build containers themselves. Instead, they will
only need to copy the Python module `run_epoch.py` in the root directory of this
repository. To run the Docker container, try:

```python
$ python3 run_epoch.py docker -d 2 -o ./my_epoch_run
```

Here, `-d` specifies the number of dimensions to run (e.g. here we are performing a 2D
simulation), `-o` specifies the output directory (which should contain `input.deck`).
Users can switch on QED effects by also providing the `--photons` argument. The output
directory should not be the current working directory.

Similarly, to run the Singularity container, try:

```python
$ python3 run_epoch.py singularity -d 2 -o ./my_epoch_run -n 4
```

The extra argument `-n` specifies the number of processes to run, which uses OpenMPI.
On HPC systems, you will need to load Singularity and OpenMPI first. For example, on
Viking at the University of York, this requires:

```bash
$ module load tools/Singularity mpi/OpenMPI
```

## Running on Viking (University of York)

To run Epoch on Viking, first create a directory within `~/scratch` in which you
want to run your code:

```
$ ssh <userid>@viking.york.ac.uk
$ mkdir -p ~/scratch/epoch/output
$ cd ~/scratch/epoch
```

You'll need to ensure your `input.deck` file is within this directory:

```bash
$ # From your own machine
$ scp input.deck <userid>@viking.york.ac.uk:/users/<userid>/scratch/epoch/output
```

To run the Singularity container, you'll need to load the following modules:

```bash
$ module load tools/Singularity mpi/OpenMPI
```

You may then run the helper script as described above.

Note that you should only run short tests on the login nodes. To run longer jobs, you'll
want to create a Slurm job file. See the `./examples` folder for an example job script
`run_sbatch.sh` and an example `input.deck`. Once we have a job script, we can submit a
job using:

```bash
$ sbatch run_sbatch.sh
```

We can check the progress of our job using:

```bash
$ squeue -u <userid>
```

## Inspecting the Container

It is also possible to pull the container from the remote repo:

```bash
$ singularity pull epoch.sif oras://ghcr.io/plasmafair/epoch.sif:latest
```

This will download the container image to the file `epoch.sif` (`.sif` denoting a
'Singularity Image Format' file). You can then use `epoch.sif` in place of
`library://account/repo/container` in any of the commands above.

If you want to inspect the container, we can use:

```bash
$ singularity shell epoch.sif
```

## Analysing code output

It is recommended to analyse Epoch output data on your own machine rather than on an HPC
machine:

```bash
$ scp <userid>@viking.york.ac.uk:/users/<userid>/scratch/epoch/*.sdf .
```

You'll need a particular Python library to read `.sdf` files, and this is packaged with
Epoch itself. To install this library, try:

```bash
$ git clone https://github.com/Warwick-Plasma/epoch
$ cd epoch/epoch1d
$ make sdfutils
```

Note that the SDF Python library is not packaged with modern best-practices in mind
(i.e. using virtual environments, uploading packages to PyPI/conda-forge). It will
install to `~/.local/lib/python3.x/site-packages` regardless of whether you're in a
`venv` or `conda` environment. If you feel you know what you're doing, you can manually
copy/move the installed files to the environment of your choice after installing, but
it's recommended to just use the base user environment.

Please see the [Epoch docs][epoch] for info on using SDF analysis tools.


## Licensing

This repo is licensed under the GNU GPLv3 license, as it contains files from the
similarly-licensed [Epoch repository][epoch_repo].

[docker]: https://docs.docker.com/
[singularity]: https://docs.sylabs.io/guides/3.11/user-guide/
[epoch]: https://epochpic.github.io/
[epoch_repo]: https://github.com/Warwick-Plasma/epoch
