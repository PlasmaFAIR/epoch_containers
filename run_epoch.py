#!/usr/bin/env python3

"""Python script for running Epoch via a container.

This script attempts to mimic the behaviour of Epoch by prompting the user to input
their output directory after the program is running. This behaviour can be overridden by
suppling the '-o' flag.

This script can also be used to launch a shell in a Singularity image with sdf_helper
pre-installed.
"""

import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from textwrap import dedent
from typing import Optional

_CONTAINERS = dict(
    docker="ghcr.io/plasmafair/epoch:latest",
    singularity="oras://ghcr.io/plasmafair/epoch.sif:latest",
)


def parse_args() -> Namespace:
    """Reads arguments from the command line."""

    parser = ArgumentParser(prog="run_epoch", description=__doc__)

    subparsers = parser.add_subparsers(
        required=True,
        dest="mode",
        help=(
            "Please select one of the subcommands provided. You can supply --help "
            "after each subcommand to view further options."
        ),
    )

    docker_parser = subparsers.add_parser(
        "docker",
        help="Run Epoch via a Docker container.",
    )

    singularity_parser = subparsers.add_parser(
        "singularity",
        help="Run Epoch via a Singularity container",
    )

    # Define function for container selection arg; will be needed in multiple places
    def container_arg(parser: ArgumentParser, default: str, cmd: str = "run") -> None:
        parser.add_argument(
            "-c",
            "--container",
            default=default,
            type=str,
            help=f"The container to {cmd}. The default is {default}.",
        )

    subparser_tuple = (docker_parser, singularity_parser)
    container_tuple = (_CONTAINERS["docker"], _CONTAINERS["singularity"])
    for subparser, container in zip(subparser_tuple, container_tuple):
        container_arg(subparser, container)

        subparser.add_argument(
            "-d",
            "--dims",
            default=1,
            type=int,
            choices=range(1, 4),
            help="The number of dimensions in your Epoch run. The default is 1.",
        )

        subparser.add_argument(
            "-o",
            "--output",
            default=None,
            type=Path,
            help=(
                "The path of the output directory. If not supplied, the user will "
                "be prompted for this information after the program starts."
            ),
        )

        subparser.add_argument(
            "--photons", action="store_true", help="Run with QED features enabled."
        )

        subparser.add_argument(
            "--no-run", action="store_true", help="Print the command but don't run it."
        )

    # Singularity multiprocess utilties
    singularity_parser.add_argument(
        "-n",
        "--nprocs",
        default=1,
        type=int,
        help=("The number of processes to run on. Uses mpirun unless --srun is set."),
    )

    singularity_parser.add_argument(
        "--srun",
        action="store_true",
        help=(
            "Run using srun instead of mpirun. "
            "Recommended for HPC machines with Slurm controllers."
        ),
    )

    # Extra singularity utilities
    subsubparsers = singularity_parser.add_subparsers(
        required=False,
        dest="singularity_mode",
        help="Additional Singularity utilities.",
    )

    # Pull: Download a singularity image to a local file
    pull_parser = subsubparsers.add_parser(
        "pull",
        help=(
            "Pull a Singularity container to a local image file. "
            "This may be used as an argument to -c/--container."
        ),
    )
    pull_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("epoch.sif"),
        help="Filename of local image file",
    )
    container_arg(pull_parser, _CONTAINERS["singularity"], cmd="pull")

    # Shell: Open a shell inside the container
    shell_parser = subsubparsers.add_parser(
        "shell", help="Open a shell in the Singularity image."
    )
    shell_parser.add_argument(
        "--python",
        action="store_true",
        help="Open directly into a Python shell",
    )
    shell_parser.add_argument(
        "--cmd",
        type=str,
        default=None,
        help="Run a specific command on entering the shell.",
    )
    container_arg(shell_parser, _CONTAINERS["singularity"])

    return parser.parse_args()


def docker_cmd(container: str, output: Path, dims: int, photons: bool) -> str:
    """Constructs the command to run Epoch via a Docker container."""
    return dedent(
        f"""\
        docker run --rm
        -v {output.resolve()}:/output
        {container}
        -d {dims}
        -o /output
        {'--photons' if photons else ''}
        """
    ).replace("\n", " ")


def singularity_cmd(
    container: str, output: Path, dims: int, photons: bool, nprocs: int, srun: bool
) -> str:
    """Constructs the command to run Epoch via a Singularity container."""
    cmd = dedent(
        f"""\
        singularity exec
        --bind {output.resolve()}:/output
        {container}
        run_epoch
        -d {dims}
        -o /output
        {'--photons' if photons else ''}
        """
    ).replace("\n", " ")

    run_mode: str
    if srun:
        run_mode = "srun"
    elif nprocs != 1:
        run_mode = f"mpirun -n {nprocs}"
    else:
        run_mode = ""

    return f"{run_mode} {cmd}".strip()


def pull_cmd(container: str, output: Path) -> str:
    """Constructs the command to pull to a local Singularity image."""
    return f"singularity pull {output} {container}"


def shell_cmd(container: str, python: bool, cmd: Optional[str] = None) -> str:
    """Construct the command to open a shell in a Singularity container."""
    if python:
        return f"singularity exec {container} python"
    if cmd is not None:
        return f"singularity exec {container} {cmd}"
    return f"singularity shell {container}"


def prompt_output(output: Optional[Path]) -> Path:
    """If output is None, prompt the user to supply it. 

    Otherwise return unchanged.
    Allows the user to run the code using ``echo output_dir | run_epoch.py``.
    """
    return Path(input("Please enter output directory:\n")) if output is None else output


def run_cmd(cmd: str, no_run: bool = False) -> None:
    """Execute ``cmd`` in a subprocess, or just print ``no_run`` is ``True``."""
    if no_run:
        print(f"Generated the command:\n{cmd}")
    else:
        print(f"Running with the command:\n{cmd}")
        subprocess.run(cmd.split())


def main() -> None:
    args = parse_args()

    if args.mode == "docker":
        cmd = docker_cmd(
            args.container, prompt_output(args.output), args.dims, args.photons
        )
        run_cmd(cmd, no_run=args.no_run)
    elif args.mode == "singularity":
        if args.singularity_mode == "pull":
            run_cmd(pull_cmd(args.container, args.output))
        elif args.singularity_mode == "shell":
            run_cmd(shell_cmd(args.container, args.python, args.cmd))
        else:
            cmd = singularity_cmd(
                args.container,
                prompt_output(args.output),
                args.dims,
                args.photons,
                args.nprocs,
                args.srun,
            )
            run_cmd(cmd, no_run=args.no_run)


if __name__ == "__main__":
    main()
