# Epoch Containers

This repository contains tools and information for building/running [Epoch][epoch] using
Docker/Singularity containers.

## Introduction

Containers package up software and dependencies so that code compiled on one machine
can be reliably run on others. When used in conjunction with scientific software, they
allow researchers to run code without needing to build it themselves, and they make
it much easier to share reproducible workflows.

We provide support for two container platforms: [Docker][docker] and
[Singularity][singularity] (or Apptainer). Docker is the most widely used platform, and
has been used here to build a 'base image' of Epoch on which other tools may be created.
Singularity is an alternative container platform that was designed to be useable on HPC
systems, so unlike Docker it can be run on multi-node architectures using MPI without
issue.

## Usage

Users of this software do not need to build containers themselves. Instead, they will
only need to copy the Python module `run_epoch.py` in the root directory of this
repository. If we run this with the argument `--help`, we can see a list of possible
commands:

```bash
$ python3 run_epoch.py --help
```

### Docker

We can run the Docker container using:

```bash
$ python3 run_epoch.py docker -d 2 -o ./my_epoch_run
```

Here, `-d` specifies the number of dimensions in the simulation, and `-o` specifies the
output directory (which should contain `input.deck`). Users can switch on QED effects by
also providing the `--photons` argument. The output directory should not be the current
working directory. To see a full list of possible options, we can also supply the
`--help` option:

```bash
$ python3 run_epoch.py docker --help
```

### Singularity/Apptainer

Singularity containers can be run similarly to Docker containers, but with extra options
for specifying the number of MPI processes to run:

```python
$ python3 run_epoch.py singularity -d 2 -o ./my_epoch_run -n 4
```

The extra argument `-n` specifies the number of processes to run.

On HPC systems, you will need to load Singularity/Apptainer and OpenMPI first. For
example, on Viking at the University of York, this requires:

```bash
$ module load OpenMPI Apptainer
```

Some machines may need to load a specific version of OpenMPI -- the version in the
container is 4.1.2.

Please see the `./viking` directory for help with running on Viking. This also contains
advice for processing the SDF files produced by Epoch.

## Licensing

This repo is licensed under the GNU GPLv3 license, as it contains files from the
similarly-licensed [Epoch repository][epoch_repo].

[docker]: https://docs.docker.com/
[singularity]: https://docs.sylabs.io/guides/3.11/user-guide/
[epoch]: https://epochpic.github.io/
[epoch_repo]: https://github.com/Warwick-Plasma/epoch
