import os
import json
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from memory.views import Dialog, convert_json_to_markdown

class Memory(BaseModel):
    """
    记忆管理器，储存对话历史

    Args：
        max_memory (int): 最大记忆数量, 默认10, 最小值为1
        messages (List[Dialog]): 对话列表, 默认空列表
        file_dir (Optional[str]): 文件目录, 用于存储对话记录, 默认None
    """
    max_memory: int = Field(default=10, ge=1, description="最大记忆数量")
    messages: List[Dialog] = []
    file_dir: Optional[str] = None
        
    def add_message(self, role:str, content: str):
        """
        添加消息到记忆中

        Args:
            role (str): 消息角色, 如 'user', 'planner', 'agent', 'evaluator'
            content (str): 消息内容
        """
        role = role.lower()
        if role not in ['user', 'planner', 'agent', 'evaluator']:
            raise ValueError("角色类型必须是 'user', 'planner', 'agent' 或 'evaluator'。")
        
        if not self.messages or role == 'user':
            # 如果是用户消息或第一次添加消息，则创建新的对话
            if len(self.messages) >= self.max_memory:
                removed = self.messages.pop(0)
                if self.file_dir:
                    self._clean_old_files()
            self.messages.append(Dialog(**{role: content}))
        else:
            # 否则，更新现有对话
            last_dialog = self.messages[-1] # 获取最后一个对话
            setattr(last_dialog, role, content) # 设置对应角色的消息内容
            self.messages[-1] = last_dialog # 更新对话
        
        if self.file_dir:
            self.save_file()

    def save_file(self):
        """
        保存对话到文件
        """
        if not self.file_dir:
            raise ValueError("file_dir 未设置，无法保存文件。")
        data = [msg.model_dump() for msg in self.messages]
        with open(self.file_dir, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_file(self):
        """
        从文件加载对话
        """
        if not self.file_dir or not os.path.exists(self.file_dir):
            raise ValueError("file_dir 未设置或文件不存在，无法加载文件。")
        with open(self.file_dir, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.messages = [Dialog(**msg) for msg in data]

    def get_recent(self, n: int = 1) -> List[Dialog]:
        """
        获取最近的 n 条对话

        Args:
            n (int): 要获取的对话数量, 默认1

        Returns:
            List[Dialog]: 最近的 n 条对话
        """
        return self.messages[-n:] if n <= len(self.messages) else self.messages
    
    def get_all(self) -> List[Dialog]:
        """
        获取所有对话

        Returns:
            List[Dialog]: 所有对话
        """
        return self.messages
    
    def clear(self):
        """
        清除所有对话
        """
        self.messages = []
        if self.file_dir and os.path.exists(self.file_dir):
            os.remove(self.file_dir)

    def __repr__(self):
        return f"<Memory: {len(self.messages)} round stored>"
    
if __name__ == "__main__":
    mem = Memory(max_memory=3, file_dir='memory.json')

    mem.add_message('user', '请读取A1单元格的内容')
    mem.add_message('planner', '使用Excel Tool读取A1单元格')
    mem.add_message('agent', '读取A1单元格的内容为：Hello World')
    mem.add_message('evaluator', '确认读取结果正确')

    mem.add_message('user', '请读取B1单元格的内容')
    mem.add_message('planner', '使用Excel Tool读取B1单元格')
    mem.add_message('agent', '读取B1单元格的内容为：Hello World')
    mem.add_message('evaluator', '确认读取结果正确')

    mem.add_message('user', '请读取C1单元格的内容')

    print(mem)
    print(mem.get_recent(1))
    print(mem.get_all())

    convert_json_to_markdown('memory.json', 'memory_export.md')

    