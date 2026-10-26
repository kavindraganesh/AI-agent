import glob
import json
import os
import sys
import urllib.error
import urllib.request

MODEL = "gemini-2.5-flash"

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("ERROR: GEMINI_API_KEY secret is missing or misnamed.")
    sys.exit(1)

# 1. Read the failed test output
log = open("test.log").read()[-6000:]

# 2. Read the project's code
code = ""
for path in glob.glob("*.py"):
    if path != "agent.py":
        code += f"\n--- {path} ---\n" + open(path).read()

# 3. Ask Gemini to diagnose it
url = ("https://generativelanguage.googleapis.com/v1beta/"
       f"models/{MODEL}:generateContent")
body = {
    "system_instruction": {"parts": [{"text":
        "You are a DevOps assistant. A CI pipeline just failed. "
        "Explain the root cause in plain English, point to the exact file "
        "and line, and give the fixed code. Be short and practical."}]},
    "contents": [{"parts": [{"text": f"TEST LOG:\n{log}\n\nCODE:\n{code}"}]}],
}
req = urllib.request.Request(
    url,
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": key},
)

try:
    data = json.load(urllib.request.urlopen(req))
    text = data["candidates"][0]["content"]["parts"][0]["text"]
except urllib.error.HTTPError as e:
    print("API ERROR", e.code, e.read().decode())
    sys.exit(1)

# 4. Save the diagnosis
with open("diagnosis.md", "w") as f:
    f.write("## 🤖 AI Failure Diagnosis\n\n" + text)
print(text)
