#!/bin/bash

# To be run on a local machine (not HPC!)

mkdir -p output
cp ./input.deck output
docker run --rm -v $(pwd)/output:/output ghcr.io/plasmafair/epoch:latest -d 2
