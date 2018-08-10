@echo 正在安装package。。。
@echo off
%USERPROFILE%\AppData\Local\Programs\Python\Python36-32\python -m pip install --upgrade pip
%USERPROFILE%\AppData\Local\Programs\Python\Python36-32\Scripts\pip install -r requirements.txt
echo from PyInstaller.utils.hooks import collect_submodules > %USERPROFILE%\AppData\Local\Programs\Python\Python36-32\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo hiddenimports = collect_submodules('pandas._libs') >> %USERPROFILE%\AppData\Local\Programs\Python\Python36-32\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo.安装成功！
pause