import React from 'react'
import { Space, Tag, Tooltip, Typography } from 'antd'
import { 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import './SystemStatus.css'

const { Text } = Typography

/**
 * 系统状态组件
 * 
 * @remarks 显示系统在线状态、向量库状态、文件数量等信息
 * @param {Object} props - 组件属性
 * @param {Object} props.status - 系统状态对象
 * @param {boolean} props.status.online - 系统是否在线
 * @param {boolean} props.status.vectorStoreReady - 向量库是否就绪
 * @param {number} props.status.fileCount - 文件数量
 * @param {string} props.status.lastUpdate - 最后更新时间
 * @returns React组件
 */
function SystemStatus({ status }) {
  const { online, vectorStoreReady, fileCount, lastUpdate } = status

  // 格式化最后更新时间
  const formatLastUpdate = (timestamp) => {
    if (!timestamp) return '未知'
    
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return '刚刚'
    if (diffMins < 60) return `${diffMins}分钟前`
    if (diffHours < 24) return `${diffHours}小时前`
    if (diffDays < 7) return `${diffDays}天前`
    
    return date.toLocaleDateString('zh-CN')
  }

  // 获取系统状态标签
  const getSystemStatusTag = () => {
    if (!online) {
      return (
        <Tag 
          icon={<CloseCircleOutlined />} 
          color="error"
          className="status-tag"
        >
          离线
        </Tag>
      )
    }

    if (!vectorStoreReady) {
      return (
        <Tag 
          icon={<ExclamationCircleOutlined />} 
          color="warning"
          className="status-tag"
        >
          未就绪
        </Tag>
      )
    }

    return (
      <Tag 
        icon={<CheckCircleOutlined />} 
        color="success"
        className="status-tag"
      >
        正常
      </Tag>
    )
  }

  // 获取向量库状态标签
  const getVectorStoreTag = () => {
    if (!online) {
      return (
        <Tag 
          icon={<CloseCircleOutlined />} 
          color="default"
          size="small"
        >
          离线
        </Tag>
      )
    }

    if (vectorStoreReady) {
      return (
        <Tag 
          icon={<DatabaseOutlined />} 
          color="success"
          size="small"
        >
          就绪
        </Tag>
      )
    }

    return (
      <Tag 
        icon={<ExclamationCircleOutlined />} 
        color="warning"
        size="small"
      >
        未就绪
      </Tag>
    )
  }

  return (
    <div className="system-status">
      <Space size="middle" className="status-items">
        {/* 系统状态 */}
        <Tooltip 
          title={
            <div>
              <div>系统状态: {online ? '在线' : '离线'}</div>
              <div>向量库: {vectorStoreReady ? '就绪' : '未就绪'}</div>
              {lastUpdate && (
                <div>最后更新: {formatLastUpdate(lastUpdate)}</div>
              )}
            </div>
          }
          placement="bottomRight"
        >
          <div className="status-item">
            {getSystemStatusTag()}
          </div>
        </Tooltip>

        {/* 向量库状态 */}
        <Tooltip 
          title={`向量数据库${vectorStoreReady ? '已就绪，可以进行问答' : '未就绪，请先上传Excel文件'}`}
          placement="bottom"
        >
          <div className="status-item">
            {getVectorStoreTag()}
          </div>
        </Tooltip>

        {/* 文件数量 */}
        <Tooltip 
          title={`知识库中共有 ${fileCount} 个Excel文件`}
          placement="bottom"
        >
          <div className="status-item">
            <Tag 
              icon={<FileTextOutlined />} 
              color="blue"
              size="small"
            >
              {fileCount} 文件
            </Tag>
          </div>
        </Tooltip>

        {/* 最后更新时间 */}
        {lastUpdate && (
          <Tooltip 
            title={`向量库最后更新时间: ${new Date(lastUpdate).toLocaleString('zh-CN')}`}
            placement="bottomLeft"
          >
            <div className="status-item">
              <Tag 
                icon={<ClockCircleOutlined />} 
                color="default"
                size="small"
              >
                {formatLastUpdate(lastUpdate)}
              </Tag>
            </div>
          </Tooltip>
        )}
      </Space>
    </div>
  )
}

export default SystemStatus
