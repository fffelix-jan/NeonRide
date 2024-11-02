#!/bin/sh

echo "Neon Ride macOS build script"

# Ensure the script exits if any command fails
set -e

# Define the main Python file of your game
MAIN_PY_FILE="main.py"

# Define the name of the app
APP_NAME="NeonRide"

# Define the output directory
DIST_DIR="dist"

# Define the assets directory
ASSETS_DIR="assets"

# Define the icon file
ICON_FILE="assets/icons/app_icon.icns"

# Clean up previous builds
echo "Cleaning up previous builds..."
rm -rf build $DIST_DIR

# Run pyinstaller to create the macOS app bundle with optimizations
echo "Building macOS app bundle with optimizations..."
pyinstaller --noconfirm --clean --onefile --windowed --name "$APP_NAME" \
    --add-data "$ASSETS_DIR:assets" \
    --add-data "$ASSETS_DIR/sounds:sounds" \
    --optimize=2 --icon "$ICON_FILE" "$MAIN_PY_FILE"

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Build failed. Check the pyinstaller log for details."
    exit 1
fi

# Move the app bundle to the dist directory
echo "Moving app bundle to $DIST_DIR..."
mkdir -p $DIST_DIR
mv "dist/$APP_NAME.app" $DIST_DIR

echo "Build complete. The app bundle is located in the $DIST_DIR directory."

