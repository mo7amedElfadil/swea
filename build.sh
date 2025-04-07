#!/usr/bin/env bash

set -euo pipefail

# Variables
readonly VENV_DIR=".venv"
readonly APP_NAME="swea"
readonly ENTRY_SCRIPT="app/run.py"
readonly DIST_DIR="dist"
readonly BUILD_DIR="build"
readonly SPEC_FILE="${APP_NAME}.spec"

# Colors for better output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Function to print error messages
error() {
  echo -e "${RED}[ERROR]${NC} $1" >&2
  exit 1
}

# Function to print success messages
success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to print info messages
info() {
  echo -e "${YELLOW}[INFO]${NC} $1"
}

# Check for Python and PyInstaller
check_dependencies() {
  if ! command -v python3 &>/dev/null; then
    error "Python3 is not installed"
  fi
}

# Main build function
build_app() {
  info "Checking dependencies..."
  check_dependencies

  # Create virtual environment if it doesn't exist
  if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment"
  fi

  info "Activating virtual environment..."
  source "$VENV_DIR/bin/activate" || error "Failed to activate virtual environment"

  info "Installing requirements..."
  pip install -r requirements.txt || error "Failed to install requirements"

  if ! python3 -c "import pyinstaller" &>/dev/null; then
    info "PyInstaller not found, installing..."
    pip install pyinstaller || error "Failed to install PyInstaller"
  fi

  info "Cleaning previous builds..."
  rm -rf "$DIST_DIR" "$BUILD_DIR" "$SPEC_FILE"

  info "Compiling the application..."
  pyinstaller --noconfirm --clean --onefile \
    --name "$APP_NAME" \
    --add-data "app/templates:app/templates" \
    --add-data "app/static:app/static" \
    --add-data "app/translations:app/translations" \
    "$ENTRY_SCRIPT" || error "PyInstaller failed"

  # Move the compiled binary
  if [ -f "$DIST_DIR/$APP_NAME" ]; then
    mv "$DIST_DIR/$APP_NAME" ./
    success "Build complete! Run the application with: ./$APP_NAME"
  else
    error "Build failed - executable not found"
  fi

  # Clean up
  info "Cleaning up..."
  rm -rf "$DIST_DIR" "$BUILD_DIR" "$SPEC_FILE"

  deactivate
}

build_app
