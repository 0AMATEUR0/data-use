from tools.service import *
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agent.views import AgentResult, AgentStep, AgentState
from agent.utils import extract_agent_data
from langchain_core.language_models.chat_models import BaseChatModel
from registry.service import Registry
from registry.views import ToolResult
from prompt.service import Prompt
from langchain_core.tools import BaseTool
from rich.markdown import Markdown
from rich.console import Console
from termcolor import colored
from textwrap import shorten
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

default_tools = [
    done_tool,
    human_tool,
    load_dataframe_tool,
    excel_head_tool,
    excel_info_tool,
    dataframe2excel_tool,
    read_dataframe_tool,
    write_dataframe_tool,
    # Add any other default tools here, e.g.:
    # get_json_data_tool
]


class Agent:
    """
    Data Use Agent
    一个可以与数据交互的代理

    Args:
        instructions (list[str], optional): 代理的指令列表。默认为空列表
        additional_tools (list[BaseTool], optional): 额外的工具列表。默认为空列表
        llm (BaseChatModel, optional): 用于代理的语言模型。默认为 None
        max_steps (int, optional): 代理的最大步骤数。默认为 100
        max_memory (int, optional): 代理的最大额外记忆大小。默认为 10(不包括最开始的system_message和user_query,也就是实际最大12条消息)
        file_path (str, optional): 文件路径。默认为 None
    """
    def __init__(self,
                 instructions: list[str] = [],
                 additional_tools: list[BaseTool] = [],
                 llm: BaseChatModel = None,
                 max_steps:int=100,
                 max_memory:int=10,
                 file_path: str = None):
        self.name = 'Data Use Agent'
        self.description = 'An agent that can interact with data'
        self.registry = Registry(tools=default_tools + additional_tools)
        self.instructions = instructions
        self.llm = llm
        self.agent_state = AgentState(max_memory=max_memory)
        self.agent_step = AgentStep(max_steps=max_steps)
        self.file_path = file_path

    def reason(self):
        message = self.llm.invoke(self.agent_state.messages)
        agent_data = extract_agent_data(message=message)
        self.agent_state.update_state(
            agent_data=agent_data,
            messages=[message]
        )
        logger.info(colored(f"💭: Thought: {agent_data.thought}",color='light_magenta',attrs=['bold']))
    
    def action(self):
        self.agent_state.messages.pop() # Remove the last message to avoid duplication
        last_message = self.agent_state.messages[-1]
        if isinstance(last_message, HumanMessage):
            self.agent_state.messages[-1]=HumanMessage(content=Prompt.previous_observation_prompt(self.agent_state.previous_observation))
        ai_message = AIMessage(content=Prompt.action_prompt(agent_data=self.agent_state.agent_data))
        name = self.agent_state.agent_data.action.name
        params = self.agent_state.agent_data.action.params
        logger.info(colored(f"🔧: Action: {name}({', '.join(f'{k}={v}' for k, v in params.items())})",color='blue',attrs=['bold']))
        tool_result = self.registry.execute(tool_name=name, **params)
        observation=tool_result.content if tool_result.is_success else tool_result.error
        logger.info(colored(f"🔭: Observation: {shorten(observation,500,placeholder='...')}",color='green',attrs=['bold']))
        prompt=Prompt.observation_prompt(agent_step=self.agent_step, agent_state=self.agent_state, tool_result=tool_result)
        human_message = HumanMessage(content=prompt)
        self.agent_state.update_state(agent_data=None,observation=observation,messages=[ai_message, human_message])

    def answer(self):
        self.agent_state.messages.pop()  # Remove the last message to avoid duplication
        last_message = self.agent_state.messages[-1]
        if isinstance(last_message, HumanMessage):
            self.agent_state.messages[-1]=HumanMessage(content=Prompt.previous_observation_prompt(self.agent_state.previous_observation))
        name = self.agent_state.agent_data.action.name
        params = self.agent_state.agent_data.action.params
        tool_result = self.registry.execute(tool_name=name, **params)
        ai_message = AIMessage(content=Prompt.answer_prompt(agent_data=self.agent_state.agent_data, tool_result=tool_result))
        logger.info(colored(f"📜: Final Answer: {tool_result.content}",color='cyan',attrs=['bold']))
        self.agent_state.update_state(agent_data=None,observation=None,result=tool_result.content,messages=[ai_message])

    def invoke(self,query: str):
        max_steps = self.agent_step.max_steps
        tools_prompt = self.registry.get_tools_prompt()
        prompt = Prompt.observation_prompt(
            agent_step= self.agent_step,
            agent_state=self.agent_state,
            tool_result=ToolResult(is_success=True, content="No Action"),
        )
        system_message = SystemMessage(
            content=Prompt.system_prompt(
                instructions=self.instructions,
                tools_prompt=tools_prompt,
                file_path=self.file_path,
                max_steps=max_steps
            )
        )
        human_message = HumanMessage(content=prompt)
        messages = [system_message,
                    HumanMessage(content=f'<user_query>{query}</user_query>'),
                    human_message]
        self.agent_state.init_state(messages=messages)
        try:
            while True:
                if self.agent_step.is_last_step():
                    logger.info(colored("🚫: Reached maximum steps, stopping execution.", color='red', attrs=['bold']))
                    return AgentResult(is_done=False, content=None, error="Reached maximum steps")
                self.reason()
                if self.agent_state.is_done():
                    logger.info(colored("✅: Task completed successfully.", color='green', attrs=['bold']))
                    self.answer()
                    return AgentResult(is_done=True, content=self.agent_state.result, error=None)
                self.action()
                if self.agent_state.consecutive_failures >= 3:
                    logger.warning(colored("⚠️: Consecutive failures exceeded, stopping execution.", color='yellow', attrs=['bold']))
                    return AgentResult(is_done=False, content=None, error="Consecutive failures exceeded")
                self.agent_step.increment_step()
        except Exception as error:
            logger.error(colored(f"❌: An error occurred during agent execution: {error}", color='red', attrs=['bold']))
            return AgentResult(is_done=False, content=None, error=str(error))
        finally:
            logger.info(colored("🛑: Agent execution finished.", color='blue', attrs=['bold']))

    def print_response(self, query: str):
        console=Console()
        response=self.invoke(query)
        console.print(Markdown(response.content or response.error))


        