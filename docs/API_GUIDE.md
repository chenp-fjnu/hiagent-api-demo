# HiAgent API 详细使用指南

## 目录
1. [快速开始](#快速开始)
2. [配置说明](#配置说明)
3. [API客户端使用](#api客户端使用)
4. [Web界面使用](#web界面使用)
5. [示例代码](#示例代码)
6. [错误处理](#错误处理)
7. [最佳实践](#最佳实践)
8. [故障排除](#故障排除)

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，填入您的API信息
# HIAGENT_API_BASE_URL=https://api.hiagent.com/v1
# HIAGENT_API_KEY=your_actual_api_key
# HIAGENT_AGENT_ID=your_agent_id
```

### 3. 启动演示服务
```bash
python start_demo.py start
# 或指定端口
python start_demo.py start --port 8080
```

### 4. 访问Web界面
打开浏览器访问：`http://localhost:5000`

## 配置说明

### 环境变量配置 (.env文件)

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|----------|
| `HIAGENT_API_BASE_URL` | HiAgent API基础URL | - | ✅ 必需 |
| `HIAGENT_API_KEY` | API密钥 | - | ✅ 必需 |
| `HIAGENT_AGENT_ID` | 智能体ID | - | ✅ 必需 |
| `HIAGENT_USER_ID` | 用户ID | `demo_user` | ❌ 可选 |
| `HIAGENT_TIMEOUT` | 请求超时时间(秒) | `30` | ❌ 可选 |
| `HIAGENT_MAX_RETRIES` | 最大重试次数 | `3` | ❌ 可选 |
| `HIAGENT_STREAMING_MODE` | 是否启用流式响应 | `false` | ❌ 可选 |
| `HIAGENT_MAX_TOKENS` | 最大token数 | `2000` | ❌ 可选 |
| `HIAGENT_TEMPERATURE` | 温度参数 | `0.7` | ❌ 可选 |

### config.json 配置

```json
{
  "api": {
    "base_url": "https://api.hiagent.com/v1",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "auth": {
    "api_key": "",
    "auth_method": "bearer"
  },
  "logging": {
    "level": "INFO"
  },
  "agent": {
    "default_agent_id": "",
    "streaming": false,
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

## API客户端使用

### 基础用法

```python
from client import HiAgentClient

# 初始化客户端
client = HiAgentClient(config_file='config.json')

# 发送消息
response = client.send_message(
    message="你好，请介绍一下自己",
    agent_id="your_agent_id",
    user_id="user123"
)

if response.success:
    print("AI回复:", response.reply)
else:
    print("错误:", response.error)
```

### 高级功能

```python
from client import HiAgentClient
import asyncio

# 流式响应
async def streaming_demo():
    client = HiAgentClient()
    
    async for chunk in client.send_message_streaming(
        message="请写一首诗",
        agent_id="your_agent_id"
    ):
        if chunk.content:
            print(chunk.content, end='', flush=True)
    
    print()

# 并行消息处理
async def batch_demo():
    client = HiAgentClient()
    
    messages = [
        "消息1",
        "消息2", 
        "消息3"
    ]
    
    results = await client.send_batch_messages(
        messages=messages,
        agent_id="your_agent_id"
    )
    
    for result in results:
        print(f"回复: {result.reply}")

# 运行异步示例
asyncio.run(batch_demo())
```

## Web界面使用

### 主要功能

1. **实时聊天**: 与HiAgent智能体进行对话
2. **配置管理**: 设置API密钥和参数
3. **连接测试**: 验证API连接状态
4. **历史记录**: 聊天历史保存
5. **响应式设计**: 支持移动端访问

### 使用步骤

1. 点击右上角"⚙️ 设置"按钮
2. 填入API配置信息：
   - **API基础URL**: HiAgent API服务器地址
   - **API密钥**: 您的API密钥
   - **智能体ID**: 要对话的智能体ID
   - **用户ID**: 自定义用户标识
3. 点击"测试连接"验证配置
4. 保存配置后开始对话

### 快捷操作

- **发送消息**: Enter键（Shift+Enter换行）
- **清空对话**: "🗑️ 清空"按钮
- **快速示例**: 点击预设消息快速发送

## 示例代码

### 基础示例 (`examples/basic_usage.py`)

```python
#!/usr/bin/env python3
"""
HiAgent API 基础使用示例
演示客户端初始化、健康检查、发送消息等基本功能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))

from client import HiAgentClient

def main():
    print("🚀 HiAgent API 基础使用示例")
    print("=" * 40)
    
    # 初始化客户端
    client = HiAgentClient()
    
    # 1. 健康检查
    print("1️⃣ 执行健康检查...")
    health_status = client.health_check()
    print(f"健康状态: {health_status}")
    
    # 2. 获取智能体列表
    print("\n2️⃣ 获取智能体列表...")
    agents = client.list_agents()
    print(f"找到 {len(agents)} 个智能体")
    
    # 3. 发送测试消息
    print("\n3️⃣ 发送测试消息...")
    test_message = "你好，请介绍一下HiAgent是什么？"
    response = client.send_message(
        message=test_message,
        agent_id="your_agent_id"  # 替换为实际ID
    )
    
    if response.success:
        print(f"✅ 成功: {response.reply}")
    else:
        print(f"❌ 失败: {response.error}")
    
    # 4. 获取使用统计
    print("\n4️⃣ 获取使用统计...")
    stats = client.get_usage_stats("your_agent_id")  # 替换为实际ID
    print(f"使用统计: {stats}")

if __name__ == "__main__":
    main()
```

### 批量处理示例 (`examples/batch_processing.py`)

```python
#!/usr/bin/env python3
"""
批量处理示例
演示如何批量发送消息和处理对话
"""

import asyncio
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client import HiAgentClient, BatchMessageResult

async def batch_process_messages():
    """批量处理消息示例"""
    client = HiAgentClient()
    
    # 待处理的消息列表
    messages = [
        "介绍一下人工智能",
        "Python有哪些优势？",
        "如何学习机器学习？"
    ]
    
    print(f"📤 批量处理 {len(messages)} 条消息...")
    
    start_time = time.time()
    
    # 批量发送消息
    results = await client.send_batch_messages(
        messages=messages,
        agent_id="your_agent_id"
    )
    
    end_time = time.time()
    
    print(f"⏱️ 处理完成，耗时: {end_time - start_time:.2f}秒")
    print("📥 处理结果:")
    
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"\n{i}. ✅ 成功")
            print(f"   消息: {result.message}")
            print(f"   回复: {result.reply}")
        else:
            print(f"\n{i}. ❌ 失败")
            print(f"   消息: {result.message}")
            print(f"   错误: {result.error}")

def multi_turn_conversation():
    """多轮对话示例"""
    client = HiAgentClient()
    
    conversation_history = []
    
    # 模拟多轮对话
    user_messages = [
        "我想学习Python",
        "我已经会基础语法了",
        "那接下来学什么？"
    ]
    
    print("🗣️ 多轮对话示例:")
    
    for i, message in enumerate(user_messages, 1):
        print(f"\n轮次 {i}:")
        print(f"👤 用户: {message}")
        
        # 构建上下文（包含历史对话）
        context = "\n".join(conversation_history)
        if context:
            context += f"\n用户: {message}"
        else:
            context = message
        
        response = client.send_message(
            message=context,
            agent_id="your_agent_id"
        )
        
        if response.success:
            assistant_reply = response.reply
            print(f"🤖 助手: {assistant_reply}")
            
            # 添加到对话历史
            conversation_history.append(f"用户: {message}")
            conversation_history.append(f"助手: {assistant_reply}")
        else:
            print(f"❌ 错误: {response.error}")
            break

if __name__ == "__main__":
    print("🚀 批量处理示例")
    print("=" * 30)
    
    # 运行批量处理
    asyncio.run(batch_process_messages())
    
    print("\n" + "=" * 50)
    
    # 运行多轮对话
    multi_turn_conversation()
```

### 高级功能示例 (`examples/advanced_features.py`)

```python
#!/usr/bin/env python3
"""
高级功能示例
演示流式响应、并行处理、会话管理等高级特性
"""

import asyncio
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.advanced_features import (
    AdvancedHiAgentClient, 
    ConversationSession,
    StreamingCallback,
    BatchProcessor
)

async def streaming_demo():
    """流式响应演示"""
    print("🌊 流式响应演示")
    print("-" * 30)
    
    client = AdvancedHiAgentClient()
    
    # 创建自定义流回调
    class MyStreamCallback(StreamingCallback):
        def __init__(self):
            self.content = ""
        
        def on_chunk(self, chunk):
            if chunk.content:
                print(chunk.content, end='', flush=True)
                self.content += chunk.content
        
        def on_complete(self, final_content):
            print(f"\n✅ 流式响应完成")
        
        def on_error(self, error):
            print(f"\n❌ 流式响应错误: {error}")
    
    callback = MyStreamCallback()
    
    print("发送流式请求...")
    await client.send_message_streaming(
        message="请详细介绍一下Python的数据结构",
        agent_id="your_agent_id",
        callback=callback
    )

def parallel_processing_demo():
    """并行处理演示"""
    print("\n⚡ 并行处理演示")
    print("-" * 30)
    
    client = AdvancedHiAgentClient()
    processor = BatchProcessor(client)
    
    # 创建多个任务
    tasks = []
    for i in range(5):
        task = client.send_message(
            message=f"第{i+1}个问题：请简单介绍一下机器学习",
            agent_id="your_agent_id"
        )
        tasks.append(task)
    
    print(f"🚀 并行处理 {len(tasks)} 个任务...")
    start_time = time.time()
    
    # 并行执行所有任务
    results = processor.execute_batch(tasks)
    
    end_time = time.time()
    print(f"⏱️ 并行处理完成，耗时: {end_time - start_time:.2f}秒")
    
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"{i}. ✅ 成功")
        else:
            print(f"{i}. ❌ 失败: {result.error}")

def conversation_session_demo():
    """会话管理演示"""
    print("\n💬 会话管理演示")
    print("-" * 30)
    
    client = AdvancedHiAgentClient()
    
    # 创建会话
    session = ConversationSession(
        session_id="demo_session_001",
        max_history=10
    )
    
    # 模拟对话流程
    messages = [
        "我想学习机器学习",
        "我是初学者，应该从哪里开始？",
        "推荐一些学习资源",
        "Python和R哪个更适合机器学习？"
    ]
    
    for message in messages:
        print(f"👤 用户: {message}")
        
        # 添加用户消息到会话
        session.add_message("user", message)
        
        # 获取AI回复
        response = client.send_message(
            message=message,
            agent_id="your_agent_id",
            context=session.get_context()
        )
        
        if response.success:
            assistant_reply = response.reply
            print(f"🤖 助手: {assistant_reply}")
            
            # 添加助手回复到会话
            session.add_message("assistant", assistant_reply)
        else:
            print(f"❌ 错误: {response.error}")
            break
    
    # 显示会话摘要
    summary = session.get_summary()
    print(f"\n📝 会话摘要: {summary}")
    
    # 显示历史记录
    history = session.get_history()
    print(f"\n📚 对话历史 ({len(history)}条记录):")
    for msg in history[-3:]:  # 显示最近3条
        print(f"  {msg['role']}: {msg['content'][:50]}...")

if __name__ == "__main__":
    print("🚀 高级功能演示")
    print("=" * 40)
    
    # 流式响应演示
    asyncio.run(streaming_demo())
    
    print("\n" + "=" * 50)
    
    # 并行处理演示
    parallel_processing_demo()
    
    print("\n" + "=" * 50)
    
    # 会话管理演示
    conversation_session_demo()
```

## 错误处理

### 常见错误类型

1. **认证错误** (401/403)
   - 检查API密钥是否正确
   - 确认权限是否足够

2. **网络错误** (连接超时/网络不可达)
   - 检查网络连接
   - 验证API基础URL是否正确
   - 尝试增加超时时间

3. **请求格式错误** (400)
   - 检查请求参数格式
   - 确认必需参数是否完整

4. **服务器错误** (500/503)
   - 检查API服务状态
   - 稍后重试

### 错误处理最佳实践

```python
from client import HiAgentClient
from client.exceptions import (
    AuthenticationError, 
    RateLimitError, 
    NetworkError,
    APIError
)

def robust_api_call():
    client = HiAgentClient()
    
    try:
        response = client.send_message(
            message="你好",
            agent_id="your_agent_id"
        )
        
        if not response.success:
            # 根据错误类型采取不同处理策略
            if isinstance(response.error, AuthenticationError):
                print("认证失败，请检查API密钥")
                # 可以尝试刷新token
            elif isinstance(response.error, RateLimitError):
                print("请求频率过高，稍后重试")
                # 等待后重试
            elif isinstance(response.error, NetworkError):
                print("网络错误，检查网络连接")
                # 重试或切换网络
            else:
                print(f"API错误: {response.error}")
        
    except Exception as e:
        print(f"未知错误: {e}")
        # 记录日志或发送告警

# 带重试机制的调用
def retry_api_call(max_retries=3, delay=1.0):
    for attempt in range(max_retries):
        try:
            return robust_api_call()
        except (NetworkError, RateLimitError) as e:
            if attempt < max_retries - 1:
                print(f"重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay * (2 ** attempt))  # 指数退避
            else:
                print("重试次数用尽，放弃请求")
                raise
```

## 最佳实践

### 1. 配置管理
- 使用环境变量存储敏感信息
- 不同环境使用不同的配置文件
- 定期轮换API密钥

### 2. 性能优化
- 启用连接池复用
- 合理设置超时时间
- 使用流式响应处理长文本

### 3. 错误处理
- 实施重试机制
- 记录详细错误日志
- 优雅降级处理

### 4. 安全考虑
- 不在前端代码中暴露API密钥
- 使用HTTPS进行通信
- 验证所有输入参数

### 5. 监控和告警
- 监控API调用成功率
- 跟踪响应时间
- 设置异常告警

## 故障排除

### 常见问题解决

#### Q1: 提示"未配置API密钥"
**解决方案:**
1. 检查`.env`文件是否存在
2. 确认环境变量是否正确设置
3. 重新启动应用使配置生效

#### Q2: 网络连接失败
**解决方案:**
1. 验证API基础URL是否正确
2. 检查防火墙设置
3. 尝试使用代理
4. 增加超时时间

#### Q3: 认证失败
**解决方案:**
1. 确认API密钥是否有效
2. 检查权限是否足够
3. 验证智能体ID是否正确

#### Q4: Web界面无法加载
**解决方案:**
1. 确认Flask服务是否正常运行
2. 检查端口是否被占用
3. 清除浏览器缓存
4. 检查静态文件路径

#### Q5: 流式响应不工作
**解决方案:**
1. 确认浏览器支持Server-Sent Events
2. 检查代理设置
3. 验证API服务器是否支持流式响应

### 调试技巧

1. **启用调试模式**
```bash
export DEBUG_MODE=true
python start_demo.py start --debug
```

2. **查看详细日志**
```bash
export LOG_LEVEL=DEBUG
python start_demo.py start
```

3. **测试API连接**
```python
# 使用客户端进行连接测试
client = HiAgentClient()
health = client.health_check()
print(health)
```

4. **检查网络请求**
- 打开浏览器开发者工具
- 查看Network标签页的API请求
- 分析请求/响应详情

### 获取帮助

如果遇到问题，请：

1. 查看错误日志和控制台输出
2. 检查配置是否正确
3. 测试API连接
4. 参考官方文档
5. 联系技术支持

---

**注意**: 本文档基于当前版本的HiAgent API编写，如API有更新，请参考最新的官方文档。