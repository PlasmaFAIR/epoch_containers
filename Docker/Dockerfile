# This is the Dockerfile for creating Epoch 
#
# To build:
#
# $ docker build . -t epoch

FROM ubuntu:22.04

# Set compiler preferences
# Options include:
# - gfortran
# - intel

ARG EPOCH_COMPILER=gfortran

# Ensure we're working with latest OS updates and have all requirements
# TODO include compilers beyond gfortran here

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install git make python3 python3-pip libgtk2.0-dev gfortran openmpi-bin libopenmpi-dev -y

# Epoch can get confused about python vs python2 vs python3 during the build stage
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create working directory
WORKDIR /app

# Get epoch
RUN git clone --recursive https://github.com/Warwick-Plasma/epoch epoch

# Create common directory for executables to live in
WORKDIR /app/epoch/bin

# Compile each dimensional version of Epoch in turn

WORKDIR /app/epoch/epoch1d
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch1d /app/epoch/bin/epoch1d
RUN make clean

WORKDIR /app/epoch/epoch2d
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch2d /app/epoch/bin/epoch2d
RUN make clean

WORKDIR /app/epoch/epoch3d
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch3d /app/epoch/bin/epoch3d
RUN make clean

# Compile versions with QED activated

WORKDIR /app/epoch/epoch1d
RUN cp Makefile Makefile.original
RUN sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch1d /app/epoch/bin/epoch1d_photons
RUN make clean
RUN mv Makefile.original Makefile

WORKDIR /app/epoch/epoch2d
RUN cp Makefile Makefile.original
RUN sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch2d /app/epoch/bin/epoch2d_photons
RUN make clean
RUN mv Makefile.original Makefile

WORKDIR /app/epoch/epoch3d
RUN cp Makefile Makefile.original
RUN sed -i 's/^#\(.*(D)PHOTONS\)$/\1/' Makefile
RUN make -j COMPILER=$EPOCH_COMPILER
RUN mv ./bin/epoch3d /app/epoch/bin/epoch3d_photons
RUN make clean
RUN mv Makefile.original Makefile

# Set up Python env

WORKDIR /app/epoch/epoch1d
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install numpy matplotlib
RUN make sdfutils

# Copy in run script

COPY run_epoch.py /app/epoch/bin/run_epoch
ENV PATH="$PATH:/app/epoch/bin"


ENTRYPOINT ["run_epoch"]
