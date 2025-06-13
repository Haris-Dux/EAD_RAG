
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Any, List

class StrictBaseModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def no_empty_strings(cls, values: dict[str, Any]) -> dict[str, Any]:
        for field, value in values.items():
            if isinstance(value, str) and value.strip() == '':
                raise ValueError(f"Field '{field}' cannot be an empty.")
        return values

class PreAssessment(StrictBaseModel):
    role: str
    pre_assessment_id: int

    @field_validator('pre_assessment_id')
    @classmethod
    def id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Pre_Assessment Id must be a valid Id')
        return v

class QueryResponse(BaseModel):
    status:str
    message:str
    data:Optional[Any] = None

class AnswerList(BaseModel):
    id:int
    correctAnswer:str

class AssessmentSubmission(BaseModel):
    assessment_submission_id:int
    answers:List[AnswerList]

class ProjectAssessment(StrictBaseModel):
    project_title:str
    assessment_title:str

class UpdateProjectFiles(StrictBaseModel):
    project_id:int
    project_title:str

    @field_validator('project_id')
    @classmethod
    def id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Project Id must be a valid id')
        return v
    
class PersonalityAssessment(StrictBaseModel):
  name:str
  personality_type:str
  selected_interests:List[str]
  preferred_role:str
  career_level:str

class Deliverables(BaseModel):
    dataSpreadsheet: str
    aiCharts: str
    dataInsights: str

class SubmitProjectAssessment(AssessmentSubmission):
    assessment_title:str
    assessment_id:int
    project_title:str
    deliverables: Deliverables
    