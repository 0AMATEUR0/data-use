import json
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

def convert_json_to_markdown(json_path: str, output_md_path: str = None):
    """
    将 JSON 文件转换为 Markdown 格式的文件。

    Args:
        json_path (str): 输入的 JSON 文件路径。
        output_md_path (Optional[str]): 输出的 Markdown 文件路径。如果未提供，则使用输入文件名加上 .md 后缀。
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"未找到JSON文件: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = ["# 对话记录\n"]

    for i, round_data in enumerate(data, start=1):
        lines.append(f"\n## 对话轮次 {i}\n")
        for role in ['user', 'planner', 'agent', 'evaluator']:
            if role in round_data and round_data[role]:
                role_name = role.capitalize()
                lines.append(f"**{role_name}**:\n\n{round_data[role]}\n")

    md_text = "\n".join(lines)

    # 如果未指定输出路径，则按时间自动生成
    if not output_md_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_md_path = f"memory_export_{timestamp}.md"

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"✅ Markdown 文件已保存至: {output_md_path}")



class Dialog(BaseModel):
    """
    对话模型，包含对话的基本信息和内容。

    Args:
        user (str): 用户名，表示对话的发起者。
        planner (Optional[str]): 规划者的用户名，表示对话的规划者。可选参数。
        agent (Optional[str]): 代理人的用户名，表示对话的执行者。可选参数。
        evaluator (Optional[str]): 评估者的用户名，表示对话的评估者。可选参数。
    """
    user: str
    planner: Optional[str] = None
    agent: Optional[str] = None
    evaluator: Optional[str] = None