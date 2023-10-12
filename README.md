# Epoch Containers

Tools and information for building/running [Epoch][epoch] using Docker/Singularity
containers. This repository is targeted at users of the Viking HPC cluster at the
University of York, but the contents may be of use to other Epoch users.

## Introduction

Containers package up software and dependencies so that code compiled on one machine
can be reliably run on others. When used in conjunction with scientific software, they
allow researchers to run code without needing to build it themselves, and they make
it much easier to share reproducible workflows.

We provide support for two container platforms: [Docker][docker] and
[Singularity][singularity]. Docker is the most widely used platform, and
has been used here to build a 'base image' of Epoch on which other tools may be built.
Singularity is an alternative that was designed from the ground up to be useable on
HPC systems, so unlike Docker it can be run on multi-node architectures using MPI
without issue.

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
      run_epoch --help
```

This should download and cache the container, and then display some help text.
You can then run using:

```bash
$ singularity exec library://liampattinson/epoch/epoch.sif:latest \
    run_epoch -d 2 -o . --photons
```

Note that you should only run short tests on the login nodes. Let's break this down:

- `singularity exec`: Run a singularity container with a user provided command.
- `library://`: Download and run a container from [sylabs.io][sylabs].
- `liampattinson/epoch/epoch.sif:latest`: The specific container we want to run. This
  one is a prebuilt Epoch container using the `Singularity/Singularity` recipe file in
  this repo. Note that the Singularity container is built on top of the Docker
  container.
- `run_epoch`: The scripting entrypoint to launch an Epoch variant.
- `-d 2`: Run 2D epoch. Can also be 1D and 3D.
- `-o .`: Location of the output directory, which should container you `input.deck`
  file. Ensure this is somewhere within your scratch space!
- `--photons`: Optional flag that switches on QED features.

For a simplified interface, we can also use the `epoch_singularity.py` script within
this repository:

```bash
$ ./epoch_singularity.py  -d 2 -o . --photons
```

This script mimics Epoch's behaviour of prompting the user to input their output
directory after the program is running, so the following also works:

```bash
$ echo . | ./epoch_singularity.py  -d 2 --photons
```

To run using MPI, we put the `mpirun` command _before_ the `singularity` command:

```bash
$ mpirun -n 2 \
    singularity exec library://liampattinson/epoch/epoch.sif:latest \
    run_epoch -d 2 -o . --photons
$ # Or...
$ mpirun -n 2 ./epoch_singularity.py -d 2 -o . --photons
```

When running the `epoch_singularity.py` script with MPI, note that  we must supply the
output directory via the `-o` flag, and can't input it using `echo output_dir |`.

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

It is also possible to pull the container from the remote repo:

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

## Running Epoch with Docker

To run Epoch on your own machine, you'll first need to install Docker if you don't have
it already.

The Epoch Docker container can be found at `ghcr.io/plasmafair/epoch:latest`.
To run it, try:

```bash
$ docker run --rm -v /path/to/output/dir:/output \
      ghcr.io/plasmafair/epoch:latest -d 2 --photons
```

Breaking down each component here:

- `docker run` starts up the container and runs its 'entrypoint', which is the script
  `run_epoch`.
- `--rm` automatically removes the container after running.
- `-v /path/to/output/dir:/output` mounts the directory `/path/to/output/dir` on the
  host machine to `/output` on the container. `/path/to/output/dir` should contain
  your `input.deck` file before running.
- `ghcr.io/plasmafair/epoch:latest` is the container to run. This will be downloaded
  the first time you run the container, and cached for future use. It is created using
  the file `Docker/Dockerfile` in this repo.
- `-d 2`: Run 2D epoch. Can also be 1D and 3D.
- `--photons`: Optional flag that switches on QED features.

Note that you shouldn't mount your current working directory. Provided the second path
provided to `-v` is `/output`, there's no need to provide an argument to the `-o` flag.
If you want to open an interactive shell inside the container, try:

```bash
$ docker run --rm -it -v /path/to/output/dir:/output \
      --entrypoint /bin/bash ghcr.io/plasmafair/epoch:latest
```

For a simplified interface, try using the script `epoch_docker.py`. To achieve the
same results as the call above, try:

```bash
$ ./epoch_docker.py -d 2 -o /path/to/output/dir --photons
```

Note that the `-o` flag here refers to the run location on the host machine, not the
location in the docker container. If `-o` is not provided, this script mimics the
behaviour of Epoch itself by prompting the user to input their output directory after
the program starts:

```bash
$ echo /path/to/output/dir | ./epoch_docker.py -d 2 --photons
```

## Building Docker images

To build a Docker image, enter the `Docker` directory and try:

```bash
$ docker build . -t epoch
```

You can then run the container via:

```bash
$ docker run --rm -v /path/to/output/dir:/output \
      epoch -d 2 --photons
```

Please see the [online docs][ghcr] to set up your GitHub account to permit pushing to
the GitHub Container Registry (GHCR). Once set up, you should tag your repo with the
name it should use online:

```bash
$ docker tag epoch ghcr.io/<my_profile>/epoch:0.1
```

You can then push using:

```bash
$ docker push ghcr.io/<my_profile>/epoch:0.1
```

## Building Singularity images

The file `Singularity/Singularity` contains the definitions for an Epoch Singularity
container. As this builds on the Docker image, it doesn't do much beyond updating
some file access permissions.

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
similarly-licensed [Epoch repository][epoch_repo].

[docker]: https://docs.docker.com/
[singularity]: https://docs.sylabs.io/guides/3.11/user-guide/
[epoch]: https://epochpic.github.io/
[epoch_repo]: https://github.com/Warwick-Plasma/epoch
[sylabs]: https://sylabs.io
[ghcr]: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry


# COPYING README FILES FROM OLD DIRS HERE

## Epoch on Docker

To build the docker container:

```bash
$ docker build . -t epoch
```

The library `epoch_container_utils` is copied and installed into the container, and
it manages the way in which Epoch is built and run. To run Epoch from a Docker
container, try:

```bash
$ docker run --rm -v /output/dir/on/host:/output \
    ghcr.io/liampattinson/epoch:latest \
    -d 2 --photons
```

Your `input.deck` file should be located at `/output/dir/on/host/input.deck`. The
parameter `-d 2` tells docker to run the 2D variant of Epoch, and the optional
`--photons` flag switches on QED effects.

To get help text, try:

```bash
$ docker run --rm ghcr.io/liampattinson/epoch:latest --help
```

If you need to inspect the container, try:

```bash
$ docker run --rm -it --entrypoint /bin/bash ghcr.io/liampattinson/epoch:latest
```

## Epoch Containers Python Package

This Python package is used to build and run Epoch variants within a Docker container.

### Usage

Within a container, the package is installed using:

```bash
$ python3 -m pip install --upgrade pip
$ python3 -m pip install .
```

To install outside of a container for development and testing, it is instead
recommended to create a virtual environment and make an editable install:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install --upgrade pip
$ python3 -m pip install -e .[lint,test]
```

This will install the scripts `build_epoch` and `run_epoch`, which are intended to
be run inside of a Docker container.

### Linting and Testing

The following tools should be used regularly:

```bash
$ black src tests
$ isort src tests
$ docformatter --in-place src
$ ruff src tests
$ refurb src  # Python 3.10+
```

These can alternatively be run automatically using tox:

```bash
$ pip install tox
$ tox run -e format  # Automatically format the code
$ tox run -e lint  # Linter reports
```

To test, try:

```bash
$ pytest -vv tests
```

With tox, we can test multiple Python versions:

```bash
$ tox run -e py38  # Test with Python 3.8 in a fresh env
$ tox run -e py310  # Test with Python 3.10 in a fresh env
```
