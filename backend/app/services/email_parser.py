import json
from pathlib import Path
from email import policy
from email.parser import BytesParser
from jsonschema import validate, ValidationError
from datetime import datetime, timezone
from fastapi import HTTPException

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "email_schema.json"

def load_schema():
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except FileNotFoundError:
        # Return a clear HTTP error if the schema file is missing
        raise HTTPException(
            status_code=500,
            detail="Schema file not found.",
        )
    except json.JSONDecodeError:
        # Return a clear HTTP error if the schema JSON is invalid
        raise HTTPException(
            status_code=500,
            detail="Invalid schema JSON.",
        )

def parse_eml_bytes(eml_bytes: bytes) -> dict:
    message = BytesParser(policy=policy.default).parsebytes(eml_bytes)

    # Extract parts
    text_body = ""
    html_body = ""
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disp:
                continue
            if ctype == "text/plain" and not text_body:
                text_body = part.get_content() or ""
            elif ctype == "text/html" and not html_body:
                html_body = part.get_content() or ""
    else:
        content = message.get_content() or ""
        if message.get_content_type() == "text/html":
            html_body = content
        else:
            text_body = content

    return {
        "schema_version": "1.0.0",
        "email_id": "123456", #TODO make filenames unique
        "headers": {
            "from": message.get("From"),
            "to": message.get("To"),
            "subject": message.get("Subject"),
            "date": message.get("Date"),
            "other_headers": {}
        },
        "body": {"text": text_body, "html": html_body},
        "urls": [],
        "attachments": [],
        "metadata": {
            "parser_version": "0.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

def validate_payload(payload: dict):
    schema = load_schema()
    validate(instance=payload, schema=schema)