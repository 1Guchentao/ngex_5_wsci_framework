from pathlib import Path
from ollama import chat
import json

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

state = {
    "problem": question.strip(),
    "device": "Windows laptop",
    "wifi_status": "operational"
}

with open("state.json", "w", encoding="utf-8") as file:
    json.dump(state, file, indent=2)

with open("state.json", "r", encoding="utf-8") as file:
    diagnostic_context = json.load(file)

print("State Loaded.")
print("-" * 40)

def select_context(question):
    q_lower = question.lower()
    selected = []
    
    if "password" in q_lower or "wi-fi" in q_lower or "wifi" in q_lower:
        selected.append(Path("knowledge/password_changes.txt"))
        selected.append(Path("knowledge/service_status.txt"))
        selected.append(Path("knowledge/wifi_setup.txt"))
    if "print" in q_lower:
        selected.append(Path("knowledge/printing.txt"))
    if "projector" in q_lower or "display" in q_lower:
        selected.append(Path("knowledge/classroom_projectors.txt"))
        
    return selected

selected_files = select_context(question)

context = ""
for f in selected_files:
    if f.exists():
        context += f.read_text(encoding="utf-8") + "\n\n"

def compress_context(context, question):
    compression_prompt = f"Extract only the critical troubleshooting steps from this context to solve this problem: '{question}'.\n\nContext:\n{context}"
    res = chat(
        model='qwen3:8b',
        messages=[{'role': 'user', 'content': compression_prompt}]
    )
    return res.message.content

compressed_context = compress_context(context, question)

print("Compressed Context Length:", len(compressed_context))
print("-" * 40)

system_prompt = f"""You are an IT diagnostic bot. 
Use the diagnostic state and the compressed knowledge context to answer.
Return ONLY a valid JSON object with two keys: "diagnosis" and "solution".

Diagnostic Context:
{json.dumps(diagnostic_context)}

Knowledge Context:
{compressed_context}
"""

response = chat(
    model='qwen3:8b',
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': question}
    ],
    format='json'
)

print(response.message.content)

try:
    final_output = json.loads(response.message.content)
    diagnostic_context["latest_diagnosis"] = final_output.get("diagnosis", "")
    diagnostic_context["proposed_solution"] = final_output.get("solution", "")
    diagnostic_context["status"] = "resolved"
except json.JSONDecodeError:
    diagnostic_context["error"] = "Failed to parse structured output."

with open("state.json", "w", encoding="utf-8") as file:
    json.dump(diagnostic_context, file, indent=2)

print("\nUpdated state.json has been written.")