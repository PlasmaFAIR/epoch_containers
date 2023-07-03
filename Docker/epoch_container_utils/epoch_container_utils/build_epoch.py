import argparse
import re
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Optional

from .utils import exe_name


def parse_build_args() -> argparse.Namespace:
    """
    Defines command line interface for building Epoch.
    """

    parser = argparse.ArgumentParser(
        prog="build_epoch",
        description="Script used to build ",
        epilog="Remember to set your WORKDIR to the top-level of the Epoch repo!",
    )

    parser.add_argument(
        "-d",
        "--dims",
        default=1,
        type=int,
        choices=range(1, 4),
        help="The number of dimensions in your Epoch build",
    )

    parser.add_argument(
        "-c",
        "--compiler",
        default="gfortran",
        type=str,
        help="The compiler to use for the build",
    )

    parser.add_argument(
        "--photons", action="store_true", help="Build with QED features enabled"
    )

    return parser.parse_args()


@contextmanager
def compiler_flags(directory: Path, flags: Optional[Iterable[str]] = None) -> None:
    """
    Set compiler flags to Makefile in current working directory
    """
    makefile = Path(directory) / "Makefile"
    tmp = Path(directory) / "Makefile.copy"

    # Check Makefile exists
    if not makefile.is_file():
        raise FileNotFoundError("Makefile not in current working directory")

    # If not given any compiler flags, do nothing
    if not flags:
        yield
        return

    # Copy Makefile to temporary location
    shutil.copyfile(makefile, tmp)

    try:
        # Read Makefile into list of strings
        with open(makefile) as f:
            lines = f.readlines()
        # Copy to new list, uncommenting lines that match flags
        newlines = []
        for line in lines:
            for flag in flags:
                if re.search(rf"\$\(D\){flag}$", line):
                    newlines.append(line.replace("#", ""))
                    break
            else:
                newlines.append(line)
        # Write back to file
        with open(makefile, "w") as f:
            f.writelines(newlines)
        # Pass out of context manager
        yield

    finally:
        # On returning to context manager, move copied makefile back to original name
        shutil.move(tmp, makefile)


def build_epoch(
    epoch_dir: Path, dims: int, compiler: str, photons: bool = False
) -> None:
    """
    Builds an Epoch executable. Returns path to executable.

    Parameters
    ----------
    epoch_dir
        Path to top level of Epoch repository
    dims
        Number of dimensions in build
    compiler
        Compiler to use for build
    photons
        Switch for QED features
    """
    # Get directory
    directory = Path(epoch_dir) / f"epoch{dims}d"
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")
    # Set up compiler flags
    flags = []
    if photons:
        flags.append("PHOTONS")

    # Build
    with compiler_flags(directory, flags=flags):
        subprocess.run(
            ["make", "-j", "--directory", str(directory), f"COMPILER={compiler}"]
        )

    # Move executable to bin dir (executable has same filename as directory)
    exe = directory / "bin" / directory.name
    bin_dir = epoch_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    new_exe = bin_dir / exe_name(dims=dims, photons=photons)
    shutil.move(exe, new_exe)

    # Clean up
    subprocess.run(["make", "--directory", str(directory), "clean"])


def main():
    """
    Entrypoint function for building Epoch.
    """
    args = parse_build_args()
    build_epoch(Path.cwd(), args.dims, args.compiler, photons=args.photons)
