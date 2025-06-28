from pydantic import BaseModel,Field
from typing import Literal, Optional, Union

class SharedBaseModel(BaseModel):
    """
    SharedBaseModel 是一个基础模型类，继承自 BaseModel。
    该模型的 Config 配置中设置了 extra='allow'，表示在模型初始化时允许包含未在模型字段中声明的额外字段。
    """
    class Config:
        extra='allow'


class Done(SharedBaseModel):
    """
    Done 是一个用于表示任务完成的参数模型。
    """
    answer:str = Field(...,description="the detailed final answer to the user query in proper markdown format",examples=["The task is completed successfully."])


class Excel2Json(SharedBaseModel):
    """
    Excel2Json 是一个用于将 Excel 文件转换为 JSON 格式的参数模型。
    """
    file_path: str = Field(..., description="The path to the Excel file to be converted", examples=["/path/to/excel/file.xlsx"])
    sheet_name: Optional[Union[str, int]] = Field(..., description="Sheet name or index (0 means the first sheet)", examples=["Sheet1", 0])
    header_row: int = Field(1, description="The row number to use as the header, 1 means the first row", examples=[10])
    output_path: str = Field(..., description="The path where the output JSON file will be saved", examples=["/path/to/output/file.json"])

class Json2Excel(SharedBaseModel):
    """
    Json2Excel 是一个用于将 JSON 格式转换为 Excel 文件的参数模型。
    """
    file_path: str = Field(..., description="The path to the JSON file to be converted", examples=["/path/to/json/file.json"])
    output_path: str = Field(..., description="The path where the output Excel file will be saved", examples=["/path/to/output/file.xlsx"])

class GetJsonData(SharedBaseModel):
    """
    GetJsonData 是一个用于获取 JSON 数据的参数模型。
    """
    file_path: str = Field(..., description="The path to the JSON file to be read", examples=["/path/to/json/file.json"])