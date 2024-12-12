from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("",response_model=dict)
async def admin_index():
    return {"message": "Welcome to the admin panel!"}