#!/bin/bash

# Build script for Neon Ride macOS application

# Configuration
APP_NAME="Neon Ride"
SCRIPT_NAME="main.py"
ICON_PATH="./assets/icons/app_icon.icns"
ASSETS_DIR="./assets"
BUILD_DIR="./dist"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "${BUILD_DIR}"
rm -rf "./build"
rm -f "./${APP_NAME}.spec"

# Build the application using python3 -m
echo "Building macOS application..."
python3 -m PyInstaller --noconfirm \
            --clean \
            --windowed \
            --name "${APP_NAME}" \
            --icon "${ICON_PATH}" \
            --collect-all pygame \
            --noupx \
            --exclude-module pygame.sndarray \
            --exclude-module pygame.surfarray \
            --exclude-module numpy \
            --exclude-module numba \
            --exclude-module llvmlite \
            --add-data "${ASSETS_DIR}:assets" \
            --osx-bundle-identifier "ca.felixan.neonride" \
            "${SCRIPT_NAME}"

# Verify build
if [ -d "${BUILD_DIR}/${APP_NAME}.app" ]; then
    echo "Build successful! App bundle created at:"
    echo "${BUILD_DIR}/${APP_NAME}.app"
else
    echo "Build failed!"
    exit 1
fi

# Fix permissions for sound files
echo "Fixing file permissions..."
find "${BUILD_DIR}/${APP_NAME}.app/Contents/Resources/assets/sounds" -type f -exec chmod 644 {} \;

echo "Build process completed!"