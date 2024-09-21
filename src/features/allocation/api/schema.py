from enum import Enum
from pydantic import BaseModel, Field
class Message(BaseModel):
    message: str = Field(..., example="hello world")

class ConceptEnum(str, Enum):
    EA = "EA"
    EC = "EC"
    EE1 = "EE1"
    EE2 = "EE2"
    
class ClientStatistics(BaseModel):
    client_id: int
    total_consumed: float
    total_injected: float
