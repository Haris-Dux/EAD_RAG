from fastapi import APIRouter, Request, Depends
from app.core.auth_jwt import verify_jwt
from app.controllers.update_vector_database import update_project_files
from app.models.schemas import UpdateProjectFiles

sync_files_router = APIRouter()

@sync_files_router.post("/updateprojectfiles")
async def query_rag(req:UpdateProjectFiles,request:Request,protected:None=Depends(dependency=verify_jwt,use_cache=False)):
  services = request.app.state.services
  db = request.app.state.db_connection
  return await update_project_files(req,services,db)
    