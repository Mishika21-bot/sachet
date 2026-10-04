from fastapi import APIRouter, Request, Response, status

router = APIRouter(prefix="/v1/webhooks", tags=["Ingress"])

@router.post("/message-channel")
async def handle_incoming_message(request: Request):
    """
    Unified ingestion webhook handling raw text payloads from chat channels 
    (WhatsApp Business API / Telegram bot polling containers).
    """
    payload = await request.json()
    
    # Extract text content dynamically based on the incoming channel signature
    raw_text = payload.get("message", {}).get("text") or payload.get("Body", "")
    sender_id = payload.get("message", {}).get("chat", {}).get("id") or payload.get("From", "Unknown")
    
    if not raw_text:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
    # Self-Contained Deterministic Pattern Matrix (No broken external imports!)
    lower_text = raw_text.lower()
    
    # Check for known retail scam keywords common in Tier-2/3 target groups
    if any(keyword in lower_text for keyword in ["guaranteed", "vip group", "paisa double", "allocation", "profit"]):
        risk_score = "RED"
        reason_hi = "तय मुनाफे का झांसा (Guaranteed high-yield investment scam vector)"
    else:
        risk_score = "GREEN"
        reason_hi = ""
    
    if risk_score == "RED":
        final_response = f"🚨 *सचेत WARNING!* This message looks like a scam.\nReason: {reason_hi}"
    else:
        # Fast fallback text when layer 1 rules clear it
        final_response = "सचेत विश्लेषण संकेत: No immediate deterministic red flags found. Still verify before paying."

    return {"status": "processed", "recipient": sender_id, "reply": final_response}
