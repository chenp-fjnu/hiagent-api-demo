# Hi Agent API Demo 项目

这是一个演示如何调用Hi Agent接口的demo项目，包含Python API客户端和一个简单的Web界面。

## 功能特性

- 🔌 Hi Agent API客户端封装
- 🌐 简单的Web界面用于测试
- 📝 多种调用示例
- ⚙️ 灵活的配置系统

## 项目结构

```
hi_agent_demo/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖包
├── config.json              # 配置文件
├── client.py                # HiAgent API客户端
├── examples/                # 示例代码目录
│   ├── basic_usage.py       # 基础使用示例
│   ├── batch_processing.py  # 批量处理示例
│   └── advanced_features.py # 高级功能示例
├── web_demo.html            # Web演示界面
└── static/                  # 静态资源
    ├── style.css           # 样式文件
    └── script.js           # JavaScript代码
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config.json` 文件，添加你的HiAgent API密钥：

```json
{
    "api_base_url": "https://api.hiagent.com",
    "api_key": "your_api_key_here",
    "timeout": 30
}
```

### 3. 运行示例

#### 基础使用
```bash
python examples/basic_usage.py
```

#### Web界面
直接在浏览器中打开 `web_demo.html` 文件即可使用。

## API使用说明

### 客户端初始化

```python
from client import HiAgentClient

# 使用配置文件初始化
client = HiAgentClient()

# 或手动配置
client = HiAgentClient(
    api_base_url="https://api.hiagent.com",
    api_key="your_api_key"
)
```

### 发送消息

```python
response = client.send_message(
    agent_id="your_agent_id",
    message="你好，请介绍一下你自己",
    user_id="user123"
)
print(response)
```

## 注意事项

1. 请确保在 `config.json` 中正确配置API密钥
2. 根据HiAgent的实际API文档调整相关参数
3. 本demo仅用于学习和演示目的

## 许可证

MIT License