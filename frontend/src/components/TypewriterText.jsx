import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

/**
 * 打字机效果文本组件
 * 
 * @remarks 实现逐字显示的打字机效果
 * @param {Object} props - 组件属性
 * @param {string} props.text - 要显示的完整文本
 * @param {number} props.speed - 打字速度（毫秒）
 * @param {boolean} props.isStreaming - 是否正在流式输入
 * @param {Function} props.onComplete - 完成回调
 * @returns React组件
 */
function TypewriterText({ text, speed = 30, isStreaming = false, onComplete }) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (!text) {
      setDisplayedText('')
      setCurrentIndex(0)
      return
    }

    // 如果不是流式模式，直接显示全部文本
    if (!isStreaming) {
      setDisplayedText(text)
      setCurrentIndex(text.length)
      onComplete?.()
      return
    }

    // 如果文本变长了，继续打字
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        const nextIndex = currentIndex + 1
        setDisplayedText(text.slice(0, nextIndex))
        setCurrentIndex(nextIndex)
        
        // 如果打字完成，调用回调
        if (nextIndex >= text.length) {
          onComplete?.()
        }
      }, speed)

      return () => clearTimeout(timer)
    }
  }, [text, currentIndex, speed, isStreaming, onComplete])

  // 重置打字机状态
  useEffect(() => {
    if (text !== displayedText && text.length < displayedText.length) {
      setDisplayedText('')
      setCurrentIndex(0)
    }
  }, [text, displayedText])

  return (
    <div className={`typewriter-text ${isStreaming && currentIndex < text.length ? 'typing-cursor' : ''}`}>
      <ReactMarkdown>{displayedText}</ReactMarkdown>
    </div>
  )
}

export default TypewriterText
