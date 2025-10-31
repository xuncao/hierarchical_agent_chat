"""
文档写作团队图构建
"""

from typing import Any, Dict, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from .base_graph import BaseGraph, AgentState


class WritingState(AgentState):
    """文档写作团队状态"""
    document_outline: Dict[str, Any]
    document_content: str
    generated_charts: List[Dict[str, Any]]
    final_document: str


class WritingGraph(BaseGraph):
    """文档写作团队图"""
    
    def __init__(self, llm_client, tool_registry):
        super().__init__(
            name="writing_team",
            description="文档写作团队：负责文档创作和编辑",
            llm_client=llm_client,
            tool_registry=tool_registry
        )
    
    def build_graph(self) -> StateGraph:
        """构建文档写作团队图"""
        # 创建状态图
        workflow = StateGraph(WritingState)
        
        # 添加节点
        workflow.add_node("writing_supervisor", self.create_writing_supervisor_node())
        workflow.add_node("note_taking_agent", self.create_note_taking_agent_node())
        workflow.add_node("document_writer_agent", self.create_document_writer_agent_node())
        workflow.add_node("chart_generator_agent", self.create_chart_generator_agent_node())
        workflow.add_node("document_editor", self.create_document_editor_node())
        
        # 设置入口点
        workflow.set_entry_point("writing_supervisor")
        
        # 添加边
        workflow.add_conditional_edges(
            "writing_supervisor",
            self.route_writing_task,
            {
                "outline": "note_taking_agent",
                "write": "document_writer_agent",
                "chart": "chart_generator_agent",
                "edit": "document_editor",
                "end": END
            }
        )
        
        workflow.add_edge("note_taking_agent", "writing_supervisor")
        workflow.add_edge("document_writer_agent", "writing_supervisor")
        workflow.add_edge("chart_generator_agent", "writing_supervisor")
        workflow.add_edge("document_editor", END)
        
        return workflow
    
    def create_writing_supervisor_node(self):
        """创建文档写作团队监督器节点"""
        
        def writing_supervisor_node(state: WritingState) -> Dict[str, Any]:
            """写作监督器节点函数"""
            # 基于当前状态决定下一步行动
            last_message = state["messages"][-1] if state["messages"] else None
            
            if not last_message:
                return {"next": "outline"}
            
            # 简单的任务路由逻辑
            content = last_message.content.lower() if hasattr(last_message, 'content') else ""
            
            if "outline" in content or "structure" in content or "大纲" in content:
                return {"next": "outline"}
            elif "write" in content or "content" in content or "文档" in content:
                return {"next": "write"}
            elif "chart" in content or "graph" in content or "图表" in content:
                return {"next": "chart"}
            elif "edit" in content or "final" in content or "编辑" in content:
                return {"next": "edit"}
            else:
                return {"next": "outline"}  # 默认创建大纲
        
        return writing_supervisor_node
    
    def create_note_taking_agent_node(self):
        """创建大纲制定代理节点"""
        system_prompt = """你是一个专业的大纲制定专家。你的任务是：
        1. 分析用户需求，创建清晰的文档结构
        2. 制定逻辑严谨的文档大纲
        3. 确保大纲覆盖所有关键要点
        4. 提供层次分明的章节结构
        
        请确保大纲结构清晰、逻辑合理，便于后续文档写作。
        """
        
        return self.create_agent_node(
            "note_taking_agent",
            system_prompt,
            ["note_taking_tool"]
        )
    
    def create_document_writer_agent_node(self):
        """创建文档写作代理节点"""
        system_prompt = """你是一个专业的文档写作专家。你的任务是：
        1. 根据大纲和用户需求撰写高质量文档
        2. 确保内容准确、语言流畅
        3. 保持文档风格一致
        4. 提供详细的解释和示例
        
        请确保文档内容专业、易懂，满足用户需求。
        """
        
        return self.create_agent_node(
            "document_writer_agent",
            system_prompt,
            ["document_writer_tool"]
        )
    
    def create_chart_generator_agent_node(self):
        """创建图表生成代理节点"""
        system_prompt = """你是一个数据可视化专家。你的任务是：
        1. 根据数据生成合适的图表
        2. 确保图表清晰、美观
        3. 提供图表的解释和说明
        4. 选择合适的图表类型展示数据
        
        请确保图表能够有效传达数据信息。
        """
        
        return self.create_agent_node(
            "chart_generator_agent",
            system_prompt,
            ["chart_generator_tool"]
        )
    
    def create_document_editor_node(self):
        """创建文档编辑器节点"""
        system_prompt = """你是一个专业的文档编辑专家。你的任务是：
        1. 整合所有文档内容
        2. 检查文档的逻辑性和一致性
        3. 优化语言表达和格式
        4. 生成最终的完整文档
        
        请确保最终文档质量高、结构完整。
        """
        
        def document_editor_node(state: WritingState) -> Dict[str, Any]:
            """文档编辑器节点函数"""
            # 整合所有文档内容
            outline = state.get("document_outline", {})
            content = state.get("document_content", "")
            charts = state.get("generated_charts", [])
            
            # 生成最终文档
            final_document = self._generate_final_document(outline, content, charts)
            
            # 使用代理进行最终编辑
            agent_node = self.create_agent_node(
                "document_editor",
                system_prompt,
                ["document_writer_tool"]
            )
            
            result = agent_node(state)
            result["final_document"] = final_document
            
            return result
        
        return document_editor_node
    
    def route_writing_task(self, state: WritingState) -> str:
        """路由写作任务"""
        last_message = state["messages"][-1] if state["messages"] else None
        
        if not last_message:
            return "outline"
        
        # 基于消息内容决定下一步
        content = last_message.content.lower() if hasattr(last_message, 'content') else ""
        
        # 检查是否需要最终编辑
        if state.get("document_content") and state.get("document_outline"):
            if "edit" in content or "final" in content or not content:
                return "edit"
        
        # 基于关键词路由
        if "outline" in content or "structure" in content:
            return "outline"
        elif "write" in content or "content" in content:
            return "write"
        elif "chart" in content or "graph" in content:
            return "chart"
        elif "edit" in content or "final" in content:
            return "edit"
        
        # 默认路由
        return "outline"
    
    def _generate_final_document(self, outline: Dict, content: str, charts: List[Dict]) -> str:
        """生成最终文档"""
        document_parts = []
        
        # 添加标题
        if outline and "title" in outline:
            document_parts.append(f"# {outline['title']}")
        else:
            document_parts.append("# 文档标题")
        
        document_parts.append("")
        
        # 添加大纲结构
        if outline and "sections" in outline:
            document_parts.append("## 文档结构")
            for section in outline["sections"]:
                if "title" in section:
                    document_parts.append(f"- {section['title']}")
        
        document_parts.append("")
        
        # 添加文档内容
        if content:
            document_parts.append("## 文档内容")
            document_parts.append(content)
        
        document_parts.append("")
        
        # 添加图表说明
        if charts:
            document_parts.append("## 数据图表")
            for i, chart in enumerate(charts, 1):
                chart_type = chart.get("chart_type", "未知类型")
                title = chart.get("title", f"图表{i}")
                document_parts.append(f"### {title}")
                document_parts.append(f"图表类型: {chart_type}")
                if "execution_result" in chart:
                    document_parts.append(f"生成状态: {chart['execution_result']}")
        
        return "\n\n".join(document_parts)