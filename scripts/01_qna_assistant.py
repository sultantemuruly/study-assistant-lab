from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

user_input = "Explain the Rules for Limits of Functions at Infinity"

with open("assistant_id.txt") as f:
    assistant_id = f.read().strip()

thread = client.beta.threads.create()

client.beta.threads.messages.create(
    thread_id=thread.id, role="user", content=user_input
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
    stream=True,
)

# stream the response
print("\nAssistant response:\n")
full_response = ""
citations = set()

for event in run:
    if event.data.object == "thread.message.delta":
        delta = event.data.delta
        if delta.get("content"):
            for item in delta["content"]:
                text = item.get("text", {}).get("value", "")
                full_response += text
                print(text, end="", flush=True)
        # Check for citations
        if "file_citation" in delta:
            file_citation = delta["file_citation"]
            file_id = file_citation.get("file_id", "unknown")
            quote = file_citation.get("quote", "")
            citations.add((file_id, quote))

print("\n\n--- Citations ---")
if citations:
    for file_id, quote in citations:
        print(f'\nFrom file {file_id}:\n"{quote}"')
else:
    print("No citations found.")
