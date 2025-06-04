
from fastapi import APIRouter, Request, Depends
from app.models.schemas import ProjectAssessment
from app.core.auth_jwt import verify_jwt
from app.controllers.project_assessment import generate_project_assessment

project_assessment_router = APIRouter()


@project_assessment_router.post("/generate-project-assessment")
async def query_rag(req:ProjectAssessment,request:Request,protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  services = request.app.state.services
  db = request.app.state.db_connection
  return await generate_project_assessment (req,services,db)

