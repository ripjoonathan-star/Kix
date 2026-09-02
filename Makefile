# Kix — Android APK build helpers.
#
# Ubuntu/Debian prerequisites (run once before the first build):
#   sudo apt-get update
#   sudo apt-get install -y python3 python3-pip python3-venv \
#        build-essential ccache git libffi-dev libssl-dev \
#        libjpeg-dev libpng-dev zlib1g-dev libfreetype6-dev \
#        libsqlite3-dev libstdc++6 openjdk-17-jdk-headless autoconf \
#        libtool pkg-config unzip zip
# macOS: install Xcode CLT, then `brew install python@3.11 openjdk@17`.
# Windows: use WSL2 with Ubuntu (Buildozer does not run natively on Windows).
#
# Quick start:
#   make install-tools
#   make icon
#   make android-debug
#
# First build downloads ~3 GB of Android SDK/NDK into .buildozer/ and takes
# 20–40 min. Subsequent builds are 30 s – 5 min unless requirements change.

PY   ?= python3

.PHONY: help install-tools icon android-debug android-release android-clean android-purge

help:
	@echo "Targets:"
	@echo "  install-tools    pip install buildozer + cython"
	@echo "  icon             (re)generate Kix/assets/icons/kix.png"
	@echo "  android-debug    build debug APK (default for development)"
	@echo "  android-release  build release APK (requires keystore — see BUILD_ANDROID.md)"
	@echo "  android-clean    remove p4a intermediates (.buildozer/android)"
	@echo "  android-purge    nuke .buildozer/ and .bin/ (full reset — never run in CI)"

install-tools:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install "buildozer==1.5.0" "cython==3.0.10"

icon:
	$(PY) tools/make_icon.py

android-debug: icon
	buildozer android debug

android-release: icon
	# Release signing requires a keystore + android.keystore.* lines in
	# buildozer.spec. See BUILD_ANDROID.md §"Release signing" before running.
	buildozer android release

android-clean:
	buildozer android clean

android-purge:
	rm -rf .buildozer .bin