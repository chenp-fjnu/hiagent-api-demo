# 🚀 自动Git提交系统使用指南

这个系统可以自动监控文件变化并提交到Git仓库，让您的开发工作更加便捷。

## ✨ 功能特性

- 🔍 **实时文件监控**: 自动检测文件创建、修改、删除
- ⏱️ **智能延迟提交**: 避免频繁提交，给您时间进行多次编辑
- 🛡️ **安全机制**: 支持分支检查和文件过滤
- 📝 **自动提交信息**: 基于时间戳和文件数量的智能提交信息
- 🔄 **自动推送**: 提交后自动推送到远程仓库
- 🎛️ **灵活配置**: 丰富的配置选项满足不同需求

## 📦 安装依赖

```bash
pip install watchdog
```

## 🚀 快速开始

### 1. 启动自动监控

```bash
python auto_commit.py
```

### 2. 首次运行

首次运行时，系统会自动创建配置文件 `auto_commit_config.json`，您可以根据需要进行调整。

## ⚙️ 配置说明

配置文件 `auto_commit_config.json` 包含以下选项：

### 基本设置

```json
{
    "watch_directory": ".",           // 监控目录
    "commit_delay": 5,               // 提交延迟（秒）
    "max_files_per_commit": 10,      // 每次提交最大文件数
    "commit_message_template": "自动提交 {timestamp} - {files_count} 个文件"
}
```

### 文件过滤

```json
{
    "exclude_patterns": [            // 排除的文件模式
        "*.pyc",
        "__pycache__/*",
        ".git/*",
        "*.log"
    ],
    "include_patterns": [            // 包含的文件模式
        "*.py",
        "*.js",
        "*.html"
    ]
}
```

### Git设置

```json
{
    "enable_branch_check": true,     // 启用分支检查
    "allowed_branches": [            // 允许的分支
        "main",
        "master",
        "develop"
    ],
    "max_commit_message_length": 100 // 提交信息最大长度
}
```

## 🔧 使用场景

### 场景1: 开发期间持续提交

```bash
# 启动监控
python auto_commit.py

# 编辑文件...
# 系统会自动检测并提交更改
```

### 场景2: 配置特定分支

```json
{
    "enable_branch_check": true,
    "allowed_branches": ["feature/*", "hotfix/*"]
}
```

### 场景3: 自定义提交信息

```json
{
    "commit_message_template": "🚀 功能更新 {timestamp}: {files_count} 个文件"
}
```

## 📋 工作流程

1. **文件监控**: 系统实时监控指定目录下的文件变化
2. **过滤检查**: 根据配置规则过滤需要提交的文件
3. **延迟处理**: 等待用户完成编辑（默认5秒）
4. **Git操作**: 自动执行 git add 和 git commit
5. **远程推送**: 尝试推送到远程仓库
6. **状态反馈**: 显示操作结果和错误信息

## 🎯 最佳实践

### ✅ 推荐配置

1. **合理设置延迟**: 建议设置5-10秒，避免频繁提交
2. **正确过滤文件**: 使用 `exclude_patterns` 排除临时文件
3. **分支保护**: 在生产环境启用分支检查
4. **提交信息模板**: 使用清晰的模板描述变更

### ⚠️ 注意事项

1. **网络检查**: 确保网络连接正常，避免推送失败
2. **权限确认**: 确保Git仓库有推送权限
3. **分支切换**: 切换分支后重新启动监控
4. **配置文件**: 根据项目特点调整过滤规则

## 🔍 故障排除

### 问题1: 提交失败

**现象**: 提示 "Git命令执行失败"

**解决**: 
- 确保在Git仓库中运行
- 检查Git配置（用户名、邮箱）
- 验证网络连接

### 问题2: 推送失败

**现象**: 提交成功但推送失败

**解决**:
- 检查远程仓库权限
- 验证网络连接
- 手动执行 `git push` 确认

### 问题3: 频繁提交

**现象**: 短时间内多次提交

**解决**:
- 增加 `commit_delay` 值
- 检查排除规则是否正确

## 📊 示例输出

```
🚀 启动文件监控服务...
💡 提示: 按 Ctrl+C 停止监控
📂 监控目录: /path/to/your/project
🌿 当前分支: main
⏱️  提交延迟: 5 秒
🔍 文件监控已启动，等待文件变化...
📝 检测到文件变化: modified - client.py
🔄 正在提交 1 个文件变更...
✅ 提交成功并推送到远程仓库: 自动提交 2024-01-20 15:30:25 - 1 个文件
```

## 🎨 高级用法

### 自定义监控目录

```json
{
    "watch_directory": "./src"
}
```

### 排除大文件

```json
{
    "exclude_patterns": [
        "*.pyc",
        "*.log",
        "*.zip",
        "*.tar.gz",
        "node_modules/*"
    ]
}
```

### 多分支支持

```json
{
    "enable_branch_check": true,
    "allowed_branches": ["main", "develop", "feature/*"]
}
```

---

🎉 **享受自动化开发流程！**

如有问题，请检查配置文件或查看错误日志。