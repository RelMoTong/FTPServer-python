#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk

# 检查必要的依赖是否已安装
try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
except ImportError:
    print("错误: 缺少必要的依赖 'pyftpdlib'")
    print("\n请按以下步骤安装依赖:")
    print("1. 打开命令提示符或终端")
    print("2. 执行以下命令:")
    print("   pip install pyftpdlib pillow")
    print("\n如果您使用的是虚拟环境, 请先激活虚拟环境:")
    print("   Windows: .venv\\Scripts\\activate")
    print("   Linux/Mac: source .venv/bin/activate")
    print("\n如果pip命令无法使用, 请尝试:")
    print("   python -m pip install pyftpdlib pillow")
    print("\n或参考安装指南: README.md")
    sys.exit(1)

from gui import FTPServerGUI

def main():
    """程序入口函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 创建FTP服务器GUI
    app = FTPServerGUI(root)
    
    # 启动主循环
    root.mainloop()
    
if __name__ == "__main__":
    main()
