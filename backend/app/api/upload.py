from fastapi import APIRouter

router = APIRouter()

@router.post('/')
def upload_file():
    return {"msg": "upload stub"} 