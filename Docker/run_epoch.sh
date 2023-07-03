#!/bin/bash

# First positional arg is version of epoch to run
# Second positional arg is output dir

help_text="Usage: <<docker run command>> cmd [output_dir]

Entrypoint to epoch on a Docker container.

Positional arguments:

cmd         The epoch command to run, e.g. epoch1d, epoch2d_qed

Optional arguments:

  output_dir  The directory within the container that epoch should write to.
              Defaults to /output. When running the container, be sure to set
              the volume flag to /output/dir/on/host:output_dir. If using the
              default, it should be /output/dir/on/host:/output.

Example:

  $ docker run --rm -v /home/username/epoch/my_data:/output epoch2d

  The --rm flag to docker removes the container after use. The -v flag sets
  the volumes, which controls how directories on the host machine are
  mounted in the container. epoch2d is a command to run the 2D version of
  epoch without any compiler flags set.

  In this example, the input file input.deck should be located at the path
  /home/username/epoch/my_data/input.deck.
"

if [[ $# -eq 0 || $# -gt 2 ]]; then
    echo "$help_text"
    exit 1
fi

cmd="/app/epoch/bin/$1"

if [[ $# -eq 2 ]]; then
    OUTPUT_DIR=$2
else
    OUTPUT_DIR="/output"
fi

echo ${OUTPUT_DIR} | ${cmd}
