[app]
title = Machine Werkz
package.name = machinewerkz
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ogg,ttf
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py
requirements = kivy, hostpython2, android
presplash.filename = %(source.dir)s/data/img/loading.png
icon.filename = %(source.dir)s/data/img/steampunk.png
orientation = portrait
fullscreen = 0
# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86
android.arch = armeabi-v7a
[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = /home/kivy/Desktop/build
# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = /home/kivy/Desktop/bin
