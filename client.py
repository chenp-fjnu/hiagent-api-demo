#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HiAgent API客户端

这是一个用于调用Hi Agent接口的Python客户端库，提供了简单易用的API封装。
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HiAgentClient:
    """HiAgent API客户端类"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化HiAgent客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.session = self._setup_session()
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件 {config_path} 格式错误")
    
    def _setup_session(self) -> requests.Session:
        """设置HTTP会话"""
        session = requests.Session()
        
        # 重试策略
        retry_strategy = Retry(
            total=self.config.get('max_retries', 3),
            backoff_factor=self.config.get('retry_delay', 1.0),
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('HiAgentClient')
        logger.setLevel(getattr(logging, self.config.get('logging_level', 'INFO')))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发起HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            API响应数据
        """
        url = urljoin(self.config['api_base_url'], endpoint)
        
        # 设置默认请求头
        default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'HiAgent-Python-Client/1.0'
        }
        
        # 添加API密钥到请求头
        api_key = self.config.get('api_key')
        if api_key and api_key != "your_api_key_here":
            default_headers['Authorization'] = f"Bearer {api_key}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            self.logger.debug(f"发起请求: {method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                timeout=self.config.get('timeout', 30),
                **kwargs
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            raise
        except json.JSONDecodeError:
            self.logger.error("响应解析失败")
            raise ValueError("无法解析API响应")
    
    def send_message(
        self, 
        agent_id: str, 
        message: str, 
        user_id: Optional[str] = None,
        context: Optional[Dict] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        发送消息给指定的智能体
        
        Args:
            agent_id: 智能体ID
            message: 用户消息
            user_id: 用户ID（可选）
            context: 上下文信息（可选）
            stream: 是否使用流式响应
            
        Returns:
            智能体回复
        """
        data = {
            'agent_id': agent_id,
            'message': message,
            'timestamp': int(time.time())
        }
        
        if user_id:
            data['user_id'] = user_id
            
        if context:
            data['context'] = context
        
        if stream:
            data['stream'] = True
            
        endpoint = f"/api/v1/agents/{agent_id}/chat"
        return self._make_request('POST', endpoint, data)
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            智能体信息
        """
        endpoint = f"/api/v1/agents/{agent_id}"
        return self._make_request('GET', endpoint)
    
    def list_agents(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取智能体列表
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            智能体列表
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', '/api/v1/agents', data=params)
    
    def create_agent(
        self, 
        name: str, 
        description: str, 
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        创建新智能体
        
        Args:
            name: 智能体名称
            description: 智能体描述
            config: 配置信息
            
        Returns:
            创建的智能体信息
        """
        data = {
            'name': name,
            'description': description
        }
        
        if config:
            data['config'] = config
            
        return self._make_request('POST', '/api/v1/agents', data)
    
    def batch_process_messages(
        self, 
        messages: List[Dict[str, Any]], 
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量处理消息
        
        Args:
            messages: 消息列表
            agent_id: 智能体ID（如果未在消息中指定）
            
        Returns:
            批量处理结果
        """
        data = {
            'batch_messages': messages
        }
        
        if agent_id:
            data['default_agent_id'] = agent_id
            
        return self._make_request('POST', '/api/v1/batch/chat', data)
    
    def get_usage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取使用统计信息
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            使用统计信息
        """
        params = {}
        if user_id:
            params['user_id'] = user_id
            
        return self._make_request('GET', '/api/v1/usage', data=params)
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            API服务状态
        """
        return self._make_request('GET', '/api/v1/health')


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化客户端
        client = HiAgentClient()
        
        # 健康检查
        health = client.health_check()
        print(f"API状态: {health}")
        
        # 获取智能体列表
        agents = client.list_agents()
        print(f"可用智能体: {agents}")
        
        # 如果有智能体ID，发送测试消息
        if agents.get('data') and len(agents['data']) > 0:
            agent_id = agents['data'][0]['id']
            response = client.send_message(
                agent_id=agent_id,
                message="你好，这是一个测试消息",
                user_id="demo_user"
            )
            print(f"智能体回复: {response}")
        
    except Exception as e:
        print(f"错误: {e}")