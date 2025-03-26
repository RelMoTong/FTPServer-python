#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging

class ConfigManager:
    """配置管理类，处理配置文件的加载、保存和验证"""
    
    def __init__(self, config_path="config/settings.json", users_path="config/users.json"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.users_path = users_path
        self.config = {}
        self.users = []
        self.logger = logging.getLogger("FTPServer.Config")
        
    def load_config(self):
        """加载服务器配置"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info("配置加载成功")
            
            # 验证配置
            errors = self.validate_config()
            if errors:
                self.logger.warning("配置验证发现问题: " + "; ".join(errors))
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            self.config = {
                "port": 2121,
                "max_connections": 256,
                "max_conn_per_ip": 5,
                "address": "0.0.0.0",
                "passive_ports": "60000-60100"
            }
        
        return self.config
        
    def load_users(self):
        """加载用户信息"""
        try:
            with open(self.users_path, 'r') as f:
                self.users = json.load(f)
            self.logger.info("用户信息加载成功")
        except Exception as e:
            self.logger.error(f"加载用户文件失败: {str(e)}")
            self.users = []
            
        return self.users
        
    def save_config(self):
        """保存服务器配置到文件"""
        # 验证配置
        errors = self.validate_config()
        if errors:
            self.logger.warning("配置验证发现问题: " + "; ".join(errors))
            return False
            
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("配置保存成功")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
            return False
            
    def save_users(self):
        """保存用户信息到文件"""
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.users_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(self.users_path, 'w') as f:
                json.dump(self.users, f, indent=4)
            self.logger.info("用户信息保存成功")
            return True
        except Exception as e:
            self.logger.error(f"保存用户信息失败: {str(e)}")
            return False
    
    def validate_config(self):
        """验证配置是否合法"""
        errors = []
        
        # 验证端口
        if not isinstance(self.config.get("port"), int):
            errors.append("端口必须是整数")
        elif self.config.get("port") < 1 or self.config.get("port") > 65535:
            errors.append("端口必须在1-65535范围内")
            
        # 验证最大连接数
        if not isinstance(self.config.get("max_connections"), int):
            errors.append("最大连接数必须是整数")
        elif self.config.get("max_connections") < 1:
            errors.append("最大连接数必须大于0")
            
        # 验证每IP最大连接数
        if not isinstance(self.config.get("max_conn_per_ip"), int):
            errors.append("每IP最大连接数必须是整数")
        elif self.config.get("max_conn_per_ip") < 1:
            errors.append("每IP最大连接数必须大于0")
            
        # 验证被动端口范围
        if "passive_ports" in self.config:
            try:
                ports = self.config["passive_ports"].split("-")
                if len(ports) != 2:
                    errors.append("被动端口格式应为'起始端口-结束端口'")
                else:
                    start, end = int(ports[0]), int(ports[1])
                    if start < 1024 or end > 65535 or start > end:
                        errors.append("被动端口范围无效，应为1024-65535之间，且起始端口小于结束端口")
            except ValueError:
                errors.append("被动端口必须是数字")
                
        return errors
        
    def add_user(self, username, password, directory, permissions="elradfmwMT"):
        """添加新用户"""
        # 检查用户是否已存在
        for user in self.users:
            if user["username"] == username:
                return False
                
        # 添加新用户
        self.users.append({
            "username": username,
            "password": password,
            "directory": directory,
            "permissions": permissions
        })
        
        # 保存用户信息
        return self.save_users()
        
    def remove_user(self, username):
        """删除用户"""
        for i, user in enumerate(self.users):
            if user["username"] == username:
                del self.users[i]
                return self.save_users()
        return False
        
    def update_config(self, new_config):
        """更新配置"""
        self.config.update(new_config)
        return self.save_config()
