[app]
title = App CNC
package.name = appcnc
package.domain = org.cnc.app
source.dir = .
source.main_py = main.py
version = 0.1

# Yêu cầu các phiên bản tương thích từ PyPI
requirements = python3,kivy==2.2.1,jnius==1.6.0,cython==3.0.10

android.arch = arm64-v8a

# Xóa các dòng source.exclude_dirs và source.exclude_patterns nếu có

[buildozer]
log_level = 2
warn_on_root = 0