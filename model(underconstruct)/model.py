from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage

from model.base import BaseModel

class GPTModel(BaseModel):
    def __init__(self, api_key: str, base_url: Optional[str] = None, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.0,
        )

    def _convert_history(self, history: Optional[List[Dict[str, str]]]) -> List:
        messages = []
        if not history:
            return messages
        for item in history:
            role = item["role"]
            content = item["content"]
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
        return messages

    def chat(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        messages = self._convert_history(history)
        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages)

        return {
            "role": "assistant",
            "content": response.content,
            "tool_calls": getattr(response, "tool_calls", None),
        }


class DeepSeekModel(GPTModel):
    def __init__(self, api_key: str, base_url: str, model_name: str = "deepseek-chat"):
        super().__init__(api_key=api_key, base_url=base_url, model_name=model_name)
