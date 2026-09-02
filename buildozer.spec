[app]

# (str) Title of your application
title = Kix

# (str) Package name (com.example.*)
package.name = kix

# (str) Package domain (needed for android/ios packaging)
package.domain = org.kix

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all)
# Allowlist so tests/, .git/, .beads/, .github/, docs don't ship in the APK.
source.include_patterns = Kix/*.py, Kix/**/*.py, Kix/**/*.json, Kix/**/*.kix, Kix/assets/icons/*.png

# (str) Application versioning (method 1)
version = 0.1.0

# (list) Application requirements (pip-style).
# Pinned to avoid p4a recipe mismatches:
#   python3==3.11.6  matches Kix/README.md "Requer Python 3.11+"
#   kivy==2.3.1      matches p4a.branch = kivy-2.3.1 below
#   Pillow==10.4.0   matches Kix/requirements.txt floor; used by render/png.py
#   cython==3.0.10   cython >= 3 breaks Kivy's generated bindings (top buildozer failure)
requirements = python3==3.11.6, kivy==2.3.1, Pillow==10.4.0, cython==3.0.10

# (str) Icon — relative to source.dir; p4a resizes into mipmaps automatically.
# Regenerate with `python3 tools/make_icon.py` (idempotent).
icon.filename = %(source.dir)s/Kix/assets/icons/kix.png

# Orientation — matches Kix/core/app.py:33 (Window.size = (390, 844)).
orientation = portrait

# Mobile-first but keep status bar visible by default.
fullscreen = 0

# 2 = verbose (shows recipe errors); 1 = quieter.
log_level = 2

# (int) Target Android API.
android.api = 31

# (int) Minimum Android API (5.0 Lollipop — covers ~99% of devices).
android.minapi = 21

# (int) NDK API (must be <= android.api).
android.ndk_api = 21

# (list) Permissions — declared at install time. Covers every sensor/hardware/
# network block Kix already references in Kix/blocks/{sensors,hardware,
# audio_advanced,arvr,io,network,notifications}.py. Runtime permission flow
# is out of scope while these blocks remain stubs.
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CAMERA, RECORD_AUDIO, NFC, VIBRATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (bool) Allow backup of the application data via adb.
android.allow_backup = True

# (str) Entry point — convention: <package.domain>.<package.name>.
android.entry_point = org.kix.kix

# (str) Bootstrap: sdl2 = standard Kivy launcher (Python on top of SDL2).
p4a.bootstrap = sdl2

# (str) p4a branch — pinned to match kivy==2.3.1 above.
p4a.branch = kivy-2.3.1

# (bool) Disable .pyo compilation (tiny build speedup).
p4a.no-compile-pyo = True

# (list) Gradle dependencies to add to the Android project (none for now).
# android.gradle_dependencies =

# --- Release signing (uncomment + fill to enable `make android-release`) ---
# android.keystore = kix.keystore
# android.keyalias = kix
# android.keystore_password =
# android.keyalias_password =