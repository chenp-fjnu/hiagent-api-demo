#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动Git提交监控系统
监控指定目录的文件变化，自动提交到Git仓库
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutoGitCommitHandler(FileSystemEventHandler):
    def __init__(self, config_path="auto_commit_config.json"):
        """初始化文件监控处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.last_commit_time = {}
        self.commit_lock = threading.Lock()
        self.pending_files = set()
        
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "watch_directory": ".",
            "commit_delay": 5,  # 秒
            "max_files_per_commit": 10,
            "commit_message_template": "自动提交 {timestamp} - {files_count} 个文件",
            "exclude_patterns": [
                "*.pyc",
                "__pycache__/*",
                ".git/*",
                "*.log",
                ".DS_Store",
                "node_modules/*",
                ".venv/*",
                "venv/*",
                "*.tmp",
                "*.temp",
                ".idea/*",
                ".vscode/*",
                "auto_commit_*",
                "*.swp",
                "*.swo"
            ],
            "include_patterns": [
                "*.py",
                "*.js",
                "*.html",
                "*.css",
                "*.md",
                "*.txt",
                "*.json",
                "*.yml",
                "*.yaml",
                "*.xml",
                "*.sql",
                "*.sh"
            ],
            "enable_branch_check": True,
            "allowed_branches": ["main", "master", "develop"],
            "max_commit_message_length": 100
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        else:
            self.save_config(default_config)
            
        return default_config
    
    def save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  配置文件保存失败: {e}")
    
    def should_include_file(self, file_path):
        """判断文件是否应该被监控"""
        file_path = Path(file_path)
        
        # 检查是否在排除列表中
        for pattern in self.config["exclude_patterns"]:
            if file_path.match(pattern):
                return False
                
        # 如果有包含列表，检查是否匹配
        if self.config["include_patterns"]:
            for pattern in self.config["include_patterns"]:
                if file_path.match(pattern):
                    return True
            return False
            
        return True
    
    def get_git_status(self):
        """获取Git仓库状态"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.config["watch_directory"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return None, f"Git命令执行失败: {result.stderr}"
            
            # 检查当前分支
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.config["watch_directory"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
            
            return {
                "changed_files": [line[3:] for line in result.stdout.strip().split('\n') if line],
                "current_branch": current_branch,
                "has_changes": len(result.stdout.strip()) > 0
            }, None
            
        except Exception as e:
            return None, f"获取Git状态失败: {e}"
    
    def commit_changes(self):
        """提交Git变更"""
        with self.commit_lock:
            try:
                git_status, error = self.get_git_status()
                if error:
                    print(f"❌ {error}")
                    return
                    
                if not git_status["has_changes"]:
                    return
                    
                # 检查分支（如果启用）
                if (self.config["enable_branch_check"] and 
                    git_status["current_branch"] and 
                    git_status["current_branch"] not in self.config["allowed_branches"]):
                    print(f"⚠️  当前分支 '{git_status['current_branch']}' 不在允许列表中，跳过提交")
                    return
                
                # 生成提交信息
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                files_count = len(git_status["changed_files"])
                
                if files_count == 0:
                    return
                    
                commit_message = self.config["commit_message_template"].format(
                    timestamp=timestamp,
                    files_count=files_count,
                    files=", ".join(git_status["changed_files"][:3]) + 
                    ("..." if files_count > 3 else "")
                )
                
                # 截断过长的提交信息
                if len(commit_message) > self.config["max_commit_message_length"]:
                    commit_message = commit_message[:self.config["max_commit_message_length"]] + "..."
                
                print(f"🔄 正在提交 {files_count} 个文件变更...")
                
                # 执行Git命令
                add_result = subprocess.run(
                    ["git", "add", "."],
                    cwd=self.config["watch_directory"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if add_result.returncode != 0:
                    print(f"❌ Git add 失败: {add_result.stderr}")
                    return
                
                commit_result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=self.config["watch_directory"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if commit_result.returncode != 0:
                    print(f"❌ Git commit 失败: {commit_result.stderr}")
                    return
                
                # 尝试推送到远程仓库
                push_result = subprocess.run(
                    ["git", "push"],
                    cwd=self.config["watch_directory"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if push_result.returncode == 0:
                    print(f"✅ 提交成功并推送到远程仓库: {commit_message}")
                else:
                    print(f"⚠️  提交成功但推送失败: {push_result.stderr}")
                    print("   💡 可能需要手动推送或检查网络连接")
                    
            except Exception as e:
                print(f"❌ 提交过程中发生错误: {e}")
    
    def on_any_event(self, event):
        """处理文件变化事件"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # 检查文件是否应该被监控
        if not self.should_include_file(file_path):
            return
            
        print(f"📝 检测到文件变化: {event.event_type} - {file_path}")
        
        # 延迟提交，给用户时间进行多次编辑
        threading.Timer(
            self.config["commit_delay"], 
            self.commit_changes
        ).start()

def start_monitoring():
    """启动文件监控"""
    config_path = "auto_commit_config.json"
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_path):
        print("📋 创建默认配置文件...")
        handler = AutoGitCommitHandler()
        print(f"✅ 配置文件已创建: {config_path}")
        print("📝 请根据需要修改配置文件")
    
    print("🚀 启动文件监控服务...")
    print("💡 提示: 按 Ctrl+C 停止监控")
    
    # 创建监控处理器
    handler = AutoGitCommitHandler(config_path)
    watch_directory = handler.config["watch_directory"]
    
    # 检查目录是否存在
    if not os.path.exists(watch_directory):
        print(f"❌ 监控目录不存在: {watch_directory}")
        return
    
    # 检查是否是Git仓库
    git_status, error = handler.get_git_status()
    if error:
        print(f"❌ {error}")
        print("💡 请确保当前目录是Git仓库")
        return
    
    if not git_status:
        print("❌ 无法获取Git状态")
        return
        
    print(f"📂 监控目录: {os.path.abspath(watch_directory)}")
    print(f"🌿 当前分支: {git_status['current_branch'] or 'unknown'}")
    print(f"⏱️  提交延迟: {handler.config['commit_delay']} 秒")
    
    # 创建观察者
    observer = Observer()
    observer.schedule(handler, watch_directory, recursive=True)
    
    try:
        observer.start()
        print("🔍 文件监控已启动，等待文件变化...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 停止文件监控...")
        observer.stop()
    
    observer.join()
    print("✅ 文件监控已停止")

if __name__ == "__main__":
    start_monitoring()