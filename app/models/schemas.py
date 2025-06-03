
from pydantic import BaseModel, field_validator
from typing import Optional, Any, List

class PreAssessment(BaseModel):
    role: str
    pre_assessment_id: int

    @field_validator('role')
    @classmethod
    def role_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Please select a valid role')
        return v

    @field_validator('pre_assessment_id')
    @classmethod
    def id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('pre_assessment_id must be a positive integer')
        return v

class QueryResponse(BaseModel):
    status:str
    message:str
    data:Optional[Any] = None

class AnswerList(BaseModel):
    id:int
    correctAnswer:str

class  AssessmentSubmission(BaseModel):
    assessment_submission_id:int
    answers:List[AnswerList]

class ProjectAssessment(BaseModel):
    project_title:str
    assessment_title:str

    @field_validator("project_title")
    @classmethod
    def project_title_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Please enter a valid project title')
        return v
    @field_validator("assessment_title")
    @classmethod
    def assessment_title_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Please enter a valid assessment title')
        return v

class UpdateProjectFiles(BaseModel):
    project_id:int
    project_title:str
    
    @field_validator("project_title")
    @classmethod
    def project_title_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Please enter a valid project title')
        return v

