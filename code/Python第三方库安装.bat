@echo 安装Python所需第三方库，请接入互联网。
@echo off
set "FileName=PIP3.6.EXE"
echo 正在搜索Python pip安装路径，请稍候...
for %%a in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%a:\nul (
        pushd %%a:\
        for /r %%b in ("*%FileName%") do (
            if /i "%%~nxb" equ "%FileName%" (
                echo.Python pip安装路径如下：
                echo.%%b
                set pippath=%%b
            )
        )
        popd
    )
)
echo.正在加载Python所需第三方库，请稍候...
"%pippath%" install openpyxl
"%pippath%" install requests
"%pippath%" install xlrd
"%pippath%" install pyinstaller
echo.安装完成！
pause