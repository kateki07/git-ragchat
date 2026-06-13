from fastapi import APIRouter

router = APIRouter(tags=["chat"],prefix="/chat")

@router.get("/")
def get_chat():
    return {"message": "This is a chat endpoint"}


