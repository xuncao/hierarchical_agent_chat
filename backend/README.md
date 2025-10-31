# Hierarchical Agent Teams 后端服务

基于LangGraph Hierarchical Agent Teams架构的大语言模型服务后端。

## 项目概述

这是一个采用分层代理团队架构的AI对话服务后端，支持研究团队和文档写作团队的协作工作流。

## 技术栈

- **后端框架**: FastAPI 0.110.0
- **AI框架**: LangGraph 1.0.1 + LangChain 0.3.27
- **大语言模型**: DEEPSEEK (兼容Cohere)
- **数据库**: SQLite/PostgreSQL
- **异步处理**: asyncio
- **类型检查**: Pydantic 2.10.3

## 核心特性

### 分层代理团队架构

1. **顶层监督器(Supervisor)**: 负责路由用户请求到合适的子团队
2. **研究团队(Research Team)**:
   - 搜索代理(Search Agent): 使用Tavily搜索引擎获取信息
   - 网页抓取代理(Web Scraper Agent): 抓取和解析网页内容
3. **文档写作团队(Document Writing Team)**:
   - 文档写作代理(Document Writer Agent): 生成和编辑文档内容
   - 大纲制定代理(Note Taking Agent): 创建文档大纲和结构
   - 图表生成代理(Chart Generating Agent): 生成数据图表

### API接口

- `POST /api/v1/api/chat/`: 标准聊天接口
- `POST /api/v1/api/chat/stream`: 流式聊天接口 (Server-Sent Events)
- `WebSocket /api/v1/api/chat/ws`: WebSocket实时聊天
- `GET /api/v1/api/chat/conversations`: 获取对话历史
- `POST /api/v1/api/chat/conversations`: 创建新对话
- `GET /api/v1/api/models`: 获取可用模型列表

### 流式输出支持

- 支持Server-Sent Events (SSE)流式传输
- 支持WebSocket实时双向通信
- 打字机效果的逐字显示
- 异步处理保证UI响应性

## 🚀 简便可复用的启动方式

### 方式一：快速启动脚本（推荐）

```bash
# 一键启动（自动检查环境、安装依赖、启动服务）
./quick_start.sh

# 或使用Python启动脚本
python start.py
```

### 方式二：分步启动

```bash
# 1. 检查环境
python start.py --check-only

# 2. 开发模式启动
python start.py --mode dev --host 0.0.0.0 --port 8000

# 3. 生产模式启动
python start.py --mode prod --host 0.0.0.0 --port 8000
```

### 方式三：传统方式

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑.env文件配置API密钥

# 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 环境要求

- Python 3.13.5
- 依赖包 (见requirements.txt)

### 环境配置

复制环境变量模板：

```bash
cp .env.example .env
```

编辑`.env`文件，配置必要的API密钥：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
COHERE_API_KEY=your_cohere_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=sqlite:///./hierarchical_agent.db
```

### Docker运行

```bash
# 构建镜像
docker build -t hierarchical-agent-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env hierarchical-agent-backend

# 使用Docker Compose
docker-compose up -d
```

## 项目结构

```bash
backend/
├── src/                          # 源代码目录
│   ├── api/                      # API接口层
│   │   └── routers/              # 路由模块
│   ├── config/                   # 配置管理
│   ├── core/                     # 核心业务逻辑
│   │   ├── cache.py              # 缓存系统
│   │   ├── error_handler.py      # 错误处理
│   │   ├── graphs/               # LangGraph图结构
│   │   ├── llm_client.py         # LLM客户端封装
│   │   └── tools/                # 工具模块
│   ├── database/                 # 数据库层
│   ├── models/                   # 数据模型
│   └── types/                    # TypeScript类型定义
├── requirements.txt              # Python依赖
└── README.md                     # 项目文档
```

## API文档

服务启动后，访问以下地址查看API文档：

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### 主要接口示例

#### 标准聊天

```bash
curl -X POST "http://localhost:8000/api/v1/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请帮我研究一下人工智能的最新发展",
    "model": "deepseek-chat",
    "team": "auto",
    "web_search": true
  }'
```

#### 流式聊天

```bash
curl -X POST "http://localhost:8000/api/v1/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "请帮我写一篇关于机器学习的文章",
    "model": "deepseek-chat"
  }'
```

#### WebSocket聊天

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/api/chat/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'chat',
    message: '你好，请帮我研究一下...',
    config: { model: 'deepseek-chat' }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};
```

## 部署

### 生产环境部署

1. **环境配置**: 确保所有环境变量正确设置
2. **数据库迁移**: 初始化数据库表结构
3. **服务监控**: 配置日志和监控系统
4. **负载均衡**: 使用Nginx或类似工具进行负载均衡

### 健康检查

服务提供健康检查端点：

```bash
curl http://localhost:8000/api/v1/api/health
```

### 性能优化建议

1. **缓存策略**: 启用Redis缓存频繁访问的数据
2. **数据库优化**: 使用连接池和索引优化
3. **异步处理**: 充分利用FastAPI的异步特性
4. **CDN加速**: 静态资源使用CDN加速

## 开发指南

### 添加新的代理团队

1. 在`src/core/graphs/`目录下创建新的图结构
2. 实现对应的工具类
3. 在顶层监督器中添加路由逻辑
4. 更新API接口支持新的团队类型

### 自定义工具

1. 在`src/core/tools/`目录下创建新的工具类
2. 实现工具的核心功能
3. 在对应的代理图中集成新工具

### 扩展数据模型

1. 在`src/models/`目录下添加新的Pydantic模型
2. 更新数据库模型定义
3. 修改API接口支持新的数据格式

## 故障排除

### 常见问题

1. **API密钥错误**: 检查`.env`文件中的API密钥配置
2. **依赖冲突**: 使用`pip check`检查依赖冲突
3. **端口占用**: 确保8000端口未被其他服务占用
4. **数据库连接失败**: 检查数据库URL配置

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues]
- 邮箱: [542189786@qq.com]

---

**注意**: 本项目仍在积极开发中，API接口和功能可能会有变动。
