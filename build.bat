@echo off
setlocal enabledelayedexpansion

echo 🚀 Building optimized Docker image...

REM Check if we want to use the optimized version
if "%1"=="--optimized" (
    set DOCKERFILE=Dockerfile.optimized
    echo 📦 Using multi-stage optimized Dockerfile
) else (
    set DOCKERFILE=Dockerfile
    echo 📦 Using standard optimized Dockerfile
)

REM Build with BuildKit for better performance
set DOCKER_BUILDKIT=1

REM Build the image
docker build ^
    --file %DOCKERFILE% ^
    --tag bff-app:latest ^
    --progress=plain ^
    .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Build completed successfully!
    echo.
    echo To run the container:
    echo docker run -p 8000:8000 bff-app:latest
    echo.
    echo To use docker-compose:
    echo docker-compose up
) else (
    echo ❌ Build failed!
    exit /b 1
) 