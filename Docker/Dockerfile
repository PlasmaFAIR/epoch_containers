# Dockerfile for creating an Epoch container

# To build:
# $ docker build . -t epoch

FROM ubuntu:22.04

# Set compiler preferences. Options include:
# - gfortran
# - intel

ARG EPOCH_COMPILER=gfortran

# Ensure we're working with latest OS updates and have all requirements
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install git make python3 python3-pip libgtk2.0-dev gfortran openmpi-bin libopenmpi-dev -y

# Epoch can get confused about python vs python2 vs python3 during the build stage
# Ensure 'python' and 'python3' are synonymous
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create working directory
WORKDIR /app

# Get epoch
RUN git clone --recursive https://github.com/Warwick-Plasma/epoch /app/epoch

# Copy in utility library
COPY epoch_container_utils /app/epoch_container_utils
RUN ls -l /app/epoch_container_utils

# Set up Python, install utility library
WORKDIR /app/epoch_container_utils
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install numpy matplotlib .

# Build Epoch variants
WORKDIR /app/epoch
RUN build_epoch --dims 1 --compiler=${EPOCH_COMPILER}
RUN build_epoch --dims 2 --compiler=${EPOCH_COMPILER}
RUN build_epoch --dims 3 --compiler=${EPOCH_COMPILER}
RUN build_epoch --dims 1 --compiler=${EPOCH_COMPILER} --photons
RUN build_epoch --dims 2 --compiler=${EPOCH_COMPILER} --photons
RUN build_epoch --dims 3 --compiler=${EPOCH_COMPILER} --photons

# Add SDF helper libs to Python env
WORKDIR /app/epoch/epoch1d
RUN make sdfutils

# Set path to include executables
ENV PATH="${PATH}:/app/epoch/bin"

# Reset workdir to base /app dir
WORKDIR /app

# Set entrypoint to that installed by epoch_container_utils
ENTRYPOINT ["run_epoch"]
