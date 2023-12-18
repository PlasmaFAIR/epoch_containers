# Epoch on Viking

This directory provides utilities for running Epoch on Viking2, a High-Performance
Computing (HPC) service accessible to researchers at the University of York. The
contents may be adapted to suit other HPC machines.

## Getting Started

To access Viking, please consult the documents on [creating an account][account] and
[connecting to Viking][connect]. Once you have an account, the following should work on
computers connected to the University of York network:

```bash
$ ssh viking
```

On logging in, you should find yourself in a directory containing `./scratch`: this is
where you should run all of your jobs on Viking. Clone this repository here:

```bash
$ cd scratch
$ git clone https://github.com/PlasmaFAIR/epoch_containers
```

If you want to try running from source, you should also clone Epoch here:

```bash
$ git clone https://github.com/Warwick-Plasma/epoch
```

You can copy files between your own machine and Viking using `scp`:

```bash
$ scp local_file viking:scratch/my_file  # send to viking
$ scp viking:scratch/my_file local_file  # download from viking
```

The following sections will cover how to run Epoch either using the containers provided
in this repository, or by compiling it from source. In either case, you will need to
submit Slurm scripts using `sbatch` to do so -- more details on this later.

> [!CAUTION]
> Do not run Epoch directly on the login nodes. Always use `sbatch`.

## Using Singularity

Viking uses a 'module' system to set up your environment, and it has a lot of different
scientific software packages pre-installed. To use Singularity containers, we'll need to
use the module `Apptainer`:

```bash
$ module load Apptainer
```

> [!NOTE]
> Apptainer is a flavour of Singularity supported by the Linux Foundation, and it is
  largely compatible with other flavours.

The first time we try to run a Singularity container, it will take a long time to be
downloaded. To speed things up, we can pre-download it using the following command from
the top level of the `epoch_containers` repository:

```bash
$ ./run_epoch.py singularity shell
```

This will download the container, cache it locally, and drop you into a command prompt.
You can escape it be pressing `Ctrl + d`.

To run Epoch using containers, please skip forward to the section
[Running Epoch][#running-epoch].

## Compiling from Source

If you run into difficulties with the Singularity containers, another option is to
compile and run Epoch from source. To do so, clone the main Epoch repo as described
above, and enter the correct version of the code:

```bash
$ git clone https://github.com/Warwick-Plasma/epoch
$ cd epoch/epoch2d
```

Here, you will find a `Makefile` containing a lot of commented out settings flags with
lines beginning with `DEFINES` -- uncomment any you need.

To install, you must first load a version of GCC that is compatible with Epoch, and the
matching version of OpenMPI:

```bash
$ module load GCC/11.3.0 OpenMPI/4.1.4-GCC-11.3.0
```

You can then build Epoch using:

```bash
$ make COMPILER=gfortran
```

This will create an executable in `./bin`, which can be moved somewhere more convenient
if you wish.

## Running Epoch

To run Epoch, you will need to use a modified version of the script `epoch_viking.sh`
provided in this directory. **Do not run this directly.**

The lines marked `#SBATCH` control how the job is submitted to the Slurm controller,
which schedules jobs on Viking. Note that the fewer resources you request, the less time
your job will sit in the queue, but make sure you request enough time, memory, nodes,
and tasks for your job to succeed!

> [!IMPORTANT]
> You'll need to set the project code to that was provided to you when you signed up to
  Viking.

The variables set under `User settings` control the Epoch run. Be sure to set the
variable `output_dir` to point to the directory containing your input deck. If you're
running using containers, you should set `run_epoch` to the location of your
`run_epoch.py` script, and set the variables `dims` and `photons` to set up your run
properly. If you're running from source, you'll need to set `epoch_exe` to your compiled
executable, and `mpi_module` to the MPI module that was loaded when you compiled Epoch.

To submit a job, use `sbatch`:

```bash
$ sbatch my_job.sh
```

To see where your job is on the queue, we can use `squeue`:

```bash
$ squeue --me
```

This will also show you the job ID. Jobs can be cancelled with `scancel`:

```bash
$ scancel JOBID
```

## Managing Output Files

Epoch outputs data in its own SDF format, which isn't particularly user friendly, and
can even be difficult to install. The containers provided by this repository come with
`sdf_helper` pre-installed, and you can open a shell using:

```bash
$ ./run_epoch.py singularity shell            # Opens bash shell at current directory.
$ ./run_epoch.py singularity shell --python   # Opens straight into Python interpreter.
```

From here, you can open and explore SDF files using Python:

```python
>>> import sdf_helper as sdf
>>> data = sdf.getdata("0005.sdf")
>>> sdf.list_variables(data)
```

Once you have the names of your grids, you can access them as NumPy arrays using:

```python
>>> data.My_Variable_Name.data
```

From here, you may wish to repackage the data into some other format that is easier to
work with. For a very straightforward approach, the NumPy function `tofile` may be of
use, or the library [`xarray`][xarray] might be useful if you want to convert to NetCDF.

For more information on `sdf_helper`, please see the [official docs][sdf].

Note that you should not perform any computationally intensive work directly on the
login nodes. If you wish to do anything more than convert a few small arrays from SDF to
some other format, consider wrapping up your data processing in a Python script, and
submitting it in a Slurm job script. To run your own Python script from the container,
use:

```bash
module load Apptainer
./run_epoch.sh singularity shell --cmd "python my_script.py"
```

If you need to install any dependencies, you can do this using a short auxiliary bash
script:

```bash
# In bash file my_script.sh:
pip install [dependency list]
python my_script.py

# In job script:
./run_epoch.sh singularity shell --cmd "/bin/bash my_script.sh"
```

Data will not be stored indefinitely on Viking's `./scratch` drives, so you should `scp`
output data to your own machine for longer term storage. It may also be easier to
perform post-processing and generate plots on your own machine than to manage these
tools via Slurm jobs.

[account]: https://vikingdocs.york.ac.uk/getting_started/creating_accounts.html
[connect]: https://vikingdocs.york.ac.uk/getting_started/connecting_to_viking.html
[sdf]: https://epochpic.github.io/documentation/visualising_output/python.html
[xarray]: https://docs.xarray.dev/en/stable/
