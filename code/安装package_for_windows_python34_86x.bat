@echo 正在安装package。。。
@echo off
C:\Python34\python -m pip install --upgrade pip
for /F %%A in (requirements.txt) do C:\Python34\Scripts\pip install %%A
echo from PyInstaller.utils.hooks import collect_submodules > C:\Python34\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo hiddenimports = collect_submodules('pandas._libs') >> C:\Python34\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo.安装成功！
pause