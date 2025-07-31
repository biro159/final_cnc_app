[app]
title = App CNC
package.name = appcnc
package.domain = org.cnc.app
source.dir = .
source.main_py = main.py
version = 0.1

# Yêu cầu các phiên bản mới nhất và tương thích
requirements = python3,kivy==2.3.0,cython==3.0.10,pillow

# Kiến trúc (đã sửa thành archs)
android.archs = arm64-v8a

# Bỏ qua các thư mục không cần thiết
source.exclude_patterns = tests/*, test/*, .github/*, venv/

[buildozer]
log_level = 2
warn_on_root = 0

# Ép Buildozer dùng phiên bản python-for-android mới nhất
p4a.branch = master