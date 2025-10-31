"""
研究团队图构建
"""

from typing import Any, Dict, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from .base_graph import BaseGraph, AgentState


class ResearchState(AgentState):
    """研究团队状态"""
    search_results: List[Dict[str, Any]]
    scraped_content: List[Dict[str, Any]]
    research_summary: str


class ResearchGraph(BaseGraph):
    """研究团队图"""
    
    def __init__(self, llm_client, tool_registry):
        super().__init__(
            name="research_team",
            description="研究团队：负责搜索和抓取信息",
            llm_client=llm_client,
            tool_registry=tool_registry
        )
    
    def build_graph(self) -> StateGraph:
        """构建研究团队图"""
        # 创建状态图
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("research_supervisor", self.create_research_supervisor_node())
        workflow.add_node("search_agent", self.create_search_agent_node())
        workflow.add_node("web_scraper_agent", self.create_web_scraper_agent_node())
        workflow.add_node("research_analyzer", self.create_research_analyzer_node())
        
        # 设置入口点
        workflow.set_entry_point("research_supervisor")
        
        # 添加边
        workflow.add_conditional_edges(
            "research_supervisor",
            self.route_research_task,
            {
                "search": "search_agent",
                "scrape": "web_scraper_agent",
                "analyze": "research_analyzer",
                "end": END
            }
        )
        
        workflow.add_edge("search_agent", "research_supervisor")
        workflow.add_edge("web_scraper_agent", "research_supervisor")
        workflow.add_edge("research_analyzer", END)
        
        return workflow
    
    def create_research_supervisor_node(self):
        """创建研究团队监督器节点"""
        
        def research_supervisor_node(state: ResearchState) -> Dict[str, Any]:
            """研究监督器节点函数"""
            # 基于当前状态决定下一步行动
            last_message = state["messages"][-1] if state["messages"] else None
            
            if not last_message:
                return {"next": "search"}
            
            # 简单的任务路由逻辑
            content = last_message.content.lower() if hasattr(last_message, 'content') else ""
            
            if "search" in content or "find" in content:
                return {"next": "search"}
            elif "scrape" in content or "extract" in content or "http" in content:
                return {"next": "scrape"}
            elif "analyze" in content or "summary" in content or "conclude" in content:
                return {"next": "analyze"}
            else:
                return {"next": "search"}  # 默认搜索
        
        return research_supervisor_node
    
    def create_search_agent_node(self):
        """创建搜索代理节点"""
        system_prompt = """你是一个专业的搜索代理。你的任务是：
        1. 理解用户的信息需求
        2. 使用搜索工具获取相关信息
        3. 提供准确、相关的搜索结果
        
        请确保搜索查询简洁明了，能够准确反映用户需求。
        """
        
        return self.create_agent_node(
            "search_agent",
            system_prompt,
            ["search_tool"]
        )
    
    def create_web_scraper_agent_node(self):
        """创建网页抓取代理节点"""
        system_prompt = """你是一个专业的网页抓取代理。你的任务是：
        1. 从提供的URL中提取有用信息
        2. 解析网页内容，提取关键信息
        3. 提供结构化的内容摘要
        
        请确保只抓取公开可访问的内容，并遵守robots.txt规则。
        """
        
        return self.create_agent_node(
            "web_scraper_agent",
            system_prompt,
            ["web_scraper_tool"]
        )
    
    def create_research_analyzer_node(self):
        """创建研究分析器节点"""
        system_prompt = """你是一个研究分析专家。你的任务是：
        1. 分析搜索和抓取的结果
        2. 整合信息，提供全面的研究总结
        3. 识别关键发现和见解
        4. 提供结构化的研究报告
        
        请确保分析全面、客观，并突出最重要的发现。
        """
        
        def research_analyzer_node(state: ResearchState) -> Dict[str, Any]:
            """研究分析器节点函数"""
            # 这里可以添加专门的分析逻辑
            # 暂时使用通用的代理节点
            agent_node = self.create_agent_node(
                "research_analyzer",
                system_prompt,
                []  # 分析节点可能不需要特定工具
            )
            
            result = agent_node(state)
            
            # 添加研究总结
            if "results" in state:
                search_results = state.get("search_results", [])
                scraped_content = state.get("scraped_content", [])
                
                # 生成研究总结
                summary = self._generate_research_summary(search_results, scraped_content)
                result["research_summary"] = summary
            
            return result
        
        return research_analyzer_node
    
    def route_research_task(self, state: ResearchState) -> str:
        """路由研究任务"""
        last_message = state["messages"][-1] if state["messages"] else None
        
        if not last_message:
            return "search"
        
        # 基于消息内容决定下一步
        content = last_message.content.lower() if hasattr(last_message, 'content') else ""
        
        # 检查是否需要分析
        if state.get("search_results") or state.get("scraped_content"):
            if "analyze" in content or "summary" in content or not content:
                return "analyze"
        
        # 基于关键词路由
        if "search" in content or "find" in content:
            return "search"
        elif "scrape" in content or "extract" in content or "http" in content:
            return "scrape"
        elif "analyze" in content or "summary" in content:
            return "analyze"
        
        # 默认路由
        return "search"
    
    def _generate_research_summary(self, search_results: List[Dict], scraped_content: List[Dict]) -> str:
        """生成研究总结"""
        summary_parts = []
        
        if search_results:
            summary_parts.append("## 搜索发现")
            for i, result in enumerate(search_results[:3], 1):
                if isinstance(result, dict):
                    title = result.get("title", "未知标题")
                    snippet = result.get("content", result.get("snippet", ""))
                    summary_parts.append(f"{i}. {title}: {snippet[:200]}...")
        
        if scraped_content:
            summary_parts.append("## 网页内容摘要")
            for i, content in enumerate(scraped_content[:2], 1):
                if isinstance(content, dict):
                    url = content.get("url", "未知URL")
                    text = content.get("content", "")
                    summary_parts.append(f"{i}. {url}: {text[:300]}...")
        
        if not summary_parts:
            return "暂无研究数据"
        
        return "\n\n".join(summary_parts)