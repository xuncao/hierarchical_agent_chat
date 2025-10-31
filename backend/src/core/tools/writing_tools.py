"""
文档写作相关工具实现
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from pydantic import Field
from langchain_community.tools import PythonREPLTool

from .base_tools import BaseTool, ToolInput, ToolOutput


class DocumentWriterInput(ToolInput):
    """文档写作工具输入参数"""
    content: str = Field(description="文档内容")
    file_path: Optional[str] = Field(default=None, description="文件保存路径")
    format: str = Field(default="markdown", description="文档格式")


class NoteTakingInput(ToolInput):
    """大纲制定工具输入参数"""
    topic: str = Field(description="主题")
    content: str = Field(description="内容")
    structure: Optional[Dict[str, Any]] = Field(default=None, description="大纲结构")


class ChartGeneratorInput(ToolInput):
    """图表生成工具输入参数"""
    data: Dict[str, Any] = Field(description="图表数据")
    chart_type: str = Field(description="图表类型（bar, line, pie等）")
    title: Optional[str] = Field(default=None, description="图表标题")


class DocumentWriterTool(BaseTool):
    """文档写作工具"""
    
    def __init__(self):
        super().__init__(
            name="document_writer_tool",
            description="生成和编辑文档内容"
        )
    
    async def execute(self, input_data: DocumentWriterInput) -> ToolOutput:
        """执行文档写作操作"""
        try:
            result = {
                "content": input_data.content,
                "format": input_data.format,
                "file_path": input_data.file_path
            }
            
            # 如果指定了文件路径，保存到文件
            if input_data.file_path:
                os.makedirs(os.path.dirname(input_data.file_path), exist_ok=True)
                with open(input_data.file_path, 'w', encoding='utf-8') as f:
                    f.write(input_data.content)
                result["saved"] = True
            
            return ToolOutput(
                success=True,
                result=result,
                error=None
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"文档写作失败: {str(e)}"
            )


class NoteTakingTool(BaseTool):
    """大纲制定工具"""
    
    def __init__(self):
        super().__init__(
            name="note_taking_tool",
            description="创建文档大纲和结构"
        )
    
    async def execute(self, input_data: NoteTakingInput) -> ToolOutput:
        """执行大纲制定操作"""
        try:
            # 生成大纲结构
            if not input_data.structure:
                structure = {
                    "title": input_data.topic,
                    "sections": [
                        {"title": "概述", "content": input_data.content[:200] + "..."},
                        {"title": "详细内容", "content": input_data.content}
                    ]
                }
            else:
                structure = input_data.structure
            
            result = {
                "topic": input_data.topic,
                "structure": structure,
                "summary": input_data.content[:500] + "..." if len(input_data.content) > 500 else input_data.content
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
                error=f"大纲制定失败: {str(e)}"
            )


class ChartGeneratorTool(BaseTool):
    """图表生成工具"""
    
    def __init__(self):
        super().__init__(
            name="chart_generator_tool",
            description="生成数据图表"
        )
        self._python_repl = None
    
    async def _initialize_tool(self):
        """初始化Python REPL工具"""
        if self._python_repl is None:
            self._python_repl = PythonREPLTool()
    
    async def execute(self, input_data: ChartGeneratorInput) -> ToolOutput:
        """执行图表生成操作"""
        try:
            await self._initialize_tool()
            
            # 生成Python代码来创建图表
            chart_code = self._generate_chart_code(input_data)
            
            # 执行Python代码
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self._python_repl.run(chart_code)
            )
            
            chart_result = {
                "chart_type": input_data.chart_type,
                "title": input_data.title,
                "data": input_data.data,
                "code": chart_code,
                "execution_result": result
            }
            
            return ToolOutput(
                success=True,
                result=chart_result,
                error=None
            )
            
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"图表生成失败: {str(e)}"
            )
    
    def _generate_chart_code(self, input_data: ChartGeneratorInput) -> str:
        """生成图表代码"""
        data_json = json.dumps(input_data.data, ensure_ascii=False)
        
        code = f"""
import matplotlib.pyplot as plt
import json

# 解析数据
data = json.loads('{data_json}')

# 创建图表
plt.figure(figsize=(10, 6))

# 根据图表类型生成不同的图表
if '{input_data.chart_type}' == 'bar':
    if isinstance(data, dict) and 'categories' in data and 'values' in data:
        plt.bar(data['categories'], data['values'])
    else:
        # 默认处理
        keys = list(data.keys())
        values = list(data.values())
        plt.bar(keys, values)
        
elif '{input_data.chart_type}' == 'line':
    if isinstance(data, dict) and 'x' in data and 'y' in data:
        plt.plot(data['x'], data['y'])
    else:
        # 默认处理
        keys = list(data.keys())
        values = list(data.values())
        plt.plot(keys, values)
        
elif '{input_data.chart_type}' == 'pie':
    if isinstance(data, dict):
        plt.pie(list(data.values()), labels=list(data.keys()), autopct='%1.1f%%')
    else:
        print("饼图数据格式不正确")

# 设置标题
if '{input_data.title}':
    plt.title('{input_data.title}')

plt.tight_layout()
plt.show()
print("图表生成完成")
"""
        
        return code