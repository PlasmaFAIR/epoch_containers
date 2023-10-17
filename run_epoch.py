#!/usr/bin/env python3

"""Python script for running Epoch via a container.

This script attempts to mimic the behaviour of Epoch by prompting the user to input
their output directory after the program is running. This behaviour can be overridden by
suppling the '-o' flag.
"""

import argparse
import subprocess
from pathlib import Path
from textwrap import dedent

_DEFAULT = "_DEFAULT"
_DEFAULTS = dict(
    docker="ghcr.io/plasmafair/epoch:latest",
    singularity="oras://ghcr.io/plasmafair/epoch.sif:latest",
)


def parse_args() -> argparse.Namespace:
    """Reads arguments from the command line."""
    parser = argparse.ArgumentParser(prog="run_epoch", description=__doc__)

    parser.add_argument(
        "platform",
        choices=("docker", "singularity"),
        type=str,
        help="The container platform service to use: either 'docker' or 'singularity'",
    )

    parser.add_argument(
        "-c",
        "--container",
        default=_DEFAULT,
        type=str,
        help=dedent(
            f"""The container to run. The default for Docker is {_DEFAULTS["docker"]},
            while the default for Singularity is {_DEFAULTS["singularity"]}.
            """
        ).replace("\n", " "),
    )

    parser.add_argument(
        "-d",
        "--dims",
        default=1,
        type=int,
        choices=range(1, 4),
        help="The number of dimensions in your Epoch run. The default is 1.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        type=Path,
        help=dedent(
            """The path of the output directory. If not supplied, the user will
            be prompted for this information after the program starts.
            """
        ).replace("\n", " "),
    )

    parser.add_argument(
        "-n",
        "--nprocs",
        default=1,
        type=int,
        help="The number of processes to run on. Uses mpirun.",
    )

    parser.add_argument(
        "--photons", action="store_true", help="Run with QED features enabled."
    )

    parser.add_argument(
        "--no-run", action="store_true", help="Print the command but don't run it."
    )

    return parser.parse_args()


def docker_cmd(
    container: str, output: Path, dims: int, photons: bool, nprocs: int
) -> str:
    """Constructs the command to run Epoch via a Docker container."""
    if nprocs != 1:
        raise ValueError("When running with Docker, nprocs must equal 1")
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
    container: str, output: Path, dims: int, photons: bool, nprocs: int
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
    return f"mpirun -n {nprocs} " + cmd if nprocs != 1 else cmd


def main() -> None:
    args = parse_args()

    # If output not supplied, prompt user
    # This allows the user to run the code using 'echo output_dir | epoch_docker.py'
    output = args.output
    if output is None:
        output = Path(input("Please enter output directory:\n"))

    if args.container == _DEFAULT:
        container = _DEFAULTS[args.platform]
    else:
        container = args.container

    cmd_func = docker_cmd if args.platform == "docker" else singularity_cmd
    cmd = cmd_func(container, output, args.dims, args.photons, args.nprocs)
    print("Running Epoch with the command:", "\n", cmd)
    if not args.no_run:
        subprocess.run(cmd.split())


if __name__ == "__main__":
    main()
