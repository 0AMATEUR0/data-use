from langchain_core.messages import BaseMessage, HumanMessage
from agent.views import AgentData
import ast
import re
import json
from typing import Any, Dict

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




SAFE_FUNCS = {
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "range": range,
    "any": any,
    "all": all,
    "sorted": sorted,
}










class AgentContext:
    def __init__(self):
        self.variables: Dict[str, Any] = {}

    def set(self, name: str, value: Any):
        self.variables[name] = value

    def get(self, name: str) -> Any:
        return self.variables.get(name)

    def has(self, name: str) -> bool:
        return name in self.variables
    
    def is_expression(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        try:
            # 如果是纯字面量（字符串、数字、列表、字典等），说明不是表达式
            ast.literal_eval(value)
            return False
        except Exception:
            # 如果字符串只是像 "AC"、"Sheet1" 这样的标识符，就不要当表达式
            if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", value):
                return False
            return True  # 非字面量，如 len(x), x+1 等，是表达式
    
    def safe_eval(self, expr: str, context: dict):
        try:
            return eval(expr, {"__builtins__": {}}, {**SAFE_FUNCS, **context})
        except NameError as e:
            return f"[UndefinedVariableError: {e}]"
        except Exception as e:
            return f"[EvalError: {e}]"

    def resolve_expression(self, expr: str) -> Any:
        return self.safe_eval(expr, self.variables)

    def resolve_dict(self, data: Dict[str, Any], skip_keys: set = None) -> Dict[str, Any]:
        skip_keys = skip_keys or set()
        resolved = {}
        for key, value in data.items():
            if key not in skip_keys and self.is_expression(value):
                resolved[key] = self.resolve_expression(value)
            else:
                resolved[key] = value
        return resolved

    def register_tool_output(self, name: str, result: Any):
        self.set(name, result)

    def __repr__(self):
        return f"AgentContext({self.variables})"