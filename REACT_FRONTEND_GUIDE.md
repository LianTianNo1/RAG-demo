# RAG Excel API - React前端使用指南

## 🎉 项目升级完成！

您的RAG Excel API现在拥有了一个现代化的React前端界面！这个界面使用了最新的React 18、Ant Design组件库，提供了优雅的用户体验。

## 🚀 快速开始

### 1. 环境准备

确保您已安装：
- **Node.js 16+** (https://nodejs.org/)
- **Python 3.8+**
- **Ollama** (https://ollama.com/)

### 2. 一键设置

```bash
# 设置前端环境（自动检查Node.js、安装依赖、测试构建）
python setup_frontend.py

# 构建前端（将React应用打包到static目录）
python build_frontend.py

# 启动服务器
python rag_api_server.py
```

### 3. 访问应用

- **🎯 React前端**: http://localhost:8000/app
- **📖 API文档**: http://localhost:8000/docs
- **🌐 简单界面**: http://localhost:8000/web_demo.html

## ✨ 新界面特性

### 🎨 现代化设计
- **响应式布局**: 完美适配桌面和移动设备
- **毛玻璃效果**: 现代化的视觉设计
- **流畅动画**: 消息动画和状态转换
- **Ant Design**: 企业级UI组件库

### 💬 智能聊天体验
- **实时流式响应**: 看到AI的思考过程
- **工具调用可视化**: 清晰展示excel_search和llm_generate工具使用
- **Markdown渲染**: 支持富文本格式回答
- **消息历史**: 保存对话记录，支持一键清空

### 📁 文件管理功能
- **拖拽上传**: 直接拖拽Excel文件到上传区域
- **实时进度**: 显示上传进度和处理状态
- **文件列表**: 查看知识库中的所有文件
- **一键删除**: 轻松管理知识库文件

### 📊 系统状态监控
- **实时状态**: 显示系统在线状态和向量库状态
- **文件统计**: 显示知识库文件数量
- **更新时间**: 显示最后更新时间
- **状态指示器**: 直观的颜色和图标提示

## 🛠️ 开发模式

如果您想修改前端代码：

```bash
# 进入前端目录
cd frontend

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

开发服务器会在 http://localhost:3000 启动，支持热重载，修改代码后会自动刷新。

## 📦 构建和部署

### 开发构建
```bash
cd frontend
npm run build
```

### 生产构建
```bash
# 使用Python脚本（推荐）
python build_frontend.py

# 或使用批处理文件（Windows）
build_frontend.bat
```

构建完成后，静态文件会输出到 `static/` 目录，并自动集成到Python服务器。

## 🎯 使用场景演示

### 场景1: 员工信息查询
```
用户: "张三在哪个部门？他的薪资是多少？"

界面显示:
🔧 工具调用: excel_search
   参数: {"query": "张三", "files": "all", "top_k": 3}

🔍 检索到 1 个相关文档

🔧 工具调用: llm_generate  
   参数: {"model": "qwen2:7b-instruct", "context": "..."}

AI回答: "根据提供的信息，张三在技术部工作，担任软件工程师职位，薪资为15万。"

📚 信息来源:
1. 文件: sample_data.xlsx, 工作表: 员工信息
```

### 场景2: 数据分析
```
用户: "请分析一下技术部的人员构成和薪资情况"

界面显示:
🔧 工具调用: excel_search
   参数: {"query": "技术部人员薪资", "files": "all", "top_k": 5}

🔍 检索到 3 个相关文档

🔧 工具调用: llm_generate
   参数: {"model": "qwen2:7b-instruct", "context": "..."}

AI回答: "技术部目前有2名员工：张三（软件工程师，15万）和王五（项目经理，18万）。平均薪资16.5万，是公司薪资水平较高的部门..."

📚 信息来源:
1. 文件: sample_data.xlsx, 工作表: 员工信息
2. 文件: sample_data.xlsx, 工作表: 部门统计
```

## 🔧 自定义配置

### 主题配置
在 `frontend/src/main.jsx` 中修改：
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

### API配置
在 `frontend/vite.config.js` 中修改代理设置：
```javascript
server: {
  proxy: {
    '/v1': 'http://localhost:8000',
    '/health': 'http://localhost:8000'
  }
}
```

## 🐛 故障排除

### 前端构建失败
```bash
# 清理并重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 开发服务器启动失败
1. 检查端口3000是否被占用
2. 确认后端服务器在8000端口运行
3. 检查防火墙设置

### API请求失败
1. 确认后端服务器正在运行
2. 检查浏览器控制台错误信息
3. 验证CORS配置

## 📁 项目文件说明

### 核心文件
- `frontend/src/App.jsx` - 主应用组件
- `frontend/src/components/ChatPanel.jsx` - 聊天面板
- `frontend/src/components/FileManager.jsx` - 文件管理
- `frontend/src/components/MessageList.jsx` - 消息列表
- `frontend/src/components/SystemStatus.jsx` - 系统状态

### 配置文件
- `frontend/package.json` - 依赖配置
- `frontend/vite.config.js` - 构建配置
- `build_frontend.py` - 构建脚本
- `setup_frontend.py` - 环境设置脚本

### 样式文件
- `frontend/src/index.css` - 全局样式
- `frontend/src/App.css` - 应用样式
- `frontend/src/components/*.css` - 组件样式

## 🔮 未来扩展

这个React前端为未来的功能扩展提供了良好的基础：

- **深色主题**: 添加主题切换功能
- **多语言**: 国际化支持
- **数据可视化**: 图表和统计展示
- **用户认证**: 登录和权限管理
- **实时协作**: 多用户同时使用
- **移动应用**: React Native版本

## 🎉 总结

现在您拥有了一个功能完整的现代化RAG系统：

✅ **后端**: FastAPI + Ollama + FAISS + Langchain
✅ **前端**: React + Ant Design + Vite
✅ **功能**: 流式响应 + 工具调用 + 文件管理
✅ **体验**: 现代化UI + 响应式设计 + 实时交互

享受您的新RAG系统吧！🚀
