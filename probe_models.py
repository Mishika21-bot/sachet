import time
import httpx
from app import llm

api_key, base_url, _m, _t = llm._client_config()
text = "Join our VIP group! Guaranteed 40% returns in 15 days. Pay Rs 5000 to [UPI] now, limited seats!"

for model in llm._model_chain():
    for thinking in (True, False):
        payload = llm._build_payload(text, "en", thinking)
        label = "with-thinking-cfg" if thinking else "no-thinking-cfg"
        t = time.monotonic()
        try:
            with httpx.Client() as c:
                result, dbg = llm._call_model(c, base_url, model, api_key, payload, 30)
            print(f"{model:32} {label:18} OK   {time.monotonic()-t:5.1f}s  verdict={result.verdict}")
        except llm.LlmError as e:
            d = e.debug
            print(f"{model:32} {label:18} FAIL {time.monotonic()-t:5.1f}s  stage={d.stage} status={d.http_status} type={d.error_type}")