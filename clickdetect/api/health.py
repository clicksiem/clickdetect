from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("/ok")
def isOk():
    return {"ok": True}
