[app]
title = Kix
package.name = kix
package.domain = org.kix
source.dir = Kix
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3==3.11.9,hostpython3==3.11.9,kivy,Pillow,cython
orientation = portrait
fullscreen = 0
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
log_level = 2
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
