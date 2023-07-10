#!/usr/bin/env python3

"""
Python script for running Epoch via a Docker container. Users must have Docker installed
on their system.

This script attempts to mimic the behaviour of Epoch by prompting the user to input
their output directory after the program is running. This behaviour can be overridden
by suppling the '-o' flag.
"""

import argparse
import subprocess
from pathlib import Path
from textwrap import dedent

DEFAULT_CONTAINER = "ghcr.io/plasmafair/epoch:latest"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="epoch_docker", description=__doc__)

    parser.add_argument(
        "-c",
        "--container",
        default=DEFAULT_CONTAINER,
        type=str,
        help=f"The container to run. The default is {DEFAULT_CONTAINER}",
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
            """\
            The path of the output directory on the host machine. If not supplied,
            the user will be prompted for this information after the program starts.
            """
        ).replace("\n", " "),
    )

    parser.add_argument(
        "--photons", action="store_true", help="Run with QED features enabled"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # If output not supplied, prompt user
    # This allows the user to run the code using 'echo output_dir | epoch_docker.py'
    output = args.output
    if output is None:
        output = Path(input("Please enter output directory:\n"))

    # Construct and run docker call
    docker_call = (
        f"docker run --rm -v {output.resolve()}:/output {args.container} "
        f"-d {args.dims} -o /output {'--photons' if args.photons else ''}"
    )
    subprocess.run(docker_call.split())


if __name__ == "__main__":
    main()
