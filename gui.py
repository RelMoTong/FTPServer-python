#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from server import FTPServerManager
from utils import ToolTip, debounce

class FTPServerGUI:
    """FTP服务器图形界面类"""
    def __init__(self, root):
        self.root = root
        self.root.title("FTP服务器管理器")
        self.root.geometry("800x600")
        
        # 创建FTP服务器管理器
        self.server_manager = FTPServerManager()
        
        # 配置根窗口的行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 创建界面
        self._create_ui()
        
        # 添加窗口关闭事件处理
        root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # 添加日志过滤配置
        self.log_filter = {
            "level": "ALL",  # ALL, INFO, WARNING, ERROR, CRITICAL
            "search_text": ""
        }
        
    def _create_ui(self):
        """创建图形界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        
        # 创建各个选项卡页面
        self.tab_server = ttk.Frame(self.notebook)
        self.tab_users = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)
        
        # 配置选项卡页面的行列权重
        for tab in [self.tab_server, self.tab_users, self.tab_logs]:
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
        
        self.notebook.add(self.tab_server, text="服务器控制")
        self.notebook.add(self.tab_users, text="用户管理")
        self.notebook.add(self.tab_logs, text="日志")
        
        # 设置服务器控制选项卡
        self._create_server_tab()
        
        # 设置用户管理选项卡
        self._create_users_tab()
        
        # 设置日志选项卡
        self._create_logs_tab()
        
        # 添加状态栏
        self._create_status_bar(main_frame)
        
    def _create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=1, column=0, sticky=tk.EW, padx=10)
        status_frame.columnconfigure(1, weight=1)  # 让状态信息标签可以扩展
        
        # 状态指示灯
        self.status_indicator = ttk.Label(status_frame, text="●", foreground="red")
        self.status_indicator.grid(row=0, column=0, padx=(5, 0), pady=2)
        
        # 状态信息
        self.status_info = ttk.Label(status_frame, text="服务器未运行")
        self.status_info.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        # 连接数信息
        self.conn_info = ttk.Label(status_frame, text="连接数: 0")
        self.conn_info.grid(row=0, column=2, padx=5, pady=2)
        
        # 开始状态栏定时更新
        self._update_status_bar()
        
    def _update_status_bar(self):
        """更新状态栏信息"""
        status = self.server_manager.get_server_status()
        
        if status["running"]:
            self.status_indicator.config(foreground="green")
            self.status_info.config(text=f"服务器运行中 - {status['address']}:{status['port']}")
            self.conn_info.config(text=f"连接数: {status['connections']}")
        else:
            self.status_indicator.config(foreground="red")
            self.status_info.config(text="服务器未运行")
            self.conn_info.config(text="连接数: 0")
            
        # 每秒更新一次状态
        self.root.after(1000, self._update_status_bar)
        
    def _create_server_tab(self):
        """创建服务器控制选项卡"""
        # 服务器控制框架
        control_frame = ttk.Frame(self.tab_server)
        control_frame.grid(row=0, column=0, sticky=tk.NSEW)
        control_frame.columnconfigure(0, weight=1)
        
        # 服务器状态框架
        frame_status = ttk.LabelFrame(control_frame, text="服务器状态")
        frame_status.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
        frame_status.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(frame_status, text="服务器未运行")
        self.status_label.grid(row=0, column=0, pady=5)
        
        # 服务器控制按钮
        frame_control = ttk.Frame(control_frame)
        frame_control.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=10)
        
        self.start_button = ttk.Button(frame_control, text="启动服务器", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(frame_control, text="停止服务器", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 服务器配置框架
        frame_config = ttk.LabelFrame(control_frame, text="服务器配置")
        frame_config.grid(row=2, column=0, sticky=tk.NSEW, padx=10, pady=10)
        frame_config.columnconfigure(0, weight=1)
        frame_config.rowconfigure(0, weight=1)
        
        # 创建PanedWindow来分割配置区域
        self.config_paned = ttk.PanedWindow(frame_config, orient=tk.HORIZONTAL)
        self.config_paned.grid(row=0, column=0, sticky=tk.NSEW)
        
        # 左侧基础配置
        basic_frame = ttk.LabelFrame(self.config_paned, text="基础设置")
        self.config_paned.add(basic_frame, weight=1)
        basic_frame.columnconfigure(1, weight=1)
        
        # 获取本地IP地址列表
        ip_addresses = self.server_manager.get_local_ip_addresses()
        
        # 添加基础配置表单
        ttk.Label(basic_frame, text="监听地址:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.address_var = tk.StringVar(value=self.server_manager.config["address"])
        ip_combobox = ttk.Combobox(basic_frame, textvariable=self.address_var, values=ip_addresses)
        ip_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ToolTip(ip_combobox, "选择服务器监听的IP地址，0.0.0.0表示所有接口")
        
        ttk.Label(basic_frame, text="端口:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.IntVar(value=self.server_manager.config["port"])
        port_entry = ttk.Entry(basic_frame, textvariable=self.port_var)
        port_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        ToolTip(port_entry, "FTP服务器监听端口 (1-65535)")
        
        ttk.Label(basic_frame, text="最大连接数:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_conn_var = tk.IntVar(value=self.server_manager.config["max_connections"])
        max_conn_entry = ttk.Entry(basic_frame, textvariable=self.max_conn_var)
        max_conn_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        ToolTip(max_conn_entry, "服务器同时允许的最大连接数")
        
        # 右侧高级配置
        adv_frame = ttk.LabelFrame(self.config_paned, text="高级设置")
        self.config_paned.add(adv_frame)
        
        ttk.Label(adv_frame, text="每IP最大连接数:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_conn_ip_var = tk.IntVar(value=self.server_manager.config["max_conn_per_ip"])
        max_conn_ip_entry = ttk.Entry(adv_frame, textvariable=self.max_conn_ip_var)
        max_conn_ip_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        ToolTip(max_conn_ip_entry, "每个IP地址同时允许的最大连接数")
        
        # 修改被动端口范围设置方式
        ttk.Label(adv_frame, text="被动模式端口范围:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 创建一个框架来包含起始和结束端口
        port_range_frame = ttk.Frame(adv_frame)
        port_range_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        port_range_frame.columnconfigure(0, weight=1)
        port_range_frame.columnconfigure(2, weight=1)
        
        # 从当前配置解析端口范围
        current_range = self.server_manager.config["passive_ports"].split("-")
        start_port = int(current_range[0])
        end_port = int(current_range[1])
        
        # 创建起始端口输入框
        self.start_port_var = tk.IntVar(value=start_port)
        start_port_entry = ttk.Entry(port_range_frame, textvariable=self.start_port_var, width=7)
        start_port_entry.grid(row=0, column=0, sticky=tk.W)
        ToolTip(start_port_entry, "被动模式起始端口 (1024-65535)")
        
        ttk.Label(port_range_frame, text=" - ").grid(row=0, column=1, padx=2)
        
        # 创建结束端口输入框
        self.end_port_var = tk.IntVar(value=end_port)
        end_port_entry = ttk.Entry(port_range_frame, textvariable=self.end_port_var, width=7)
        end_port_entry.grid(row=0, column=2, sticky=tk.W)
        ToolTip(end_port_entry, "被动模式结束端口 (1024-65535)")
        
        # 添加一个标签显示端口数量
        self.port_count_label = ttk.Label(port_range_frame, text=f"共 {end_port - start_port + 1} 个端口")
        self.port_count_label.grid(row=0, column=3, padx=10)
        
        # 添加端口数量更新函数
        def update_port_count(*args):
            try:
                start = self.start_port_var.get()
                end = self.end_port_var.get()
                if start <= end:
                    count = end - start + 1
                    self.port_count_label.config(text=f"共 {count} 个端口")
                else:
                    self.port_count_label.config(text="无效范围")
            except tk.TclError:
                self.port_count_label.config(text="输入错误")
        
        # 当端口值改变时更新端口数量
        self.start_port_var.trace_add("write", update_port_count)
        self.end_port_var.trace_add("write", update_port_count)
        
        # 保存配置按钮
        save_button = ttk.Button(frame_config, text="保存配置", command=self.save_config)
        save_button.grid(row=1, column=0, pady=10)

        # 添加连接监控区域
        connection_frame = ttk.LabelFrame(control_frame, text="连接监控")
        connection_frame.grid(row=3, column=0, sticky=tk.NSEW, padx=10, pady=10)
        connection_frame.columnconfigure(0, weight=1)
        connection_frame.rowconfigure(0, weight=1)
        
        # 连接列表视图
        columns = ("ip", "port", "user", "time", "status", "file", "bytes")
        self.conn_tree = ttk.Treeview(connection_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题
        self.conn_tree.heading("ip", text="客户端IP")
        self.conn_tree.heading("port", text="端口")
        self.conn_tree.heading("user", text="用户")
        self.conn_tree.heading("time", text="连接时间")
        self.conn_tree.heading("status", text="状态")
        self.conn_tree.heading("file", text="文件")
        self.conn_tree.heading("bytes", text="已传输")
        
        # 设置列宽
        self.conn_tree.column("ip", width=100)
        self.conn_tree.column("port", width=50)
        self.conn_tree.column("user", width=80)
        self.conn_tree.column("time", width=130)
        self.conn_tree.column("status", width=80)
        self.conn_tree.column("file", width=150)
        self.conn_tree.column("bytes", width=80)
        
        # 添加滚动条
        conn_scrollbar = ttk.Scrollbar(connection_frame, orient=tk.VERTICAL, command=self.conn_tree.yview)
        self.conn_tree.configure(yscroll=conn_scrollbar.set)
        
        # 放置连接列表和滚动条
        conn_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.conn_tree.grid(row=0, column=0, sticky=tk.NSEW)
        
        # 开始定时更新连接信息
        self._update_connections()

        # 在基本配置完成后设置自动保存
        self._setup_auto_save()
        
    def _update_connections(self):
        """更新连接列表"""
        # 清空现有项目
        for item in self.conn_tree.get_children():
            self.conn_tree.delete(item)
            
        # 获取当前连接信息并添加到视图
        connections = self.server_manager.get_connections()
        for conn in connections:
            self.conn_tree.insert("", tk.END, values=(
                conn.get('ip', ''),
                conn.get('port', ''),
                conn.get('user', '匿名'),
                conn.get('time_connected', ''),
                conn.get('status', 'IDLE'),
                conn.get('file', ''),
                conn.get('bytes_transferred', '')
            ))
            
        # 每2秒更新一次连接信息
        self.root.after(2000, self._update_connections)
    
    def _create_users_tab(self):
        """创建用户管理选项卡"""
        # 用户管理框架
        users_frame = ttk.Frame(self.tab_users)
        users_frame.grid(row=0, column=0, sticky=tk.NSEW)
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(0, weight=1)
        
        # 用户列表框架
        frame_users = ttk.LabelFrame(users_frame, text="用户列表")
        frame_users.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        frame_users.columnconfigure(0, weight=1)
        frame_users.rowconfigure(0, weight=1)
        
        # 用户列表视图
        #columns = ("username", "directory", "permissions")
        columns = ("username", "directory")
        self.user_tree = ttk.Treeview(frame_users, columns=columns, show="headings")
        
        # 设置列标题
        self.user_tree.heading("username", text="用户名")
        self.user_tree.heading("directory", text="主目录")
        #self.user_tree.heading("permissions", text="权限")
        
        # 设置列宽
        self.user_tree.column("username", width=100)
        self.user_tree.column("directory", width=300)
        #self.user_tree.column("permissions", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame_users, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.user_tree.grid(row=0, column=0, sticky=tk.NSEW)
        
        # 分页控件
        page_frame = ttk.Frame(frame_users)
        page_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        self.prev_button = ttk.Button(page_frame, text="上一页", command=lambda: self._change_page(-1))
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.page_info = ttk.Label(page_frame, text="第 1/1 页")
        self.page_info.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ttk.Button(page_frame, text="下一页", command=lambda: self._change_page(1))
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # 存储当前页码
        self.current_page = 1
        self.page_size = 100
        
        # 加载用户数据
        self._load_users(self.current_page, self.page_size)
        
        # 用户操作框架
        frame_actions = ttk.Frame(users_frame)
        frame_actions.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=10)
        
        add_button = ttk.Button(frame_actions, text="添加用户", command=self.show_add_user_dialog)
        add_button.pack(side=tk.LEFT, padx=5)
        
        edit_button = ttk.Button(frame_actions, text="编辑用户", command=self.edit_user)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame_actions, text="删除用户", command=self.remove_user)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # 添加双击编辑功能
        self.user_tree.bind("<Double-1>", lambda e: self.edit_user())
    
    def _change_page(self, delta):
        """更改用户列表页码"""
        self.current_page += delta
        self._load_users(self.current_page, self.page_size)

    def _load_users(self, page=1, page_size=100):
        """分页加载用户列表"""
        # 清空现有项目
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
            
        # 获取当前页的用户
        start = (page - 1) * page_size
        end = start + page_size
        page_users = self.server_manager.users[start:end]
        
        # 添加用户
        for user in page_users:
            self.user_tree.insert("", tk.END, values=(user["username"], user["directory"], user["permissions"]))
        
        # 更新分页信息
        total_pages = max(1, (len(self.server_manager.users) + page_size - 1) // page_size)
        self.page_info.config(text=f"第 {page}/{total_pages} 页")
        
        # 更新按钮状态
        self.prev_button.config(state=tk.NORMAL if page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if page < total_pages else tk.DISABLED)
        
    def _create_logs_tab(self):
        """创建日志选项卡"""
        # 日志框架
        logs_frame = ttk.Frame(self.tab_logs)
        logs_frame.grid(row=0, column=0, sticky=tk.NSEW)
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(1, weight=1)  # 日志显示区域占用更多空间
        
        # 添加搜索和过滤控件
        filter_frame = ttk.Frame(logs_frame)
        filter_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5)
        filter_frame.columnconfigure(1, weight=1)  # 搜索框可以扩展
        
        # 日志级别过滤
        ttk.Label(filter_frame, text="级别:").grid(row=0, column=0, padx=(0, 5))
        level_values = ["ALL", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(filter_frame, textvariable=self.level_var, values=level_values, width=10)
        level_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        level_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_logs())
        
        # 搜索框
        ttk.Label(filter_frame, text="搜索:").grid(row=0, column=2, padx=(10, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=5, sticky=tk.EW)
        search_entry.bind("<Return>", lambda e: self._filter_logs())
        
        # 搜索按钮
        search_button = ttk.Button(filter_frame, text="搜索", command=self._filter_logs)
        search_button.grid(row=0, column=4, padx=5)
        
        # 清除按钮
        clear_button = ttk.Button(filter_frame, text="清除", 
                               command=lambda: [self.search_var.set(""), self.level_var.set("ALL"), self._filter_logs()])
        clear_button.grid(row=0, column=5, padx=5)
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=(0, 10))
        
        # 配置日志文本标签
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("DEBUG", foreground="gray")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("CRITICAL", foreground="red", background="yellow")
        self.log_text.tag_configure("HIGHLIGHT", background="yellow")
        
        # 存储原始日志内容
        self.log_entries = []
        
        # 加载日志
        self._load_logs()
        
        # 自动刷新日志
        self.root.after(5000, self._refresh_logs)
    
    def _load_logs(self):
        """加载日志内容"""
        try:
            if os.path.exists("logs/ftp_server.log"):
                with open("logs/ftp_server.log", "r") as f:
                    log_content = f.read()
                
                # 清空当前记录
                self.log_entries = []
                
                # 使用正则表达式匹配日志级别
                log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.*?)(?=\d{4}-\d{2}-\d{2}|\Z)'
                matches = re.findall(log_pattern, log_content, re.DOTALL)
                
                # 存储解析后的日志条目
                for timestamp, logger, level, message in matches:
                    self.log_entries.append({
                        "timestamp": timestamp,
                        "logger": logger,
                        "level": level,
                        "message": message.strip(),
                        "text": f"{timestamp} - {logger} - {level} - {message.strip()}\n"
                    })
                
                # 应用过滤并显示
                self._filter_logs()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载日志文件: {str(e)}")

    def _filter_logs(self):
        """根据过滤条件显示日志"""
        # 获取过滤条件
        level = self.level_var.get()
        search_text = self.search_var.get().lower()
        
        # 清空现有内容
        self.log_text.delete(1.0, tk.END)
        
        # 应用过滤条件
        filtered_entries = []
        for entry in self.log_entries:
            # 级别过滤
            if level != "ALL" and entry["level"] != level:
                continue
                
            # 搜索文本过滤
            if search_text and search_text not in entry["text"].lower():
                continue
                
            filtered_entries.append(entry)
        
        # 如果过滤后条目过多，只显示最近的500条以避免性能问题
        MAX_ENTRIES = 500
        if len(filtered_entries) > MAX_ENTRIES:
            filtered_entries = filtered_entries[-MAX_ENTRIES:]
            self.log_text.insert(tk.END, f"[注意: 仅显示最近 {MAX_ENTRIES} 条匹配日志]\n\n", "WARNING")
        
        # 显示过滤后的日志
        for entry in filtered_entries:
            log_level = entry["level"]
            text = entry["text"]
            
            # 插入带有适当标签的文本
            self.log_text.insert(tk.END, text, log_level)
            
            # 如果有搜索文本，高亮它
            if search_text:
                self._highlight_text(search_text)
        
        # 滚动到末尾
        self.log_text.see(tk.END)
    
    def _highlight_text(self, search_text):
        """高亮显示搜索的文本"""
        search_text = search_text.lower()
        start_pos = "1.0"
        
        while True:
            # 查找下一个匹配位置
            start_pos = self.log_text.search(search_text, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
                
            # 计算结束位置
            end_pos = f"{start_pos}+{len(search_text)}c"
            
            # 添加高亮标签
            self.log_text.tag_add("HIGHLIGHT", start_pos, end_pos)
            
            # 更新开始位置
            start_pos = end_pos
            
    def _refresh_logs(self):
        """定时刷新日志"""
        self._load_logs()  # 加载并应用当前过滤器
        self.root.after(5000, self._refresh_logs)
    
    # 为配置字段添加自动保存功能
    def _setup_auto_save(self):
        """设置配置项的自动保存功能"""
        # 为每个配置项添加跟踪变量
        self.address_var.trace_add("write", lambda *args: self._auto_save())
        self.port_var.trace_add("write", lambda *args: self._auto_save())
        self.max_conn_var.trace_add("write", lambda *args: self._auto_save())
        self.max_conn_ip_var.trace_add("write", lambda *args: self._auto_save())
        # 使用新的端口范围变量
        self.start_port_var.trace_add("write", lambda *args: self._auto_save())
        self.end_port_var.trace_add("write", lambda *args: self._auto_save())
    
    @debounce(1.0)  # 1秒内只执行一次
    def _auto_save(self):
        """自动保存配置（防抖动版本）"""
        self.save_config(show_message=False)  # 不显示保存成功消息
    
    def save_config(self, show_message=True):
        """保存服务器配置"""
        # 验证数值输入
        try:
            port = self.port_var.get()
            if port < 1 or port > 65535:
                if show_message:
                    messagebox.showerror("错误", "端口必须在1-65535范围内")
                return False
                
            max_conn = self.max_conn_var.get()
            if max_conn < 1:
                if show_message:
                    messagebox.showerror("错误", "最大连接数必须大于0")
                return False
                
            max_conn_ip = self.max_conn_ip_var.get()
            if max_conn_ip < 1:
                if show_message:
                    messagebox.showerror("错误", "每IP最大连接数必须大于0")
                return False
                
            # 验证被动端口范围
            try:
                start_port = self.start_port_var.get()
                end_port = self.end_port_var.get()
                
                if start_port < 1024 or start_port > 65535:
                    if show_message:
                        messagebox.showerror("错误", "起始端口必须在1024-65535范围内")
                    return False
                    
                if end_port < 1024 or end_port > 65535:
                    if show_message:
                        messagebox.showerror("错误", "结束端口必须在1024-65535范围内")
                    return False
                    
                if start_port > end_port:
                    if show_message:
                        messagebox.showerror("错误", "起始端口不能大于结束端口")
                    return False
                    
                # 生成被动端口范围字符串
                passive_ports = f"{start_port}-{end_port}"
                
            except tk.TclError:
                if show_message:
                    messagebox.showerror("错误", "端口必须是有效整数")
                return False
                
        except tk.TclError:
            if show_message:
                messagebox.showerror("错误", "输入值必须是有效整数")
            return False
            
        # 更新配置
        self.server_manager.config["address"] = self.address_var.get()
        self.server_manager.config["port"] = port
        self.server_manager.config["max_connections"] = max_conn
        self.server_manager.config["max_conn_per_ip"] = max_conn_ip
        self.server_manager.config["passive_ports"] = passive_ports
        
        # 保存配置
        result = self.server_manager.save_config()
        if result and show_message:
            messagebox.showinfo("成功", "配置已保存")
        elif not result and show_message:
            messagebox.showerror("错误", "保存配置失败")
            
        return result
    
    def start_server(self):
        """启动FTP服务器"""
        # 更新配置
        self.save_config(show_message=False)
        
        # 启动服务器
        result, error_msg = self.server_manager.start_server()
        if result:
            self.status_label.config(text=f"服务器正在运行 - {self.server_manager.config['address']}:{self.server_manager.config['port']}")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("成功", "FTP服务器已成功启动")
        else:
            messagebox.showerror("错误", f"启动FTP服务器失败\n\n{error_msg}")
            
    def stop_server(self):
        """停止FTP服务器"""
        result, error_msg = self.server_manager.stop_server()
        if result:
            self.status_label.config(text="服务器未运行")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showinfo("成功", "FTP服务器已停止")
        else:
            messagebox.showerror("错误", f"停止FTP服务器失败\n\n{error_msg}")
    
    def show_add_user_dialog(self):
        """显示添加用户对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加用户")
        dialog.geometry("500x400")  # 增大对话框尺寸以容纳复选框
        dialog.resizable(False, False)
        dialog.grab_set()  # 模态对话框
        
        # 创建表单
        ttk.Label(dialog, text="用户名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(dialog, text="密码:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="*").grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(dialog, text="主目录:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        directory_var = tk.StringVar()
        directory_entry = ttk.Entry(dialog, textvariable=directory_var)
        directory_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        browse_button = ttk.Button(dialog, text="浏览...", 
                                 command=lambda: directory_var.set(filedialog.askdirectory()))
        browse_button.grid(row=2, column=2, padx=5, pady=5)
        
        # 创建权限选择框架
        perm_frame = ttk.LabelFrame(dialog, text="权限设置")
        perm_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky=tk.EW)
        
        # 定义权限选项
        permissions = [
            ("e", "更改目录"),
            ("l", "列出文件"),
            ("r", "下载文件"),
            ("a", "追加数据"),
            ("d", "删除文件"),
            ("f", "重命名文件"),
            ("m", "创建目录"),
            ("w", "上传文件"),
            ("M", "修改权限"),
            ("T", "修改时间"),
        ]
        
        # 创建权限复选框
        perm_vars = {}
        for i, (perm, desc) in enumerate(permissions):
            row, col = divmod(i, 2)
            perm_vars[perm] = tk.BooleanVar(value=True)  # 默认全选
            cb = ttk.Checkbutton(perm_frame, text=f"{desc} ({perm})", variable=perm_vars[perm])
            cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # 全选/全不选按钮
        select_frame = ttk.Frame(perm_frame)
        select_frame.grid(row=len(permissions)//2 + 1, column=0, columnspan=2, pady=5)
        
        def select_all():
            for var in perm_vars.values():
                var.set(True)
        
        def deselect_all():
            for var in perm_vars.values():
                var.set(False)
        
        ttk.Button(select_frame, text="全选", command=select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="全不选", command=deselect_all).pack(side=tk.LEFT, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        def get_permissions_string():
            """根据复选框状态生成权限字符串"""
            return ''.join(perm for perm, var in perm_vars.items() if var.get())
        
        ttk.Button(button_frame, text="添加", 
                 command=lambda: self._add_user(
                     dialog, 
                     username_var.get(), 
                     password_var.get(), 
                     directory_var.get(), 
                     get_permissions_string()
                 )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="取消", 
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
                 
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
        
    def _add_user(self, dialog, username, password, directory, permissions):
        """添加用户"""
        if not username or not password or not directory:
            messagebox.showerror("错误", "所有字段都必须填写", parent=dialog)
            return
            
        # 添加用户，获取状态和消息
        success, message = self.server_manager.add_user(username, password, directory, permissions)
        
        if success:
            self._load_users()  # 重新加载用户列表
            dialog.destroy()
            messagebox.showinfo("成功", f"用户 {username} 已添加")
        else:
            # 显示具体的错误原因
            if "已存在" in message:
                messagebox.showerror("错误", f"用户 {username} 已存在，请使用其他用户名", parent=dialog)
            else:
                messagebox.showerror("错误", f"添加用户失败: {message}", parent=dialog)
            
    def remove_user(self):
        """删除选定用户"""
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的用户")
            return
            
        username = self.user_tree.item(selected_item[0])["values"][0]
        if messagebox.askyesno("确认", f"确定要删除用户 {username} 吗?"):
            if self.server_manager.remove_user(username):
                self._load_users()  # 重新加载用户列表
                messagebox.showinfo("成功", f"用户 {username} 已删除")
            else:
                messagebox.showerror("错误", f"删除用户 {username} 失败")
                
    def edit_user(self):
        """编辑选定用户"""
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要编辑的用户")
            return
            
        # 获取选定用户的信息
        selected_values = self.user_tree.item(selected_item[0])["values"]
        username = selected_values[0]
        
        # 查找用户完整信息
        user_info = None
        for user in self.server_manager.users:
            if user["username"] == username:
                user_info = user
                break
        
        if not user_info:
            messagebox.showerror("错误", f"找不到用户 {username} 的信息")
            return
            
        # 显示编辑对话框
        self.show_edit_user_dialog(user_info)

    def show_edit_user_dialog(self, user_info):
        """显示编辑用户对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"编辑用户: {user_info['username']}")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()  # 模态对话框
        
        # 创建表单
        ttk.Label(dialog, text="用户名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        username_label = ttk.Label(dialog, text=user_info["username"])
        username_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="新密码:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(dialog, textvariable=password_var, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        ttk.Label(dialog, text="(留空表示不修改)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(dialog, text="主目录:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        directory_var = tk.StringVar(value=user_info["directory"])
        directory_entry = ttk.Entry(dialog, textvariable=directory_var)
        directory_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        browse_button = ttk.Button(dialog, text="浏览...", 
                                 command=lambda: directory_var.set(filedialog.askdirectory()))
        browse_button.grid(row=2, column=2, padx=5, pady=5)
        
        # 创建权限选择框架
        perm_frame = ttk.LabelFrame(dialog, text="权限设置")
        perm_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky=tk.EW)
        
        # 定义权限选项
        permissions = [
            ("e", "更改目录"),
            ("l", "列出文件"),
            ("r", "下载文件"),
            ("a", "追加数据"),
            ("d", "删除文件"),
            ("f", "重命名文件"),
            ("m", "创建目录"),
            ("w", "上传文件"),
            ("M", "修改权限"),
            ("T", "修改时间"),
        ]
        
        # 创建权限复选框
        perm_vars = {}
        current_perms = user_info.get("permissions", "elradfmwMT")
        for i, (perm, desc) in enumerate(permissions):
            row, col = divmod(i, 2)
            perm_vars[perm] = tk.BooleanVar(value=perm in current_perms)  # 根据当前权限设置
            cb = ttk.Checkbutton(perm_frame, text=f"{desc} ({perm})", variable=perm_vars[perm])
            cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # 全选/全不选按钮
        select_frame = ttk.Frame(perm_frame)
        select_frame.grid(row=len(permissions)//2 + 1, column=0, columnspan=2, pady=5)
        
        def select_all():
            for var in perm_vars.values():
                var.set(True)
        
        def deselect_all():
            for var in perm_vars.values():
                var.set(False)
        
        ttk.Button(select_frame, text="全选", command=select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="全不选", command=deselect_all).pack(side=tk.LEFT, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        def get_permissions_string():
            """根据复选框状态生成权限字符串"""
            return ''.join(perm for perm, var in perm_vars.items() if var.get())
        
        def save_changes():
            """保存用户信息更改"""
            # 获取新密码(如果有修改)
            new_password = password_var.get() if password_var.get() else None
            
            # 获取新目录(如果有修改)
            new_directory = directory_var.get()
            if new_directory == user_info["directory"]:
                new_directory = None
                
            # 获取新权限
            new_permissions = get_permissions_string()
            if new_permissions == user_info.get("permissions", "elradfmwMT"):
                new_permissions = None
                
            # 如果没有任何修改，直接关闭对话框
            if new_password is None and new_directory is None and new_permissions is None:
                dialog.destroy()
                return
                
            # 保存更改
            if self.server_manager.update_user(
                user_info["username"], 
                new_password, 
                new_directory, 
                new_permissions
            ):
                self._load_users(self.current_page, self.page_size)  # 重新加载用户列表
                dialog.destroy()
                messagebox.showinfo("成功", f"用户 {user_info['username']} 的信息已更新")
            else:
                messagebox.showerror("错误", "更新用户信息失败", parent=dialog)
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 设置列权重
        dialog.columnconfigure(1, weight=1)
                
    def on_exit(self):
        """处理窗口关闭事件"""
        if self.server_manager.running:
            result, _ = self.server_manager.stop_server()
            if result:
                self.status_label.config(text="服务器未运行")
        self.root.destroy()
