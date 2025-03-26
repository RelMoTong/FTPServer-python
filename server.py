#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import threading
import socket
from datetime import datetime

# 导入FTP服务器依赖
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# 导入配置管理器
from config import ConfigManager

class FTPServerManager:
    """FTP服务器管理类，负责服务器的启动、停止和管理"""
    
    def __init__(self, config_path="config/settings.json", users_path="config/users.json"):
        """初始化FTP服务器管理器"""
        # 初始化配置
        self.config_manager = ConfigManager(config_path, users_path)
        self.server = None
        self.server_thread = None
        self.running = False
        
        # 初始化日志
        self.setup_logging()
        
        # 加载配置
        self.config = self.config_manager.load_config()
        self.users = self.config_manager.load_users()
        
    def setup_logging(self):
        """设置日志记录"""
        log_dir = os.path.dirname("logs/ftp_server.log")
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except Exception as e:
            print(f"无法创建日志目录: {str(e)}")
            sys.exit(1)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("logs/ftp_server.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("FTPServer")
    
    def get_local_ip_addresses(self):
        """获取本机所有有效IP地址列表"""
        ip_list = []
        try:
            # 获取本机主机名
            hostname = socket.gethostname()
            # 获取本机IP (包括IPv4和IPv6)
            addresses = socket.getaddrinfo(hostname, None)
            
            # 筛选IPv4地址
            for addr in addresses:
                if addr[0] == socket.AF_INET:  # 只取IPv4地址
                    ip = addr[4][0]
                    if ip not in ip_list and not ip.startswith('127.'):  # 排除localhost
                        ip_list.append(ip)
            
            # 始终添加localhost和0.0.0.0（所有接口）
            if '127.0.0.1' not in ip_list:
                ip_list.append('127.0.0.1')
            if '0.0.0.0' not in ip_list:
                ip_list.append('0.0.0.0')
                
            return ip_list
        except Exception as e:
            self.logger.error(f"获取本机IP地址失败: {str(e)}")
            return ['127.0.0.1', '0.0.0.0']  # 返回默认值
    
    def is_valid_binding_address(self, address):
        """验证IP地址是否可以用于绑定"""
        # 特殊情况: 0.0.0.0表示绑定所有接口，始终有效
        if address == "0.0.0.0":
            return True
            
        # 获取本机所有IP地址
        valid_ips = self.get_local_ip_addresses()
        
        return address in valid_ips
    
    def start_server(self):
        """启动FTP服务器"""
        if self.running:
            self.logger.warning("服务器已经在运行")
            return False, "服务器已经在运行"
            
        try:
            # 验证绑定地址是否有效
            if not self.is_valid_binding_address(self.config["address"]):
                valid_ips = self.get_local_ip_addresses()
                err_msg = f"IP地址 {self.config['address']} 不是本机有效的网络接口地址。\n\n"
                err_msg += "请使用以下有效的IP地址之一:\n- " + "\n- ".join(valid_ips)
                self.logger.error(f"无效的绑定地址: {self.config['address']}")
                raise ValueError(err_msg)
                
            # 创建认证器
            authorizer = DummyAuthorizer()
            
            # 添加用户
            for user in self.users:
                perm = user.get("permissions", "elradfmwMT")  # 默认权限
                authorizer.add_user(
                    user["username"], 
                    user["password"], 
                    user["directory"], 
                    perm=perm
                )
            
            # 设置FTP处理器
            handler = FTPHandler
            handler.authorizer = authorizer
            handler.banner = "FTP服务器已准备就绪"
            
            # 被动模式设置
            if "passive_ports" in self.config:
                try:
                    ports = self.config["passive_ports"].split("-")
                    if len(ports) != 2:
                        raise ValueError("被动端口格式应为'起始端口-结束端口'")
                    start, end = int(ports[0]), int(ports[1])
                    if start > end:
                        raise ValueError("起始端口不能大于结束端口")
                    handler.passive_ports = range(start, end + 1)  # 结束端口+1
                except ValueError as e:
                    return False, f"无效的被动端口设置: {str(e)}"
            
            # 创建FTP服务器
            address = (self.config["address"], self.config["port"])
            self.server = FTPServer(address, handler)
            
            # 设置并发连接限制
            self.server.max_cons = self.config["max_connections"]
            self.server.max_cons_per_ip = self.config["max_conn_per_ip"]
            
            # 在单独的线程中启动服务器
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            self.logger.info(f"FTP服务器启动成功，监听地址: {self.config['address']}:{self.config['port']}")
            return True, None
            
        except ValueError as ve:
            # 处理我们自定义的IP验证错误
            self.logger.error(f"启动服务器失败: {str(ve)}")
            return False, str(ve)
        except socket.error as se:
            # 处理套接字相关错误
            if hasattr(se, 'errno') and se.errno == 10049:  # Windows特定的错误码WSAEADDRNOTAVAIL
                valid_ips = self.get_local_ip_addresses()
                err_msg = f"IP地址 {self.config['address']} 不是本机有效的网络接口地址。\n\n"
                err_msg += "请使用以下有效的IP地址之一:\n- " + "\n- ".join(valid_ips)
                self.logger.error(f"无效的绑定地址: {self.config['address']}, 错误: {str(se)}")
                return False, err_msg
            else:
                self.logger.error(f"启动服务器失败，套接字错误: {str(se)}")
                return False, f"套接字错误: {str(se)}"
        except Exception as e:
            self.logger.error(f"启动服务器失败: {str(e)}")
            return False, str(e)
    
    def stop_server(self):
        """停止FTP服务器"""
        if not self.running:
            self.logger.warning("服务器未在运行")
            return False, "服务器未在运行"
        
        try:
            self.server.close_all()
            self.server.close()  # 关闭监听套接字
            if self.server_thread:
                self.server_thread.join(timeout=5)
            self.running = False
            self.logger.info("FTP服务器已停止")
            return True, None
        except Exception as e:
            self.logger.error(f"停止服务器失败: {str(e)}")
            return False, str(e)
    
    def add_user(self, username, password, directory, permissions="elradfmwMT"):
        """添加新用户
        
        返回:
            tuple: (成功状态, 消息)
        """
        # 检查用户是否已存在
        for user in self.users:
            if user["username"] == username:
                self.logger.warning(f"尝试添加重复的用户名: {username}")
                return False, "用户名已存在"
                
        # 创建用户目录
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            error_msg = f"创建目录失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
                
        # 添加新用户到配置管理器
        self.users.append({
            "username": username,
            "password": password,
            "directory": directory,
            "permissions": permissions
        })
        
        # 保存用户信息
        if self.config_manager.save_users():
            return True, "用户添加成功"
        else:
            return False, "保存用户信息失败"
        
    def remove_user(self, username):
        """删除用户"""
        for i, user in enumerate(self.users):
            if user["username"] == username:
                del self.users[i]
                return self.config_manager.save_users()
        return False
        
    def update_user(self, username, new_password=None, new_directory=None, new_permissions=None):
        """更新用户信息"""
        for i, user in enumerate(self.users):
            if user["username"] == username:
                # 仅更新提供的字段
                if new_password is not None:
                    self.users[i]["password"] = new_password
                if new_directory is not None:
                    # 确保目录存在
                    try:
                        os.makedirs(new_directory, exist_ok=True)
                        self.users[i]["directory"] = new_directory
                    except OSError as e:
                        self.logger.error(f"创建目录失败: {str(e)}")
                        return False
                if new_permissions is not None:
                    self.users[i]["permissions"] = new_permissions
                    
                # 保存更新后的用户信息
                return self.config_manager.save_users()
        
        # 如果没有找到用户
        return False

    def save_config(self):
        """保存服务器配置"""
        return self.config_manager.save_config()

    def get_server_status(self):
        """获取服务器当前状态信息"""
        if not self.running:
            return {
                "running": False,
                "connections": 0,
                "address": "-",
                "port": "-"
            }
        
        # 获取当前连接数
        try:
            active_conns = len(self.server._map) - 2  # 减去监听socket和定时器
            if active_conns < 0:
                active_conns = 0
                
            return {
                "running": True,
                "connections": active_conns,
                "address": self.config["address"],
                "port": self.config["port"]
            }
        except:
            return {
                "running": True,
                "connections": 0,
                "address": self.config["address"],
                "port": self.config["port"]
            }

    def get_connections(self):
        """获取当前所有连接的信息"""
        connections = []
        if not self.running or not self.server:
            return connections
            
        try:
            # 遍历所有活动连接
            for sock in list(self.server._map.values()):
                # 跳过服务器监听socket和定时器
                if not hasattr(sock, 'cmd_channel') or not hasattr(sock, 'remote_ip'):
                    continue
                    
                # 获取连接信息
                conn_info = {
                    'ip': sock.remote_ip,
                    'port': sock.remote_port,
                    'user': sock.username if hasattr(sock, 'username') else '匿名',
                    'time_connected': datetime.fromtimestamp(sock.created).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'IDLE' if not hasattr(sock, 'data_channel') else 'ACTIVE'
                }
                
                # 如果正在传输，添加传输信息
                if hasattr(sock, 'data_channel') and sock.data_channel is not None:
                    if hasattr(sock.data_channel, 'file_obj'):
                        conn_info['file'] = os.path.basename(sock.data_channel.file_obj.name) 
                        conn_info['bytes_transferred'] = sock.data_channel.tot_bytes_sent
                    conn_info['status'] = 'TRANSFERRING'
                    
                connections.append(conn_info)
        except Exception as e:
            self.logger.error(f"获取连接信息失败: {str(e)}")
            
        return connections
