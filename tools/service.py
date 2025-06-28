from tools.views import Done
from langchain.tools import tool
from typing import Literal
from tools.views import *
import pandas as pd
import json

@tool('Done Tool', args_schema=Done)
def done_tool(answer: str):
    """
    表明任务已完成的工具。
    """
    return answer

@tool('Excel to JSON Tool', args_schema=Excel2Json)
def excel2json_tool(file_path: str, sheet_name: str, header_row: int, output_path: str):
    """
    将 Excel 文件转换为 JSON 格式的工具。
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    df.to_json(output_path, orient='records', force_ascii=False)
    return f"Excel file '{file_path}' converted to JSON and saved to '{output_path}'"

@tool('JSON to Excel Tool', args_schema=Json2Excel)
def json2excel_tool(file_path: str, output_path: str):
    """
    将 JSON 文件转换为 Excel 格式的工具。
    """
    df = pd.read_json(file_path, orient='records')
    df.to_excel(output_path, index=False)
    return f"JSON file '{file_path}' converted to Excel and saved to '{output_path}'"

@tool('Get JSON Data Tool', args_schema=GetJsonData)
def get_json_data_tool(file_path: str) -> list:
    """
    从 JSON 文件中获取数据的工具。
    """
    df = pd.read_json(file_path, orient='records')
    json_data = df.to_dict(orient='records')
    return f"Data from JSON file '{file_path}': \n{json.dumps(json_data, indent=2, ensure_ascii=False)}"

# Todo: 这个读取json数据有上下文爆炸的问题

