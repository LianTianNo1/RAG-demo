import React, { useState, useEffect } from 'react'
import { Layout, Row, Col, Card, Typography, Space, Divider } from 'antd'
import { 
  RobotOutlined, 
  FileTextOutlined, 
  CloudServerOutlined,
  GithubOutlined 
} from '@ant-design/icons'
import ChatPanel from './components/ChatPanel'
import FileManager from './components/FileManager'
import SystemStatus from './components/SystemStatus'
import './App.css'

const { Header, Content, Footer } = Layout
const { Title, Text } = Typography

/**
 * 主应用组件
 * 
 * @remarks 整合聊天面板、文件管理和系统状态等功能模块
 * @returns React组件
 */
function App() {
  const [systemStatus, setSystemStatus] = useState({
    online: false,
    vectorStoreReady: false,
    fileCount: 0,
    lastUpdate: null
  })

  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // 触发刷新的函数
  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  // 检查系统状态
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const response = await fetch('/health')
        if (response.ok) {
          const data = await response.json()
          setSystemStatus({
            online: true,
            vectorStoreReady: data.vector_store_ready,
            fileCount: data.knowledge_base_files,
            lastUpdate: data.last_update
          })
        } else {
          setSystemStatus(prev => ({ ...prev, online: false }))
        }
      } catch (error) {
        console.error('系统状态检查失败:', error)
        setSystemStatus(prev => ({ ...prev, online: false }))
      }
    }

    // 立即检查一次
    checkSystemStatus()

    // 每30秒检查一次
    const interval = setInterval(checkSystemStatus, 30000)

    return () => clearInterval(interval)
  }, [refreshTrigger])

  return (
    <Layout className="app-layout">
      {/* 头部 */}
      <Header className="app-header">
        <div className="header-content">
          <Space align="center" size="large">
            <div className="logo">
              <RobotOutlined className="logo-icon" />
              <Title level={3} className="logo-text">
                RAG Excel API
              </Title>
            </div>
            <Divider type="vertical" className="header-divider" />
            <Text className="subtitle">智能Excel问答系统</Text>
          </Space>
          
          <Space align="center">
            <SystemStatus status={systemStatus} />
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="header-link"
            >
              <CloudServerOutlined /> API文档
            </a>
          </Space>
        </div>
      </Header>

      {/* 主内容区 */}
      <Content className="app-content">
        <div className="content-container">
          <Row gutter={[24, 24]} className="main-row">
            {/* 左侧：文件管理 */}
            <Col xs={24} lg={8} xl={6}>
              <Card 
                title={
                  <Space>
                    <FileTextOutlined />
                    文件管理
                  </Space>
                }
                className="file-manager-card"
                bodyStyle={{ padding: '16px' }}
              >
                <FileManager 
                  onFileChange={triggerRefresh}
                  fileCount={systemStatus.fileCount}
                />
              </Card>
            </Col>

            {/* 右侧：聊天面板 */}
            <Col xs={24} lg={16} xl={18}>
              <Card 
                title={
                  <Space>
                    <RobotOutlined />
                    智能问答
                  </Space>
                }
                className="chat-panel-card"
                bodyStyle={{ padding: 0 }}
              >
                <ChatPanel 
                  systemOnline={systemStatus.online}
                  vectorStoreReady={systemStatus.vectorStoreReady}
                />
              </Card>
            </Col>
          </Row>
        </div>
      </Content>

      {/* 底部 */}
      <Footer className="app-footer">
        <div className="footer-content">
          <Space split={<Divider type="vertical" />}>
            <Text type="secondary">
              © 2024 RAG Excel API - 基于检索增强生成的智能问答系统
            </Text>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="footer-link"
            >
              <GithubOutlined /> GitHub
            </a>
            <Text type="secondary">
              Powered by FastAPI + React + Ollama
            </Text>
          </Space>
        </div>
      </Footer>
    </Layout>
  )
}

export default App
