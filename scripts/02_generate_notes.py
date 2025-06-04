import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("assistant_id.txt") as f:
    assistant_id = f.read().strip()

with open("file_id.txt") as f:
    file_id = f.read().strip()


class Note(BaseModel):
    id: int = Field(..., ge=1, le=10)
    heading: str = Field(..., example="Mean Value Theorem")
    summary: str = Field(..., max_length=150)
    page_ref: Optional[int] = Field(None, description="Page number in source PDF")


system = (
    "You are a study summarizer. "
    "Return exactly 10 unique and helpful revision notes extracted from the attached PDF. "
    "Each note must be structured with: an `id` (1–10), a `heading`, a `summary` (max 150 chars), "
    "and an optional `page_ref` (page number from the source). "
    "Respond *only* with valid JSON matching this schema:\n"
    '{ "notes": [ { "id": 1, "heading": "...", "summary": "...", "page_ref": 1 }, ... ] }'
)

thread = client.beta.threads.create()

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Please summarize the key revision points from the PDF.",
    file_ids=[file_id],
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
    instructions=system,
    response_format={"type": "json_object"},
)

# wait for the run to complete
import time

while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run_status.status in ("completed", "failed", "cancelled"):
        break
    time.sleep(1)

messages = client.beta.threads.messages.list(thread_id=thread.id)
latest_message = messages.data[0]

# parse the content as JSON and validate with Pydantic
try:
    content_json = json.loads(latest_message.content[0].text.value)
    notes: List[Note] = [Note(**item) for item in content_json["notes"]]
except (json.JSONDecodeError, ValidationError, KeyError) as e:
    print("Error parsing notes:", e)
    exit(1)

# print pretty notes
from pprint import pprint

pprint([note.dict() for note in notes])

# save to file
with open("exam_notes.json", "w") as f:
    json.dump([note.dict() for note in notes], f, indent=2)

print("Notes successfully saved to exam_notes.json.")
