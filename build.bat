@echo off
echo FTP服务器打包工具
echo =================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python。请确保Python已安装并添加到系统环境变量中。
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

REM 运行打包脚本
python build_exe.py
if %errorlevel% neq 0 (
    echo.
    echo 打包过程中发生错误。
    pause
    exit /b 1
)

echo.
echo 打包过程完成！
pause
