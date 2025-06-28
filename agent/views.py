from langchain_core.messages.base import BaseMessage
from pydantic import BaseModel,Field
from typing import Optional
from uuid import uuid4

class AgentState(BaseModel):
    """
    代理状态模型，包含代理的唯一标识符和当前状态。
    
    Args:
        agent_id (str): 代理的唯一标识符，默认为 UUID。
        status (str): 代理的当前状态，默认为 'idle'。
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="代理的唯一标识符")
    consecutive_failures: int = Field(default=0, description="连续失败次数")
    result: str = ''
    agent_data: 'AgentData' = None
    messages: list[BaseMessage] = Field(default_factory=list, description="代理的消息列表")
    previous_observation: str = None

    def is_done(self):
         return self.agent_data is not None and self.agent_data.action.name == 'Done Tool'
    
    def init_state(self, messages: list[BaseMessage]):
        self.consecutive_failures = 0
        self.result = ""
        self.messages = messages

    def update_state(self, agent_data: 'AgentData' = None, observation: str = None, result: str = None, messages: list[BaseMessage] = None):
        self.result = result
        self.previous_observation = observation
        self.agent_data = agent_data
        self.messages.extend(messages or [])

        
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