from registry.views import ToolResult
from agent.views import AgentStep, AgentData, AgentState
from langchain.prompts import PromptTemplate
from importlib.resources import files
from textwrap import dedent



class Prompt:
    """
    该类用于生成代理的提示信息。
    
    
    """
    @staticmethod
    def system_prompt(tools_prompt: str,
                      max_steps: int,
                      file_path: str = None,
                      instructions: list[str]=[]) -> str:
        """
        生成系统提示信息。
        
        Returns:
            str: 系统提示信息。
        """
        template = PromptTemplate.from_file(files('prompt').joinpath('system.md'))
        return template.format(**{
            'instructions': '\n'.join(instructions),
            'tools_prompt': tools_prompt,
            'file_path': file_path,
            'max_steps': max_steps
        })

    @staticmethod
    def action_prompt(agent_data: AgentData) -> str:
        """
        生成动作提示信息。
        
        Args:
            agent_data (AgentData): 代理数据。
        
        Returns:
            str: 动作提示信息。
        """
        template = PromptTemplate.from_file(files('prompt').joinpath('action.md'))
        return template.format(**{
            'evaluate': agent_data.evaluate,
            'memory': agent_data.memory,
            'thought': agent_data.thought,
            'action_name': agent_data.action.name,
            'action_input': agent_data.action.params
        })
    
    @staticmethod
    def previous_observation_prompt(observation: str)-> str:
        template=PromptTemplate.from_template(dedent('''
        ```xml
        <output>{observation}</output>
        ```
        '''))
        return template.format(**{'observation': observation})
    
    @staticmethod
    def observation_prompt(agent_step: AgentStep, agent_state: AgentState, tool_result:ToolResult) -> str:
        """
        生成观察提示信息。
        
        Args:
            agent_step (AgentStep): 代理步骤。
            tool_result (ToolResult): 工具结果。
        
        Returns:
            str: 观察提示信息。
        """
        template = PromptTemplate.from_file(files('prompt').joinpath('observation.md'))
        return template.format(**{
            'steps': agent_step.step_number,
            'max_steps': agent_step.max_steps,
            'observation': tool_result.content if tool_result.is_success else tool_result.error,
            'forgotten_memories': agent_state.forgotten_memories,
        })
    
    @staticmethod
    def answer_prompt(agent_data: AgentData, tool_result: ToolResult) -> str:
        """
        生成答案提示信息。
        
        Args:
            agent_data (AgentData): 代理数据。
            tool_result (ToolResult): 工具结果。
        
        Returns:
            str: 答案提示信息。
        """
        template = PromptTemplate.from_file(files('prompt').joinpath('answer.md'))
        return template.format(**{
            'evaluate': agent_data.evaluate,
            'memory': agent_data.memory,
            'thought': agent_data.thought,
            'final_answer': tool_result.content
        })