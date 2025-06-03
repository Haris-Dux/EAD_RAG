
from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from app.controllers.pre_assessment import update_preassessment_pdf, generate_pre_assessment, submit_pre_assessment
from app.models.schemas import PreAssessment,AssessmentSubmission
from app.core.auth_jwt import verify_jwt

pre_assessment_router = APIRouter()

@pre_assessment_router.post("/update-preassessment-pdf")
async def query_rag(services:Request,file:UploadFile = File(...),roleName:str=Form(...),protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  return await update_preassessment_pdf(services.app.state.services,file,roleName)

@pre_assessment_router.post("/generate-pre-assessment")
async def query_rag(req:PreAssessment,request:Request,protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  services = request.app.state.services
  db = request.app.state.db_connection
  return await generate_pre_assessment (req,services,db)

@pre_assessment_router.post("/submit-assessment")
async def query_rag(req:AssessmentSubmission,request:Request,protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  db = request.app.state.db_connection
  return await submit_pre_assessment (req,db)