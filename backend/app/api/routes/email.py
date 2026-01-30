# backend/routers/emails.py
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from jsonschema import ValidationError, validate

# May delete later this was mainly for testing email parsing logic and how to encorporate it into FastAPI
# TODO: update docstrings

APP_DIR = Path(__file__).resolve().parents[2]  # backend/app
SCHEMA_PATH = (
    APP_DIR / "schema" / "email_schema.json"
)  # backend/app/schema/email_schema.json

router = APIRouter(prefix="/email", tags=["email"])


def load_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail=f"Schema file not found: {schema_path}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Schema file is not valid JSON: {e}"
        )


def parse_eml_bytes(eml_bytes: bytes) -> Dict[str, Any]:
    # Parse email message
    message = BytesParser(policy=policy.default).parsebytes(eml_bytes)

    # Extract body content
    text_body = ""
    html_body = ""

    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            disp = (part.get("Content-Disposition") or "").lower()

            # Skip attachments in body extraction
            if "attachment" in disp:
                continue

            if ctype == "text/plain" and not text_body:
                text_body = part.get_content() or ""
            elif ctype == "text/html" and not html_body:
                html_body = part.get_content() or ""
    else:
        ctype = message.get_content_type()
        content = message.get_content() or ""
        if ctype == "text/html":
            html_body = content
        else:
            text_body = content

    parsed_email: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "email_id": "123456",  # TODO: replace with real ID logic
        "headers": {
            "from": message.get("From"),
            "to": message.get("To"),
            "subject": message.get("Subject"),
            "date": message.get("Date"),
            "other_headers": {},
        },
        "body": {"text": text_body, "html": html_body},
        "urls": [],  # TODO: extract URLs from text/html
        "attachments": [],  # TODO: collect attachment metadata
        "metadata": {
            "parser_version": "0.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }

    return parsed_email


def validate_email_payload(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    try:
        validate(instance=payload, schema=schema)
    except ValidationError as e:
        # Return a 422 since the payload doesn't conform
        raise HTTPException(
            status_code=422, detail=f"Schema validation failed: {e.message}"
        )


@router.post("/parse")
async def parse_email(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload an .eml file and get back the parsed+validated JSON payload.
    """
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Please upload a .eml file")

    eml_bytes = await file.read()
    if not eml_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file was empty")

    schema = load_schema()
    payload = parse_eml_bytes(eml_bytes)
    validate_email_payload(payload, schema)

    return payload


@router.get("/parse/sample")
def parse_sample(server_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper for local testing: parse an .eml from disk. May be removed later.
    """
    if not server_path:
        raise HTTPException(
            status_code=400,
            detail="Provide ?server_path=/absolute/or/relative/path.eml",
        )

    path = Path(server_path).expanduser().resolve()
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if path.suffix.lower() != ".eml":
        raise HTTPException(
            status_code=400, detail="server_path must point to a .eml file"
        )

    schema = load_schema()
    payload = parse_eml_bytes(path.read_bytes())
    validate_email_payload(payload, schema)

    return payload
