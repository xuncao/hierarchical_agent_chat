"""代理相关数据模型"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

from .base_models import AgentType, ModelProvider


class ToolType(str, Enum):
    """工具类型枚举"""
    SEARCH = "search"
    WEB_SCRAPER = "web_scraper"
    FILE_OPERATION = "file_operation"
    PYTHON_REPL = "python_repl"
    CHART_GENERATION = "chart_generation"
    NOTE_TAKING = "note_taking"
    DOCUMENT_WRITING = "document_writing"


class AgentRole(str, Enum):
    """代理角色枚举"""
    SUPERVISOR = "supervisor"
    WORKER = "worker"
    COORDINATOR = "coordinator"


class ToolDefinition(BaseModel):
    """工具定义模型"""
    name: str = Field(..., description="工具名称")
    type: ToolType = Field(..., description="工具类型")
    description: str = Field(..., description="工具描述")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    is_enabled: bool = Field(True, description="是否启用")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="工具元数据")


class AgentDefinition(BaseModel):
    """代理定义模型"""
    name: str = Field(..., description="代理名称")
    role: AgentRole = Field(..., description="代理角色")
    agent_type: AgentType = Field(..., description="代理类型")
    description: str = Field(..., description="代理描述")
    model_provider: ModelProvider = Field(..., description="模型提供商")
    model_name: str = Field(..., description="模型名称")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(2000, ge=100, le=4000, description="最大token数")
    tools: List[ToolDefinition] = Field(default_factory=list, description="可用工具列表")
    capabilities: List[str] = Field(default_factory=list, description="代理能力列表")
    is_enabled: bool = Field(True, description="是否启用")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="代理元数据")


class TeamDefinition(BaseModel):
    """团队定义模型"""
    name: str = Field(..., description="团队名称")
    agent_type: AgentType = Field(..., description="团队类型")
    description: str = Field(..., description="团队描述")
    supervisor: AgentDefinition = Field(..., description="监督器代理")
    workers: List[AgentDefinition] = Field(default_factory=list, description="工作代理列表")
    workflow_config: Dict[str, Any] = Field(default_factory=dict, description="工作流配置")
    is_enabled: bool = Field(True, description="是否启用")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="团队元数据")


class AgentState(BaseModel):
    """代理状态模型"""
    agent_id: str = Field(..., description="代理ID")
    agent_name: str = Field(..., description="代理名称")
    status: str = Field(..., description="代理状态")
    current_task: Optional[str] = Field(None, description="当前任务")
    queue_size: int = Field(0, description="队列大小")
    error_count: int = Field(0, description="错误计数")
    last_activity: Optional[str] = Field(None, description="最后活动时间")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="状态元数据")


class TaskRequest(BaseModel):
    """任务请求模型"""
    task_id: str = Field(..., description="任务ID")
    agent_type: AgentType = Field(..., description="代理类型")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    priority: int = Field(1, ge=1, le=10, description="任务优先级")
    timeout: int = Field(300, ge=10, le=3600, description="超时时间（秒）")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="任务元数据")


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    agent_id: str = Field(..., description="代理ID")
    status: str = Field(..., description="任务状态")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(0.0, description="执行时间（秒）")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="响应元数据")


class WorkflowState(BaseModel):
    """工作流状态模型"""
    workflow_id: str = Field(..., description="工作流ID")
    current_step: str = Field(..., description="当前步骤")
    completed_steps: List[str] = Field(default_factory=list, description="已完成步骤")
    pending_steps: List[str] = Field(default_factory=list, description="待处理步骤")
    state_data: Dict[str, Any] = Field(default_factory=dict, description="状态数据")
    status: str = Field(..., description="工作流状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="工作流元数据")


class GraphNode(BaseModel):
    """图节点模型"""
    node_id: str = Field(..., description="节点ID")
    node_type: str = Field(..., description="节点类型")
    agent_id: Optional[str] = Field(None, description="关联代理ID")
    tool_name: Optional[str] = Field(None, description="工具名称")
    config: Dict[str, Any] = Field(default_factory=dict, description="节点配置")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="节点元数据")


class GraphEdge(BaseModel):
    """图边模型"""
    source_node: str = Field(..., description="源节点")
    target_node: str = Field(..., description="目标节点")
    condition: Optional[str] = Field(None, description="转移条件")
    priority: int = Field(1, description="边优先级")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="边元数据")


class GraphDefinition(BaseModel):
    """图定义模型"""
    graph_id: str = Field(..., description="图ID")
    name: str = Field(..., description="图名称")
    description: str = Field(..., description="图描述")
    nodes: List[GraphNode] = Field(default_factory=list, description="节点列表")
    edges: List[GraphEdge] = Field(default_factory=list, description="边列表")
    entry_node: str = Field(..., description="入口节点")
    exit_node: str = Field(..., description="出口节点")
    config: Dict[str, Any] = Field(default_factory=dict, description="图配置")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="图元数据")


class AgentConfiguration(BaseModel):
    """代理配置模型"""
    agent_definitions: List[AgentDefinition] = Field(default_factory=list, description="代理定义列表")
    team_definitions: List[TeamDefinition] = Field(default_factory=list, description="团队定义列表")
    graph_definitions: List[GraphDefinition] = Field(default_factory=list, description="图定义列表")
    tool_definitions: List[ToolDefinition] = Field(default_factory=list, description="工具定义列表")
    default_model: ModelProvider = Field(ModelProvider.DEEPSEEK, description="默认模型提供商")
    default_agent: AgentType = Field(AgentType.COORDINATOR, description="默认代理类型")
    config_version: str = Field("1.0.0", description="配置版本")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="配置元数据")