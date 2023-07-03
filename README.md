# Epoch Containers

Tools and information for building/running [Epoch][epoch] using Docker/Singularity
containers. This repository is targeted at users of the Viking HPC cluster at the
University of York, but the contents may be of use to other Epoch users.

## Introduction

Containers package up software and dependencies so that code compiled on one machine
can be reliably run on others. When used in conjunction with scientific software, they
allow researchers to run code without needing to build it themselves, and they make
it is much easier to share reproducible workflows.

We provide support for two container platforms: [Docker][docker] and
[Singularity][singularity]. Docker is the most widely used platform, and
has been used here to build a 'base image' of Epoch on which other tools may be built.
Singularity is an alternative that was designed from the ground up to be useable on
HPC systems, so unlike Docker it can be run on multi-node architectures using MPI
without issue.

## Running Epoch with Docker

To run Epoch on your own machine, you'll first need to install Docker if you don't have
it already.

The Epoch Docker container can be found at `ghcr.io/liampattinson/epoch:latest`.
To run it, try:

```bash
$ docker run --rm -v /path/to/output/dir:/output \
      ghcr.io/liampattinson/epoch:latest epoch2d
```

Breaking down each component here:

- `docker run` starts up the container and runs its 'entrypoint', which is the script
  `docker/run_epoch.sh` in this repository.
- `--rm` automatically removes the container after running.
- `-v /path/to/output/dir:/output` mounts the directory `/path/to/output/dir` on the
  host machine to `/output` on the container. `/path/to/output/dir` should contain
  your `input.deck` file before running.
- `ghcr.io/liampattinson/epoch:latest` is the container to run. This will be downloaded
  the first time you run the container, and cached for future use. It is created using
  the file `Docker/Dockerfile` in this repo.
- `epoch2d` is the command to run within the container. The options are:
  - `epoch1d`
  - `epoch2d`
  - `epoch3d`
  - `epoch1d_qed`
  - `epoch2d_qed`
  - `epoch3d_qed`

Note that you shouldn't mount your current working directory. If you want to open an
interactive shell inside the container, try:

```bash
$ docker run --rm -it -v /path/to/output/dir:/output \
      --entrypoint /bin/bash ghcr.io/liampattinson/epoch:latest
```

## Running Epoch with Singularity

To run Epoch on Viking, first create a directory within `~/scratch` in which you
want to run your code:

```
$ ssh <userid>@viking.york.ac.uk
$ mkdir -p ~/scratch/epoch
$ cd ~/scratch/epoch
```

You'll need to ensure your `input.deck` file is within this directory:

```bash
$ # From your own machine
$ scp input.deck <userid>@viking.york.ac.uk:/users/<userid>/scratch/epoch
```

To run the Singularity container, you'll need to load the following modules:

```bash
$ module load tools/Singularity mpi/OpenMPI
```

You can then run using:

```bash
$ singularity exec library://liampattinson/epoch/epoch.sif:latest \
      run_epoch.sh epoch2d ./output
```

Note that you should only run short tests on the login nodes. Let's break this down:

- `singularity exec`: Run a singularity container with a user provided command.
- `library://`: Download and run a container from [sylabs.io][sylabs].
- `liampattinson/epoch/epoch.sif`: The specific container we want to run. This one
  is a prebuilt Epoch container using the `Singularity/Singularity` recipe file in
  this repo. Note that the Singularity container is built on top of the Docker
  container.
- `run_epoch.sh epoch2d .`: The command to run within the container. The shell script
  `run_epoch.sh` is the same command invoked by the Docker container, but with
  Singularity we need to name it explicitly. We also must provide a second argument
  which is the output directory, in which we should have our `input.deck` file.

To run using MPI, we put the `mpirun` command _before_ the `singularity` command:

```bash
$ mpirun -n 2 singularity exec \
      library://liampattinson/epoch/epoch.sif:latest \
      run_epoch.sh epoch2d ./output
```

For real runs, we'll want to run Epoch via the Slurm scheduler. See the `./examples`
folder for an example job script `run_sbatch.sh` and an example `input.deck`. Once we
have a job script, we can submit a job using:

```bash
$ sbatch run_sbatch.sh
```

We can check the progress of our job using:

```bash
$ squeue -u <userid>
```

The first time we run the container might be slow as we first have to download the
container. We can speed things up by first pulling the container from the remote
repo:

```bash
$ singularity pull epoch.sif library://liampattinson/epoch/epoch.sif:latest
```

This will download the container image to the file `epoch.sif` (`.sif` denoting a
'Singularity Image Format' file). You can then use `epoch.sif` in place of
`library://account/repo/container` in any of the commands above.

To see help text for the Singularity container, first pull it using the methods above,
and then try:

```bash
$ singularity run-help epoch.sif
```

If you want to inspect the container, it has been set up so that the following
command opens a bash shell inside of it:

```bash
$ singularity run epoch.sif
```

Try to avoid getting `singularity exec` and `singularity run` mixed up; the
former lets you specify which command you want to run, while the later runs a
pre-defined script.

## Analysing code output

It is recommended to analyse Epoch output data on your own machine rather than on
Viking:

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

## Building Docker images

TODO

## Building Singularity images

TODO recommend docker first

The file `Singularity` in the top-level of this repository contains the definitions
for an Epoch Singularity container. This is the recipe we use to create new container
images. If you want to make additions/changes to the recipe in this repo, please feel
free to create a fork and do so!

Due to permission issues, we can't build new containers directly on Viking. However,
we can make use of the Sylabs remote builder. To use this, first go to
[sylabs.io][sylabs] and create an account. From there, you should be able to generate
an 'access token'. After doing so, copy the generated token to a file `.token` on
your system. Then:

```bash
$ singularity remote login
```

Copy-paste your access token when prompted. You can then build your image using:

```bash
$ singularity build --remote epoch.sif Singularity
```

This may take some time. Once it's done, you should find the image file `epoch.sif`
in your current directory. You can run this container directly using `singularity exec`
as shown above.

If you wish to share your container with others, you'll first need to sign it. This can
be done using:

```bash
$ singularity keys newpair
$ # Fill in the prompts as they appear.
$ # Use the same email as your sylabs account.
$ # You can leave passwords blank
$ singularity sign epoch.sif
```

We can check it worked using:

```bash
$ singularity verify epoch.sif
```

Finally, we can upload it to Sylabs using:

```bash
$ singularity push epoch.sif library://<my_sylabs_account>/epoch/epoch.sif:latest
```

In addition to uploading an image with the `:latest` tag, we may also want to upload a
version with a version code like `:1.0`. If we add new features to the container, we
can then upload version `:1.1` etc. If we change how the container works in such a way
that our users must interact with it differently (e.g. we might have renamed an existing
executable), we can then upload version `:2.0` etc.

## Licensing

This repo is licensed under the GNU GPLv3 license, as it contains files from the
similarly-licensed [Epoch repository][epoch-repo].

[docker]: https://docs.docker.com/
[singularity]: https://docs.sylabs.io/guides/3.11/user-guide/
[epoch]: https://epochpic.github.io/
[epoch_repo]: https://github.com/Warwick-Plasma/epoch
[sylabs]: https://sylabs.io
