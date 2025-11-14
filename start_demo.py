#!/usr/bin/env python3
"""
HiAgent API Demo - 启动脚本
一键启动演示服务的便捷工具
"""

import os
import sys
import json
import webbrowser
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flask import Flask, send_from_directory, jsonify, request
    from flask_cors import CORS
    import click
    from dotenv import load_dotenv
except ImportError as e:
    print(f"错误：缺少必要的依赖包: {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

# 加载环境变量
load_dotenv()

class HiAgentDemoServer:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static', static_url_path='/static')
        self.setup_config()
        self.setup_routes()
    
    def setup_config(self):
        """设置Flask配置"""
        # CORS 配置
        CORS(self.app, origins=os.getenv('CORS_ORIGINS', '*').split(','),
             methods=os.getenv('CORS_METHODS', 'GET,POST,OPTIONS,PUT,DELETE').split(','),
             allow_headers=os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(','))
        
        # 其他配置
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hiagent-demo-secret-key')
        self.app.config['JSON_AS_ASCII'] = False  # 支持中文
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return send_from_directory(self.app.static_folder, 'web_demo.html')
        
        @self.app.route('/api/health')
        def health_check():
            """健康检查"""
            return jsonify({
                'status': 'healthy',
                'service': 'HiAgent API Demo',
                'version': '1.0.0'
            })
        
        @self.app.route('/api/agents', methods=['GET'])
        def list_agents():
            """获取智能体列表（模拟）"""
            # 在实际应用中，这里应该调用真实的HiAgent API
            agents = [
                {
                    'id': 'agent-001',
                    'name': '对话助手',
                    'description': '通用的智能对话助手',
                    'status': 'active'
                },
                {
                    'id': 'agent-002', 
                    'name': '代码助手',
                    'description': '专业的编程和代码审查助手',
                    'status': 'active'
                },
                {
                    'id': 'agent-003',
                    'name': '数据分析助手',
                    'description': '数据分析和可视化专家',
                    'status': 'active'
                }
            ]
            return jsonify({'agents': agents})
        
        @self.app.route('/api/agents/<agent_id>/info', methods=['GET'])
        def get_agent_info(agent_id):
            """获取智能体详细信息"""
            agent_info = {
                'id': agent_id,
                'name': f'智能体-{agent_id}',
                'description': '这是一个示例智能体',
                'capabilities': ['对话', '问答', '文本生成'],
                'status': 'active',
                'model': 'hiagent-base-v1',
                'max_tokens': 2000,
                'temperature': 0.7
            }
            return jsonify({'agent': agent_info})
        
        @self.app.route('/api/agents/<agent_id>/chat', methods=['POST'])
        def chat_with_agent(agent_id):
            """与智能体对话"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                user_id = data.get('user_id', 'anonymous')
                
                if not message:
                    return jsonify({'error': '消息内容不能为空'}), 400
                
                # 简单的模拟回复逻辑
                reply = self.generate_mock_reply(message, agent_id)
                
                return jsonify({
                    'success': True,
                    'reply': reply,
                    'agent_id': agent_id,
                    'user_id': user_id,
                    'timestamp': self.get_timestamp()
                })
                
            except Exception as e:
                return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500
        
        @self.app.route('/api/agents/<agent_id>/usage', methods=['GET'])
        def get_usage_stats(agent_id):
            """获取使用统计"""
            # 模拟使用统计数据
            stats = {
                'agent_id': agent_id,
                'total_requests': 156,
                'total_tokens': 24560,
                'avg_response_time': 1.23,
                'success_rate': 0.98,
                'date_range': {
                    'start': '2024-01-01',
                    'end': '2024-12-31'
                }
            }
            return jsonify({'stats': stats})
        
        @self.app.route('/api/test-connection', methods=['POST'])
        def test_connection():
            """测试API连接"""
            try:
                data = request.get_json()
                api_base_url = data.get('api_base_url', '')
                api_key = data.get('api_key', '')
                
                if not api_base_url or not api_key:
                    return jsonify({
                        'success': False,
                        'message': '缺少必要的配置参数'
                    }), 400
                
                # 在实际应用中，这里应该测试真实的API连接
                # 目前只是模拟测试
                import random
                success = random.choice([True, False])
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': '连接测试成功'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '连接测试失败，请检查API配置'
                    })
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'测试连接时出错: {str(e)}'
                }), 500
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """静态文件服务"""
            return send_from_directory(self.app.static_folder, filename)
    
    def generate_mock_reply(self, message, agent_id):
        """生成模拟回复"""
        message_lower = message.lower()
        
        if '你好' in message or 'hello' in message_lower:
            return f"你好！我是{agent_id}智能体，很高兴为您服务！我可以帮助您处理各种任务。有什么需要帮助的吗？"
        elif '做什么' in message or '功能' in message:
            return "我可以为您提供以下服务：\n• 智能对话和问答\n• 文本创作和编辑\n• 数据分析和处理\n• 代码编写和调试\n• 知识查询和学习"
        elif '人工智能' in message or 'ai' in message_lower:
            return "人工智能是计算机科学的重要分支，通过机器学习、深度学习等技术，让机器能够模拟人类智能行为。AI技术在现代社会中有着广泛的应用前景。"
        elif '谢谢' in message or '感谢' in message:
            return "不客气！很高兴能帮助到您。如果还有其他问题，请随时告诉我！"
        elif '再见' in message or '拜拜' in message_lower:
            return "再见！感谢使用HiAgent API Demo，期待为您提供更多帮助！"
        else:
            return f"感谢您的消息：'{message}'。作为{agent_id}智能体，我正在学习和改进中。我会尽力为您提供有用的信息！"
    
    def get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

# 创建Flask应用实例
demo_server = HiAgentDemoServer()
app = demo_server.app

@click.group()
def cli():
    """HiAgent API Demo 启动工具"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器主机地址')
@click.option('--port', default=5000, help='服务器端口')
@click.option('--debug/--no-debug', default=True, help='调试模式')
@click.option('--open-browser/--no-open-browser', default=True, help='自动打开浏览器')
def start(host, port, debug, open_browser):
    """启动演示服务器"""
    click.echo("🚀 启动 HiAgent API Demo...")
    
    try:
        if open_browser:
            # 延迟打开浏览器，等待服务器启动
            import threading
            import time
            
            def open_browser_delayed():
                time.sleep(2)
                url = f'http://{host}:{port}'
                click.echo(f"🌐 在浏览器中打开: {url}")
                webbrowser.open(url)
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        click.echo(f"📍 服务地址: http://{host}:{port}")
        click.echo("📖 按 Ctrl+C 停止服务")
        click.echo("-" * 50)
        
        app.run(host=host, port=port, debug=debug, threaded=True)
        
    except KeyboardInterrupt:
        click.echo("\n🛑 服务已停止")
    except Exception as e:
        click.echo(f"❌ 启动失败: {e}", err=True)
        sys.exit(1)

@cli.command()
def info():
    """显示项目信息"""
    info_data = {
        'name': 'HiAgent API Demo',
        'version': '1.0.0',
        'description': 'HiAgent API接口调用演示项目',
        'features': [
            'Web界面交互',
            'API客户端封装',
            '配置管理',
            '错误处理',
            '批量处理示例',
            '高级功能演示'
        ],
        'files': {
            'config.json': '主配置文件',
            'client.py': 'API客户端封装',
            'web_demo.html': 'Web演示界面',
            'static/style.css': '界面样式',
            'static/script.js': '前端交互逻辑',
            'examples/': '使用示例目录'
        }
    }
    
    click.echo("📋 项目信息")
    click.echo("=" * 30)
    click.echo(f"名称: {info_data['name']}")
    click.echo(f"版本: {info_data['version']}")
    click.echo(f"描述: {info_data['description']}")
    click.echo("\n🎯 主要功能:")
    for feature in info_data['features']:
        click.echo(f"  • {feature}")
    click.echo("\n📁 关键文件:")
    for file, desc in info_data['files'].items():
        click.echo(f"  • {file}: {desc}")

@cli.command()
@click.option('--force', is_flag=True, help='强制创建，忽略现有文件')
def setup(force):
    """初始化项目配置"""
    click.echo("🔧 初始化项目配置...")
    
    # 检查.env文件
    env_file = Path('.env')
    if env_file.exists() and not force:
        click.echo("⚠️  .env 文件已存在，使用 --force 覆盖")
        return
    
    # 创建.env文件
    env_example = Path('.env.example')
    if env_example.exists():
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        click.echo("✅ 已创建 .env 文件")
        click.echo("📝 请编辑 .env 文件填入您的API配置")
    else:
        click.echo("❌ 未找到 .env.example 文件")

@cli.command()
def check():
    """检查项目配置"""
    click.echo("🔍 检查项目配置...")
    
    # 检查必要文件
    required_files = ['config.json', 'client.py', 'requirements.txt', '.env']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        click.echo("❌ 缺少必要文件:")
        for file in missing_files:
            click.echo(f"  • {file}")
        return False
    
    # 检查.env配置
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        required_env_vars = ['HIAGENT_API_BASE_URL', 'HIAGENT_API_KEY', 'HIAGENT_AGENT_ID']
        missing_env_vars = []
        
        for var in required_env_vars:
            if var not in content or 'your_' in content:
                missing_env_vars.append(var)
        
        if missing_env_vars:
            click.echo("⚠️  环境变量未配置:")
            for var in missing_env_vars:
                click.echo(f"  • {var}")
        else:
            click.echo("✅ 环境变量配置完整")
    
    click.echo("✅ 项目配置检查完成")
    return True

if __name__ == '__main__':
    cli()