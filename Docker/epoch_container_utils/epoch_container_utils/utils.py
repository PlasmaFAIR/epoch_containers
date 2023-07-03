def exe_name(dims: int, photons: bool = False) -> str:
    """
    Generate the name of an Epoch executable.
    """
    name = f"epoch_{dims}d"
    if photons:
        name += "_photons"
    return name
