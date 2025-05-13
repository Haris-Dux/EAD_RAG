from app.models.schemas import  QueryResponse, PreAssessment
from app.services.pre_assessment import update_preassessment_data, generate_preassessment_for_role
from app.utils.responses import success_response


async def update_preassessment_pdf(services,file,roleName) -> QueryResponse:
    result = await update_preassessment_data(services,file,roleName)  
    return success_response(result,"knowledge base updated successfully.")

async def generate_pre_assessment (req:PreAssessment,services) -> QueryResponse:
    result = await generate_preassessment_for_role(req,services)
    return success_response(result,"Pre assessment generated successfully.")