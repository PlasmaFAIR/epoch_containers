# Epoch on Docker

To build the docker container:

```bash
$ docker build . -t epoch
```

The library `epoch_container_utils` is copied and installed into the container, and
it manages the way in which Epoch is built and run. To run Epoch from a Docker
container, try:

```bash
$ docker run --rm -v /output/dir/on/host:/output \
    ghcr.io/liampattinson/epoch:latest \
    -d 2 --photons
```

Your `input.deck` file should be located at `/output/dir/on/host/input.deck`. The
parameter `-d 2` tells docker to run the 2D variant of Epoch, and the optional
`--photons` flag switches on QED effects.

To get help text, try:

```bash
$ docker run --rm ghcr.io/liampattinson/epoch:latest --help
```

If you need to inspect the container, try:

```bash
$ docker run --rm -it --entrypoint /bin/bash ghcr.io/liampattinson/epoch:latest
```
