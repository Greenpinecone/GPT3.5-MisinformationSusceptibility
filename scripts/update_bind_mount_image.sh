#!/bin/bash

# Set variables for image and container names
IMAGE_NAME="bachelor_work_project_image"
CONTAINER_NAME="bachelor_work_project_container"

# Path in the container where the current directory will be mounted
MOUNT_PATH="/app"

# Port mapping (host:container)
PORT_MAPPING="8501:8501"

# Remove any existing container with the same name
echo "Removing existing container named $CONTAINER_NAME..."
docker rm -f $CONTAINER_NAME

# Build the Docker image (this assumes your Dockerfile is in the current directory)
echo "Building Docker image $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Run the container with the specified configurations / Only Unix / Linux
echo "Running new container named $CONTAINER_NAME from image $IMAGE_NAME..."
docker run -d -v $(pwd):$MOUNT_PATH --name $CONTAINER_NAME -p $PORT_MAPPING $IMAGE_NAME

echo "Container $CONTAINER_NAME is now running."