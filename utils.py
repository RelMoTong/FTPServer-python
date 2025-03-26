#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import threading
import time
import tkinter as tk
from tkinter import ttk

class ToolTip:
    """创建工具提示类"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        
    def show_tip(self, event=None):
        """显示提示信息"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # 创建顶级窗口
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # 去掉窗口边框
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # 创建提示标签
        label = ttk.Label(self.tooltip, text=self.text, background="#FFFFCC", 
                         relief=tk.SOLID, borderwidth=1, wraplength=250,
                         justify=tk.LEFT, padding=(5, 5))
        label.pack()
        
    def hide_tip(self, event=None):
        """隐藏提示信息"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


# 防抖动装饰器，用于避免短时间内频繁调用函数
def debounce(wait):
    """防抖动装饰器，限制函数调用频率"""
    def decorator(fn):
        last_call = [0]
        timer = [None]
        
        @functools.wraps(fn)
        def debounced(*args, **kwargs):
            def call_fn():
                fn(*args, **kwargs)
                last_call[0] = time.time()
                timer[0] = None
                
            elapsed = time.time() - last_call[0]
            if elapsed >= wait:
                call_fn()
            else:
                if timer[0]:
                    timer[0].cancel()
                timer[0] = threading.Timer(wait - elapsed, call_fn)
                timer[0].start()
                
        return debounced
    return decorator
