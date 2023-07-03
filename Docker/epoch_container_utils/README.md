# Epoch Container Utils

This Python package is used to build and run Epoch variants within a Docker container.

## Usage

To install in a container, change into this directory and call:

```bash
$ python3 -m pip install --upgrade pip
$ python3 -m pip install .
```

To install outside of a container for development and testing, it is instead
recommended to create a virtual environment and make an editable install:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install --upgrade pip
$ python3 -m pip install -e .[lint,test]
```

## Linting and Testing

The following tools should be used regularly:

```bash
$ black epoch_container_utils
$ isort epoch_container_utils
$ flake8 epoch_container_utils
```

The tool `ruff` may be used for additional code improvements.
