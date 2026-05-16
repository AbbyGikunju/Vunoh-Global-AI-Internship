import os
import json
import uuid
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq
import psycopg2
import psycopg2.extras
from database import get_db

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── HELPERS ────────────────────────────────────────────

def generate_task_code():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"VG-{letters}{numbers}"

def assign_team(intent):
    mapping = {
        "send_money": "Finance Team",
        "hire_service": "Operations Team",
        "verify_document": "Legal Team",
        "airport_transfer": "Logistics Team",
        "check_status": "Support Team"
    }
    return mapping.get(intent, "General Support")

def calculate_risk(intent, entities_str):
    entities = entities_str if isinstance(entities_str, dict) else {}
    score = 20
    reasons = []

    urgency = str(entities.get("urgency", "")).lower()
    if "urgent" in urgency or "asap" in urgency or "immediately" in urgency:
        score += 20
        reasons.append("high urgency flagged")

    amount = entities.get("amount", "")
    try:
        amount_val = float(str(amount).replace("KES", "").replace(",", "").strip())
        if amount_val > 50000:
            score += 25
            reasons.append("large transfer amount")
        elif amount_val > 20000:
            score += 10
            reasons.append("medium transfer amount")
    except:
        pass

    if intent == "verify_document":
        doc_type = str(entities.get("document_type", "")).lower()
        if "land" in doc_type or "title" in doc_type:
            score += 20
            reasons.append("land title verification - high fraud risk")
        else:
            score += 10
            reasons.append("document verification requested")

    recipient = str(entities.get("recipient", "")).lower()
    if not recipient or recipient == "unknown":
        score += 15
        reasons.append("recipient unverified")

    score = min(score, 100)
    reason = ", ".join(reasons) if reasons else "standard request"
    return score, reason

def call_groq(user_request):
    system_prompt = """You are an AI assistant for Vunoh Global, a platform helping Kenyans in the diaspora manage tasks back home.

Your job is to analyze a customer request and return a JSON object with exactly these fields:

{
  "intent": one of: send_money, hire_service, verify_document, airport_transfer, check_status,
  "entities": {
    "amount": extracted amount if mentioned (e.g. "KES 15000") or null,
    "recipient": name of recipient if mentioned or null,
    "location": location mentioned or null,
    "service_type": type of service if hire_service or null,
    "document_type": type of document if verify_document or null,
    "urgency": urgency level if mentioned or null,
    "date": date or time mentioned or null
  },
  "steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ..."
  ],
  "whatsapp_message": "A conversational WhatsApp-style confirmation with line breaks and 1-2 emojis",
  "email_message": "A formal email-style confirmation with full details and the task code placeholder [TASK_CODE]",
  "sms_message": "Under 160 characters. Include [TASK_CODE] and key action only."
}

Rules:
- Return ONLY the JSON object. No explanation, no markdown, no extra text.
- Steps must be specific to the intent, not generic.
- All three messages must feel genuinely different in tone and format.
- Use Kenyan context: mention M-Pesa for money, local counties for locations."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ],
        temperature=0.4
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    
    # Find the first { and last } to extract clean JSON
    start = raw.find('{')
    end = raw.rfind('}') + 1
    raw = raw[start:end]
    
    return json.loads(raw)

# ─── ROUTES ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process", methods=["POST"])
def process_request():
    data = request.get_json()
    user_request = data.get("request", "").strip()

    if not user_request:
        return jsonify({"error": "No request provided"}), 400

    try:
        ai_result = call_groq(user_request)
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500

    intent = ai_result.get("intent", "check_status")
    entities = ai_result.get("entities", {})
    steps = ai_result.get("steps", [])
    whatsapp = ai_result.get("whatsapp_message", "")
    email = ai_result.get("email_message", "")
    sms = ai_result.get("sms_message", "")
    
    # Handle check_status specially
    if intent == "check_status":
        words = user_request.upper().split()
        found_task = None
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        for word in words:
            cleaned = word.strip('.,!?')
            if cleaned.startswith("VG-"):
                cur.execute("SELECT * FROM tasks WHERE task_code = %s", (cleaned,))
                found_task = cur.fetchone()
                break
        cur.close()
        conn.close()

        if found_task:
            status = found_task['status']
            code = found_task['task_code']
            intent_found = found_task['intent']
            whatsapp = f"Hi! 👋 Here's your update:\n\nTask Code: {code}\nService: {intent_found}\nStatus: *{status}*\n\nWe'll notify you when there's a change. 🙏"
            email = f"Dear Customer,\n\nYour task {code} for {intent_found} is currently: {status}.\n\nPlease keep your task code safe for future follow-ups.\n\nBest regards,\nVunoh Global Team"
            sms = f"Vunoh: Task {code} status is {status}. Reply HELP for assistance."
            steps = [
                f"Step 1: Located task {code} in our system",
                f"Step 2: Current status is {status}",
                "Step 3: No further action needed at this time",
                "Step 4: You will be notified on any status change"
            ]
            entities = {"task_code": code, "current_status": status, "service": intent_found}
        else:
            whatsapp = "Hi! 👋 Please provide your task code to check status.\n\nIt looks like: *VG-ABC1234* 🙏"
            email = "Dear Customer,\n\nPlease provide your task code to check your request status.\n\nBest regards,\nVunoh Global Team"
            sms = "Vunoh: Please provide your task code (e.g. VG-ABC1234) to check status."
            steps = [
                "Step 1: Customer requested status check",
                "Step 2: Task code not found or not provided",
                "Step 3: Prompt customer to provide their task code",
                "Step 4: Look up and return status once code is provided"
            ]
            entities = {"task_code": "not provided", "current_status": "unknown"}

    risk_score, risk_reason = calculate_risk(intent, entities)
    team = assign_team(intent)
    task_code = generate_task_code()

    whatsapp = whatsapp.replace("[TASK_CODE]", task_code)
    email = email.replace("[TASK_CODE]", task_code)
    sms = sms.replace("[TASK_CODE]", task_code)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (task_code, original_request, intent, entities, risk_score,
                           risk_reason, steps, employee_team, status,
                           whatsapp_message, email_message, sms_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, created_at
    """, (
        task_code, user_request, intent,
        json.dumps(entities), risk_score, risk_reason,
        json.dumps(steps), team, "Pending",
        whatsapp, email, sms
    ))
    row = cur.fetchone()
    task_id = row[0]
    created_at = row[1]

    cur.execute("""
        INSERT INTO status_history (task_id, old_status, new_status)
        VALUES (%s, %s, %s)
    """, (task_id, None, "Pending"))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "task_code": task_code,
        "intent": intent,
        "entities": entities,
        "risk_score": risk_score,
        "risk_reason": risk_reason,
        "steps": steps,
        "team": team,
        "status": "Pending",
        "whatsapp_message": whatsapp,
        "email_message": email,
        "sms_message": sms,
        "created_at": str(created_at)
    })

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(t) for t in tasks])

@app.route("/api/tasks/<int:task_id>/status", methods=["PATCH"])
def update_status(task_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Pending", "In Progress", "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT status FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "Task not found"}), 404

    old_status = row[0]
    cur.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
    cur.execute("""
        INSERT INTO status_history (task_id, old_status, new_status)
        VALUES (%s, %s, %s)
    """, (task_id, old_status, new_status))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "new_status": new_status})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)