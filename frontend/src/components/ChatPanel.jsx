import React, { useState, useRef, useEffect } from 'react'
import {
  Input,
  Button,
  Space,
  Alert,
  Spin,
  Empty,
  Tooltip
} from 'antd'
import {
  SendOutlined,
  ClearOutlined,
  ExclamationCircleOutlined,
  RobotOutlined
} from '@ant-design/icons'
import MessageList from './MessageList'
import './ChatPanel.css'
import { http } from '../utils/fetch'

const { TextArea } = Input

/**
 * 聊天面板组件
 *
 * @remarks 处理用户输入、发送消息、接收流式响应等功能
 * @param {Object} props - 组件属性
 * @param {boolean} props.systemOnline - 系统是否在线
 * @param {boolean} props.vectorStoreReady - 向量库是否就绪
 * @returns React组件
 */
function ChatPanel({ systemOnline, vectorStoreReady }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: '👋 欢迎使用RAG Excel智能问答系统！\n\n请先上传Excel文件到左侧的文件管理器，然后就可以开始提问了。\n\n💡 **使用提示：**\n- 支持询问Excel中的具体数据\n- 可以进行数据分析和统计\n- 支持多文件联合查询\n- 实时显示工具调用过程',
      timestamp: new Date().toISOString(),
      toolCalls: [],
      sources: []
    }
  ])

  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // useEffect(() => {
  //   scrollToBottom()
  // }, [messages, currentStreamingMessage])
  useEffect(() => {
    scrollToBottom()
  }, [messages.length])

  // 生成消息ID
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`
  }

  // 添加消息
  const addMessage = (message) => {
    setMessages(prev => [...prev, { ...message, id: generateMessageId() }])
  }

  // 更新流式消息
  const updateStreamingMessage = (content, toolCalls = [], sources = [], isTyping = false) => {
    const streamingMessage = {
      id: generateMessageId(),
      role: 'assistant',
      content,
      timestamp: new Date().toISOString(),
      toolCalls,
      sources,
      isStreaming: true,
      isTyping
    };
    setCurrentStreamingMessage(streamingMessage)
    // 更新 messages 的最后一条消息
    setMessages(prev => {
      // 如果最后一条消息是 机器人 就直接更新，如果不是则添加
      if (prev[prev.length - 1].role === 'assistant') {
        return [...prev.slice(0, -1), streamingMessage]
      } else {
        return [...prev, streamingMessage]
      }
    })
  }

  // 添加工具调用消息
  const addToolCallMessage = (toolCall) => {
    const toolMessage = {
      id: `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: 'tool',
      content: '',
      timestamp: new Date().toISOString(),
      toolCalls: [toolCall],
      sources: [],
      isStreaming: false
    }
    setMessages(prev => [...prev, toolMessage])
  }

  // 完成流式消息
  const finishStreamingMessage = () => {

  }

  // 发送消息
  const sendMessage = async () => {
    const message = inputValue.trim()
    if (!message || isLoading) return

    // 检查系统状态
    if (!systemOnline) {
      addMessage({
        role: 'system',
        content: '❌ 系统离线，请检查服务器连接状态',
        timestamp: new Date().toISOString(),
        toolCalls: [],
        sources: []
      })
      return
    }

    if (!vectorStoreReady) {
      addMessage({
        role: 'system',
        content: '⚠️ 向量数据库未就绪，请先上传Excel文件',
        timestamp: new Date().toISOString(),
        toolCalls: [],
        sources: []
      })
      return
    }

    // 清空输入框和重置状态
    setInputValue('')
    setIsLoading(true)
    setCurrentStreamingMessage(null) // 清理之前的流式消息

    try {
      // 构建完整的对话历史（包含当前用户消息）
      const conversationHistory = messages
        .filter(msg => msg.role === 'user' || msg.role === 'assistant')
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      // 添加当前用户消息
      conversationHistory.push({ role: 'user', content: message })

      // 添加用户消息到界面显示
      addMessage({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
        toolCalls: [],
        sources: []
      })

      // 发送流式请求
      const response = await http('/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'rag-excel',
          messages: conversationHistory,
          temperature: 0.7,
          stream: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // 处理流式响应
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      let allToolCalls = []
      let sources = []
      let hasStartedContent = false

      // 创建初始的流式消息
      updateStreamingMessage('🤖 正在思考...', [], [], true)

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留不完整的行

        for (const line of lines) {
          if (line.trim() === '') continue

          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6)

            if (dataStr.trim() === '[DONE]') {
              // 流式响应完成
              setTimeout(() => {
                finishStreamingMessage()
              }, 500)
              break
            }

            try {
              const data = JSON.parse(dataStr)

              if (data.choices && data.choices[0]) {
                const choice = data.choices[0]
                const delta = choice.delta || {}

                // 处理工具调用 - 收集但不立即显示
                if (delta.tool_calls) {
                  for (const toolCall of delta.tool_calls) {
                    if (toolCall.function && toolCall.function.name) {
                      // 检查是否已存在相同的工具调用
                      const existingIndex = allToolCalls.findIndex(tc => tc.id === toolCall.id)
                      if (existingIndex >= 0) {
                        allToolCalls[existingIndex] = toolCall
                      } else {
                        allToolCalls.push(toolCall)
                      }
                    }
                  }

                  // 更新流式消息显示工具调用状态
                  if (allToolCalls.length > 0 && !hasStartedContent) {
                    const toolNames = allToolCalls.map(tc => tc.function.name).join(', ')
                    updateStreamingMessage(`🔧 使用工具: ${toolNames}`, allToolCalls, sources, true)
                  }
                }

                // 处理内容 - 逐字显示
                if (delta.content) {
                  if (!hasStartedContent) {
                    // 第一次收到内容，清除"正在思考"状态
                    fullContent = ''
                    hasStartedContent = true
                  }

                  fullContent += delta.content

                  // 实现打字机效果 - 逐字显示，包含工具调用信息
                  updateStreamingMessage(fullContent, allToolCalls, sources, true)
                }

                // 检查是否完成
                if (choice.finish_reason === 'stop') {
                  // 添加来源信息到最终内容
                  if (sources.length > 0) {
                    fullContent += '\n\n📚 **信息来源:**\n'
                    sources.forEach((source, index) => {
                      fullContent += `${index + 1}. 文件: ${source.file}, 工作表: ${source.sheet}\n`
                    })
                  }

                  updateStreamingMessage(fullContent, allToolCalls, sources, false)
                  // 延迟100ms 再调用 finishStreamingMessage
                  setTimeout(() => {
                    finishStreamingMessage()
                  }, 500)
                  break
                }
              }
            } catch (e) {
              console.warn('解析SSE数据失败:', e, dataStr)
            }
          }
        }
      }

    } catch (error) {
      console.error('发送消息失败:', error)
      addMessage({
        role: 'system',
        content: `❌ 发送失败: ${error.message}`,
        timestamp: new Date().toISOString(),
        toolCalls: [],
        sources: []
      })
      setCurrentStreamingMessage(null)
    } finally {
      setIsLoading(false)
    }
  }

  // 清空对话
  const clearMessages = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: '对话已清空，可以开始新的提问。',
        timestamp: new Date().toISOString(),
        toolCalls: [],
        sources: []
      }
    ])
    setCurrentStreamingMessage(null)
  }

  // 处理键盘事件
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // 系统状态警告
  const renderSystemAlert = () => {
    if (!systemOnline) {
      return (
        <Alert
          message="系统离线"
          description="无法连接到后端服务，请检查服务器状态"
          type="error"
          icon={<ExclamationCircleOutlined />}
          showIcon
          className="system-alert"
        />
      )
    }

    if (!vectorStoreReady) {
      return (
        <Alert
          message="向量数据库未就绪"
          description="请先上传Excel文件到左侧文件管理器"
          type="warning"
          icon={<ExclamationCircleOutlined />}
          showIcon
          className="system-alert"
        />
      )
    }

    return null
  }

  return (
    <div className="chat-panel">
      {/* 系统状态提示 */}
      {renderSystemAlert()}

      {/* 消息列表 */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <Empty
            image={<RobotOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            description="暂无对话消息"
          />
        ) : (
          <MessageList
            messages={messages}
            streamingMessage={currentStreamingMessage}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="input-container">
        <div className="input-wrapper">
          <TextArea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              !systemOnline
                ? "系统离线，无法发送消息..."
                : !vectorStoreReady
                ? "请先上传Excel文件..."
                : "输入您的问题... (Shift+Enter换行，Enter发送)"
            }
            disabled={!systemOnline || !vectorStoreReady || isLoading}
            autoSize={{ minRows: 1, maxRows: 4 }}
            className="message-input"
          />

          <Space className="input-actions">
            <Tooltip title="清空对话">
              <Button
                icon={<ClearOutlined />}
                onClick={clearMessages}
                disabled={isLoading || messages.length <= 1}
                type="text"
              />
            </Tooltip>

            <Button
              type="primary"
              icon={isLoading ? <Spin size="small" /> : <SendOutlined />}
              onClick={sendMessage}
              disabled={!inputValue.trim() || !systemOnline || !vectorStoreReady || isLoading}
              loading={isLoading}
            >
              发送
            </Button>
          </Space>
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
