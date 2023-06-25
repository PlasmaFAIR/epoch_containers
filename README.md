# Epoch Singularity

Tools and information for building/running the Epoch Singularity container. This
repository is targeted at users of the Viking HPC cluster at the University of York,
but the contents may be of use to other Epoch users.

## Introduction

Singularity is a _container_ platform. Containers allow us to package up code and
dependencies in a way that is portable and reproducible. Using containers, we don't
need to compile complex scientific software from scratch, and instead can get
straight to running code without worrying about the tedious set-up stages.

You may have heard of another popular container platform called _Docker_. The main
benefit of using Singularity over Docker is that it was designed from the ground up to
be usable on HPC systems, so it's capable of running software on multi-node
architectures using MPI.

## Running Epoch with Singularity

There's no need to clone the Epoch repository or compile the code to use the
container. On Viking, first create a directory within `~/scratch` in which you
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
$ singularity exec library://liampattinson/epoch/epoch.sif epoch1d
```

Note that you should only run short tests on the login nodes. Let's break this down:

- `singularity exec`: Run a singularity container with a user provided command.
- `library://`: Download and run a container from [sylabs.io][sylabs].
- `liampattinson/epoch/epoch.sif`: The specific container we want to run. This one
  is a prebuilt Epoch container using the `Singularity` recipe file in this repo.
- `epoch1d`: The command to run within the container. It has been set up so that the
  following commands will work:
    - `epoch1d`
    - `epoch2d`
    - `epoch3d`
    - `epoch1d_qed`
    - `epoch2d_qed`
    - `epoch3d_qed`

To run using MPI, we put the `mpirun` command _before_ the `singularity` command:

```bash
$ mpirun -n 2 singularity exec library://liampattinson/epoch/epoch.sif epoch1d
```

We can also get around Epoch prompting us to provide an output directory with:

```bash
$ echo . | mpirun -n 2 singularity exec library://liampattinson/epoch/epoch.sif epoch1d
```

For real runs, we'll want to run Epoch via the Slurm scheduler. See the `./examples`
folder for an example job script `run.sh` and an example `input.deck`. Once we have a
job script, we can submit a job using:

```bash
$ sbatch run.sh
```

We can check the progress of our job using:

```bash
$ squeue -u <userid>
```

The first time we run the container might be slow as we first have to download the
container. We can speed things up by first pulling the container from the remote
repo:

```bash
$ singularity pull epoch.sif library://liampattinson/epoch/epoch.sif
```

This will download the container image to the file `epoch.sif` (`.sif` denoting a
'Singularity Image Format' file). You can then use `epoch.sif` in place of
`library://account/repo/container` in any of the commands above.

## Getting help

To see help text for the container, first pull it using the methods above, and then
try:

```bash
$ singularity run-help epoch.sif
```

If you want to inspect the container, it has been set up so that the following
command opens a bash shell inside of it:

```bash
$ singularity run epoch.sif
```

Note that you shouldn't get `singularity exec` and `singularity run` mixed up. The
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

## Building Singularity images

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

## Background Reading

- [Epoch Documentation][epoch]
- [Singularity Documentation][singularity]

[epoch]: https://epochpic.github.io/
[epoch_repo]: https://github.com/Warwick-Plasma/epoch
[singularity]: https://docs.sylabs.io/guides/3.11/user-guide/
[sylabs]: https://sylabs.io
