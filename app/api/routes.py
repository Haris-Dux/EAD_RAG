
from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from app.controllers.pre_assessment import update_preassessment_pdf, generate_pre_assessment, submit_assessment
from app.models.schemas import PreAssessment,AssessmentSubmission
from app.core.auth_jwt import verify_jwt

router = APIRouter()

@router.post("/pre-assessment/update-preassessment-pdf")
async def query_rag(services:Request,file:UploadFile = File(...),roleName:str=Form(...),protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  return await update_preassessment_pdf(services.app.state.services,file,roleName)

@router.post("/pre-assessment/generate-pre-assessment")
async def query_rag(req:PreAssessment,request:Request):
  services = request.app.state.services
  db = request.app.state.db_connection
  return await generate_pre_assessment (req,services,db)

@router.post("/assessment/submit-assessment")
async def query_rag(req:AssessmentSubmission,request:Request):
  db = request.app.state.db_connection
  return await submit_assessment (req,db)