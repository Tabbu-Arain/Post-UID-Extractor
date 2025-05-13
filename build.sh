#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# Update package list and install Chromium and Chromedriver
apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver

# Create symlinks so Selenium can find Chromium and Chromedriver
ln -sf /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome

echo "✅ Chromium and Chromedriver installed."
