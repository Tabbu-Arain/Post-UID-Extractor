#!/usr/bin/env bash

apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver

# Create symlinks if needed
ln -s /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
ln -s /usr/bin/chromium-browser /usr/bin/chrome
