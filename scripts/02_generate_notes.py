from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("assistant_id.txt") as f:
    assistant_id = f.read().strip()

with open("file_id.txt") as f:
    file_id = f.read().strip()

user_input = "Generate 10 revision notes on key concepts in calculus, particularly focusing on limits, derivatives, integrals, and continuity."

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input,
    attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}],
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant_id
)

print(f"Run completed with status: {run.status}")

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for message in messages.data:
        if message.role == "assistant":
            print("\nAssistant response:")
            for content in message.content:
                if content.type == "text":
                    print(content.text.value)

                    if content.text.annotations:
                        print("\n--- Citations ---")
                        for annotation in content.text.annotations:
                            if hasattr(annotation, "file_citation"):
                                print(f"File: {annotation.file_citation.file_id}")
            break
else:
    print(f"Run failed with status: {run.status}")
