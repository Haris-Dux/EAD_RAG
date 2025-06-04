from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.pre_assessment import pre_assessment_router 
from app.api.update_vector_database import sync_files_router
from app.api.project_assessment import project_assessment_router
from app.api.personality_assessment import personality_assessment_router
from app.core.error_handlers import register_exception_handlers
from app.core.config import Config
from app.core.services_initializer import servicesContainer
from app.database.connection import get_db_connection



Config.validate()
app = FastAPI()
services_container = servicesContainer()

@app.on_event("startup")
async def startup_event():
    services_container.initialize_services()
    app.state.services = services_container
    app.state.db_connection =  get_db_connection()
    
register_exception_handlers(app)
origins = [
    "http://localhost:5173",
    "https://taskproject.site",
    "https://dev.taskproject.site",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(pre_assessment_router, prefix="/pre-assessment")
app.include_router(project_assessment_router, prefix="/project-assessment")
app.include_router(sync_files_router, prefix="/update-files")
app.include_router(personality_assessment_router, prefix="/career-consultancy")


