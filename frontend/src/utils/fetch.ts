// 封装fetch 跨域 和 baseUrl

import { message } from 'antd'

const baseUrl = 'http://localhost:8000'

export const http = (url: string, options: RequestInit) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  }
  // 合并options的headers
  const mergedOptions = {
    ...options,
    headers: { ...(options?.headers || {}), ...headers }
  }
  return fetch(`${baseUrl}${url}`, mergedOptions)
}
