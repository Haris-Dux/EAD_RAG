

from app.utils.responses import success_response,error_response, file_response
from app.services.personality_assessment import generate_personality_assessment_pdf
from fastapi import HTTPException

async def generate_personality_assessment_report(req,services):
    try:
        pdf = await generate_personality_assessment_pdf(req,services)
        return file_response(pdf)
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail,status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error), status_code=500) 
