@echo 生成exe文件。
@echo off
%USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts\pyinstaller.exe %cd%\library_system64x.spec
echo.生成成功！
pause