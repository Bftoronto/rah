from pydantic import BaseModel
from typing import Any, Dict

class FrontendError(BaseModel):
    type: str
    data: Dict[str, Any] 