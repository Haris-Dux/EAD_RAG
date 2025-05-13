
from pydantic import BaseModel,field_validator
from typing import Optional, Any

class PreAssessment(BaseModel):
    role:str
    @field_validator('role')
    @classmethod
    def role_cannot_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Please select a valid role')
        return v

class QueryResponse(BaseModel):
    status:str
    message:str
    data:Optional[Any] = None