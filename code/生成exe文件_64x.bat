@echo 生成exe文件。
@echo off
%USERPROFILE%\AppData\Local\Programs\Python\Python35\Scripts\pyinstaller.exe -F %cd%\library_system.py
echo.生成成功！
pause