from app.utils.responses import success_response,error_response
from app.services.project_assessment import generate_assessment_for_project,evaluate_project_assessment
from fastapi import HTTPException

async def generate_project_assessment(req,services,db):
    try:
        data = await generate_assessment_for_project(req,services,db)
        return success_response(data,"Assessment generated successfully")
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail,status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error), status_code=500) 
    
async def submit_project_assessment(req,services,db,user):
    try:
        await evaluate_project_assessment(req,services,db,user)
        return success_response("Assessment submitted successfully")
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail,status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error), status_code=500) 
