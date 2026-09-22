from pathlib import Path
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text(encoding="utf-8")
    context += "\n\n"

response = chat(
    model='qwen3:8b',
    messages=[
        {'role': 'system', 'content': f"You are a helpful IT support assistant. Answer the user's question using this knowledge base:\n{context}"},
        {'role': 'user', 'content': question}
    ]
)

print(
    "Context characters:",
    len(context)
)

print(response.message.content)