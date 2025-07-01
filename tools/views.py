from pydantic import BaseModel,Field
from typing import Literal, Optional, Union, List, Any
import pandas as pd

class SharedBaseModel(BaseModel):
    """
    SharedBaseModel 是一个基础模型类，继承自 BaseModel。
    该模型的 Config 配置中设置了 extra='allow'，表示在模型初始化时允许包含未在模型字段中声明的额外字段。
    """
    class Config:
        extra='allow'


class Done(SharedBaseModel):
    """
    Done 是用于指示任务已完成的模型。

    用途：
        - 该模型用于代理或工具在任务执行完毕后，向用户返回最终结果或结论。
        - answer 字段通常包含详细的任务完成说明、结果总结或最终输出，格式为 Markdown，便于前端直接渲染。

    字段说明：
        answer (str): 
            - 需要用规范的 Markdown 格式，详细描述任务完成情况、结果、结论或最终输出内容。
    """
    answer:str = Field(...,description="the detailed final answer to the user query in proper markdown format",examples=["The task is completed successfully."])

class HumanTool(SharedBaseModel):
    """
    HumanTool 是用于与人类用户交互的模型。

    用途：
        - 当自动化流程无法继续，需要人工决策、补充信息或确认时，使用该模型向用户发起提问。
        - 适用于需要人类输入、选择、确认等场景。

    字段说明：
        question (str):
            - 需要向用户提出的具体问题或请求，内容应简明清晰，便于用户理解和作答。
    """
    question: str = Field(..., description="The question to be answered by the human user", examples=["What should I do next?"])

class LoadDataFrame(SharedBaseModel):
    """
    LoadDataFrame 是用于从文件加载 DataFrame 的参数模型。

    用途：
        - 用于指定如何从本地文件（如 Excel、CSV 等）加载数据到 DataFrame，并注册到全局对象池，供后续数据处理工具使用。
        - 支持指定表名、工作表、表头行等，适配多种数据源格式。

    字段说明：
        df_name (str):
            - 指定加载后 DataFrame 在全局注册表中的名称，后续操作可通过该名称引用此数据对象。
        file_path (str):
            - 要加载的数据文件的完整路径，支持绝对路径或相对路径。
            - 支持 Excel（.xlsx）、CSV 等常见格式。
        sheet_name (Optional[Union[str, int]]):
            - Excel 文件时指定工作表名（如 'Sheet1'）或索引（0 表示第一个 sheet）。
        origin_header_row (int):
            - 指定原始表格中哪一行为表头（0 表示第一行，1 表示第二行，以此类推）。
            - 该行内容将作为 DataFrame 的列名，表头行本身不会出现在数据部分。

    注意事项：
        - 如果 origin_header_row 设置不正确，可能导致数据错位或表头识别异常。
        - sheet_name 仅对 Excel 文件有效，CSV 文件请勿设置。
        - df_name 必须唯一，否则会覆盖已注册的同名 DataFrame。
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be created", examples=["my_dataframe"])
    file_path: str = Field(..., description="The path to the file to be loaded", examples=["/path/to/file.csv"])
    sheet_name: Optional[Union[str, int]] = Field(0, description="Sheet name or index (0 means the first sheet)", examples=["Sheet1", 0])
    origin_header_row: int = Field(0, description="The row numbers used as headers in the original table, 0 means the first row", examples=[10])


class ExcelHead(SharedBaseModel):
    """
    ExcelHead 是用于获取 Excel 文件前几行数据的参数模型。

    用途：
        - 用于读取指定 Excel 文件的前若干行数据，常用于预览表格结构、快速查看数据内容。
        - 适合在数据加载前，先让用户确认表头、数据格式或内容示例。

    字段说明：
        file_path (str):
            - 需要读取的 Excel 文件的完整路径，支持绝对路径或相对路径。
        head (int):
            - 指定要返回的前几行数据的行数（从表格第一行开始计数）。

    注意事项：
        - 只支持 Excel 文件（如 .xlsx），不支持 CSV 等其它格式。
        - 返回的数据通常用于预览，不建议用于正式数据处理。
    """
    file_path: str = Field(..., description="The path to the Excel file", examples=["/path/to/file.xlsx"])
    head: int = Field(..., description="The number of rows to return from the top of the DataFrame", examples=[10])

class ExcelInfo(SharedBaseModel):
    """
    ExcelInfo 是用于获取 Excel 文件信息的参数模型。

    用途：
        - 用于获取已加载 DataFrame 对象（通常由 Excel 文件加载而来）的基本信息，如行数、列数、列名、数据类型等。
        - 适合在数据分析、数据处理前，快速了解表格结构和数据分布。

    字段说明：
        df_name (str):
            - 需要获取信息的 DataFrame 对象名称，必须是已注册（已加载）的 DataFrame。

    注意事项：
        - df_name 必须对应已加载并注册的 DataFrame，否则无法获取信息。
        - 返回信息通常包括行数、列数、列名、每列数据类型等。
    """
    df_name: str = Field(..., description="The name of the DataFrame object to get information from", examples=["my_dataframe"])

class ReadDataFrame(SharedBaseModel):
    """
    ReadDataFrame 是用于从已加载的 DataFrame 中读取指定行/列数据的参数模型。

    用途：
        - 用于读取已注册（已加载）DataFrame 对象中的部分或全部数据，支持按行、按列、按单元格灵活读取。
        - 适合在数据分析、数据处理、数据导出等场景下，按需获取 DataFrame 的子集。

    字段说明：
        df_name (str):
            - 需要读取数据的 DataFrame 对象名称，必须是已注册（已加载）的 DataFrame。
        row (Optional[Union[int, List[int]]]):
            - 指定要读取的行号（从 0 开始计数），可以是单个整数或整数列表。
        col (Optional[Union[int, str, List[Union[int, str]]]]):
            - 指定要读取的列，可以是列索引（int）、列名（str）、或它们的列表。

    注意事项：
        - df_name 必须对应已加载并注册的 DataFrame，否则无法读取数据。
        - row 和 col 都为 None 时，返回整个 DataFrame 的所有数据。
        - row/col 支持混合索引和名称，便于灵活选取数据。
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be created", examples=["my_dataframe"])
    row: Optional[Union[int, List[int]]] = Field(None, description="The row number(s) to read from the DataFrame, None means all rows", examples=[0, [0, 1, 2]])
    col: Optional[Union[int, str, List[Union[int, str]]]] = Field(None, description="The column index or name(s) to read from the DataFrame, None means all columns", examples=[0, "Column1", "A", [0, "Column1", "A"]])

class WriteDataFrame(SharedBaseModel):
    """
    WriteDataFrame 是用于向已加载的 DataFrame 写入数据的参数模型。

    用途：
        - 用于将指定的值写入已注册（已加载）的 DataFrame 对象的指定位置（行、列或矩阵区域）。
        - 支持灵活指定写入起始行、起始列、步长、写入方向（按行、按列、按矩阵）等，适用于数据更新、批量填充、自动化表格处理等场景。

    字段说明：
        df_name (str):
            - 需要写入数据的 DataFrame 对象名称，必须是已注册（已加载）的 DataFrame。
        start_row (int):
            - 指定写入的起始行号（从0开始计数），0表示第一行。
        start_col (Optional[Union[int, str]]):
            - 指定写入的起始列，可以是列索引（int）、列名（str），或 None（表示第一列）。
        values (Union[Any, List[Any], List[List[Any]]]):
            - 要写入 DataFrame 的值，可以是单个值、一维列表（按行或按列写入）、或二维列表（按矩阵写入）。
        axis (Literal['row', 'column', 'matrix']):
            - 指定写入方向或方式：
                - 'row'：按行写入（每个元素写入一行的同一列）
                - 'column'：按列写入（每个元素写入一列的同一行）
                - 'matrix'：按矩阵区域写入（二维数据块）
        step (int):
            - 写入时的步长（即每次写入后跳过的行数或列数），用于间隔写入或特殊排布。

    注意事项：
        - df_name 必须对应已加载并注册的 DataFrame，否则无法写入数据。
        - start_row、start_col 支持 None，工具内部会自动处理为0或合适的起始位置。
        - values 的结构需与 axis 匹配，否则可能写入异常。
        - 写入越界（超出 DataFrame 行列范围）会报错。
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be written", examples=["my_dataframe"])
    start_row: int = Field(None, description="The row number to start writing from DataFrame Object, 0 means the first row", examples=[0])
    start_col: Optional[Union[int, str]] = Field(None, description="The column index or name to start writing from DataFrame Object, None means the first column", examples=[0, "A", "Column1"])
    values: Union[Any, List[Any], List[List[Any]]] = Field(..., description="The values to write to the DataFrame", examples=["New Value", 42, 3.14, True, ["Value1", "Value2"]])
    axis: Literal['row', 'column', 'matrix'] = Field(..., description="The axis to write the values to, 'row' means writing a row, 'column' means writing a column, 'matrix' means writing a matrix", examples=['row', 'column', 'matrix'])
    step: int = Field(1, description="The step number for writing, None means no specific step", examples=[1, 2])

class DataFrame2Excel(SharedBaseModel):
    """
    DataFrame2Excel 是用于将已加载的 DataFrame 对象导出为 Excel 文件的参数模型。

    用途：
        - 用于将指定名称的 DataFrame（已注册/已加载）对象保存为 Excel 文件，支持数据持久化、数据导出、数据共享等场景。
        - 常用于数据处理、分析后，将结果输出为标准 Excel 文件，便于后续查看、汇报或进一步处理。

    字段说明：
        df_name (str):
            - 需要导出的 DataFrame 对象名称，必须是已注册（已加载）的 DataFrame。
            - 工具会根据该名称在全局注册表中查找对应的 DataFrame，并将其内容写入 Excel 文件。

    注意事项：
        - df_name 必须对应已加载并注册的 DataFrame，否则无法导出。
        - 导出时会自动备份原 DataFrame 的数据，确保不会覆盖原有数据。
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be converted", examples=["my_dataframe"])

