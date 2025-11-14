#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Git自动化系统安装和配置脚本
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    
    requirements_file = "requirements_git_automation.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ 依赖文件不存在: {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def setup_github_auth():
    """设置GitHub认证"""
    print("\n🔐 设置GitHub认证...")
    
    auth_method = input("选择认证方式 (1: Personal Access Token, 2: SSH密钥) [默认: 1]: ").strip()
    if not auth_method:
        auth_method = "1"
    
    if auth_method == "1":
        print("\n请输入您的GitHub Personal Access Token:")
        print("获取方法: GitHub Settings > Developer settings > Personal access tokens")
        token = input("Token: ").strip()
        
        if token:
            token_file = ".github_token"
            with open(token_file, 'w') as f:
                f.write(token)
            print(f"✅ Token已保存到: {token_file}")
            print("⚠️  请确保 .github_token 已添加到 .gitignore 中")
        else:
            print("⚠️  未设置Token，将使用环境变量 GITHUB_TOKEN")
    
    elif auth_method == "2":
        ssh_key_path = input("SSH密钥路径 [默认: ~/.ssh/id_rsa]: ").strip()
        if not ssh_key_path:
            ssh_key_path = "~/.ssh/id_rsa"
        
        ssh_key_path = os.path.expanduser(ssh_key_path)
        
        if os.path.exists(ssh_key_path):
            print(f"✅ SSH密钥存在: {ssh_key_path}")
        else:
            print(f"❌ SSH密钥不存在: {ssh_key_path}")
            print("💡 使用以下命令生成SSH密钥:")
            print("   ssh-keygen -t ed25519 -C 'your_email@example.com'")
    
    else:
        print("❌ 无效的认证方式")

def check_git_repository():
    """检查Git仓库状态"""
    print("\n📂 检查Git仓库状态...")
    
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 当前目录是Git仓库")
            
            # 获取当前分支
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            if branch_result.returncode == 0:
                current_branch = branch_result.stdout.strip()
                print(f"🌿 当前分支: {current_branch}")
                
                # 检查是否有远程仓库
                remote_result = subprocess.run(['git', 'remote', '-v'], 
                                             capture_output=True, text=True)
                if remote_result.returncode == 0 and remote_result.stdout.strip():
                    print("✅ 已配置远程仓库")
                    print(f"📡 远程仓库: {remote_result.stdout.split()[1]}")
                else:
                    print("⚠️  未配置远程仓库")
                    repo_url = input("请输入GitHub仓库URL (如: https://github.com/user/repo.git): ").strip()
                    if repo_url:
                        subprocess.run(['git', 'remote', 'add', 'origin', repo_url])
                        print("✅ 远程仓库已添加")
                
            return True
        else:
            print("❌ 当前目录不是Git仓库")
            init_choice = input("是否初始化Git仓库? (y/N): ").strip().lower()
            if init_choice == 'y':
                subprocess.run(['git', 'init'])
                print("✅ Git仓库已初始化")
                return True
            return False
            
    except FileNotFoundError:
        print("❌ 未找到Git，请先安装Git")
        return False

def create_sample_ignore():
    """创建示例忽略文件"""
    print("\n📝 配置文件忽略规则...")
    
    ignore_patterns = [
        "# 增强版Git自动化系统",
        ".github_token",
        "enhanced_git_config.yaml",
        "enhanced_git_automation.log",
        "",
        "# Python",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "env/",
        "venv/",
        ".venv/",
        "pip-log.txt",
        "",
        "# IDE",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "",
        "# System",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Logs",
        "*.log",
        ".cache/",
        "",
        "# Environment",
        ".env",
        ".env.*",
        "config.local.*",
        "",
        "# Database",
        "*.db",
        "*.sqlite",
    ]
    
    # 检查是否已有.gitignore
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
        
        # 只添加新的忽略模式
        new_patterns = []
        for pattern in ignore_patterns:
            if pattern and pattern not in existing_content:
                new_patterns.append(pattern)
        
        if new_patterns:
            with open(gitignore_path, 'a') as f:
                f.write('\n'.join(new_patterns) + '\n')
            print("✅ 已更新 .gitignore 文件")
        else:
            print("✅ .gitignore 文件已包含必要规则")
    else:
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(ignore_patterns) + '\n')
        print("✅ 已创建 .gitignore 文件")

def test_installation():
    """测试安装"""
    print("\n🧪 测试安装...")
    
    try:
        # 测试Python依赖
        import watchdog
        import yaml
        print("✅ Python依赖正常")
        
        # 测试Git命令
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git版本: {result.stdout.strip()}")
        
        # 测试配置文件
        if os.path.exists("enhanced_git_config.yaml"):
            print("✅ 配置文件存在")
        else:
            print("⚠️  配置文件不存在，将自动创建")
        
        print("✅ 安装测试完成")
        return True
        
    except ImportError as e:
        print(f"❌ 依赖包导入失败: {e}")
        return False

def main():
    """主安装流程"""
    print("🚀 增强版Git自动化系统安装向导")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查Git仓库
    if not check_git_repository():
        print("❌ 需要Git仓库才能使用自动化系统")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，程序退出")
        return
    
    # 设置认证
    setup_github_auth()
    
    # 配置忽略文件
    create_sample_ignore()
    
    # 测试安装
    if test_installation():
        print("\n🎉 安装完成！")
        print("\n📖 使用方法:")
        print("1. 启动监控: python enhanced_git_automation.py")
        print("2. 测试认证: python enhanced_git_automation.py --test-auth")
        print("3. 配置文件: enhanced_git_config.yaml")
        print("4. 查看帮助: python enhanced_git_automation.py --help")
    else:
        print("\n❌ 安装测试失败，请检查配置")

if __name__ == "__main__":
    main()