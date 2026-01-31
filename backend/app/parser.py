import os
from email import policy
from email.parser import BytesParser
import json
from jsonschema import validate, ValidationError
import logging

# Initalize Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Set more dynamics File Paths. TODO make more robust file paths
# Designate import file path TODO: make dynamic
full_path = os.path.realpath(__file__)
dir_path = os.path.dirname(full_path)
json_path = f"{dir_path}/schema/email_schema.json"
file_path = f"{dir_path}/input/UTC ACM's First Meeting of the Semester!.eml"

logging.debug(f"[*] Full File Path: {full_path}\n")
logging.debug(f"[*] Directory File Path: {full_path}\n")
logging.debug(f"[*] Email File Path: {full_path}\n")
logging.debug(f"[*] EML File Path: {full_path}\n")

# Open the schema file for email messages
with open(json_path, "r") as schema_file:
    schema = json.load(schema_file)

# Convert email file into email message object
with open(file_path, "rb") as fp:
    message = BytesParser(policy=policy.default).parse(fp)

# Create a dictionary that matches the schema
parsed_email = {
    "schema_version": "1.0.0",
    "email_id": "123456",
    "headers": {
        "from": message.get("From"),
        "to": message.get("To"),
        "subject": message.get("Subject"),
        "date": message.get("Date"),
        "other_headers": {},
    },
    "body": {"text": "", "html": ""},
    "urls": [],
    "attachments": [],
    "metadata": {"parser_version": "0.1.0", "timestamp": "2026-01-26T00:00:00Z"},
}

# Validate parsed email against schema
try:
    validate(instance=parsed_email, schema=schema)
except ValidationError as e:
    print("Schema validation failed:", e)
    raise

# Designate output filepath and make folder if it does not exist
folder_path = "output"
file_path = os.path.join(folder_path, "data.json")
os.makedirs(folder_path, exist_ok=True)

# Write the list to a json file TODO: make location dynamic, make each filename unique
try:
    with open("output/data.json", "w") as outfile:
        json.dump(parsed_email, outfile, indent=2)
except IOError as e:
    print(f"An error occurred while writing to the file: {e}")
except TypeError as e:
    print(f"An error occurred while serializing data: {e}")
