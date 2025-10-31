"""
搜索相关工具实现
"""

import asyncio
from typing import Optional
from pydantic import Field
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader

from .base_tools import BaseTool, ToolInput, ToolOutput


class SearchInput(ToolInput):
    """搜索工具输入参数"""
    query: str = Field(description="搜索查询")
    max_results: int = Field(default=5, description="最大结果数量")


class WebScraperInput(ToolInput):
    """网页抓取工具输入参数"""
    url: str = Field(description="网页URL")
    timeout: int = Field(default=30, description="超时时间（秒）")


class SearchTool(BaseTool):
    """搜索工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="search_tool",
            description="使用Tavily搜索引擎进行网络搜索"
        )
        self.api_key = api_key
        self._search_tool = None
    
    async def _initialize_tool(self):
        """初始化搜索工具"""
        if self._search_tool is None:
            self._search_tool = TavilySearchResults(
                max_results=5,
                api_key=self.api_key
            )
    
    async def execute(self, input_data: SearchInput) -> ToolOutput:
        """执行搜索操作"""
        try:
            await self._initialize_tool()
            
            # 执行搜索
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self._search_tool.run({
                    "query": input_data.query,
                    "max_results": input_data.max_results
                })
            )
            
            return ToolOutput(
                success=True,
                result=result,
                error=None
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"搜索失败: {str(e)}"
            )


class WebScraperTool(BaseTool):
    """网页抓取工具"""
    
    def __init__(self):
        super().__init__(
            name="web_scraper_tool",
            description="抓取和解析网页内容"
        )
    
    async def execute(self, input_data: WebScraperInput) -> ToolOutput:
        """执行网页抓取操作"""
        try:
            # 创建网页加载器
            loader = WebBaseLoader(input_data.url)
            
            # 异步加载网页内容
            documents = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: loader.load()
            )
            
            # 提取网页内容
            content = "\n\n".join([doc.page_content for doc in documents])
            meta_info = documents[0].meta_info if documents else {}
            
            result = {
                "content": content,
                "meta_info": meta_info,
                "url": input_data.url
            }
            
            return ToolOutput(
                success=True,
                result=result,
                error=None
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"网页抓取失败: {str(e)}"
            )