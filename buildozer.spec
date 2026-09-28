[app]
title = Напёрстки Offline
package.name = thimblesoffline
package.domain = org.vanyalgrw.thimbles
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
p4a.branch = master
