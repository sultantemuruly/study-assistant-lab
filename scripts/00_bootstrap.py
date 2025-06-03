from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

file = client.files.create(
    file=open("data/BasicCalculus.pdf", "rb"), purpose="assistants"
)

# create assistant with file_search tool
assistant = client.beta.assistants.create(
    name="Study Q&A Assistant",
    instructions=(
        "You are a helpful tutor. "
        "Use the knowledge in the attached files to answer questions. "
        "Cite sources where possible."
    ),
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
)

# create a thread and attach the file to the message
with open("assistant_id.txt", "w") as f:
    f.write(assistant.id)

with open("file_id.txt", "w") as f:
    f.write(file.id)

print(f"Assistant created with ID: {assistant.id}")
print(f"File uploaded with ID: {file.id}")
print("Setup complete! The file will be attached per message in the Q&A script.")
