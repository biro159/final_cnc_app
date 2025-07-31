[app]
title = App CNC
package.name = appcnc
package.domain = org.cnc.app
source.dir = .
source.main_py = main.py
version = 0.1
requirements = python3,kivy
android.arch = arm64-v8a

# Dòng mới bạn vừa thêm vào/thay thế
source.exclude_patterns = tests/*, test/*, .github/*

[buildozer]
log_level = 2
warn_on_root = 0