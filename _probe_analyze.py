import json
import urllib.request

payload = {
    "text": (
        "Our senior analyst's private circle has been multiplying members' "
        "capital every month with zero downside. DM me for the entry window."
    ),
    "lang": "en",
}
req = urllib.request.Request(
    "http://127.0.0.1:8000/analyze",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=60) as response:
    data = json.loads(response.read().decode())
print("analysis_mode", data.get("analysis_mode"))
print("verdict", data.get("verdict"))
print("risk_score", data.get("risk_score"))
print("confidence", data.get("confidence"))
print("flags", [flag["id"] for flag in data.get("red_flags", [])])
