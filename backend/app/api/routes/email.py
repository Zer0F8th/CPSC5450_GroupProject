from fastapi import APIRouter, UploadFile, File, HTTPException
from jsonschema import ValidationError

from app.services.email_parser import parse_eml_bytes, validate_payload

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/parse")
async def parse_email(file: UploadFile = File(...)):
    # Ensure filename exists AND is a string
    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(400, "Uploaded file has no filename")

    if not file.filename.lower().endswith(".eml"):
        raise HTTPException(400, "Please upload a .eml file")

    eml_bytes = await file.read()
    if not eml_bytes:
        raise HTTPException(400, "Uploaded file was empty")

    payload = parse_eml_bytes(eml_bytes)

    try:
        validate_payload(payload)
    except ValidationError as e:
        raise HTTPException(422, f"Schema validation failed: {e.message}")

    return payload