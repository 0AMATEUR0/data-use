from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class BaseModel(ABC):
    @abstractmethod
    def chat(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        pass