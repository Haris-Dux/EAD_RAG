
from fastapi import APIRouter, Request
from app.controllers.personality_assessment import generate_personality_assessment_report
from app.models.schemas import PersonalityAssessment


personality_assessment_router = APIRouter()

@personality_assessment_router.post("/genertae-personality-assessment-report")
async def query_rag(req:PersonalityAssessment,request:Request):
    services = request.app.state.services
    return await generate_personality_assessment_report (req,services)