from app.utils.responses import success_response,error_response
from app.services.project_assessment import generate_project_assessment as generate_assessment_service
from fastapi import HTTPException

async def generate_project_assessment(req,services,db):
    try:
        data = await generate_assessment_service(req,services,db)
        return success_response(data,"Assessment generated successfull")
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail,status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error), status_code=500) 
