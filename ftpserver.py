#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FTP服务器管理程序
这个文件作为向后兼容性入口点，导入并执行main.py中的程序。
"""

import sys
import os

# 检查Python版本
if sys.version_info < (3, 6):
    print("错误: 需要 Python 3.6 或更高版本")
    sys.exit(1)

# 导入并执行主程序
try:
    from main import main
    main()
except ImportError as e:
    print(f"错误: 无法导入主程序: {e}")
    print("请确保所有必要的模块文件 (main.py, gui.py, server.py, config.py, utils.py) 都在同一目录下。")
    sys.exit(1)
