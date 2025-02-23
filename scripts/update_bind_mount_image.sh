#!/bin/bash

# Set variables for image and container names
IMAGE_NAME="gpt-3.5-misinformation-image"
CONTAINER_NAME="gpt-3.5-misinformation-container"

# Path in the container where the current directory will be mounted
MOUNT_PATH="/app"

# Port mapping (host:container)
PORT_MAPPING="8501:8501"

# Remove any existing container with the same name
echo "Removing existing container named $CONTAINER_NAME..."
docker rm -f $CONTAINER_NAME

# Build the Docker image (this assumes your Dockerfile is in the current directory) + forcing no cache
echo "Building Docker image $IMAGE_NAME..."
docker build --no-cache -t $IMAGE_NAME .

echo "Docker image built successfully!"

# ONLY RUN THIS CODE IF YOU WANT YOUR PRIVATE DATA TO BE INCLUDED IN THE DOCKER IMAGE - PRIVATE USE
# Run the container with the specified configurations / Only Unix / Linux
# echo "Running new container named $CONTAINER_NAME from image $IMAGE_NAME..."
# docker run -d \
#   --env-file $(pwd)/.env \  # Load environment variables from .env file
#   -v $(pwd):$MOUNT_PATH \  # Mount current directory to /app in the container
#   -v $(pwd)/google_auth_key/gpt_streamlit_misinformation_auth_key.json:/app/google_auth_key/gpt_streamlit_misinformation_auth_key.json \  # Mount the auth key file
#   --name $CONTAINER_NAME \  # Assign a name to the container
#   -p $PORT_MAPPING \  # Map port 8501 from host to container
#   $IMAGE_NAME

# echo "Container $CONTAINER_NAME is now running."