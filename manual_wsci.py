from pathlib import Path
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    Path("knowledge/password_changes.txt"),
    Path("knowledge/service_status.txt"),
    Path("knowledge/wifi_setup.txt")
]

context = ""

for file in selected_files:
    if file.exists():
        context += file.read_text(encoding="utf-8")
        context += "\n\n"

response = chat(
    model='qwen3:8b',
    messages=[
        {'role': 'system', 'content': f"You are an IT support assistant. Answer the user's question using strictly this context:\n{context}"},
        {'role': 'user', 'content': question}
    ]
)

print(
    "Context characters:",
    len(context)
)
print(response.message.content)