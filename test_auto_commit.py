#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动提交功能测试脚本
用于测试自动Git提交系统的各项功能
"""

import os
import time
import json
import tempfile
import subprocess
from datetime import datetime

def test_file_creation():
    """测试文件创建后的自动提交"""
    print("🧪 测试1: 文件创建自动提交")
    
    # 创建一个测试文件
    test_file = "test_auto_commit_file.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(f"测试文件创建时间: {datetime.now()}")
    
    print(f"✅ 创建测试文件: {test_file}")
    return test_file

def test_file_modification():
    """测试文件修改后的自动提交"""
    print("\n🧪 测试2: 文件修改自动提交")
    
    test_file = "test_auto_commit_file.txt"
    if os.path.exists(test_file):
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(f"\n测试文件修改时间: {datetime.now()}")
        print(f"✅ 修改测试文件: {test_file}")
        return True
    return False

def test_git_status():
    """检查Git状态"""
    print("\n📊 检查Git状态:")
    
    try:
        # 获取变更状态
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"   📝 检测到 {len([c for c in changes if c])} 个变更")
            for change in changes:
                if change:
                    print(f"      {change}")
        else:
            print(f"   ❌ Git状态检查失败: {result.stderr}")
            
        # 获取当前分支
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()
            print(f"   🌿 当前分支: {branch}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ Git状态检查异常: {e}")
        return False

def manual_commit_test():
    """手动提交测试"""
    print("\n🔧 手动提交测试:")
    
    try:
        # 添加文件
        add_result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if add_result.returncode != 0:
            print(f"   ❌ Git add 失败: {add_result.stderr}")
            return False
        
        # 提交
        commit_message = f"测试提交 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if commit_result.returncode == 0:
            print(f"   ✅ 手动提交成功: {commit_message}")
            
            # 尝试推送
            push_result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if push_result.returncode == 0:
                print("   ✅ 推送成功")
            else:
                print(f"   ⚠️  推送失败: {push_result.stderr}")
            
            return True
        else:
            print(f"   ❌ 提交失败: {commit_result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 手动提交异常: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件:")
    
    test_files = ["test_auto_commit_file.txt"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   ✅ 删除文件: {file}")
            except Exception as e:
                print(f"   ⚠️  删除文件失败 {file}: {e}")

def main():
    """主测试流程"""
    print("🚀 开始测试自动Git提交功能")
    print("=" * 50)
    
    # 检查Git状态
    git_ok = test_git_status()
    
    if not git_ok:
        print("\n❌ Git状态异常，跳过其他测试")
        return
    
    # 测试文件创建
    test_file = test_file_creation()
    
    # 等待几秒钟让自动提交系统检测到变化
    print("\n⏳ 等待自动提交系统检测文件变化...")
    time.sleep(10)
    
    # 检查Git状态
    test_git_status()
    
    # 测试文件修改
    if test_file and os.path.exists(test_file):
        test_file_modification()
        
        # 等待检测
        print("\n⏳ 等待自动提交系统检测文件修改...")
        time.sleep(10)
        
        # 检查Git状态
        test_git_status()
    
    # 手动提交测试（如果自动提交没有工作）
    print("\n💡 如果自动提交未生效，尝试手动提交...")
    if manual_commit_test():
        print("\n✅ 手动提交测试成功！")
    
    # 清理测试文件
    cleanup_test_files()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n📝 下一步:")
    print("   1. 启动自动监控: python auto_commit.py")
    print("   2. 编辑任意代码文件")
    print("   3. 观察自动提交过程")
    print("   4. 查看 GitHub 仓库确认推送")

if __name__ == "__main__":
    main()