#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版自动化Git工作流程系统
功能包括：智能文件监控、智能提交消息、安全认证、错误处理、冲突预防
"""

import os
import sys
import json
import time
import subprocess
import threading
import hashlib
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml

class GitHubAuthManager:
    """GitHub认证管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.auth_method = config.get('auth_method', 'token')  # 'token' or 'ssh'
        self.token_file = config.get('token_file', '.github_token')
        self.ssh_key_path = config.get('ssh_key_path', os.path.expanduser('~/.ssh/id_rsa'))
        
    def get_auth_config(self) -> Tuple[Dict[str, str], bool]:
        """获取认证配置和状态"""
        auth_config = {}
        auth_success = False
        
        if self.auth_method == 'token':
            # 尝试从文件读取token
            if os.path.exists(self.token_file):
                try:
                    with open(self.token_file, 'r') as f:
                        token = f.read().strip()
                    auth_config['GIT_TERMINAL_PROMPT'] = '0'
                    auth_config['GIT_ASKPASS'] = 'echo'
                    os.environ['GIT_TERMINAL_PROMPT'] = '0'
                    subprocess.run(['echo', token], check=True)
                    auth_success = True
                except Exception:
                    pass
            
            # 如果没有token文件，尝试环境变量
            if not auth_success:
                token = os.getenv('GITHUB_TOKEN') or os.getenv('GIT_PASSWORD')
                if token:
                    auth_config['GIT_TERMINAL_PROMPT'] = '0'
                    auth_config['GIT_ASKPASS'] = 'echo'
                    auth_success = True
                    
        elif self.auth_method == 'ssh':
            # 检查SSH密钥
            if os.path.exists(self.ssh_key_path):
                ssh_key = os.path.expanduser(self.ssh_key_path)
                auth_config['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key} -o StrictHostKeyChecking=no'
                auth_success = True
        
        return auth_config, auth_success
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试GitHub连接"""
        try:
            auth_config, _ = self.get_auth_config()
            
            env = os.environ.copy()
            env.update(auth_config)
            
            result = subprocess.run(
                ['git', 'ls-remote', '--heads', 'origin'],
                capture_output=True,
                text=True,
                env=env,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "连接成功"
            else:
                return False, f"连接失败: {result.stderr}"
                
        except Exception as e:
            return False, f"连接测试异常: {e}"

class IntelligentCommitGenerator:
    """智能提交消息生成器"""
    
    def __init__(self, config: dict):
        self.config = config
        
    def generate_commit_message(self, 
                              change_type: str, 
                              files: List[str], 
                              branch: str = None,
                              context: Dict = None) -> str:
        """生成智能提交消息"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files_count = len(files)
        
        # 根据变更类型生成前缀
        type_prefixes = {
            'added': '✨ 新增',
            'modified': '📝 修改', 
            'deleted': '🗑️ 删除',
            'renamed': '📦 重命名',
            'mixed': '🔄 混合变更'
        }
        
        prefix = type_prefixes.get(change_type, '🔄 变更')
        
        # 文件类型分类
        file_categories = self._categorize_files(files)
        
        # 生成描述部分
        if files_count == 1:
            file_desc = f"1 个文件"
        else:
            file_desc = f"{files_count} 个文件"
            
        category_desc = ""
        if file_categories:
            main_category = max(file_categories.keys(), key=lambda k: file_categories[k])
            category_names = {
                'code': '代码',
                'config': '配置', 
                'docs': '文档',
                'style': '样式',
                'test': '测试',
                'other': '其他'
            }
            category_desc = f" [{category_names.get(main_category, '文件')}]"
        
        # 生成消息
        message_parts = [prefix, file_desc + category_desc]
        
        # 如果文件少，显示主要文件
        if files_count <= 3:
            message_parts.append(f": {', '.join(files)}")
        elif files_count == 4:
            message_parts.append(f": {', '.join(files)}")
        else:
            message_parts.append(f": {', '.join(files[:3])} 等")
        
        # 添加时间戳（可选）
        if self.config.get('include_timestamp', True):
            message_parts.append(f" [{timestamp}]")
        
        commit_message = ''.join(message_parts)
        
        # 限制消息长度
        max_length = self.config.get('max_message_length', 100)
        if len(commit_message) > max_length:
            commit_message = commit_message[:max_length-3] + "..."
            
        return commit_message
    
    def _categorize_files(self, files: List[str]) -> Dict[str, int]:
        """对文件进行分类统计"""
        categories = {
            'code': 0,      # .py, .js, .html, .css
            'config': 0,    # .json, .yml, .yaml, .toml
            'docs': 0,      # .md, .txt, .rst
            'style': 0,     # .css, .scss, .less
            'test': 0,      # test_*.py, *_test.py
            'other': 0
        }
        
        for file_path in files:
            file_lower = file_path.lower()
            file_name = Path(file_path).name.lower()
            
            # 代码文件
            if any(file_lower.endswith(ext) for ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.cpp', '.c', '.h']):
                categories['code'] += 1
            # 配置文件
            elif any(file_lower.endswith(ext) for ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.cfg']):
                categories['config'] += 1
            # 文档文件
            elif any(file_lower.endswith(ext) for ext in ['.md', '.txt', '.rst', '.doc', '.docx']):
                categories['docs'] += 1
            # 样式文件
            elif any(file_lower.endswith(ext) for ext in ['.css', '.scss', '.less', '.sass']):
                categories['style'] += 1
            # 测试文件
            elif file_name.startswith('test_') or file_name.endswith('_test.py') or 'test' in file_lower:
                categories['test'] += 1
            else:
                categories['other'] += 1
        
        return {k: v for k, v in categories.items() if v > 0}

class MergeConflictPrevention:
    """合并冲突预防机制"""
    
    def __init__(self, config: dict):
        self.config = config
        self.max_retry_attempts = config.get('max_retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 2)  # 秒
        
    def check_for_conflicts(self, target_branch: str = None) -> Tuple[bool, str]:
        """检查是否存在潜在的合并冲突"""
        try:
            # 获取远程最新状态
            fetch_result = subprocess.run(
                ['git', 'fetch', 'origin'],
                capture_output=True,
                text=True
            )
            
            if fetch_result.returncode != 0:
                return False, f"获取远程状态失败: {fetch_result.stderr}"
            
            # 检查本地分支是否落后
            current_branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            if target_branch is None:
                target_branch = current_branch
            
            # 检查是否有未推送的提交
            unpushed_result = subprocess.run(
                ['git', 'log', '--oneline', 'origin/HEAD..HEAD'],
                capture_output=True,
                text=True
            )
            
            if unpushed_result.returncode == 0 and unpushed_result.stdout.strip():
                return True, f"本地分支 {current_branch} 有未推送的提交"
            
            # 检查是否需要合并远程更新
            merge_base_result = subprocess.run(
                ['git', 'merge-base', 'HEAD', f'origin/{target_branch}'],
                capture_output=True,
                text=True
            )
            
            if merge_base_result.returncode != 0:
                return False, f"无法确定合并基础: {merge_base_result.stderr}"
            
            common_ancestor = merge_base_result.stdout.strip()
            
            # 检查HEAD是否是common_ancestor的后代
            check_result = subprocess.run(
                ['git', 'merge-tree', '--no-autostash', common_ancestor, 'HEAD', f'origin/{target_branch}'],
                capture_output=True,
                text=True
            )
            
            if check_result.returncode == 0:
                # 检查是否包含冲突标记
                if '=======' in check_result.stdout or '<<<<<<<' in check_result.stdout:
                    return True, f"检测到潜在冲突：{target_branch}"
                else:
                    return False, "无冲突"
            else:
                return False, "无法检查冲突状态"
                
        except Exception as e:
            return False, f"冲突检查异常: {e}"
    
    def handle_conflicts(self, max_retries: int = None) -> Tuple[bool, str]:
        """处理合并冲突"""
        max_retries = max_retries or self.max_retry_attempts
        
        for attempt in range(max_retries):
            try:
                # 先检查冲突
                has_conflicts, reason = self.check_for_conflicts()
                if not has_conflicts:
                    return True, "无冲突，准备提交"
                
                # 尝试自动合并
                pull_result = subprocess.run(
                    ['git', 'pull', '--no-edit'],
                    capture_output=True,
                    text=True
                )
                
                if pull_result.returncode == 0:
                    return True, "自动合并成功"
                else:
                    # 检查是否是合并冲突
                    if 'CONFLICT' in pull_result.stdout.upper():
                        # 尝试自动解决冲突
                        resolve_result = subprocess.run(
                            ['git', 'add', '.'],
                            capture_output=True,
                            text=True
                        )
                        
                        if resolve_result.returncode == 0:
                            # 创建合并提交
                            merge_commit_result = subprocess.run(
                                ['git', 'commit', '--no-edit'],
                                capture_output=True,
                                text=True
                            )
                            
                            if merge_commit_result.returncode == 0:
                                return True, "自动解决合并冲突"
                    
                    # 如果自动解决失败，等待后重试
                    if attempt < max_retries - 1:
                        print(f"⚠️  冲突处理失败，等待 {self.retry_delay} 秒后重试... ({attempt + 1}/{max_retries})")
                        time.sleep(self.retry_delay)
                    else:
                        return False, f"冲突处理失败，请手动解决: {pull_result.stderr}"
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False, f"冲突处理异常: {e}"
        
        return False, "达到最大重试次数"

class EnhancedGitAutomation:
    """增强版Git自动化系统"""
    
    def __init__(self, config_path: str = "enhanced_git_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.auth_manager = GitHubAuthManager(self.config.get('github_auth', {}))
        self.commit_generator = IntelligentCommitGenerator(self.config.get('commit_generation', {}))
        self.conflict_prevention = MergeConflictPrevention(self.config.get('conflict_handling', {}))
        
        self.pending_changes = []
        self.change_lock = threading.Lock()
        self.last_commit_time = 0
        self.processing_changes = False
        
    def load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            'monitoring': {
                'watch_directory': '.',
                'recursive': True,
                'file_types': ['*'],
                'ignore_patterns': [
                    '*.pyc', '__pycache__/*', '.git/*', '*.log', '.DS_Store',
                    'node_modules/*', '.venv/*', 'venv/*', '*.tmp', '*.temp',
                    '.idea/*', '.vscode/*', 'enhanced_git_*', '*.swp', '*.swo',
                    '.env', '.env.*', 'config.local.*', '*.db', '*.sqlite'
                ],
                'min_file_age': 1,  # 秒
                'batch_size': 10
            },
            'commit_generation': {
                'enabled': True,
                'auto_generate': True,
                'include_timestamp': True,
                'max_message_length': 100,
                'group_similar_changes': True
            },
            'github_auth': {
                'auth_method': 'token',
                'token_file': '.github_token',
                'ssh_key_path': '~/.ssh/id_rsa'
            },
            'conflict_handling': {
                'enabled': True,
                'max_retry_attempts': 3,
                'retry_delay': 2,
                'auto_resolve': True
            },
            'scheduling': {
                'commit_delay': 5,  # 秒
                'max_commits_per_hour': 60,
                'enable_rate_limiting': True
            },
            'target_branch': 'main',
            'auto_push': True,
            'debug': False
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        else:
            # 创建默认配置文件
            self.save_config(default_config)
            
        return default_config
    
    def save_config(self, config: dict):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config, f, indent=2, allow_unicode=True)
                else:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置文件已保存: {self.config_path}")
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
    
    def test_github_connection(self) -> bool:
        """测试GitHub连接"""
        print("🔐 测试GitHub连接...")
        success, message = self.auth_manager.test_connection()
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            print("💡 请检查以下配置:")
            print("   - GitHub Personal Access Token")
            print("   - SSH密钥配置")
            print("   - 网络连接")
            return False
    
    def get_git_status(self) -> Tuple[Optional[dict], Optional[str]]:
        """获取详细Git状态"""
        try:
            # 检查是否在Git仓库中
            repo_result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True
            )
            
            if repo_result.returncode != 0:
                return None, "当前目录不是Git仓库"
            
            # 获取当前分支
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True
            )
            
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
            
            # 获取变更文件
            status_result = subprocess.run(
                ['git', 'status', '--porcelain=v1'],
                capture_output=True,
                text=True
            )
            
            if status_result.returncode != 0:
                return None, f"获取Git状态失败: {status_result.stderr}"
            
            # 解析变更文件
            changes = []
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    change_type = 'modified'
                    if status_code[0] == 'A' or status_code == '??':
                        change_type = 'added'
                    elif status_code[0] == 'D':
                        change_type = 'deleted'
                    elif status_code[0] == 'R':
                        change_type = 'renamed'
                    elif status_code[0] == 'C':
                        change_type = 'copied'
                    
                    changes.append({
                        'file': file_path,
                        'type': change_type,
                        'status_code': status_code
                    })
            
            git_info = {
                'current_branch': current_branch,
                'changes': changes,
                'has_changes': len(changes) > 0,
                'total_changes': len(changes)
            }
            
            return git_info, None
            
        except Exception as e:
            return None, f"获取Git状态异常: {e}"
    
    def should_process_file(self, file_path: str) -> bool:
        """判断是否应该处理该文件"""
        file_path = Path(file_path)
        
        # 检查文件年龄
        try:
            if file_path.exists():
                file_age = time.time() - file_path.stat().st_mtime
                if file_age < self.config['monitoring']['min_file_age']:
                    return False
        except:
            pass
        
        # 检查忽略模式
        for pattern in self.config['monitoring']['ignore_patterns']:
            if file_path.match(pattern):
                return False
        
        return True
    
    def process_changes(self) -> bool:
        """处理待处理的变更"""
        with self.change_lock:
            if self.processing_changes or not self.pending_changes:
                return False
            
            self.processing_changes = True
            
        try:
            # 获取当前Git状态
            git_status, error = self.get_git_status()
            if error:
                print(f"❌ {error}")
                return False
            
            if not git_status['has_changes']:
                self.pending_changes.clear()
                return False
            
            # 分析变更类型
            change_types = set(change['type'] for change in git_status['changes'])
            
            if len(change_types) == 1:
                primary_change_type = list(change_types)[0]
            else:
                primary_change_type = 'mixed'
            
            # 生成提交消息
            files = [change['file'] for change in git_status['changes']]
            commit_message = self.commit_generator.generate_commit_message(
                change_type=primary_change_type,
                files=files,
                branch=git_status['current_branch']
            )
            
            print(f"🔄 准备提交: {commit_message}")
            
            # 检查合并冲突
            if self.config['conflict_handling']['enabled']:
                success, message = self.conflict_prevention.check_for_conflicts()
                if not success:
                    print(f"⚠️  {message}")
                    return False
            
            # 执行Git操作
            auth_config, auth_success = self.auth_manager.get_auth_config()
            env = os.environ.copy()
            env.update(auth_config)
            
            # Git add
            add_result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                env=env
            )
            
            if add_result.returncode != 0:
                print(f"❌ Git add 失败: {add_result.stderr}")
                return False
            
            # Git commit
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                env=env
            )
            
            if commit_result.returncode != 0:
                print(f"❌ Git commit 失败: {commit_result.stderr}")
                return False
            
            print(f"✅ 提交成功: {commit_message}")
            
            # 自动推送（如果配置启用）
            if self.config['auto_push']:
                push_result = subprocess.run(
                    ['git', 'push', 'origin', git_status['current_branch']],
                    capture_output=True,
                    text=True,
                    env=env
                )
                
                if push_result.returncode == 0:
                    print(f"🚀 推送到远程仓库成功")
                else:
                    print(f"⚠️  推送失败: {push_result.stderr}")
            
            self.pending_changes.clear()
            self.last_commit_time = time.time()
            return True
            
        except Exception as e:
            print(f"❌ 处理变更时发生错误: {e}")
            return False
        finally:
            self.processing_changes = False
    
    def start_monitoring(self):
        """启动文件监控"""
        print("🚀 启动增强版Git自动化系统...")
        
        # 检查GitHub连接
        if not self.test_github_connection():
            print("❌ GitHub连接失败，程序退出")
            return
        
        # 检查Git仓库
        git_status, error = self.get_git_status()
        if error:
            print(f"❌ {error}")
            return
        
        print(f"📂 监控目录: {os.path.abspath(self.config['monitoring']['watch_directory'])}")
        print(f"🌿 当前分支: {git_status['current_branch']}")
        print(f"🎯 目标分支: {self.config['target_branch']}")
        print(f"⏱️  提交延迟: {self.config['scheduling']['commit_delay']} 秒")
        
        # 创建文件监控处理器
        class GitAutomationHandler(FileSystemEventHandler):
            def __init__(self, automation_system):
                self.automation_system = automation_system
                
            def on_any_event(self, event):
                if event.is_directory:
                    return
                
                file_path = event.src_path
                
                if not self.automation_system.should_process_file(file_path):
                    return
                
                print(f"📝 检测到文件变化: {event.event_type} - {file_path}")
                
                # 添加到待处理队列
                with self.automation_system.change_lock:
                    self.automation_system.pending_changes.append({
                        'event_type': event.event_type,
                        'file_path': file_path,
                        'timestamp': time.time()
                    })
                
                # 延迟处理
                threading.Timer(
                    self.automation_system.config['scheduling']['commit_delay'],
                    self.automation_system.process_changes
                ).start()
        
        # 启动监控
        handler = GitAutomationHandler(self)
        observer = Observer()
        observer.schedule(
            handler, 
            self.config['monitoring']['watch_directory'],
            recursive=self.config['monitoring']['recursive']
        )
        
        try:
            observer.start()
            print("🔍 文件监控已启动，等待文件变化...")
            print("💡 按 Ctrl+C 停止监控")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 停止文件监控...")
            observer.stop()
        
        observer.join()
        print("✅ 文件监控已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版Git自动化系统")
    parser.add_argument('--config', default='enhanced_git_config.yaml', help='配置文件路径')
    parser.add_argument('--test-auth', action='store_true', help='测试GitHub认证')
    parser.add_argument('--init-config', action='store_true', help='初始化配置文件')
    
    args = parser.parse_args()
    
    # 创建系统实例
    git_automation = EnhancedGitAutomation(args.config)
    
    if args.init_config:
        print(f"📋 配置文件已创建: {args.config}")
        print("🔧 请根据需要修改配置")
        return
    
    if args.test_auth:
        git_automation.test_github_connection()
        return
    
    # 启动监控
    git_automation.start_monitoring()

if __name__ == "__main__":
    main()