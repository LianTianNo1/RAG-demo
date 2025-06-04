# -*- coding: utf-8 -*-
"""
Excel RAG系统 - 从Excel文件中检索信息并使用大语言模型回答问题

@remarks 这是一个基于检索增强生成(RAG)的系统，能够读取Excel文件内容，
         构建向量数据库，并结合本地Ollama大语言模型来回答用户问题
@author AI Assistant
@version 1.0
"""

# 导入必要的库
import os
import glob
import pandas as pd

# Langchain库，用于构建RAG流程
from langchain_community.embeddings import HuggingFaceEmbeddings  # 用于将文本转换为向量
from langchain_community.vectorstores import FAISS              # 用于存储和检索向量的数据库
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 用于将长文本切分成小块
from langchain_community.llms import Ollama                     # 用于与Ollama大语言模型交互
from langchain_core.prompts import ChatPromptTemplate           # 用于创建提示模板
from langchain_core.output_parsers import StrOutputParser       # 用于解析模型输出
from langchain_core.documents import Document                   # Langchain中文档对象的基本单元

# --- 全局配置 ---
# Excel文件所在的目录路径
EXCEL_FILES_DIRECTORY = "./data/"
# 使用的句子嵌入模型的名称 (HuggingFace上的模型)
# paraphrase-multilingual-MiniLM-L12-v2 是一个不错的多语言模型
# 如果主要处理中文，也可以考虑 'shibing624/text2vec-base-chinese'
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# 使用的Ollama大语言模型的名称 (需要预先通过 ollama pull <model_name> 下载)
# 例如 'qwen2:7b-instruct', 'llama3', 'mistral' 等
LLM_MODEL_NAME = "qwen3:4b"  # 推荐使用这个，中文效果好
# LLM_MODEL_NAME = "qwen2:7b-instruct"  # 推荐使用这个，中文效果好
# 文本切分时，每个块的目标大小
CHUNK_SIZE = 500
# 文本切分时，块之间的重叠大小
CHUNK_OVERLAP = 50


class ExcelRAGSystem:
    """
    一个简单的RAG系统，用于从Excel文件中检索信息并使用LLM回答问题

    @remarks 该系统实现了完整的RAG流程：
             1. 从Excel文件加载数据
             2. 将数据转换为文本并分割
             3. 使用嵌入模型生成向量
             4. 构建FAISS向量数据库
             5. 根据用户问题检索相关信息
             6. 使用Ollama大语言模型生成答案
    """

    def __init__(self, excel_dir_path, embedding_model_name, llm_model_name):
        """
        初始化RAG系统

        @param excel_dir_path - 存放Excel文件的目录路径
        @param embedding_model_name - HuggingFace上嵌入模型的名称
        @param llm_model_name - Ollama中大语言模型的名称
        @returns 无返回值
        @example
        ```python
        rag_system = ExcelRAGSystem(
            excel_dir_path="./data/",
            embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            llm_model_name="qwen3:4b"
        )
        ```
        """
        print(f"RAG系统初始化开始...")
        self.excel_dir_path = excel_dir_path  # 保存Excel目录路径

        # 1. 初始化嵌入模型
        #    这个模型会把文本转换成计算机能理解的数字列表（向量）
        #    device='cpu' 表示使用CPU进行计算，如果有GPU可以设置为 'cuda'
        print(f"  1. 正在加载嵌入模型: {embedding_model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'}  # 如果有GPU，可以改成 'cuda'
        )
        print(f"  嵌入模型加载完毕。")

        # 2. 初始化大语言模型 (LLM)
        #    这里使用Ollama在本机运行的大模型
        print(f"  2. 正在连接Ollama大语言模型: {llm_model_name}")
        self.llm = Ollama(model=llm_model_name)
        print(f"  Ollama大语言模型连接成功。")

        # 3. 初始化文本分割器
        #    用于将较长的文本内容切分成适合模型处理的小块
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,          # 每个文本块的最大字符数
            chunk_overlap=CHUNK_OVERLAP,    # 文本块之间的重叠字符数，有助于保持上下文联系
            length_function=len,            # 使用Python内置的len函数计算长度
            is_separator_regex=False,       # 不使用正则表达式作为分隔符
        )
        print(f"  文本分割器初始化完毕。")

        # 4. 初始化向量数据库 (Vector Store)
        #    这里先设置为None，在setup()方法中加载数据后创建
        self.vector_store = None
        print(f"RAG系统初始化完成。\n")

    def _load_excel_documents(self):
        """
        从指定目录加载所有Excel文件，并将每个工作表的内容转换为Langchain的Document对象

        @returns 包含所有Excel工作表内容的Document对象列表
        @example
        ```python
        documents = self._load_excel_documents()
        print(f"加载了 {len(documents)} 个文档")
        ```
        """
        print(f"开始从 '{self.excel_dir_path}' 目录加载Excel文件...")
        all_docs = []  # 用于存储所有从Excel中提取的文档片段

        # glob.glob会找到所有匹配路径模式的文件
        #  os.path.join用于正确地组合目录和文件名
        #  f"{self.excel_dir_path}/*.xlsx" 表示查找目录下所有.xlsx文件
        excel_files = glob.glob(os.path.join(self.excel_dir_path, "*.xlsx"))

        if not excel_files:
            print(f"警告：在目录 '{self.excel_dir_path}' 中未找到任何 .xlsx 文件。")
            return []

        for file_path in excel_files:
            print(f"  正在处理文件: {file_path}")
            try:
                # pandas.read_excel(None) 会读取所有工作表，返回一个字典，键是工作表名，值是DataFrame
                xls = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, df in xls.items():
                    print(f"    正在处理工作表: {sheet_name}")
                    # 将DataFrame转换为文本字符串
                    # df.empty检查工作表是否为空
                    if not df.empty:
                        # 将整个工作表转换为一个字符串，每行数据用换行符分隔
                        # 并且在前面加上列名，使内容更易理解
                        # 示例："列名1: 值A, 列名2: 值B\n列名1: 值C, 列名2: 值D"
                        sheet_content = ""
                        for index, row in df.iterrows():  # 遍历DataFrame的每一行
                            row_texts = []
                            for col_name, cell_value in row.items():  # 遍历当前行的每个单元格
                                # 确保单元格内容是字符串，并去除首尾空格
                                cell_text = str(cell_value).strip()
                                if cell_text:  # 如果单元格内容不为空
                                    row_texts.append(f"{str(col_name).strip()}: {cell_text}")
                            if row_texts:  # 如果当前行有内容
                                sheet_content += ", ".join(row_texts) + "\n"

                        if sheet_content.strip():  # 如果工作表内容不为空
                            # 创建Langchain的Document对象
                            # page_content是文本内容
                            # metadata是元数据，有助于后续筛选或理解来源
                            doc = Document(
                                page_content=sheet_content.strip(),
                                metadata={"source_file": os.path.basename(file_path), "sheet_name": sheet_name}
                            )
                            all_docs.append(doc)
                        else:
                            print(f"      工作表 '{sheet_name}' 内容为空，已跳过。")
                    else:
                        print(f"      工作表 '{sheet_name}' 为空，已跳过。")

            except Exception as e:
                print(f"    处理文件 {file_path} 时发生错误: {e}")

        print(f"Excel文件加载完毕，共加载了 {len(all_docs)} 个文档（每个工作表算一个文档）。\n")
        return all_docs

    def _split_documents(self, documents):
        """
        将加载的文档分割成更小的文本块

        @param documents - 需要分割的Document对象列表
        @returns 分割后的文本块列表
        @example
        ```python
        split_docs = self._split_documents(documents)
        print(f"分割得到 {len(split_docs)} 个文本块")
        ```
        """
        if not documents:
            print("没有文档可供分割。")
            return []

        print(f"开始分割 {len(documents)} 个文档...")
        # 使用之前初始化的text_splitter来分割文档
        split_docs = self.text_splitter.split_documents(documents)
        print(f"文档分割完成，共得到 {len(split_docs)} 个文本块。\n")
        return split_docs

    def _build_vector_store(self, text_chunks):
        """
        使用文本块和嵌入模型构建FAISS向量数据库

        @param text_chunks - 文本块列表
        @returns 无返回值，但会设置self.vector_store
        @example
        ```python
        self._build_vector_store(text_chunks)
        if self.vector_store:
            print("向量数据库构建成功")
        ```
        """
        if not text_chunks:
            print("没有文本块可用于构建向量数据库。系统将无法进行检索。")
            self.vector_store = None
            return

        print(f"开始使用 {len(text_chunks)} 个文本块构建FAISS向量数据库...")
        # FAISS.from_documents会为每个文本块生成嵌入向量，并存储它们
        self.vector_store = FAISS.from_documents(documents=text_chunks, embedding=self.embeddings)
        print(f"FAISS向量数据库构建完成。\n")

    def setup(self):
        """
        执行RAG系统的所有设置步骤：加载数据、分割文本、构建向量库

        @returns 无返回值
        @example
        ```python
        rag_system = ExcelRAGSystem(...)
        rag_system.setup()  # 完成所有初始化工作
        ```
        """
        print("--- RAG系统设置流程开始 ---")
        # 1. 加载Excel数据为文档
        documents = self._load_excel_documents()
        if not documents:
            print("未能从Excel加载任何数据，RAG系统设置中止。")
            print("--- RAG系统设置流程结束 ---\n")
            return

        # 2. 分割文档为文本块
        text_chunks = self._split_documents(documents)
        if not text_chunks:
            print("未能将文档分割成文本块，RAG系统设置中止。")
            print("--- RAG系统设置流程结束 ---\n")
            return

        # 3. 构建向量数据库
        self._build_vector_store(text_chunks)
        print("--- RAG系统设置流程结束 ---\n")

    def query(self, user_question, k=3):
        """
        接收用户问题，检索相关信息，并让LLM生成答案

        @param user_question - 用户提出的问题
        @param k - 从向量数据库中检索最相关的k个文本块
        @returns LLM生成的答案字符串
        @example
        ```python
        answer = rag_system.query("张三在哪个部门？")
        print(f"答案: {answer}")
        ```
        """
        if self.vector_store is None:
            return "错误：向量数据库尚未初始化。请先运行setup()方法。"
        if not user_question:
            return "请输入一个问题。"

        print(f"收到用户问题: \"{user_question}\"")

        # 1. 知识检索 (Retrieval)
        #    使用向量数据库的similarity_search方法找到与问题最相似的k个文本块
        print(f"  1. 正在从向量数据库中检索相关的 {k} 个文本块...")
        try:
            retrieved_docs = self.vector_store.similarity_search(user_question, k=k)
        except Exception as e:
            return f"在向量数据库中检索时发生错误: {e}"

        if not retrieved_docs:
            print("  未能从向量数据库中检索到相关信息。")
            context_text = "未在提供的Excel文件中找到相关信息。"
        else:
            print(f"  成功检索到 {len(retrieved_docs)} 个文本块。")
            # 将检索到的文本块内容连接起来，作为LLM的上下文背景
            context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
            print(f"  组合的上下文信息预览:\n{context_text[:500]}...\n")  # 打印前500个字符预览

        # 2. 构建提示 (Prompt Engineering)
        #    创建一个包含上下文和问题的提示，引导LLM回答
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

        # 3. 生成答案 (Generation)
        #    使用Langchain Expression Language (LCEL) 创建一个处理链
        #    这个链将：获取提示 -> 传递给LLM -> 解析LLM的输出为字符串
        rag_chain = prompt_template | self.llm | StrOutputParser()

        print(f"  2. 正在将问题和上下文发送给大语言模型 ({LLM_MODEL_NAME})...")
        # 调用链，传入上下文和问题
        try:
            answer = rag_chain.invoke({"context": context_text, "question": user_question})
            print(f"  3. 大语言模型已生成回答。")
            return answer
        except Exception as e:
            print(f"  调用大语言模型时发生错误: {e}")
            return "抱歉，在尝试生成答案时遇到了一个内部错误。"


def test_rag_excel_system():
    """
    测试ExcelRAGSystem的功能

    @returns 无返回值
    @example
    ```python
    test_rag_excel_system()  # 运行完整的测试流程
    ```
    """
    print("--- 开始测试Excel RAG系统 ---")

    # 0. 准备测试数据 (如果测试数据目录不存在，则创建)
    test_data_dir = "./test_data_temp/"
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir)
        print(f"创建了临时测试数据目录: {test_data_dir}")

    # 创建一个示例Excel文件用于测试
    sample_excel_path = os.path.join(test_data_dir, "test_employees.xlsx")
    test_data = {
        "员工表": pd.DataFrame({
            'ID': [1, 2, 3, 4],
            '姓名': ['赵一', '钱二', '孙三', '李四'],
            '部门': ['研发部', '市场部', '研发部', '财务部'],
            '薪资': [15000, 12000, 18000, 10000]
        }),
        "项目表": pd.DataFrame({
            '项目名': ['项目X', '项目Y'],
            '负责人': ['孙三', '钱二'],
            '状态': ['进行中', '已完成']
        })
    }
    # 使用ExcelWriter将多个DataFrame写入同一个Excel文件的不同sheet
    with pd.ExcelWriter(sample_excel_path, engine='openpyxl') as writer:
        for sheet_name, df_data in test_data.items():
            df_data.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"创建了测试Excel文件: {sample_excel_path}")

    # 1. 初始化RAG系统
    #    注意：这里我们使用测试数据目录 test_data_dir
    rag_system = ExcelRAGSystem(
        excel_dir_path=test_data_dir,  # 使用临时测试目录
        embedding_model_name=EMBEDDING_MODEL_NAME,
        llm_model_name=LLM_MODEL_NAME
    )

    # 2. 设置RAG系统 (加载数据、构建向量库)
    rag_system.setup()

    # 3. 提问并获取答案
    if rag_system.vector_store is None:
        print("\n测试中止：向量数据库未成功构建，无法进行提问。")
        print("请检查之前的日志输出，确认Ollama服务是否运行，模型是否已下载，以及Excel文件是否正确加载。")
    else:
        questions = [
            "孙三在哪个部门？他的薪资是多少？",
            "项目X的负责人是谁？",
            "市场部有哪些员工？",
            "有没有关于'王五'的信息？"  # 预期：无法找到
        ]

        for q_idx, question in enumerate(questions):
            print(f"\n--- 测试问题 {q_idx + 1} ---")
            print(f"用户问题: {question}")
            answer = rag_system.query(question)
            print(f"系统回答: {answer}")

    # 4. 清理测试数据 (可选)
    try:
        os.remove(sample_excel_path)
        os.rmdir(test_data_dir)
        print(f"\n已清理临时测试数据目录和文件: {test_data_dir}")
    except OSError as e:
        print(f"\n清理测试数据时出错: {e} (可能是因为目录非空或文件被占用)")

    print("--- Excel RAG系统测试结束 ---")


# --- 主程序入口 ---
if __name__ == "__main__":
    # 运行测试函数
    test_rag_excel_system()

    # 如果想直接使用 'data/' 目录下的Excel文件进行交互式问答，可以取消以下代码的注释：
    print("\n--- 启动交互式RAG问答系统 (基于 './data/' 目录) ---")
    print(f"确保你的Excel文件放在 '{EXCEL_FILES_DIRECTORY}' 目录下。")
    print(f"确保Ollama服务正在运行，并且模型 '{LLM_MODEL_NAME}' 已通过 'ollama pull {LLM_MODEL_NAME}' 下载。")

    # 1. 初始化RAG系统 (使用全局配置的EXCEL_FILES_DIRECTORY)
    main_rag_system = ExcelRAGSystem(
        excel_dir_path=EXCEL_FILES_DIRECTORY,
        embedding_model_name=EMBEDDING_MODEL_NAME,
        llm_model_name=LLM_MODEL_NAME
    )

    # 2. 设置RAG系统
    main_rag_system.setup()

    # 3. 进入问答循环
    if main_rag_system.vector_store is None:
        print("\n交互式问答中止：向量数据库未成功构建。")
        print("请检查之前的日志输出，确认Ollama服务是否运行，模型是否已下载，以及Excel文件是否正确加载。")
    else:
        print("\n可以开始提问了。输入 '退出' 来结束程序。")
        while True:
            user_input = input("请输入你的问题: ")
            if user_input.lower() == '退出':
                print("感谢使用，再见！")
                break
            if not user_input.strip():
                print("问题不能为空，请重新输入。")
                continue

            answer = main_rag_system.query(user_input)
            print(f"回答: {answer}\n")
