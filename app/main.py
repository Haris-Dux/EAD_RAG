from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.error_handlers import register_exception_handlers
from app.core.config import Config
from app.core.services_initializer import servicesContainer



Config.validate()
app = FastAPI()
servicees_container = servicesContainer()

@app.on_event("startup")
async def startup_event():
    servicees_container.initialize_services()
    app.state.services = servicees_container
    

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
app.include_router(router)
