import itertools
import sys
from pathlib import Path
from textwrap import dedent

import pytest

from epoch_containers.build_epoch import build_epoch, compiler_flags, parse_build_args
from epoch_containers.utils import exe_name


@pytest.mark.parametrize(
    "dims,compiler,photons,long_names",
    itertools.product(
        (None, 1, 2, 3),
        (None, "gfortran", "intel"),
        (None, False, True),
        (False, True),
    ),
)
def test_parse_build_args(
    monkeypatch,
    dims: int | None,
    compiler: str | None,
    photons: bool | None,
    long_names: bool,
):
    # Set up false argv
    argv: list[str] = ["test"]
    if dims is not None:
        argv.extend(["--dims" if long_names else "-d", str(dims)])
    if compiler is not None:
        argv.extend(["--compiler" if long_names else "-c", compiler])
    if photons:
        argv.append("--photons")

    # Parse args
    with monkeypatch.context() as mpatch:
        mpatch.setattr(sys, "argv", argv)
        args = parse_build_args()

    # Test args existence. All should be present, even if not provided.
    for key in ("dims", "compiler", "photons"):
        assert key in vars(args)

    # Test correctness
    if dims is not None:
        assert args.dims == dims
    if compiler is not None:
        assert args.compiler == compiler
    if photons is not None:
        assert args.photons == photons


@pytest.fixture
def mock_epoch_dir(tmp_path: Path) -> Path:
    d = tmp_path / "build_epoch"
    d.mkdir(exist_ok=True)
    for dims in range(1, 4):
        dd = d / f"epoch{dims}d"
        dd.mkdir(exist_ok=True)
        bin_dir = dd / "bin"
        bin_dir.mkdir(exist_ok=True)
        makefile = dedent(
            f"""\
            # This is a comment
            # There are 7 in the file
            DEFINES := $(DEFINE)
            D := D
            # DEFINES += $(D)ICE_CREAM
            DEFINES += $(D)PIZZA
            # DEFINES += $(D)MILKSHAKE
            # DEFINES += $(D)ICE_CREAM_SUNDAE
            # DEFINES += $(D)PHOTONS
            # DEFINES += $(D)MORE_PHOTONS

            hello_world:
            \techo $(DEFINES) > bin/epoch{dims}d

            clean:
            \trm -f bin/epoch{dims}d
            """
        )
        (dd / "Makefile").write_text(makefile)
    return d


@pytest.fixture
def mock_make_dir(mock_epoch_dir: Path) -> Path:
    return mock_epoch_dir / "epoch1d"


@pytest.mark.parametrize(
    "flags,expected_hashes",
    (
        (None, 7),
        (["ICE_CREAM"], 6),  # Shouldn't affect ICE_CREAM_SUNDAE
        (["PIZZA"], 7),  # Already uncommented
        (["ICE_CREAM", "MILKSHAKE"], 5),
        (["ICE_CREAM_SUNDAE"], 6),  # Shouldn't affect ICE_CREAM
        (["PHOTONS"], 6),  # Shouldn't affect MORE_PHOTONS
        (["MORE_PHOTONS"], 6),  # Shouldn't affect PHOTONS
        (["PHOTONS", "MORE_PHOTONS"], 5),
    ),
)
def test_compiler_flags(
    mock_make_dir: Path,
    flags: list[str] | None,
    expected_hashes: int,
):
    with compiler_flags(mock_make_dir, flags=flags):
        assert (mock_make_dir / "Makefile").is_file()
        assert (mock_make_dir / "Makefile").read_text().count("#") == expected_hashes
        # Make a copy makefile only if provided with flags
        if flags is not None:
            assert (mock_make_dir / "Makefile.copy").is_file()
            assert (mock_make_dir / "Makefile.copy").read_text().count("#") == 7
    # Expect Makefile back to usual
    assert (mock_make_dir / "Makefile").is_file()
    assert (mock_make_dir / "Makefile").read_text().count("#") == 7
    assert not (mock_make_dir / "Makefile.copy").is_file()


@pytest.mark.parametrize(
    "dims,compiler,photons",
    itertools.product(
        (1, 2, 3),
        ("gfortran", "intel"),
        (False, True),
    ),
)
def test_build_epoch(mock_epoch_dir: Path, dims: int, compiler: str, photons: bool):
    build_epoch(mock_epoch_dir, dims, compiler, photons=photons)
    expected_file = mock_epoch_dir / "bin" / exe_name(dims, photons)
    assert expected_file.is_file()
    text = expected_file.read_text()
    if photons:
        assert "PHOTONS" in text
    else:
        assert "PHOTONS" not in text
