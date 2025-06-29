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
    Done is a model for indicating that a task is completed.
    """
    answer:str = Field(...,description="the detailed final answer to the user query in proper markdown format",examples=["The task is completed successfully."])

class HumanTool(SharedBaseModel):
    """
    HumanTool is a model for human input.
    """
    question: str = Field(..., description="The question to be answered by the human user", examples=["What should I do next?"])

class LoadDataFrame(SharedBaseModel):
    """
    LoadDataFrame is a model for loading a DataFrame from a file.
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be created", examples=["my_dataframe"])
    file_path: str = Field(..., description="The path to the file to be loaded", examples=["/path/to/file.csv"])
    sheet_name: Optional[Union[str, int]] = Field(0, description="Sheet name or index (0 means the first sheet)", examples=["Sheet1", 0])
    origin_header_row: int = Field(0, description="The row numbers used as headers in the original table, 0 means the first row", examples=[10])

class ExcelHead(SharedBaseModel):
    """
    ExcelHead is a model for getting the first few rows of an Excel file.
    """
    file_path: str = Field(..., description="The path to the Excel file", examples=["/path/to/file.xlsx"])
    head: int = Field(..., description="The number of rows to return from the top of the DataFrame", examples=[10])

class ExcelInfo(SharedBaseModel):
    """
    ExcelInfo is a model for getting information about an Excel file.
    """
    df_name: str = Field(..., description="The name of the DataFrame object to get information from", examples=["my_dataframe"])

class ReadDataFrame(SharedBaseModel):
    """
    ReadDataFrame is a model for reading a DataFrame from a file.
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be created", examples=["my_dataframe"])
    row: Optional[Union[int, List[int]]] = Field(None, description="The row number(s) to read from the DataFrame, None means all rows", examples=[0, [0, 1, 2]])
    col: Optional[Union[int, str, List[Union[int, str]]]] = Field(None, description="The column index or name(s) to read from the DataFrame, None means all columns", examples=[0, "Column1", "A", [0, "Column1", "A"]])

class WriteDataFrame(SharedBaseModel):
    """
    WriteDataFrame is a model for writing a DataFrame to a file.
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be written", examples=["my_dataframe"])
    start_row: int = Field(None, description="The row number to start writing from DataFrame Object, 0 means the first row", examples=[0])
    start_col: Optional[Union[int, str]] = Field(None, description="The column index or name to start writing from DataFrame Object, None means the first column", examples=[0, "A", "Column1"])
    values: Union[Any, List[Any], List[List[Any]]] = Field(..., description="The values to write to the DataFrame", examples=["New Value", 42, 3.14, True, ["Value1", "Value2"]])
    axis: Literal['row', 'column', 'matrix'] = Field(..., description="The axis to write the values to, 'row' means writing a row, 'column' means writing a column, 'matrix' means writing a matrix", examples=['row', 'column', 'matrix'])
    step: int = Field(1, description="The step number for writing, None means no specific step", examples=[1, 2])

class DataFrame2Excel(SharedBaseModel):
    """
    DataFrame2Excel is a model for converting a DataFrame to an Excel file.
    """
    df_name: str = Field(..., description="The name of the DataFrame object to be converted", examples=["my_dataframe"])

