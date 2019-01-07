#!/usr/bin/env bash

# Print sub commands and fail on error
set -ex

REPOSITORY=
IMAGE_LOCATION=gcr.io/scarlet-labs
RUN_IMAGE_NAME=selenium-py37-image
RUN_IMAGE_VERSION=$(date +"%Y%m%dT%H%M%S")

mkdir -p target/docker

# Write tags to files similar to how docker-maven-plugin does it
echo $IMAGE_LOCATION/$RUN_IMAGE_NAME:$RUN_IMAGE_VERSION > target/docker/image-name

# Build docker image, name and tag it, and push to registry.
gcloud docker -- build -f selenium.docker -t $IMAGE_LOCATION/$RUN_IMAGE_NAME:$RUN_IMAGE_VERSION -t $IMAGE_LOCATION/$RUN_IMAGE_NAME:latest .
gcloud docker -- push $IMAGE_LOCATION/$RUN_IMAGE_NAME:$RUN_IMAGE_VERSION
gcloud docker -- push $IMAGE_LOCATION/$RUN_IMAGE_NAME:latest

echo "Successfully built image as version $RUN_IMAGE_VERSION"
