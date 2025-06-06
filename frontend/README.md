# RAG Excel API - React前端

这是RAG Excel API的现代化React前端界面，使用Ant Design组件库构建，提供优雅的用户体验。

## 🚀 功能特性

### 💬 智能聊天
- **流式响应**: 实时显示AI回答过程
- **工具调用展示**: 可视化显示excel_search和llm_generate工具使用
- **Markdown支持**: 支持富文本格式的回答
- **消息历史**: 保存对话历史，支持清空

### 📁 文件管理
- **拖拽上传**: 支持拖拽Excel文件上传
- **文件列表**: 显示知识库中的所有文件
- **文件删除**: 支持删除不需要的文件
- **实时状态**: 显示上传进度和处理状态

### 📊 系统监控
- **实时状态**: 显示系统在线状态和向量库状态
- **文件统计**: 显示知识库文件数量
- **更新时间**: 显示最后更新时间

### 🎨 用户体验
- **响应式设计**: 适配桌面和移动设备
- **现代UI**: 使用Ant Design组件库
- **流畅动画**: 消息动画和状态转换
- **深色主题**: 支持浅色主题（可扩展深色主题）

## 🛠️ 技术栈

- **React 18**: 现代React框架
- **Vite**: 快速构建工具
- **Ant Design**: 企业级UI组件库
- **Axios**: HTTP客户端
- **React Markdown**: Markdown渲染
- **CSS3**: 现代CSS特性

## 📦 安装和构建

### 前置要求
- Node.js 16+ 
- npm 或 yarn

### 开发模式
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

开发服务器会在 http://localhost:3000 启动，并自动代理API请求到后端服务器。

### 生产构建
```bash
# 方法1: 使用Python脚本（推荐）
python build_frontend.py

# 方法2: 使用批处理文件（Windows）
build_frontend.bat

# 方法3: 手动构建
cd frontend
npm install
npm run build
```

构建完成后，静态文件会输出到 `static/` 目录，并自动集成到Python服务器。

## 🎯 使用方法

### 1. 构建前端
```bash
python build_frontend.py
```

### 2. 启动服务器
```bash
python rag_api_server.py
```

### 3. 访问应用
- **前端应用**: http://localhost:8000/app
- **API文档**: http://localhost:8000/docs
- **旧版界面**: http://localhost:8000/web_demo.html

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/                    # 源代码
│   ├── components/         # React组件
│   │   ├── ChatPanel.jsx   # 聊天面板
│   │   ├── MessageList.jsx # 消息列表
│   │   ├── FileManager.jsx # 文件管理
│   │   └── SystemStatus.jsx# 系统状态
│   ├── App.jsx            # 主应用组件
│   ├── main.jsx           # 应用入口
│   └── index.css          # 全局样式
├── package.json           # 项目配置
├── vite.config.js         # Vite配置
└── README.md             # 说明文档
```

## 🔧 配置说明

### Vite配置 (vite.config.js)
```javascript
export default defineConfig({
  plugins: [react()],
  base: '/static/',           // 静态文件基础路径
  build: {
    outDir: '../static',      // 输出到上级目录的static文件夹
    emptyOutDir: true
  },
  server: {
    port: 3000,
    proxy: {                  // 开发时代理API请求
      '/v1': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
```

### 代理配置
开发模式下，Vite会自动将API请求代理到后端服务器：
- `/v1/*` → `http://localhost:8000/v1/*`
- `/health` → `http://localhost:8000/health`

## 🎨 组件说明

### App.jsx
主应用组件，负责：
- 整体布局和路由
- 系统状态管理
- 组件间通信

### ChatPanel.jsx
聊天面板组件，负责：
- 用户输入处理
- 流式响应接收
- 消息状态管理

### MessageList.jsx
消息列表组件，负责：
- 消息渲染和样式
- 工具调用展示
- Markdown渲染

### FileManager.jsx
文件管理组件，负责：
- 文件上传（拖拽支持）
- 文件列表显示
- 文件删除操作

### SystemStatus.jsx
系统状态组件，负责：
- 实时状态显示
- 状态指示器
- 工具提示

## 🔄 API集成

### 聊天API
```javascript
const response = await fetch('/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'rag-excel',
    messages: [{ role: 'user', content: message }],
    stream: true  // 启用流式响应
  })
})
```

### 文件上传API
```javascript
const formData = new FormData()
formData.append('file', file)

const response = await fetch('/v1/files/upload', {
  method: 'POST',
  body: formData
})
```

## 🎯 自定义和扩展

### 主题定制
在 `src/main.jsx` 中修改Ant Design主题：
```javascript
<ConfigProvider 
  theme={{
    token: {
      colorPrimary: '#1890ff',  // 主色调
      borderRadius: 8,          // 圆角大小
    },
  }}
>
```

### 添加新组件
1. 在 `src/components/` 下创建新组件
2. 创建对应的CSS文件
3. 在 `App.jsx` 中引入和使用

### 样式修改
- 全局样式：修改 `src/index.css`
- 组件样式：修改对应的 `.css` 文件
- 主题配置：修改 `src/main.jsx`

## 🐛 故障排除

### 构建失败
1. 检查Node.js版本（需要16+）
2. 清除node_modules重新安装
3. 检查网络连接

### 开发服务器无法启动
1. 检查端口3000是否被占用
2. 检查后端服务器是否在8000端口运行
3. 检查防火墙设置

### API请求失败
1. 确认后端服务器正在运行
2. 检查CORS配置
3. 查看浏览器控制台错误信息

## 📝 开发建议

1. **组件设计**: 保持组件单一职责，便于维护
2. **状态管理**: 使用React Hooks管理组件状态
3. **错误处理**: 添加适当的错误边界和异常处理
4. **性能优化**: 使用React.memo和useMemo优化渲染
5. **代码规范**: 遵循ESLint规则，保持代码一致性

## 🔮 未来计划

- [ ] 添加深色主题支持
- [ ] 实现多语言国际化
- [ ] 添加更多图表和可视化
- [ ] 支持更多文件格式
- [ ] 添加用户认证功能
- [ ] 实现实时协作功能
