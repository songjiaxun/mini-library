@echo 正在安装package。。。
@echo off
%USERPROFILE%\AppData\Local\Programs\Python\Python36\python -m pip install --upgrade pip
%USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts\pip install -r requirements.txt
echo.安装成功！
pause