import json, urllib.request, urllib.error

env = {}
for line in open(".env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY") or env.get("LLM_API_KEY")
model = env.get("LLM_MODEL", "gemini-3.8-flash")
print("key found:", bool(key), "| length:", len(key or ""), "| model:", model)

url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
body = json.dumps({
    "contents": [{"parts": [{"text": "Reply with exactly this JSON: {\"ok\": true}"}]}],
    "generationConfig": {"responseMimeType": "application/json"}
}).encode()
req = urllib.request.Request(url, data=body, headers={
    "Content-Type": "application/json", "x-goog-api-key": key or ""})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("HTTP", r.status)
        print(r.read().decode()[:800])
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode()[:800])
except Exception as e:
    print("ERROR", type(e).__name__, e)