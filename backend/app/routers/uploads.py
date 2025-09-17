import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import get_db
from ..models import Business


router = APIRouter()


def save_file(file: UploadFile, subdir: str) -> str:
    os.makedirs(os.path.join(settings.upload_dir, subdir), exist_ok=True)
    filename = file.filename or "upload.bin"
    path = os.path.join(settings.upload_dir, subdir, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


@router.post("/business/{business_id}/logo")
def upload_business_logo(business_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    path = save_file(file, f"business_{business_id}")
    business.logo_path = path
    db.commit()
    return {"path": path}


@router.post("/business/{business_id}/signature")
def upload_manager_signature(business_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    path = save_file(file, f"business_{business_id}")
    business.manager_signature_path = path
    db.commit()
    return {"path": path}

