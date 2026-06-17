[app]
title = DS 余额
package.name = dsbalance
package.domain = com.dsbalance
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,pyjnius,android
orientation = portrait
fullscreen = 1

# Android 权限（悬浮窗 + 通知栏）
android.permissions = INTERNET,SYSTEM_ALERT_WINDOW
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a,armeabi-v7a
android.logcat_filters = *:S python:D

# 图标
icon = icon.png
presplash.color = #0f0f23

[buildozer]
log_level = 2
warn_on_root = 1
