#!/bin/bash

# Build script for Neon Ride macOS application

# Configuration
APP_NAME="Neon Ride"
SCRIPT_NAME="neon_ride.py"
ICON_PATH="./assets/icons/app_icon.icns"
SOUNDS_DIR="./assets/sounds/"
BUILD_DIR="./dist"
SPEC_FILE="${APP_NAME}.spec"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "${BUILD_DIR}"
rm -rf "./build"
rm -f "${SPEC_FILE}"

# Create PyInstaller spec file
echo "Generating spec file..."
pyi-makespec --name "${APP_NAME}" \
             --windowed \
             --icon "${ICON_PATH}" \
             --add-data "${SOUNDS_DIR}/*:assets/sounds" \
             --osx-bundle-identifier "com.greenyman.neonride" \
             "${SCRIPT_NAME}"

# Modify spec file to include ICNS properly
sed -i '' -e $'s/iconfile=None/iconfile="\'${ICON_PATH}\'"/' "${SPEC_FILE}"

# Build the application
echo "Building macOS application..."
python3 -m PyInstaller --noconfirm \
            --clean \
            --windowed \
            --icon "${ICON_PATH}" \
            --add-data "${SOUNDS_DIR}/*:assets/sounds" \
            --osx-bundle-identifier "com.greenyman.neonride" \
            "${SPEC_FILE}"

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