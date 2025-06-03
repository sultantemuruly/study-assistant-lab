from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read assistant and file IDs
with open("assistant_id.txt") as f:
    assistant_id = f.read().strip()

with open("file_id.txt") as f:
    file_id = f.read().strip()

user_input = "Explain the Rules for Limits of Functions at Infinity"

# Create thread
thread = client.beta.threads.create()

# Create message with file attachment
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input,
    attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}],
)

# Run the assistant
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

                    # Print citations
                    if content.text.annotations:
                        print("\n--- Citations ---")
                        for annotation in content.text.annotations:
                            if hasattr(annotation, "file_citation"):
                                print(f"File: {annotation.file_citation.file_id}")
            break
else:
    print(f"Run failed with status: {run.status}")
