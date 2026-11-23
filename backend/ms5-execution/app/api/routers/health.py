from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["Supervision"])


@router.get("/health", summary="État du service et de la base")
def health(session: Session = Depends(get_db)):
    try:
        session.execute(text("SELECT 1"))
        db = "UP"
    except Exception:  # noqa: BLE001
        db = "DOWN"
    status = "UP" if db == "UP" else "DOWN"
    return JSONResponse(
        status_code=200 if status == "UP" else 503,
        content={"status": status, "components": {"db": {"status": db}}},
    )
