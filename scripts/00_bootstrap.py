from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
    name="Study Q&A Assistant",
    instructions=(
        "You are a helpful tutor. Use the knowledge in the attached files to answer questions. "
        "Cite sources where possible."
    ),
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
)

file_id = client.files.create(
    purpose="knowledge_retrieval", file=open("data/BasicCalculus.pdf", "rb")
).id
client.assistants.update(
    assistant.id, tool_resources={"file_search": {"vector_store_files": [file_id]}}
)

with open("assistant_id.txt", "w") as f:
    f.write(assistant.id)
