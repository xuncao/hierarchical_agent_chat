"""
顶层监督器图 - 协调研究团队和文档写作团队
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from ..llm_client import LLMClient
from .base_graph import BaseGraph, AgentState
from .research_graph import ResearchGraph
from .writing_graph import WritingGraph


class SupervisorGraph(BaseGraph):
    """顶层监督器图 - 负责路由用户请求到合适的子团队"""
    
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)
        self.research_graph = ResearchGraph(llm_client)
        self.writing_graph = WritingGraph(llm_client)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建顶层监督器图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("research_team", self._research_team_node)
        workflow.add_node("writing_team", self._writing_team_node)
        workflow.add_node("final_response", self._final_response_node)
        
        # 设置入口点
        workflow.set_entry_point("supervisor")
        
        # 添加边
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_team,
            {
                "research": "research_team",
                "writing": "writing_team",
                "both": "research_team",  # 先研究后写作
                "direct": "final_response"
            }
        )
        
        # 研究团队到最终响应
        workflow.add_conditional_edges(
            "research_team",
            self._after_research,
            {
                "writing": "writing_team",
                "final": "final_response"
            }
        )
        
        # 写作团队到最终响应
        workflow.add_edge("writing_team", "final_response")
        workflow.add_edge("final_response", END)
        
        return workflow.compile()
    
    def _supervisor_node(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """顶层监督器节点 - 决定路由到哪个团队"""
        messages = state.get("messages", [])
        
        # 构建监督器提示
        supervisor_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能任务路由监督器。你的职责是分析用户请求，决定应该由哪个专业团队来处理。

可用的团队：
1. 研究团队 (research): 擅长搜索信息、网络研究、数据收集
2. 文档写作团队 (writing): 擅长文档创作、内容编写、格式整理
3. 综合处理 (both): 需要先研究后写作的复杂任务
4. 直接响应 (direct): 简单问题可以直接回答

请根据用户请求的内容和意图，选择最合适的处理路径。

返回格式：
{{"team": "research|writing|both|direct", "reasoning": "你的决策理由"}}"""),
            ("human", "用户请求: {user_input}")
        ])
        
        # 获取用户输入
        user_input = self._extract_user_input(messages)
        
        # 调用LLM进行路由决策
        response = self.llm_client.invoke(
            supervisor_prompt.format(user_input=user_input),
            config=config
        )
        
        # 解析响应
        try:
            import json
            decision = json.loads(response.content)
            team = decision.get("team", "direct")
            reasoning = decision.get("reasoning", "")
        except:
            team = "direct"
            reasoning = "解析失败，使用默认路由"
        
        # 更新状态
        state["supervisor_decision"] = {
            "team": team,
            "reasoning": reasoning
        }
        
        # 添加监督器思考消息
        state["messages"].append(SystemMessage(
            content=f"监督器决策: 路由到{team}团队。理由: {reasoning}"
        ))
        
        return state
    
    def _route_to_team(self, state: AgentState) -> str:
        """路由决策函数"""
        decision = state.get("supervisor_decision", {})
        team = decision.get("team", "direct")
        
        if team == "both":
            # 需要两个团队协作，先走研究团队
            return "research"
        
        return team
    
    def _research_team_node(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """研究团队节点"""
        # 调用研究团队图
        research_result = self.research_graph.invoke(state, config)
        
        # 合并结果
        state["research_result"] = research_result.get("research_result", {})
        state["messages"] = research_result.get("messages", [])
        
        return state
    
    def _writing_team_node(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """文档写作团队节点"""
        # 调用文档写作团队图
        writing_result = self.writing_graph.invoke(state, config)
        
        # 合并结果
        state["writing_result"] = writing_result.get("writing_result", {})
        state["messages"] = writing_result.get("messages", [])
        
        return state
    
    def _after_research(self, state: AgentState) -> str:
        """研究完成后决定下一步"""
        decision = state.get("supervisor_decision", {})
        team = decision.get("team", "direct")
        
        if team == "both":
            # 需要继续到写作团队
            return "writing"
        
        return "final"
    
    def _final_response_node(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """最终响应节点 - 整合各团队结果"""
        messages = state.get("messages", [])
        research_result = state.get("research_result", {})
        writing_result = state.get("writing_result", {})
        
        # 构建最终响应提示
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，负责整合各专业团队的工作成果，为用户提供最终的完整回答。

请基于以下信息生成专业、全面的回答：
- 用户原始请求
- 研究团队的发现（如果有）
- 文档写作团队的成果（如果有）

确保回答结构清晰、内容准确、语言自然。"""),
            ("human", """用户原始请求: {user_input}

研究团队发现: {research_summary}
写作团队成果: {writing_summary}

请基于以上信息生成最终回答：""")
        ])
        
        user_input = self._extract_user_input(messages)
        research_summary = research_result.get("summary", "无研究结果")
        writing_summary = writing_result.get("summary", "无写作成果")
        
        # 生成最终响应
        response = self.llm_client.invoke(
            final_prompt.format(
                user_input=user_input,
                research_summary=research_summary,
                writing_summary=writing_summary
            ),
            config=config
        )
        
        # 添加最终响应到消息历史
        state["messages"].append(response)
        state["final_response"] = response.content
        
        return state
    
    def _extract_user_input(self, messages: List[BaseMessage]) -> str:
        """从消息历史中提取用户输入"""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                return msg.content
        return ""


class SupervisorManager:
    """监督器管理器 - 管理顶层监督器的生命周期"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.supervisor_graph = SupervisorGraph(llm_client)
    
    async def process_request(self, user_input: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        if config is None:
            config = {}
        
        # 初始化状态
        initial_state = AgentState(
            messages=[HumanMessage(content=user_input)],
            supervisor_decision={},
            research_result={},
            writing_result={},
            final_response=""
        )
        
        # 执行图
        result = self.supervisor_graph.invoke(initial_state, config)
        
        return {
            "final_response": result.get("final_response", ""),
            "supervisor_decision": result.get("supervisor_decision", {}),
            "research_result": result.get("research_result", {}),
            "writing_result": result.get("writing_result", {}),
            "message_history": [msg.dict() for msg in result.get("messages", [])]
        }
    
    async def stream_request(self, user_input: str, config: Optional[Dict] = None):
        """流式处理用户请求"""
        if config is None:
            config = {}
        
        # 初始化状态
        initial_state = AgentState(
            messages=[HumanMessage(content=user_input)],
            supervisor_decision={},
            research_result={},
            writing_result={},
            final_response=""
        )
        
        # 流式执行图
        async for chunk in self.graph.astream(initial_state, config):
            yield chunk