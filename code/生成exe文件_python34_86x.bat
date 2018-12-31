@echo 生成exe文件...
@echo off
C:\Python34\python.exe VERSION.py
C:\Python34\Scripts\pyinstaller.exe "%cd%\library_system.spec"
echo.生成成功！
pause