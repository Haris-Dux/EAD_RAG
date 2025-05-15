from app.models.schemas import  QueryResponse, PreAssessment
from app.services.pre_assessment import update_preassessment_data, generate_preassessment_for_role
from app.utils.responses import success_response,error_response
from fastapi import HTTPException


async def update_preassessment_pdf(services,file,roleName) -> QueryResponse:
     try:
         result = await update_preassessment_data(services,file,roleName)  
         return success_response(result,"knowledge base updated successfully.")
     except Exception as error:
        return error_response(message=error)

async def generate_pre_assessment (req:PreAssessment,services) -> QueryResponse:
    try:
        result = await generate_preassessment_for_role(req,services)
        return success_response(result,"Pre assessment generated successfully.")
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail, status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error), status_code=500)