from langchain_core.messages.base import BaseMessage
from pydantic import BaseModel,Field
from typing import Optional
from uuid import uuid4

class AgentState(BaseModel):
    """
    代理状态模型，包含代理的唯一标识符和当前状态。
    
    Args:
        id (str): 代理的唯一标识符，默认为随机生成的 UUID。
        consecutive_failures (int): 连续失败次数，默认为0。
        result (str): 代理执行的结果，默认为空字符串。
        agent_data (AgentData): 代理的数据，默认为 None。
        messages (list[BaseMessage]): 代理的消息列表，默认为空列表。
        previous_observation (str): 上一次观察到的内容，默认为 None。
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="代理的唯一标识符")
    consecutive_failures: int = Field(default=0, description="连续失败次数")
    result: str = ''
    agent_data: 'AgentData' = None
    messages: list[BaseMessage] = Field(default_factory=list, description="代理的消息列表")
    previous_observation: str = None
    max_memory: int = Field(default=10, ge=1, description="最大记忆数量")
    forgotten_memories: int = Field(default=0, description="被遗忘的记忆数量")

    def is_done(self):
         return self.agent_data is not None and self.agent_data.action.name == 'Done Tool'
    
    def init_state(self, messages: list[BaseMessage]):
        self.consecutive_failures = 0
        self.result = ""
        self.messages = messages
        self.forgotten_memories = 0

    def update_state(self, agent_data: 'AgentData' = None, observation: str = None, result: str = None, messages: list[BaseMessage] = None):
        self.result = result
        self.previous_observation = observation
        self.agent_data = agent_data
        self.messages.extend(messages or [])
        while len(self.messages) > self.max_memory + 2:
            self.messages.pop(2)
            self.forgotten_memories += 1

        
class AgentStep(BaseModel):
    step_number: int=0
    max_steps: int

    def is_last_step(self):
        return self.step_number >= self.max_steps-1
    
    def increment_step(self):
        self.step_number += 1
    
class AgentResult(BaseModel):
    is_done:bool|None=False
    content:str|None=None
    error:str|None=None

class Action(BaseModel):
    name:str
    params: dict

class AgentData(BaseModel):
    evaluate: Optional[str]=None
    memory: Optional[str]=None
    thought: Optional[str]=None
    action: Optional[Action]=None