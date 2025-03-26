#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        # Check if PyInstaller is installed by running a simple command
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        print("安装失败。请手动执行: pip install pyinstaller")
        return False

def build_exe():
    """构建可执行文件"""
    print("开始构建FTP服务器可执行文件...")
    
    # 确保工作目录正确
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 创建dist和build目录（如果不存在）
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # 创建固定图标 (如果不存在)
    icon_path = os.path.join(script_dir, "resources", "ftp_icon.ico")
    if not os.path.exists(icon_path):
        os.makedirs(os.path.join(script_dir, "resources"), exist_ok=True)
        print("注意: FTP图标文件不存在。")
        print("将使用默认图标。")
        icon_path = None
    
    # 配置PyInstaller命令
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--name=FTPServer",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 无控制台窗口
        "--clean",  # 清理临时文件
        "--add-data", f"config{os.pathsep}config",  # 添加配置目录
        "--add-data", f"logs{os.pathsep}logs"  # 添加日志目录
    ]
    
    # 添加图标（如果存在）
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # 添加主脚本
    cmd.append("ftpserver.py")
    
    # 执行打包命令
    try:
        subprocess.check_call(cmd)
        print("\n打包完成！可执行文件位于 dist/FTPServer.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        return False

def create_distribution_package():
    """创建完整的分发包"""
    print("正在创建分发包...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(script_dir, "dist")
    package_dir = os.path.join(dist_dir, "FTP服务器")
    
    try:
        # 创建分发目录
        os.makedirs(package_dir, exist_ok=True)
        
        # 复制可执行文件
        shutil.copy(os.path.join(dist_dir, "FTPServer.exe"), package_dir)
        
        # 复制配置模板
        config_dir = os.path.join(package_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # 创建默认配置文件
        with open(os.path.join(config_dir, "settings.json"), "w", encoding="utf-8") as f:
            f.write('''{
    "port": 2121,
    "max_connections": 256,
    "max_conn_per_ip": 5,
    "address": "0.0.0.0",
    "passive_ports": "60000-60100"
}''')
        
        with open(os.path.join(config_dir, "users.json"), "w", encoding="utf-8") as f:
            f.write('''[
    {
        "username": "admin",
        "password": "admin",
        "directory": "ftp_files/admin",
        "permissions": "elradfmwMT"
    }
]''')
        
        # 创建用户文件目录
        os.makedirs(os.path.join(package_dir, "ftp_files", "admin"), exist_ok=True)
        
        # 创建日志目录
        os.makedirs(os.path.join(package_dir, "logs"), exist_ok=True)
        
        # 创建README文件
        with open(os.path.join(package_dir, "使用说明.txt"), "w", encoding="utf-8") as f:
            f.write('''FTP服务器使用说明

1. 启动服务器：
   双击 FTPServer.exe 文件启动服务器

2. 默认用户：
   用户名：admin
   密码：admin
   
3. 配置文件：
   服务器配置：config/settings.json
   用户配置：config/users.json
   
4. 文件存储：
   用户上传的文件存储在 ftp_files/[用户名] 目录下

5. 日志：
   服务器运行日志保存在 logs 目录下

6. 修改配置：
   可以通过图形界面修改服务器配置和用户信息，也可以直接编辑配置文件
''')
        
        print(f"\n分发包创建成功! 位置: {package_dir}")
        print("你可以将此文件夹复制到任何Windows电脑上运行。")
        return True
    except Exception as e:
        print(f"创建分发包失败: {e}")
        return False

def main():
    """主函数"""
    print("FTP服务器打包工具\n")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller。这是必需的打包工具。")
        if not install_pyinstaller():
            return
    
    # 构建可执行文件
    if not build_exe():
        return
    
    # 创建完整分发包
    create_distribution_package()
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()
