import argparse
import subprocess
from pathlib import Path
from textwrap import dedent

from .utils import exe_name


def parse_run_args() -> argparse.Namespace:
    """Defines command line interface for running Epoch."""

    epilog = dedent(
        """Docker example:

         $ docker run --rm -v /home/username/epoch/my_data:/output_dir\\
               ghcr.io/PlasmaFAIR/epoch:latest\\
               -d 2 -o /output_dir --photons

         Arguments to this script are supplied after specifying the Docker container.

         The --rm flag to docker removes the container after use.

         The -v flag sets the volumes, which controls how directories on the host
         machine are mounted in the container. In this example, the input file
         'input.deck' should be located at the path
         /home/username/epoch/my_data/input.deck. It is not recommended to use your
         current working directory. The directory in the container must
         match the directory supplied to the -o/--output flag.

        Singularity example:

         $ singularity exec docker://PlasmaFAIR/epoch:latest\\
             run_epoch -d 2 -o . --photons

         Arguments to this script are supplied after specifying the Singularity
         container.

         Unlike when running with the Docker container, the command provided to
         the container must begin with 'run_epoch'. Users should not use the
         default value supplied to -o/--output, as this will cause permissions
         issues. Instead, this should be somewhere within scratch space.
        """
    )

    parser = argparse.ArgumentParser(
        prog="run_epoch",
        description="Entrypoint script to containerised Epoch.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-d",
        "--dims",
        default=1,
        type=int,
        choices=range(1, 4),
        help="The number of dimensions in your Epoch run",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=Path("/output"),
        type=Path,
        help=dedent(
            """The path of the output directory in the container.

            With Docker, this should match the second path passed to -v/--volume in
            your call to 'docker run'. With Singularity, this should simply be the
            directory in which your 'input.deck' file is stored.
            """
        ).replace("\n", " "),
    )

    parser.add_argument(
        "--photons", action="store_true", help="Run with QED features enabled"
    )

    return parser.parse_args()


def run_epoch(
    dims: int, output: Path, photons: bool = False, bin_dir: Path | None = None
) -> None:
    """Launches an Epoch subprocess.

    Parameters
    ----------
    dims
        Number of dimensions to include in the run.
    output
        Output directory to pass to Epoch.
    photons
        Switch to run with QED features.
    bin_dir
        Directory containing Epoch executables. If not provided, assumes executables
        are located on the system PATH.
    """
    exe = exe_name(dims=dims, photons=photons)
    if bin_dir is not None:
        exe = str(Path(bin_dir).resolve() / exe)

    if not output.is_dir():
        raise NotADirectoryError(str(output))

    subprocess.run([exe], input=str(output.resolve()).encode("utf-8"))


def main() -> None:
    """Entrypoint function for running Epoch."""
    run_epoch(**vars(parse_run_args()))
