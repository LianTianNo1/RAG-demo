import React, { useState, useEffect, useRef } from 'react'
import { 
  Upload, 
  List, 
  Button, 
  Space, 
  Typography, 
  message, 
  Popconfirm,
  Empty,
  Spin,
  Progress,
  Tag
} from 'antd'
import { 
  InboxOutlined, 
  FileExcelOutlined, 
  DeleteOutlined,
  ReloadOutlined,
  CloudUploadOutlined
} from '@ant-design/icons'
import './FileManager.css'

const { Dragger } = Upload
const { Text } = Typography

/**
 * 文件管理组件
 * 
 * @remarks 处理Excel文件的上传、列表显示、删除等功能
 * @param {Object} props - 组件属性
 * @param {Function} props.onFileChange - 文件变化回调
 * @param {number} props.fileCount - 文件数量
 * @returns React组件
 */
function FileManager({ onFileChange, fileCount }) {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef(null)

  // 加载文件列表
  const loadFiles = async () => {
    setLoading(true)
    try {
      const response = await fetch('/v1/files/list')
      if (response.ok) {
        const data = await response.json()
        setFiles(data.files || [])
      } else {
        message.error('获取文件列表失败')
      }
    } catch (error) {
      console.error('加载文件列表失败:', error)
      message.error('网络错误，无法获取文件列表')
    } finally {
      setLoading(false)
    }
  }

  // 组件挂载时加载文件列表
  useEffect(() => {
    loadFiles()
  }, [fileCount])

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 格式化日期
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 上传文件
  const uploadFile = async (file) => {
    // 检查文件类型
    const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                   file.type === 'application/vnd.ms-excel' ||
                   file.name.endsWith('.xlsx') ||
                   file.name.endsWith('.xls')

    if (!isExcel) {
      message.error('只支持Excel文件格式 (.xlsx, .xls)')
      return false
    }

    // 检查文件大小 (限制为10MB)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      message.error('文件大小不能超过10MB')
      return false
    }

    setUploading(true)
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('file', file)

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + Math.random() * 20
        })
      }, 200)

      const response = await fetch('/v1/files/upload', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response.ok) {
        const result = await response.json()
        message.success(result.message || '文件上传成功')
        
        // 延迟刷新文件列表，等待后台处理
        setTimeout(() => {
          loadFiles()
          onFileChange?.()
        }, 1000)
      } else {
        const error = await response.json()
        message.error(error.detail || '上传失败')
      }
    } catch (error) {
      console.error('上传文件失败:', error)
      message.error('网络错误，上传失败')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }

    return false // 阻止antd的默认上传行为
  }

  // 删除文件
  const deleteFile = async (filename) => {
    try {
      const response = await fetch(`/v1/files/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        const result = await response.json()
        message.success(result.message || '文件删除成功')
        loadFiles()
        onFileChange?.()
      } else {
        const error = await response.json()
        message.error(error.detail || '删除失败')
      }
    } catch (error) {
      console.error('删除文件失败:', error)
      message.error('网络错误，删除失败')
    }
  }

  // 拖拽上传配置
  const uploadProps = {
    name: 'file',
    multiple: true,
    accept: '.xlsx,.xls',
    beforeUpload: uploadFile,
    showUploadList: false,
    disabled: uploading
  }

  return (
    <div className="file-manager">
      {/* 上传区域 */}
      <div className="upload-section">
        <Dragger {...uploadProps} className="upload-dragger">
          <p className="ant-upload-drag-icon">
            {uploading ? <Spin size="large" /> : <InboxOutlined />}
          </p>
          <p className="ant-upload-text">
            {uploading ? '正在上传...' : '点击或拖拽文件到此区域上传'}
          </p>
          <p className="ant-upload-hint">
            支持 .xlsx 和 .xls 格式，单个文件不超过10MB
          </p>
        </Dragger>

        {/* 上传进度 */}
        {uploading && (
          <div className="upload-progress">
            <Progress 
              percent={Math.round(uploadProgress)} 
              size="small" 
              status="active"
            />
          </div>
        )}
      </div>

      {/* 文件列表 */}
      <div className="files-section">
        <div className="files-header">
          <Space>
            <Text strong>知识库文件</Text>
            <Tag color="blue">{files.length} 个文件</Tag>
          </Space>
          <Button
            icon={<ReloadOutlined />}
            size="small"
            onClick={loadFiles}
            loading={loading}
            type="text"
          />
        </div>

        <div className="files-list">
          {loading ? (
            <div className="loading-container">
              <Spin tip="加载中..." />
            </div>
          ) : files.length === 0 ? (
            <Empty
              image={<FileExcelOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />}
              description="暂无Excel文件"
              imageStyle={{ height: 60 }}
            >
              <Button 
                type="primary" 
                icon={<CloudUploadOutlined />}
                onClick={() => fileInputRef.current?.click()}
              >
                上传文件
              </Button>
            </Empty>
          ) : (
            <List
              dataSource={files}
              renderItem={(file) => (
                <List.Item
                  className="file-item"
                  actions={[
                    <Popconfirm
                      title="确定要删除这个文件吗？"
                      description="删除后将从知识库中移除，无法恢复"
                      onConfirm={() => deleteFile(file.filename)}
                      okText="确定"
                      cancelText="取消"
                      key="delete"
                    >
                      <Button
                        icon={<DeleteOutlined />}
                        size="small"
                        type="text"
                        danger
                      />
                    </Popconfirm>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<FileExcelOutlined className="file-icon" />}
                    title={
                      <Text className="file-name" title={file.filename}>
                        {file.filename}
                      </Text>
                    }
                    description={
                      <Space direction="vertical" size={2}>
                        <Text type="secondary" className="file-size">
                          {formatFileSize(file.size)}
                        </Text>
                        <Text type="secondary" className="file-date">
                          {formatDate(file.modified_time)}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls"
        multiple
        style={{ display: 'none' }}
        onChange={(e) => {
          const files = Array.from(e.target.files)
          files.forEach(uploadFile)
          e.target.value = '' // 清空输入
        }}
      />
    </div>
  )
}

export default FileManager
