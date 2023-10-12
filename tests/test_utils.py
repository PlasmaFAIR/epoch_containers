import itertools

import pytest

from epoch_containers.utils import exe_name


@pytest.mark.parametrize("dims,photons", itertools.product((1, 2, 3), (False, True)))
def test_exe_name(dims: int, photons: bool):
    exe = exe_name(dims=dims, photons=photons)
    assert exe == f"epoch_{dims}d{'_photons' if photons else ''}"
