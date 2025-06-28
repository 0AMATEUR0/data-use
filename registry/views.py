from pydantic import BaseModel
from typing import Callable

class Tool(BaseModel):
    """
    Tool 类用于表示一个具有特定功能的工具及其相关元数据。

    属性:
        name (str): 工具的名称。
        description (str): 工具的详细描述，说明其用途和功能。
        function (Callable): 实现该工具功能的可调用对象（函数）。
        params (dict): 包含该函数所需参数的字典，键为参数名，值为参数的描述或默认值。
    """
    name: str
    description: str
    function: Callable
    params: dict

class ToolResult(BaseModel):
    """
    ToolResult 用于表示工具操作的结果。

    属性:
        is_success (bool): 操作是否成功。True 表示成功，False 表示失败。
        content (str | None): 操作成功时返回的内容，默认为 None。
        error (str | None): 操作失败时的错误信息，默认为 None。

    用法示例:
        result = ToolResult(is_success=True, content="操作成功")
        if result.is_success:
            print(result.content)
        else:
            print(result.error)
    """
    is_success: bool
    content: str | None = None
    error: str | None = None