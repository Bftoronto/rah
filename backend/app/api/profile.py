from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_profile():
    return {"msg": "profile stub"}

@router.put('/')
def update_profile():
    return {"msg": "update profile stub"} 