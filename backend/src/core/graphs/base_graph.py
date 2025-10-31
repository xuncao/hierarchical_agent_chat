"""
基础图构建框架
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ..llm_client import LLMClient
from ..tools import ToolRegistry


class AgentState(TypedDict):
    """代理状态基类"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: str
    team: str
    task: str
    results: Dict[str, Any]
    errors: List[str]


class BaseGraph(BaseModel):
    """基础图构建类"""
    
    name: str = Field(description="图名称")
    description: str = Field(description="图描述")
    llm_client: LLMClient = Field(description="LLM客户端")
    tool_registry: ToolRegistry = Field(description="工具注册表")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self._graph = None
        self._compiled_graph = None
    
    def build_graph(self) -> StateGraph:
        """构建状态图"""
        raise NotImplementedError("子类必须实现build_graph方法")
    
    def compile_graph(self) -> Any:
        """编译图"""
        if self._compiled_graph is None:
            self._graph = self.build_graph()
            self._compiled_graph = self._graph.compile()
        return self._compiled_graph
    
    async def run(self, input_state: AgentState, config: Optional[Dict[str, Any]] = None) -> AgentState:
        """运行图"""
        graph = self.compile_graph()
        
        if config is None:
            config = {"configurable": {"thread_id": "default"}}
        
        # 运行图
        result = await graph.ainvoke(input_state, config)
        return result
    
    def create_agent_node(self, name: str, system_prompt: str, tools: List[str]) -> Any:
        """创建代理节点"""
        # 获取指定工具
        langchain_tools = []
        for tool_name in tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                langchain_tools.append(tool.to_langchain_tool())
        
        # 创建代理
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}")
        ])
        
        agent = create_react_agent(
            self.llm_client.get_llm(),
            langchain_tools,
            prompt=prompt
        )
        
        def agent_node(state: AgentState) -> Dict[str, Any]:
            """代理节点函数"""
            result = agent.invoke(state)
            return {
                "messages": [result["messages"][-1]],
                "current_step": name,
                "results": {
                    **state.get("results", {}),
                    name: result
                }
            }
        
        return agent_node
    
    def create_supervisor_node(self, team_members: List[str]) -> Any:
        """创建监督器节点"""
        
        def supervisor_node(state: AgentState) -> Dict[str, Any]:
            """监督器节点函数"""
            # 基于当前状态决定下一步行动
            last_message = state["messages"][-1] if state["messages"] else None
            
            if last_message and isinstance(last_message, HumanMessage):
                # 如果是用户消息，路由到合适的团队成员
                return {"next": team_members[0]}  # 默认路由到第一个成员
            
            # 基于消息内容决定下一步
            # 这里可以添加更复杂的路由逻辑
            return {"next": END}
        
        return supervisor_node