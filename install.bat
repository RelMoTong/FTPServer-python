@echo off
echo 正在安装FTP服务器所需依赖...
echo.

REM 尝试使用常规pip命令
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 常规pip命令失败，尝试使用python -m pip...
    echo.
    python -m pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo.
        echo 安装失败。请尝试以下操作:
        echo 1. 确认Python已经正确安装
        echo 2. 确认pip已正确安装
        echo 3. 尝试手动执行: python -m pip install pyftpdlib pillow pytest pytest-cov
        echo 4. 详细指南请查看README.md文件
        exit /b 1
    )
)

echo.
echo 依赖安装成功!
echo 现在可以通过执行 python ftpserver.py 来启动FTP服务器了
echo.
pause
