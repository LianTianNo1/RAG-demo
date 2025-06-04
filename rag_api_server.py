# -*- coding: utf-8 -*-
"""
RAG API服务器 - 提供标准的Chat API和文件上传接口

@remarks 这是一个基于FastAPI的RAG服务，提供兼容OpenAI格式的聊天接口，
         支持文件上传、智能RAG触发、工具调用展示等功能
@author AI Assistant
@version 2.0
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# FastAPI相关导入
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import asyncio

# 文件监控
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 原有的RAG系统导入
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# --- 全局配置 ---
KNOWLEDGE_BASE_DIR = "./knowledge_base/"  # 知识库文件存储目录
VECTOR_STORE_DIR = "./vector_store/"      # 向量数据库存储目录
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL_NAME = "qwen3:4b"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
API_HOST = "0.0.0.0"
API_PORT = 8000

# --- API数据模型 ---
class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")

class ToolCall(BaseModel):
    """工具调用模型"""
    id: str = Field(..., description="工具调用ID")
    type: str = Field(default="function", description="工具类型")
    function: Dict[str, Any] = Field(..., description="函数调用信息")

class ChatCompletionRequest(BaseModel):
    """聊天完成请求模型"""
    model: str = Field(default="rag-excel", description="模型名称")
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大token数")
    stream: bool = Field(default=False, description="是否流式响应")
    tools: Optional[List[Dict[str, Any]]] = Field(default=None, description="可用工具列表")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(default="auto", description="工具选择策略")

class ChatCompletionResponse(BaseModel):
    """聊天完成响应模型"""
    id: str = Field(..., description="响应ID")
    object: str = Field(default="chat.completion", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[Dict[str, Any]] = Field(..., description="响应选择列表")
    usage: Dict[str, int] = Field(..., description="使用统计")

class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool = Field(..., description="上传是否成功")
    filename: str = Field(..., description="文件名")
    file_id: str = Field(..., description="文件ID")
    message: str = Field(..., description="响应消息")
    file_hash: str = Field(..., description="文件哈希值")

# --- 增强的RAG系统 ---
class EnhancedRAGSystem:
    """
    增强的RAG系统，支持文件监控和智能更新

    @remarks 相比原版增加了以下功能：
             1. 文件变化监控
             2. 向量库缓存和增量更新
             3. 工具调用模拟
             4. 文件级别的查询支持
    """

    def __init__(self, knowledge_base_dir: str, vector_store_dir: str,
                 embedding_model_name: str, llm_model_name: str):
        """
        初始化增强RAG系统

        @param knowledge_base_dir - 知识库文件目录
        @param vector_store_dir - 向量数据库存储目录
        @param embedding_model_name - 嵌入模型名称
        @param llm_model_name - 大语言模型名称
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.vector_store_dir = Path(vector_store_dir)

        # 确保目录存在
        self.knowledge_base_dir.mkdir(exist_ok=True)
        self.vector_store_dir.mkdir(exist_ok=True)

        # 初始化模型
        print(f"正在初始化增强RAG系统...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'}
        )
        self.llm = Ollama(model=llm_model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

        # 向量数据库和文件哈希缓存
        self.vector_store = None
        self.file_hashes = {}  # 文件哈希缓存，用于检测文件变化
        self.last_update_time = None

        # 加载现有的向量数据库（如果存在）
        self._load_existing_vector_store()

        print(f"增强RAG系统初始化完成。")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件的MD5哈希值

        @param file_path - 文件路径
        @returns 文件的MD5哈希值
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"计算文件哈希时出错 {file_path}: {e}")
            return ""

    def _load_existing_vector_store(self):
        """
        加载现有的向量数据库（如果存在）

        @returns 无返回值
        """
        vector_store_path = self.vector_store_dir / "faiss_index"
        if vector_store_path.exists():
            try:
                print("正在加载现有的向量数据库...")
                self.vector_store = FAISS.load_local(
                    str(vector_store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

                # 加载文件哈希缓存
                hash_cache_path = self.vector_store_dir / "file_hashes.json"
                if hash_cache_path.exists():
                    with open(hash_cache_path, 'r', encoding='utf-8') as f:
                        self.file_hashes = json.load(f)

                print(f"成功加载现有向量数据库，包含 {self.vector_store.index.ntotal} 个向量。")
                self.last_update_time = datetime.now()
            except Exception as e:
                print(f"加载现有向量数据库失败: {e}")
                self.vector_store = None

    def _save_vector_store(self):
        """
        保存向量数据库到磁盘

        @returns 无返回值
        """
        if self.vector_store is not None:
            try:
                vector_store_path = self.vector_store_dir / "faiss_index"
                self.vector_store.save_local(str(vector_store_path))

                # 保存文件哈希缓存
                hash_cache_path = self.vector_store_dir / "file_hashes.json"
                with open(hash_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self.file_hashes, f, ensure_ascii=False, indent=2)

                print("向量数据库已保存到磁盘。")
            except Exception as e:
                print(f"保存向量数据库失败: {e}")

    def check_files_changed(self) -> bool:
        """
        检查知识库文件是否有变化

        @returns 如果有文件变化返回True，否则返回False
        """
        current_hashes = {}
        files_changed = False

        # 检查所有Excel文件
        for file_path in self.knowledge_base_dir.glob("*.xlsx"):
            current_hash = self._calculate_file_hash(file_path)
            file_key = str(file_path.relative_to(self.knowledge_base_dir))
            current_hashes[file_key] = current_hash

            # 检查是否是新文件或文件已修改
            if file_key not in self.file_hashes or self.file_hashes[file_key] != current_hash:
                files_changed = True
                print(f"检测到文件变化: {file_key}")

        # 检查是否有文件被删除
        for file_key in self.file_hashes:
            if file_key not in current_hashes:
                files_changed = True
                print(f"检测到文件删除: {file_key}")

        self.file_hashes = current_hashes
        return files_changed

    def _load_excel_documents(self) -> List[Document]:
        """
        从知识库目录加载所有Excel文件

        @returns Document对象列表
        """
        print(f"正在从知识库目录加载Excel文件...")
        all_docs = []

        excel_files = list(self.knowledge_base_dir.glob("*.xlsx"))
        if not excel_files:
            print(f"警告：在知识库目录中未找到任何Excel文件。")
            return []

        for file_path in excel_files:
            print(f"  正在处理文件: {file_path.name}")
            try:
                xls = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, df in xls.items():
                    if not df.empty:
                        sheet_content = ""
                        for index, row in df.iterrows():
                            row_texts = []
                            for col_name, cell_value in row.items():
                                cell_text = str(cell_value).strip()
                                if cell_text and cell_text != 'nan':
                                    row_texts.append(f"{str(col_name).strip()}: {cell_text}")
                            if row_texts:
                                sheet_content += ", ".join(row_texts) + "\n"

                        if sheet_content.strip():
                            doc = Document(
                                page_content=sheet_content.strip(),
                                metadata={
                                    "source_file": file_path.name,
                                    "sheet_name": sheet_name,
                                    "file_path": str(file_path)
                                }
                            )
                            all_docs.append(doc)
            except Exception as e:
                print(f"    处理文件 {file_path.name} 时发生错误: {e}")

        print(f"Excel文件加载完毕，共加载了 {len(all_docs)} 个文档。")
        return all_docs

    def rebuild_vector_store(self) -> bool:
        """
        重新构建向量数据库

        @returns 构建成功返回True，否则返回False
        """
        print("正在重新构建向量数据库...")

        # 1. 加载文档
        documents = self._load_excel_documents()
        if not documents:
            print("没有找到文档，无法构建向量数据库。")
            return False

        # 2. 分割文档
        text_chunks = self.text_splitter.split_documents(documents)
        if not text_chunks:
            print("文档分割失败，无法构建向量数据库。")
            return False

        print(f"文档分割完成，共得到 {len(text_chunks)} 个文本块。")

        # 3. 构建向量数据库
        try:
            self.vector_store = FAISS.from_documents(documents=text_chunks, embedding=self.embeddings)
            self.last_update_time = datetime.now()

            # 保存到磁盘
            self._save_vector_store()

            print(f"向量数据库重建完成，包含 {self.vector_store.index.ntotal} 个向量。")
            return True
        except Exception as e:
            print(f"构建向量数据库时发生错误: {e}")
            return False

    def update_if_needed(self) -> bool:
        """
        如果文件有变化，则更新向量数据库

        @returns 如果进行了更新返回True，否则返回False
        """
        if self.check_files_changed():
            print("检测到文件变化，正在更新向量数据库...")
            return self.rebuild_vector_store()
        return False

    def query_with_tools(self, user_question: str, specific_files: Optional[List[str]] = None, k: int = 3) -> Dict[str, Any]:
        """
        使用工具进行查询，返回包含工具调用信息的结果

        @param user_question - 用户问题
        @param specific_files - 指定查询的文件列表，None表示查询所有文件
        @param k - 检索的文档数量
        @returns 包含答案和工具调用信息的字典
        """
        # 确保向量数据库是最新的
        self.update_if_needed()

        if self.vector_store is None:
            return {
                "answer": "错误：向量数据库未初始化。请先上传一些Excel文件。",
                "tool_calls": [],
                "sources": []
            }

        # 模拟工具调用
        tool_calls = []
        sources = []

        # 1. Excel搜索工具
        search_tool_call = {
            "id": f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "function",
            "function": {
                "name": "excel_search",
                "arguments": {
                    "query": user_question,
                    "files": specific_files or "all",
                    "top_k": k
                }
            }
        }
        tool_calls.append(search_tool_call)

        try:
            # 执行检索
            if specific_files:
                # 如果指定了文件，则过滤检索结果
                retrieved_docs = self.vector_store.similarity_search(user_question, k=k*2)  # 多检索一些，然后过滤
                filtered_docs = []
                for doc in retrieved_docs:
                    if doc.metadata.get("source_file") in specific_files:
                        filtered_docs.append(doc)
                        if len(filtered_docs) >= k:
                            break
                retrieved_docs = filtered_docs
            else:
                retrieved_docs = self.vector_store.similarity_search(user_question, k=k)

            # 收集来源信息
            for doc in retrieved_docs:
                source_info = {
                    "file": doc.metadata.get("source_file", "unknown"),
                    "sheet": doc.metadata.get("sheet_name", "unknown"),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources.append(source_info)

            if not retrieved_docs:
                context_text = "未在指定的Excel文件中找到相关信息。"
            else:
                context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

            # 2. LLM生成工具
            llm_tool_call = {
                "id": f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_llm",
                "type": "function",
                "function": {
                    "name": "llm_generate",
                    "arguments": {
                        "context": context_text[:500] + "..." if len(context_text) > 500 else context_text,
                        "question": user_question,
                        "model": LLM_MODEL_NAME
                    }
                }
            }
            tool_calls.append(llm_tool_call)

            # 构建提示并生成答案
            prompt_template = ChatPromptTemplate.from_template(
                """
                请你扮演一个有用的助手。请根据下面提供的背景信息来回答用户的问题。
                如果背景信息中没有足够的内容来回答问题，请明确说明你无法从提供的信息中找到答案，不要编造。
                请使用中文回答。

                背景信息:
                {context}

                用户问题:
                {question}

                回答:
                """
            )

            rag_chain = prompt_template | self.llm | StrOutputParser()
            answer = rag_chain.invoke({"context": context_text, "question": user_question})

            return {
                "answer": answer,
                "tool_calls": tool_calls,
                "sources": sources
            }

        except Exception as e:
            error_msg = f"查询过程中发生错误: {e}"
            return {
                "answer": error_msg,
                "tool_calls": tool_calls,
                "sources": []
            }

    async def query_with_tools_stream(self, user_question: str, specific_files: Optional[List[str]] = None, k: int = 3):
        """
        使用工具进行流式查询，返回异步生成器

        @param user_question - 用户问题
        @param specific_files - 指定查询的文件列表，None表示查询所有文件
        @param k - 检索的文档数量
        @returns 异步生成器，产生流式响应数据
        """
        # 确保向量数据库是最新的
        self.update_if_needed()

        if self.vector_store is None:
            yield {
                "error": "向量数据库未初始化。请先上传一些Excel文件。",
                "tool_calls": [],
                "sources": []
            }
            return

        # 模拟工具调用
        tool_calls = []
        sources = []

        # 1. Excel搜索工具
        search_tool_call = {
            "id": f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "function",
            "function": {
                "name": "excel_search",
                "arguments": {
                    "query": user_question,
                    "files": specific_files or "all",
                    "top_k": k
                }
            }
        }
        tool_calls.append(search_tool_call)

        # 先发送工具调用信息
        yield {
            "type": "tool_call",
            "tool_call": search_tool_call
        }

        try:
            # 执行检索
            if specific_files:
                retrieved_docs = self.vector_store.similarity_search(user_question, k=k*2)
                filtered_docs = []
                for doc in retrieved_docs:
                    if doc.metadata.get("source_file") in specific_files:
                        filtered_docs.append(doc)
                        if len(filtered_docs) >= k:
                            break
                retrieved_docs = filtered_docs
            else:
                retrieved_docs = self.vector_store.similarity_search(user_question, k=k)

            # 收集来源信息
            for doc in retrieved_docs:
                source_info = {
                    "file": doc.metadata.get("source_file", "unknown"),
                    "sheet": doc.metadata.get("sheet_name", "unknown"),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources.append(source_info)

            # 发送检索结果
            yield {
                "type": "retrieval_result",
                "sources": sources,
                "retrieved_count": len(retrieved_docs)
            }

            if not retrieved_docs:
                context_text = "未在指定的Excel文件中找到相关信息。"
            else:
                context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

            # 2. LLM生成工具
            llm_tool_call = {
                "id": f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_llm",
                "type": "function",
                "function": {
                    "name": "llm_generate",
                    "arguments": {
                        "context": context_text[:500] + "..." if len(context_text) > 500 else context_text,
                        "question": user_question,
                        "model": LLM_MODEL_NAME
                    }
                }
            }
            tool_calls.append(llm_tool_call)

            # 发送LLM工具调用
            yield {
                "type": "tool_call",
                "tool_call": llm_tool_call
            }

            # 构建提示并生成答案
            prompt_template = ChatPromptTemplate.from_template(
                """
                请你扮演一个有用的助手。请根据下面提供的背景信息来回答用户的问题。
                如果背景信息中没有足够的内容来回答问题，请明确说明你无法从提供的信息中找到答案，不要编造。
                请使用中文回答。

                背景信息:
                {context}

                用户问题:
                {question}

                回答:
                """
            )

            rag_chain = prompt_template | self.llm | StrOutputParser()

            # 开始生成答案
            yield {
                "type": "generation_start"
            }

            # 模拟流式生成（因为当前Ollama不支持真正的流式，我们模拟分块发送）
            answer = rag_chain.invoke({"context": context_text, "question": user_question})

            # 将答案分块发送
            words = answer.split()
            chunk_size = 3  # 每次发送3个词

            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if i + chunk_size < len(words):
                    chunk += " "

                yield {
                    "type": "content_chunk",
                    "content": chunk
                }

                # 模拟生成延迟
                await asyncio.sleep(0.1)

            # 发送完成信息
            yield {
                "type": "generation_complete",
                "full_answer": answer,
                "tool_calls": tool_calls,
                "sources": sources
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": f"查询过程中发生错误: {e}",
                "tool_calls": tool_calls,
                "sources": []
            }

# --- 全局RAG系统实例 ---
rag_system = None

def get_rag_system() -> EnhancedRAGSystem:
    """
    获取全局RAG系统实例

    @returns EnhancedRAGSystem实例
    """
    global rag_system
    if rag_system is None:
        rag_system = EnhancedRAGSystem(
            knowledge_base_dir=KNOWLEDGE_BASE_DIR,
            vector_store_dir=VECTOR_STORE_DIR,
            embedding_model_name=EMBEDDING_MODEL_NAME,
            llm_model_name=LLM_MODEL_NAME
        )
    return rag_system

# --- FastAPI应用初始化 ---
app = FastAPI(
    title="RAG Excel API",
    description="基于Excel文件的检索增强生成API服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API端点 ---

@app.get("/")
async def root():
    """根端点，返回API信息"""
    return {
        "message": "RAG Excel API服务正在运行",
        "version": "2.0.0",
        "docs": "/docs",
        "web_demo": "/web_demo.html",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "upload": "/v1/files/upload",
            "health": "/health"
        }
    }

@app.get("/web_demo.html")
async def web_demo():
    """提供Web演示界面"""
    from fastapi.responses import FileResponse
    import os

    web_demo_path = os.path.join(os.path.dirname(__file__), "web_demo.html")
    if os.path.exists(web_demo_path):
        return FileResponse(web_demo_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Web演示界面文件未找到")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    rag = get_rag_system()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "vector_store_ready": rag.vector_store is not None,
        "last_update": rag.last_update_time.isoformat() if rag.last_update_time else None,
        "knowledge_base_files": len(list(Path(KNOWLEDGE_BASE_DIR).glob("*.xlsx")))
    }

@app.post("/v1/files/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="要上传的Excel文件")
):
    """
    上传Excel文件到知识库

    @param file - 上传的Excel文件
    @returns 上传结果信息
    """
    # 检查文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="只支持Excel文件格式 (.xlsx, .xls)"
        )

    try:
        # 确保知识库目录存在
        knowledge_base_path = Path(KNOWLEDGE_BASE_DIR)
        knowledge_base_path.mkdir(exist_ok=True)

        # 保存文件
        file_path = knowledge_base_path / file.filename
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        # 计算文件哈希
        file_hash = hashlib.md5(content).hexdigest()

        # 生成文件ID
        file_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash[:8]}"

        # 在后台任务中更新向量数据库
        background_tasks.add_task(update_vector_store_background)

        return FileUploadResponse(
            success=True,
            filename=file.filename,
            file_id=file_id,
            message=f"文件 {file.filename} 上传成功，正在后台更新知识库...",
            file_hash=file_hash
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )

async def update_vector_store_background():
    """
    后台任务：更新向量数据库
    """
    try:
        rag = get_rag_system()
        rag.update_if_needed()
        print("后台向量数据库更新完成。")
    except Exception as e:
        print(f"后台更新向量数据库失败: {e}")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    聊天完成接口，兼容OpenAI格式，支持流式和非流式响应

    @param request - 聊天请求
    @returns 聊天响应或流式响应
    """
    # 如果请求流式响应
    if request.stream:
        return StreamingResponse(
            generate_stream_response(request),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

    # 非流式响应（原有逻辑）
    try:
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="未找到用户消息"
            )

        # 检查是否指定了特定文件（从消息中解析）
        specific_files = None
        # 这里可以添加解析逻辑，比如检查消息中是否包含 "在文件X中" 这样的指令

        # 使用RAG系统查询
        rag = get_rag_system()
        result = rag.query_with_tools(user_message, specific_files)

        # 构建响应
        response_id = f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        created_timestamp = int(datetime.now().timestamp())

        # 构建工具调用信息（如果有）
        tool_calls_data = []
        if result.get("tool_calls"):
            for tool_call in result["tool_calls"]:
                tool_calls_data.append({
                    "id": tool_call["id"],
                    "type": tool_call["type"],
                    "function": {
                        "name": tool_call["function"]["name"],
                        "arguments": json.dumps(tool_call["function"]["arguments"], ensure_ascii=False)
                    }
                })

        # 构建消息内容
        message_content = result["answer"]

        # 如果有来源信息，添加到消息末尾
        if result.get("sources"):
            message_content += "\n\n📚 **信息来源:**\n"
            for i, source in enumerate(result["sources"], 1):
                message_content += f"{i}. 文件: {source['file']}, 工作表: {source['sheet']}\n"

        choice = {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": message_content,
                "tool_calls": tool_calls_data if tool_calls_data else None
            },
            "finish_reason": "stop"
        }

        # 移除None值
        if choice["message"]["tool_calls"] is None:
            del choice["message"]["tool_calls"]

        return ChatCompletionResponse(
            id=response_id,
            created=created_timestamp,
            model=request.model,
            choices=[choice],
            usage={
                "prompt_tokens": len(user_message.split()),  # 简单估算
                "completion_tokens": len(result["answer"].split()),  # 简单估算
                "total_tokens": len(user_message.split()) + len(result["answer"].split())
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"聊天处理失败: {str(e)}"
        )

async def generate_stream_response(request: ChatCompletionRequest):
    """
    生成流式响应的异步生成器

    @param request - 聊天请求
    @returns 异步生成器，产生SSE格式的数据
    """
    try:
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            yield f"data: {json.dumps({'error': '未找到用户消息'}, ensure_ascii=False)}\n\n"
            return

        # 检查是否指定了特定文件
        specific_files = None

        # 使用RAG系统进行流式查询
        rag = get_rag_system()

        response_id = f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        created_timestamp = int(datetime.now().timestamp())

        # 发送初始响应
        initial_response = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created_timestamp,
            "model": request.model,
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(initial_response, ensure_ascii=False)}\n\n"

        # 流式处理
        full_content = ""
        tool_calls_data = []
        sources_data = []

        async for chunk in rag.query_with_tools_stream(user_message, specific_files):
            chunk_type = chunk.get("type")

            if chunk_type == "tool_call":
                # 发送工具调用信息
                tool_call = chunk["tool_call"]
                tool_calls_data.append({
                    "id": tool_call["id"],
                    "type": tool_call["type"],
                    "function": {
                        "name": tool_call["function"]["name"],
                        "arguments": json.dumps(tool_call["function"]["arguments"], ensure_ascii=False)
                    }
                })

                # 发送工具调用块
                tool_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "tool_calls": [{
                                "index": len(tool_calls_data) - 1,
                                "id": tool_call["id"],
                                "type": tool_call["type"],
                                "function": {
                                    "name": tool_call["function"]["name"],
                                    "arguments": json.dumps(tool_call["function"]["arguments"], ensure_ascii=False)
                                }
                            }]
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(tool_chunk, ensure_ascii=False)}\n\n"

            elif chunk_type == "retrieval_result":
                # 保存来源信息
                sources_data = chunk["sources"]

                # 发送检索结果信息
                retrieval_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "content": f"🔍 检索到 {chunk['retrieved_count']} 个相关文档\n"
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(retrieval_chunk, ensure_ascii=False)}\n\n"

            elif chunk_type == "generation_start":
                # 发送生成开始信息
                start_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": "🤖 正在生成回答...\n\n"},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(start_chunk, ensure_ascii=False)}\n\n"

            elif chunk_type == "content_chunk":
                # 发送内容块
                content = chunk["content"]
                full_content += content

                content_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": content},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(content_chunk, ensure_ascii=False)}\n\n"

            elif chunk_type == "generation_complete":
                # 添加来源信息
                if sources_data:
                    sources_text = "\n\n📚 **信息来源:**\n"
                    for i, source in enumerate(sources_data, 1):
                        sources_text += f"{i}. 文件: {source['file']}, 工作表: {source['sheet']}\n"

                    sources_chunk = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created_timestamp,
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": sources_text},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(sources_chunk, ensure_ascii=False)}\n\n"

                # 发送完成块
                final_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"

            elif chunk_type == "error":
                # 发送错误信息
                error_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": f"❌ 错误: {chunk['error']}"},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"

        # 发送结束标记
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_chunk = {
            "id": f"chatcmpl-error-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "delta": {"content": f"❌ 系统错误: {str(e)}"},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

@app.get("/v1/files/list")
async def list_files():
    """
    列出知识库中的所有文件

    @returns 文件列表信息
    """
    try:
        knowledge_base_path = Path(KNOWLEDGE_BASE_DIR)
        files = []

        for file_path in knowledge_base_path.glob("*.xlsx"):
            file_stat = file_path.stat()
            file_hash = ""
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
            except Exception:
                pass

            files.append({
                "filename": file_path.name,
                "size": file_stat.st_size,
                "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "file_hash": file_hash
            })

        return {
            "files": files,
            "total_count": len(files),
            "knowledge_base_dir": str(knowledge_base_path.absolute())
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文件列表失败: {str(e)}"
        )

@app.delete("/v1/files/{filename}")
async def delete_file(filename: str, background_tasks: BackgroundTasks):
    """
    删除知识库中的指定文件

    @param filename - 要删除的文件名
    @returns 删除结果
    """
    try:
        file_path = Path(KNOWLEDGE_BASE_DIR) / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"文件 {filename} 不存在"
            )

        if not file_path.suffix.lower() in ['.xlsx', '.xls']:
            raise HTTPException(
                status_code=400,
                detail="只能删除Excel文件"
            )

        # 删除文件
        file_path.unlink()

        # 在后台更新向量数据库
        background_tasks.add_task(update_vector_store_background)

        return {
            "success": True,
            "message": f"文件 {filename} 删除成功，正在后台更新知识库...",
            "filename": filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文件失败: {str(e)}"
        )

@app.post("/v1/vector_store/rebuild")
async def rebuild_vector_store(background_tasks: BackgroundTasks):
    """
    手动重建向量数据库

    @returns 重建任务状态
    """
    try:
        # 在后台任务中重建向量数据库
        background_tasks.add_task(rebuild_vector_store_background)

        return {
            "success": True,
            "message": "向量数据库重建任务已启动，请稍后查看状态",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动重建任务失败: {str(e)}"
        )

async def rebuild_vector_store_background():
    """
    后台任务：强制重建向量数据库
    """
    try:
        rag = get_rag_system()
        success = rag.rebuild_vector_store()
        if success:
            print("后台向量数据库重建完成。")
        else:
            print("后台向量数据库重建失败。")
    except Exception as e:
        print(f"后台重建向量数据库失败: {e}")

# --- 启动事件 ---
@app.on_event("startup")
async def startup_event():
    """
    应用启动时的初始化事件
    """
    print("🚀 RAG Excel API服务启动中...")

    # 确保必要的目录存在
    Path(KNOWLEDGE_BASE_DIR).mkdir(exist_ok=True)
    Path(VECTOR_STORE_DIR).mkdir(exist_ok=True)

    # 初始化RAG系统
    rag = get_rag_system()

    # 如果知识库中有文件但没有向量数据库，则构建
    knowledge_files = list(Path(KNOWLEDGE_BASE_DIR).glob("*.xlsx"))
    if knowledge_files and rag.vector_store is None:
        print("检测到知识库文件但向量数据库不存在，正在构建...")
        rag.rebuild_vector_store()

    print("✅ RAG Excel API服务启动完成！")
    print(f"📁 知识库目录: {Path(KNOWLEDGE_BASE_DIR).absolute()}")
    print(f"🗄️ 向量库目录: {Path(VECTOR_STORE_DIR).absolute()}")
    print(f"📊 当前知识库文件数: {len(knowledge_files)}")
    print(f"🔗 API文档: http://{API_HOST}:{API_PORT}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时的清理事件
    """
    print("🛑 RAG Excel API服务正在关闭...")

    # 保存向量数据库
    rag = get_rag_system()
    if rag.vector_store is not None:
        rag._save_vector_store()
        print("💾 向量数据库已保存")

    print("✅ RAG Excel API服务已安全关闭")

# --- 主程序入口 ---
if __name__ == "__main__":
    import uvicorn

    print("🎯 启动RAG Excel API服务器...")
    print(f"📍 服务地址: http://{API_HOST}:{API_PORT}")
    print(f"📖 API文档: http://{API_HOST}:{API_PORT}/docs")
    print(f"🔄 ReDoc文档: http://{API_HOST}:{API_PORT}/redoc")

    uvicorn.run(
        "rag_api_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,  # 开发模式下启用热重载
        log_level="info"
    )
