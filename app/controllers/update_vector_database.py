from app.utils.responses import success_response,error_response
from fastapi import HTTPException
from app.services.update_vector_database import sync_project_files


async def update_project_files(req,services,db):
    try:
        data = await sync_project_files(req,services,db)
        return success_response(data,"Files updated successfully")
    except HTTPException as http_exc:
        return error_response(message=http_exc.detail,status_code=http_exc.status_code)
    except Exception as error:
        return error_response(message=str(error),status_code=500)
