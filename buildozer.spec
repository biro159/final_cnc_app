[app]

title = App CNC
package.name = appcnc
package.domain = org.cnc.app
source.dir = .
source.main_py = main.py
version = 0.1

# YÊU CẦU QUAN TRỌNG NHẤT: Ép build với Python 3.9.18
requirements = python3==3.9.18,kivy==2.2.1,jnius==1.6.0,cython==0.29.37

android.arch = arm64-v8a

# Thêm dòng này để tăng thời gian chờ, tránh lỗi timeout khi tải
p4a.local_recipes = ./recipes