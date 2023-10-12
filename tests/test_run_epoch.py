import itertools
import os
import sys
from pathlib import Path
from textwrap import dedent

import pytest

from epoch_containers.run_epoch import parse_run_args, run_epoch
from epoch_containers.utils import exe_name


@pytest.mark.parametrize(
    "dims,output,photons,long_names",
    itertools.product(
        (None, 1, 2, 3),
        (None, ".", "/output"),
        (None, False, True),
        (False, True),
    ),
)
def test_parse_run_args(
    monkeypatch,
    dims: int | None,
    output: str | None,
    photons: bool | None,
    long_names: bool,
):
    # Set up false argv
    argv: list[str] = ["test"]
    if dims is not None:
        argv.extend(["--dims" if long_names else "-d", str(dims)])
    if output is not None:
        argv.extend(["--output" if long_names else "-o", output])
    if photons:
        argv.append("--photons")

    # Parse args
    with monkeypatch.context() as mpatch:
        mpatch.setattr(sys, "argv", argv)
        args = parse_run_args()

    # Test args existence. All should be present, even if not provided.
    for key in ("dims", "output", "photons"):
        assert key in vars(args)

    # Test correctness
    if dims is not None:
        assert args.dims == dims
    if output is not None:
        assert str(args.output) == output
    if photons is not None:
        assert args.photons == photons


@pytest.fixture
def mock_epoch_bin_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run_epoch" / "bin"
    d.mkdir(parents=True, exist_ok=True)
    for dims, photons in itertools.product((1, 2, 3), (False, True)):
        script_file = d / exe_name(dims, photons)
        script_text = dedent(
            f"""\
            #!/bin/bash

            read OUTPUT
            echo {dims}{' PHOTONS' if photons else ''} $OUTPUT > {script_file}.out
            """
        )
        script_file.write_text(script_text)
        os.chmod(str(script_file), 0o755)
    return d


@pytest.mark.parametrize(
    "dims,output,photons",
    itertools.product(
        (1, 2, 3),
        (".", "/output"),
        (False, True),
    ),
)
def test_run_epoch(mock_epoch_bin_dir, dims: int, output: Path, photons: bool):
    run_epoch(dims, output, photons=photons, bin_dir=mock_epoch_bin_dir)
    expected_file = mock_epoch_bin_dir / f"{exe_name(dims, photons)}.out"
    assert expected_file.is_file()
    text = expected_file.read_text()
    assert str(dims) in text
    assert output in text
    if photons:
        assert "PHOTONS" in text
    else:
        assert "PHOTONS" not in text
