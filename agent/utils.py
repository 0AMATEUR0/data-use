from langchain_core.messages import BaseMessage, HumanMessage
from agent.views import AgentData
import ast
import re
import json

def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()
    
def extract_agent_data(message: BaseMessage) -> AgentData:
    """
    从消息中提取 AgentData 对象。
    
    Args:
        message (BaseMessage): 包含 AgentData 的消息。
        
    Returns:
        AgentData: 提取的 AgentData 对象。
    """
    text = message.content

    result = {}

    memory_match = re.search(r"<memory>(.*?)<\/memory>", text, re.DOTALL)
    if memory_match:
        result['memory'] = memory_match.group(1).strip()
    
    evaluate_match = re.search(r"<evaluate>(.*?)<\/evaluate>", text, re.DOTALL)
    if evaluate_match:
        result['evaluate'] = evaluate_match.group(1).strip()

    thought_match = re.search(r"<thought>(.*?)<\/thought>", text, re.DOTALL)
    if thought_match:
        result['thought'] = thought_match.group(1).strip()

    action = {}
    action_name_match = re.search(r"<action_name>(.*?)<\/action_name>", text, re.DOTALL)
    if action_name_match:
        action['name'] = action_name_match.group(1).strip()
    
    action_input_match = re.search(r"<action_input>(.*?)<\/action_input>", text, re.DOTALL)

    if action_input_match:
        action_input_str = action_input_match.group(1).strip()
        try:
            # Convert string to dictionary safely using ast.literal_eval
            action['params'] = ast.literal_eval(action_input_str)
        except (ValueError, SyntaxError):
            # If there's an issue with conversion, store it as raw string
            action['params'] = action_input_str
    result['action'] = action
    return  AgentData.model_validate(result)
