#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "USAGE: Takes sylabs account and version number as positional args"
    exit 1
fi

if ! [[ -f "Singularity" ]]; then
    echo "Could not find file 'Singularity'"
    exit 1
fi

account=$1
version=$2
local_file="epoch_$version.sif"
destination="library://$account/epoch/epoch.sif:$version"
latest="library://$account/epoch/epoch.sif:latest"

echo "Building version $version"
echo "Will create the file $local_file and upload the images $destination and $latest"

echo "(Use CTRL+C to escape if you can't complete any steps)"

echo "LOGGING IN"
echo "Set up API token at sylabs.io if you haven't already"
singularity remote login

echo "BUILDING"
singularity build --remote ${local_file} Singularity

echo "SIGNING"
echo "Generate keys using 'singularity key newpair' if you haven't already"
singularity sign ${local_file}

echo "PUSHING"
singularity push ${local_file} ${destination}
singularity push ${local_file} ${latest}
