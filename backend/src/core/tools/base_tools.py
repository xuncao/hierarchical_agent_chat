"""
基础工具类和工具注册表
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool as LangChainBaseTool
from langchain_core.tools import tool


class ToolInput(BaseModel):
    """工具输入参数基类"""
    pass


class ToolOutput(BaseModel):
    """工具输出结果基类"""
    success: bool = Field(description="操作是否成功")
    result: Optional[Any] = Field(description="操作结果")
    error: Optional[str] = Field(description="错误信息")


class BaseTool(ABC):
    """基础工具类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """执行工具操作"""
        pass
    
    def to_langchain_tool(self) -> LangChainBaseTool:
        """转换为LangChain工具"""
        @tool(self.name, description=self.description)
        async def tool_function(**kwargs):
            input_data = ToolInput(**kwargs)
            result = await self.execute(input_data)
            return result.dict()
        
        return tool_function


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def get_langchain_tools(self) -> List[LangChainBaseTool]:
        """获取所有LangChain工具"""
        return [tool.to_langchain_tool() for tool in self._tools.values()]
    
    def clear(self):
        """清空注册表"""
        self._tools.clear()