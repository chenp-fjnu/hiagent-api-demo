#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理示例

展示如何批量处理消息
"""

import time
from typing import List, Dict, Any
from client import HiAgentClient


def create_sample_messages() -> List[Dict[str, Any]]:
    """创建示例消息数据"""
    return [
        {
            'user_id': 'user_001',
            'message': '你好，请介绍一下你自己',
            'timestamp': int(time.time())
        },
        {
            'user_id': 'user_002', 
            'message': '你能帮我做什么？',
            'timestamp': int(time.time()) + 1
        },
        {
            'user_id': 'user_003',
            'message': '请解释一下人工智能的概念',
            'timestamp': int(time.time()) + 2
        },
        {
            'user_id': 'user_004',
            'message': '今天天气怎么样？',
            'timestamp': int(time.time()) + 3
        },
        {
            'user_id': 'user_005',
            'message': '谢谢你的帮助',
            'timestamp': int(time.time()) + 4
        }
    ]


def batch_process_example(client: HiAgentClient, agent_id: str):
    """批量处理示例"""
    print("=== 批量处理消息示例 ===\n")
    
    try:
        # 创建示例消息
        messages = create_sample_messages()
        
        print(f"1. 准备批量处理 {len(messages)} 条消息...")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. {msg['user_id']}: {msg['message'][:30]}{'...' if len(msg['message']) > 30 else ''}")
        
        # 批量处理
        print(f"\n2. 开始批量处理...")
        start_time = time.time()
        
        try:
            results = client.batch_process_messages(
                messages=messages,
                agent_id=agent_id
            )
            
            processing_time = time.time() - start_time
            print(f"   ✓ 批量处理完成，耗时: {processing_time:.2f}秒")
            
            # 显示结果
            if results.get('data'):
                print(f"\n3. 处理结果:")
                for i, result in enumerate(results['data'], 1):
                    user_id = result.get('user_id', 'unknown')
                    reply = result.get('reply', 'No reply')
                    print(f"   {i}. {user_id}: {reply[:100]}{'...' if len(reply) > 100 else ''}")
            else:
                print("   ℹ 未返回处理结果")
                
        except Exception as e:
            print(f"   ⚠ 批量处理失败: {e}")
            print("   ℹ 尝试单独处理消息...")
            
            # 单独处理每条消息作为备选方案
            individual_results = []
            for msg in messages:
                try:
                    response = client.send_message(
                        agent_id=agent_id,
                        message=msg['message'],
                        user_id=msg['user_id']
                    )
                    individual_results.append({
                        'user_id': msg['user_id'],
                        'reply': response.get('reply', 'No reply')
                    })
                except Exception as msg_e:
                    print(f"   ⚠ 处理消息失败 ({msg['user_id']}): {msg_e}")
                    individual_results.append({
                        'user_id': msg['user_id'],
                        'reply': f'处理失败: {msg_e}'
                    })
            
            if individual_results:
                print(f"\n4. 单独处理结果:")
                for i, result in enumerate(individual_results, 1):
                    print(f"   {i}. {result['user_id']}: {result['reply'][:100]}{'...' if len(result['reply']) > 100 else ''}")
    
    except Exception as e:
        print(f"❌ 批量处理示例失败: {e}")


def conversation_context_example(client: HiAgentClient, agent_id: str):
    """对话上下文示例"""
    print("\n=== 对话上下文示例 ===\n")
    
    conversation_history = []
    
    # 模拟多轮对话
    messages = [
        "你好",
        "我叫张三",
        "我来自北京",
        "你知道我是谁吗？"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"{i}. 用户: {message}")
        
        try:
            # 构建上下文
            context = {
                'conversation_history': conversation_history,
                'user_profile': {
                    'name': '张三',
                    'location': '北京'
                }
            }
            
            response = client.send_message(
                agent_id=agent_id,
                message=message,
                user_id="demo_user",
                context=context
            )
            
            reply = response.get('reply', 'No reply')
            print(f"   智能体: {reply}")
            
            # 更新对话历史
            conversation_history.append({
                'user': message,
                'assistant': reply
            })
            
        except Exception as e:
            print(f"   错误: {e}")
        
        print()  # 空行分隔


def main():
    """主函数"""
    print("=== HiAgent批量处理示例 ===\n")
    
    try:
        # 初始化客户端
        client = HiAgentClient()
        
        # 获取智能体ID
        agent_id = client.config.get('agent_settings', {}).get('default_agent_id')
        
        if not agent_id or not agent_id.strip():
            print("❌ 未配置默认智能体ID")
            print("请在 config.json 中设置 agent_settings.default_agent_id")
            return
        
        print(f"使用智能体ID: {agent_id}\n")
        
        # 运行批量处理示例
        batch_process_example(client, agent_id)
        
        # 运行上下文对话示例
        conversation_context_example(client, agent_id)
        
        print("=== 所有示例完成 ===")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n🔧 请检查:")
        print("   1. 是否安装了所需依赖")
        print("   2. config.json 配置是否正确")
        print("   3. API 密钥是否有效")


if __name__ == "__main__":
    main()