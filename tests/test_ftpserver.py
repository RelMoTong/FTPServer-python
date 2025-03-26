#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径，以便引入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ftpserver import FTPServerManager

class TestFTPServerManager:
    """FTP服务器管理器测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
        
    @pytest.fixture
    def server_manager(self, temp_dir):
        """创建带有临时配置的FTPServerManager实例"""
        # 创建临时配置文件
        config_dir = os.path.join(temp_dir, 'config')
        os.makedirs(config_dir)
        
        # 创建settings.json
        settings_file = os.path.join(config_dir, 'settings.json')
        settings = {
            "port": 2121,
            "max_connections": 256,
            "max_conn_per_ip": 5,
            "address": "127.0.0.1",
            "passive_ports": "60000-60100"
        }
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
            
        # 创建users.json
        users_file = os.path.join(config_dir, 'users.json')
        users = [
            {
                "username": "test_user",
                "password": "password123",
                "directory": os.path.join(temp_dir, 'ftp_files', 'test_user'),
                "permissions": "elr"
            }
        ]
        with open(users_file, 'w') as f:
            json.dump(users, f)
            
        # 创建日志目录
        log_dir = os.path.join(temp_dir, 'logs')
        os.makedirs(log_dir)
        
        # 创建用户目录
        os.makedirs(os.path.join(temp_dir, 'ftp_files', 'test_user'))
        
        # 返回服务器管理器
        return FTPServerManager(settings_file, users_file)
    
    def test_load_config(self, server_manager):
        """测试配置加载功能"""
        assert server_manager.config["port"] == 2121
        assert server_manager.config["address"] == "127.0.0.1"
        assert len(server_manager.users) == 1
        assert server_manager.users[0]["username"] == "test_user"
        assert server_manager.users[0]["password"] == "password123"
        
    def test_add_user(self, server_manager, temp_dir):
        """测试添加用户功能"""
        # 添加新用户
        user_dir = os.path.join(temp_dir, 'ftp_files', 'new_user')
        result = server_manager.add_user("new_user", "new_pass", user_dir)
        
        # 验证结果
        assert result is True
        assert len(server_manager.users) == 2
        assert any(user["username"] == "new_user" for user in server_manager.users)
        assert os.path.exists(user_dir)
        
    def test_remove_user(self, server_manager):
        """测试删除用户功能"""
        # 删除用户
        result = server_manager.remove_user("test_user")
        
        # 验证结果
        assert result is True
        assert len(server_manager.users) == 0
        
    def test_save_config(self, server_manager):
        """测试保存配置功能"""
        # 修改配置
        server_manager.config["port"] = 2222
        
        # 保存配置
        result = server_manager.save_config()
        
        # 验证结果
        assert result is True
        
        # 重新加载配置
        server_manager.load_config()
        assert server_manager.config["port"] == 2222
        
    def test_server_start_stop(self, server_manager):
        """测试服务器启动和停止功能"""
        # 启动服务器
        start_result, _ = server_manager.start_server()
        assert start_result is True
        assert server_manager.running is True
        
        # 停止服务器
        stop_result, _ = server_manager.stop_server()
        assert stop_result is True
        assert server_manager.running is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])
