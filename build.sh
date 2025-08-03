#!/bin/bash

# Build script for optimized Docker image

set -e

echo "🚀 Building optimized Docker image..."

# Check if we want to use the optimized version
if [ "$1" = "--optimized" ]; then
    DOCKERFILE="Dockerfile.optimized"
    echo "📦 Using multi-stage optimized Dockerfile"
else
    DOCKERFILE="Dockerfile"
    echo "📦 Using standard optimized Dockerfile"
fi

# Build with BuildKit for better performance
export DOCKER_BUILDKIT=1

# Build the image
docker build \
    --file $DOCKERFILE \
    --tag bff-app:latest \
    --progress=plain \
    .

echo "✅ Build completed successfully!"
echo ""
echo "To run the container:"
echo "docker run -p 8000:8000 bff-app:latest"
echo ""
echo "To use docker-compose:"
echo "docker-compose up" 