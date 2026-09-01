[app]
# (str) Title of your application
title = Kix

# (str) Package name
package.name = kix

# (str) Package domain (needed for android/ios packaging)
package.domain = org.kixengine

# (str) Source code where the main.py live
source.dir = Kix

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (str) Application versioning (method 1)
version = 0.7.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,Pillow

# (str) Presplash (wait screen)
# (str) Icon of the application
# icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB, #AARRGGBB, or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (str) Icon background color (for android toolchain)
# Supported formats are: #RRGGBB, #AARRGGBB, or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.icon_background_color = #0D0D0E

# (list) Permissions
#android.permissions = INTERNET

# (bool) Indicate whether the screen should be rotated on device orientation change
# Behavior: True - allow rotation, False - disable rotation
#android.orientations = portrait

# Python for android: p4a
# (str) python-for-android URL to use for checkout
#p4a.url =

# (str) python-for-android fork to use in case git clone of p4a fails
#p4a.fork = kivy

# (str) python-for-android branch to use, default is master
#p4a.branch = master

# (list) python-for-android recipes to include
#p4a.local_recipes =

# (bool) If True, then skip trying to download the NDK
#p4a.no_ndk = False

# (str) The version of the NDK to use
#p4a.ndk_version = r23b

# (str) android NDK version to use
#android.ndk_version = r23b

# (str) android SDK version to use
#android.sdk_version = 33

# (int) Android entry point (default 0)
#android.entrypoint = 0

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to the asset directory
# (str) Path to the data directory
# (str) Path to the translation directory
# (str) Path to the persistence directory

# (str) Path to custom icon
# (str) Path to custom presplash

# (str) Whether to use system library or build SDL/SDL_image from sources
#android.use_system_libs = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if the app used a Python feature (default 1)
warn_on_python = 1
