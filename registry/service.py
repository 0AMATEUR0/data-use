from langchain.tools import Tool
from registry.views import Tool as ToolData, ToolResult
from textwrap import dedent

class Registry:
    """
    该类用于管理和注册工具。
    """
    def __init__(self, tools: list[Tool] = []):
        self.tools = tools
        self.tool_registry = self.registry()

    def tool_prompt(self, tool_name: str) -> str:
        """
        获取工具的提示信息。

        Args:
            tool_name (str): 工具名称。

        Returns:
            str: 工具的提示信息。
        """
        tool = self.tool_registry.get(tool_name)
        if tool is None:
            return f"工具 '{tool_name}' 未注册"
        return dedent(f"""
        Tool Name: {tool.name}
        Description: {tool.description}
        Parameters: {tool.params}
                      """)

    def registry(self):
        """
        注册所有工具，将工具名称映射到对应的 ToolData 实例。

        Returns:
            dict: 工具名称到 ToolData 实例的映射字典。
        """
        return {
            tool.name: ToolData(
                name=tool.name,
                description=tool.description,
                params=tool.args,
                function=tool.run
            ) for tool in self.tools
        }
    def get_tools_prompt(self) -> str:
        """
        生成一个格式化的字符串，列出所有可用工具及其提示信息。

        返回:
            str: 一个去除缩进的字符串，包含所有工具的名称和提示信息，每个工具之间用两个换行符分隔，标题为 'Available Tools:'。
        """
        tools_prompt = [self.tool_prompt(tool.name) for tool in self.tools]
        return dedent(f"""
        Available Tools:
        {'\n\n'.join(tools_prompt)}
        """)
    
    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """
        执行指定名称的工具，并返回结果。

        参数:
            tool_name (str): 工具名称。
            **kwargs: 传递给工具的参数。

        返回:
            ToolResult: 工具执行结果，包含是否成功、内容或错误信息。
        """
        tool = self.tool_registry.get(tool_name)
        if tool is None:
            return ToolResult(
                is_success=False,
                error=f"工具 '{tool_name}' 未注册"
            )
        try:
            content = tool.function(tool_input=kwargs)
            return ToolResult(is_success=True, content=content)
        except Exception as error:
            return ToolResult(is_success=False, error=str(error))

