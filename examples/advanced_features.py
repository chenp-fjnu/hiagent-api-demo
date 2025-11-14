#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级功能示例

展示HiAgent客户端的高级功能，包括流式响应、错误处理、自定义配置等
"""

import json
import time
import threading
from typing import Dict, Any, Iterator
from client import HiAgentClient


class AdvancedHiAgentClient(HiAgentClient):
    """扩展的HiAgent客户端，添加高级功能"""
    
    def send_message_stream(
        self, 
        agent_id: str, 
        message: str, 
        user_id: str = "stream_user"
    ) -> Iterator[str]:
        """
        发送消息并接收流式响应
        
        Args:
            agent_id: 智能体ID
            message: 用户消息
            user_id: 用户ID
            
        Yields:
            流式响应内容
        """
        try:
            data = {
                'agent_id': agent_id,
                'message': message,
                'user_id': user_id,
                'stream': True
            }
            
            # 注意：这里需要HiAgent API实际支持流式响应
            # 如果不支持，可以模拟流式输出
            response = self._make_request('POST', f"/api/v1/agents/{agent_id}/chat", data)
            
            # 如果API支持流式，这里会处理流数据
            # 暂时返回完整响应
            reply = response.get('reply', '')
            if reply:
                # 模拟流式输出
                for chunk in self._stream_response(reply):
                    yield chunk
            
        except Exception as e:
            yield f"错误: {e}"
    
    def _stream_response(self, text: str, chunk_size: int = 3) -> Iterator[str]:
        """将文本分块模拟流式输出"""
        words = text.split()
        current_chunk = ""
        
        for word in words:
            current_chunk += word + " "
            if len(current_chunk.split()) >= chunk_size:
                yield current_chunk
                current_chunk = ""
                time.sleep(0.1)  # 模拟网络延迟
        
        if current_chunk:
            yield current_chunk
    
    def parallel_message_processing(
        self, 
        agent_id: str, 
        messages: list, 
        max_workers: int = 3
    ) -> Dict[str, Any]:
        """
        并行处理多条消息
        
        Args:
            agent_id: 智能体ID
            messages: 消息列表
            max_workers: 最大并发数
            
        Returns:
            处理结果
        """
        import concurrent.futures
        
        results = {}
        
        def process_single_message(message_data):
            try:
                response = self.send_message(
                    agent_id=agent_id,
                    message=message_data['message'],
                    user_id=message_data.get('user_id', 'parallel_user')
                )
                return {
                    'success': True,
                    'reply': response.get('reply', ''),
                    'user_id': message_data.get('user_id', 'unknown')
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'user_id': message_data.get('user_id', 'unknown')
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_message = {
                executor.submit(process_single_message, msg): msg 
                for msg in messages
            }
            
            for future in concurrent.futures.as_completed(future_to_message):
                result = future.result()
                results[result['user_id']] = result
        
        return results
    
    def create_conversation_session(
        self, 
        agent_id: str, 
        user_id: str,
        max_history: int = 10
    ) -> 'ConversationSession':
        """创建对话会话"""
        return ConversationSession(self, agent_id, user_id, max_history)


class ConversationSession:
    """对话会话管理类"""
    
    def __init__(self, client: AdvancedHiAgentClient, agent_id: str, user_id: str, max_history: int = 10):
        self.client = client
        self.agent_id = agent_id
        self.user_id = user_id
        self.max_history = max_history
        self.conversation_history = []
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """发送消息并自动维护历史记录"""
        try:
            # 构建上下文
            context = {
                'conversation_history': self.conversation_history[-self.max_history:],
                'session_id': f"{self.user_id}_{int(time.time())}"
            }
            
            response = self.client.send_message(
                agent_id=self.agent_id,
                message=message,
                user_id=self.user_id,
                context=context
            )
            
            # 更新对话历史
            self.conversation_history.append({
                'user': message,
                'assistant': response.get('reply', ''),
                'timestamp': time.time()
            })
            
            # 保持历史记录在限制范围内
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'reply': f"发送消息失败: {e}"
            }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        if not self.conversation_history:
            return {'summary': '暂无对话记录'}
        
        total_messages = len(self.conversation_history)
        last_message_time = self.conversation_history[-1]['timestamp']
        
        # 简单的对话摘要生成
        topics = []
        for record in self.conversation_history:
            user_msg = record['user'].lower()
            if '天气' in user_msg:
                topics.append('天气查询')
            elif '你好' in user_msg or 'hello' in user_msg:
                topics.append('问候')
            elif '谢谢' in user_msg or '感谢' in user_msg:
                topics.append('感谢')
        
        return {
            'total_messages': total_messages,
            'duration_minutes': (last_message_time - self.conversation_history[0]['timestamp']) / 60,
            'topics': list(set(topics)),
            'conversation_history': self.conversation_history
        }


def streaming_example():
    """流式响应示例"""
    print("=== 流式响应示例 ===\n")
    
    try:
        client = AdvancedHiAgentClient()
        agent_id = client.config.get('agent_settings', {}).get('default_agent_id')
        
        if not agent_id:
            print("❌ 未配置默认智能体ID")
            return
        
        print(f"使用智能体ID: {agent_id}")
        print("发送消息并接收流式响应...\n")
        
        message = "请详细介绍一下人工智能的发展历史"
        print(f"用户: {message}\n")
        print("智能体 (流式输出):")
        
        # 接收流式响应
        for chunk in client.send_message_stream(agent_id, message):
            print(chunk, end='', flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"❌ 流式示例失败: {e}")


def parallel_processing_example():
    """并行处理示例"""
    print("=== 并行处理示例 ===\n")
    
    try:
        client = AdvancedHiAgentClient()
        agent_id = client.config.get('agent_settings', {}).get('default_agent_id')
        
        if not agent_id:
            print("❌ 未配置默认智能体ID")
            return
        
        # 准备测试消息
        test_messages = [
            {'message': '你好', 'user_id': 'user_001'},
            {'message': '今天天气怎么样？', 'user_id': 'user_002'},
            {'message': '什么是机器学习？', 'user_id': 'user_003'},
            {'message': '你能帮我做什么？', 'user_id': 'user_004'},
            {'message': '谢谢你的帮助', 'user_id': 'user_005'},
        ]
        
        print(f"准备并行处理 {len(test_messages)} 条消息...")
        
        start_time = time.time()
        results = client.parallel_message_processing(agent_id, test_messages)
        processing_time = time.time() - start_time
        
        print(f"并行处理完成，耗时: {processing_time:.2f}秒\n")
        
        # 显示结果
        for user_id, result in results.items():
            print(f"{user_id}:")
            if result['success']:
                print(f"  回复: {result['reply'][:100]}{'...' if len(result['reply']) > 100 else ''}")
            else:
                print(f"  错误: {result['error']}")
            print()
        
    except Exception as e:
        print(f"❌ 并行处理示例失败: {e}")


def conversation_session_example():
    """对话会话示例"""
    print("=== 对话会话示例 ===\n")
    
    try:
        client = AdvancedHiAgentClient()
        agent_id = client.config.get('agent_settings', {}).get('default_agent_id')
        
        if not agent_id:
            print("❌ 未配置默认智能体ID")
            return
        
        # 创建对话会话
        session = client.create_conversation_session(
            agent_id=agent_id,
            user_id="session_user",
            max_history=5
        )
        
        # 多轮对话
        conversation_flow = [
            "你好，我是小明",
            "我想了解一下人工智能",
            "你能推荐一些学习资源吗？",
            "谢谢你的建议",
            "再见"
        ]
        
        print("开始多轮对话...")
        print("-" * 50)
        
        for i, message in enumerate(conversation_flow, 1):
            print(f"\n轮次 {i}:")
            print(f"用户: {message}")
            
            response = session.send_message(message)
            if 'success' in response and not response['success']:
                print(f"智能体: {response.get('reply', '处理失败')}")
            else:
                print(f"智能体: {response.get('reply', 'No reply')}")
        
        print("\n" + "-" * 50)
        
        # 获取对话摘要
        summary = session.get_conversation_summary()
        print("\n对话摘要:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 对话会话示例失败: {e}")


def main():
    """主函数"""
    print("=== HiAgent高级功能示例 ===\n")
    
    try:
        # 运行各种示例
        streaming_example()
        parallel_processing_example()
        conversation_session_example()
        
        print("=== 所有高级功能示例完成 ===")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


if __name__ == "__main__":
    main()