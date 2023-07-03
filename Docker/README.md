# Dockerfile

To build the docker container:

```bash
$ docker build . -t epoch
```

The script `run_epoch.sh` is copied into the Dockerfile, and acts as an entrypoint.
To run the container:

```bash
$ docker run --rm -v /output/dir/on/host:/output epoch epoch2d
```

Your `input.deck` file should be located at `/output/dir/on/host/input.deck`. The
parameter `epoch` tells docker to run the `epoch` container built in the previous
step, while the parameter `epoch2d` tells it to run the 2D version of epoch within
the container.

To get help text, try running without arguments:

```bash
$ docker run --rm epoch
```

If you need to inspect the container, try:

```bash
$ docker run --rm -it --entrypoint /bin/bash epoch
```
