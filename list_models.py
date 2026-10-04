import json, urllib.request

env = {}
for line in open(".env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY") or env.get("LLM_API_KEY")

req = urllib.request.Request(
    "https://generativelanguage.googleapis.com/v1beta/models?pageSize=100",
    headers={"x-goog-api-key": key})
data = json.load(urllib.request.urlopen(req, timeout=30))
for m in data.get("models", []):
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print(m["name"])