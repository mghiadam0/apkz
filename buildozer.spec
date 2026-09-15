[app]
title = Quick Notes
package.name = quicknotes
package.domain = org.mghiadam0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*,static/*

version = 1.0.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = False
android.debug = True
android.release = False

p4a.branch = master
p4a.python_version = 3.11.5

[buildozer]
log_level = 2
warn_on_root = 1
