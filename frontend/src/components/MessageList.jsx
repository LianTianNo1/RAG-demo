import React from 'react'
import { Space, Tag, Collapse, Typography } from 'antd'
import { 
  UserOutlined, 
  RobotOutlined, 
  ToolOutlined,
  FileTextOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import './MessageList.css'

const { Text } = Typography
const { Panel } = Collapse

/**
 * 消息列表组件
 * 
 * @remarks 显示聊天消息列表，包括用户消息、助手回复、工具调用等
 * @param {Object} props - 组件属性
 * @param {Array} props.messages - 消息列表
 * @param {Object} props.streamingMessage - 当前流式消息
 * @returns React组件
 */
function MessageList({ messages, streamingMessage }) {
  
  // 格式化时间
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // 渲染工具调用
  const renderToolCalls = (toolCalls) => {
    if (!toolCalls || toolCalls.length === 0) return null

    return (
      <div className="tool-calls-section">
        <Collapse 
          size="small" 
          ghost
          items={toolCalls.map((toolCall, index) => {
            let args = {}
            try {
              args = JSON.parse(toolCall.function?.arguments || '{}')
            } catch (e) {
              args = { raw: toolCall.function?.arguments || '' }
            }

            return {
              key: index,
              label: (
                <Space>
                  <ToolOutlined />
                  <Text strong>{toolCall.function?.name || 'unknown'}</Text>
                  <Tag color="blue" size="small">工具调用</Tag>
                </Space>
              ),
              children: (
                <div className="tool-call-content">
                  <Text code className="tool-args">
                    {JSON.stringify(args, null, 2)}
                  </Text>
                </div>
              )
            }
          })}
        />
      </div>
    )
  }

  // 渲染来源信息
  const renderSources = (sources) => {
    if (!sources || sources.length === 0) return null

    return (
      <div className="sources-section">
        <div className="sources-header">
          <FileTextOutlined />
          <Text strong>信息来源</Text>
        </div>
        <div className="sources-list">
          {sources.map((source, index) => (
            <div key={index} className="source-item">
              <Tag color="green" size="small">
                {source.file}
              </Tag>
              <Text type="secondary">
                工作表: {source.sheet}
              </Text>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // 渲染单个消息
  const renderMessage = (message) => {
    const isUser = message.role === 'user'
    const isSystem = message.role === 'system'
    const isStreaming = message.isStreaming

    return (
      <div 
        key={message.id} 
        className={`message-item ${isUser ? 'user' : isSystem ? 'system' : 'assistant'} ${isStreaming ? 'streaming' : ''}`}
      >
        <div className="message-avatar">
          {isUser ? (
            <UserOutlined />
          ) : isSystem ? (
            <ClockCircleOutlined />
          ) : (
            <RobotOutlined />
          )}
        </div>
        
        <div className="message-content">
          <div className="message-header">
            <Text strong className="message-role">
              {isUser ? '用户' : isSystem ? '系统' : 'AI助手'}
            </Text>
            <Text type="secondary" className="message-time">
              {formatTime(message.timestamp)}
            </Text>
          </div>
          
          <div className="message-body">
            {isSystem ? (
              <Text className="system-message">{message.content}</Text>
            ) : (
              <div className={`message-text ${isStreaming ? 'typing-cursor' : ''}`}>
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
            
            {/* 工具调用 */}
            {renderToolCalls(message.toolCalls)}
            
            {/* 来源信息 */}
            {renderSources(message.sources)}
          </div>
        </div>
      </div>
    )
  }

  // 合并消息列表和流式消息
  const allMessages = [...messages]
  if (streamingMessage) {
    allMessages.push(streamingMessage)
  }

  return (
    <div className="message-list">
      {allMessages.map(renderMessage)}
    </div>
  )
}

export default MessageList
