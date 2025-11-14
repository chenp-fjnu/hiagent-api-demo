#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例

展示如何基本使用HiAgent客户端
"""

import json
from client import HiAgentClient


def main():
    """基础使用示例"""
    print("=== HiAgent客户端基础使用示例 ===\n")
    
    try:
        # 1. 初始化客户端
        print("1. 初始化客户端...")
        client = HiAgentClient()
        
        # 2. 健康检查
        print("2. 进行健康检查...")
        try:
            health = client.health_check()
            print(f"   ✓ API服务状态: {health.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ⚠ 健康检查失败: {e}")
            print("   ℹ 可能需要配置正确的API密钥")
        
        # 3. 获取智能体列表
        print("3. 获取智能体列表...")
        try:
            agents = client.list_agents()
            if agents.get('data'):
                print(f"   ✓ 发现 {len(agents['data'])} 个智能体:")
                for agent in agents['data'][:3]:  # 只显示前3个
                    print(f"     - {agent.get('name', 'Unknown')}: {agent.get('description', 'No description')}")
            else:
                print("   ℹ 未发现任何智能体")
        except Exception as e:
            print(f"   ⚠ 获取智能体列表失败: {e}")
        
        # 4. 演示发送消息（如果有智能体）
        print("4. 发送测试消息...")
        try:
            # 如果配置了默认智能体ID，使用它
            default_agent_id = client.config.get('agent_settings', {}).get('default_agent_id')
            
            if default_agent_id and default_agent_id.strip():
                response = client.send_message(
                    agent_id=default_agent_id,
                    message="你好，请简单介绍一下你自己",
                    user_id="demo_user"
                )
                print(f"   ✓ 智能体回复: {response.get('reply', 'No reply')}")
            else:
                print("   ℹ 未配置默认智能体ID，跳过消息发送")
                print("   ℹ 请在 config.json 中设置 agent_settings.default_agent_id")
        except Exception as e:
            print(f"   ⚠ 发送消息失败: {e}")
        
        # 5. 获取使用统计
        print("5. 获取使用统计...")
        try:
            stats = client.get_usage_stats()
            print(f"   ✓ 使用统计: {stats}")
        except Exception as e:
            print(f"   ⚠ 获取使用统计失败: {e}")
        
        print("\n=== 示例完成 ===")
        print("\n💡 提示:")
        print("   - 请确保在 config.json 中正确配置 API 密钥")
        print("   - 根据实际 HiAgent API 文档调整相关参数")
        print("   - 可以通过 client.send_message() 方法与智能体交互")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n🔧 请检查:")
        print("   1. 是否安装了所需依赖: pip install -r requirements.txt")
        print("   2. config.json 文件是否存在且格式正确")
        print("   3. API 密钥是否有效")


if __name__ == "__main__":
    main()