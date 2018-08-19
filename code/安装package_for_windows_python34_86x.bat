@echo 正在安装package。。。
@echo off
C:\Python34_86x\python -m pip install --upgrade pip
C:\Python34_86x\Scripts\pip3.4 install -r requirements1.txt
C:\Python34_86x\Scripts\pip3.4 install -r requirements2.txt
echo from PyInstaller.utils.hooks import collect_submodules > C:\Python34_86x\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo hiddenimports = collect_submodules('pandas._libs') >> C:\Python34_86x\Lib\site-packages\PyInstaller\hooks\hook-pandas.py
echo.安装成功！
pause