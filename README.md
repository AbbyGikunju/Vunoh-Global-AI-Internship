# Vunoh Diaspora Assistant

An AI-powered web application that helps Kenyans living abroad initiate and 
track services back home - money transfers, local service hires, and document 
verification.

Built for the Vunoh Global AI Internship Practical Test 2026.
Reference Number: 271

---

## What It Does

A customer types a plain English request. The system:

1. Extracts the intent and key details using AI
2. Calculates a risk score based on diaspora-specific logic
3. Creates a tracked task with a unique code
4. Generates fulfilment steps specific to the service
5. Produces three confirmation messages: WhatsApp, Email, and SMS
6. Assigns the task to the right internal team
7. Displays everything on a live dashboard with status controls

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python + Flask |
| Database | PostgreSQL |
| AI | Groq (LLaMA 3.3 70b) |
| Frontend | Vanilla HTML, CSS, JavaScript |

---

## Project Structure
vunoh-diaspora-assistant/
├── static/
│   └── style.css            # Frontend styling
├── templates/
│   └── index.html           # Single Page Application frontend
├── .env                     # Local API keys (excluded from git)
├── app.py                   # Flask routing and core backend logic
├── database.py              # PostgreSQL connection setup
├── requirements.txt         # Python package dependencies
└── schema.sql               # Database table definitions


---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/vunoh-diaspora-assistant.git
cd vunoh-diaspora-assistant
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/vunoh_db

### 5. Create the database
In pgAdmin, create a database called `vunoh_db` then run:
```bash
python database.py
```

### 6. Run the application
```bash
python app.py
```

Visit `http://localhost:5000`

---

## Risk Scoring Logic

Scores range from 0 to 100. Higher scores flag tasks for closer review.

| Factor | Points | Reasoning |
|--------|--------|-----------|
| High urgency keyword | +20 | Urgency is a common trigger in diaspora fraud |
| Large amount over KES 50,000 | +25 | High-value transfers carry greater exposure |
| Medium amount over KES 20,000 | +10 | Moderate financial risk |
| Land title verification | +20 | Land fraud is among the most common in Kenya |
| Other document verification | +10 | Documents are frequently forged |
| Unknown or unverified recipient | +15 | No relationship history increases risk |
| Base score | 20 | Every request carries baseline risk |

---

## Decisions I Made and Why

### AI tools used
I used Claude (claude.ai) as a coding assistant — it helped me when I was 
stuck, suggested fixes, and explained concepts I was unsure about. I made 
the architectural decisions, typed and reviewed every line of code, and 
tested everything myself. I also used Groq's LLaMA 3.3 70b model as the 
AI brain of the application for intent extraction and message generation.

### How I designed the system prompt
I designed the system prompt to return a strict JSON object every time. I 
specified exact field names, exact intent options, and told the model to return 
nothing else - no explanation, no markdown. I included Kenyan context 
instructions such as mentioning M-Pesa for money transfers and local counties 
for locations. I excluded open-ended instructions because they produce 
inconsistent output that is hard to parse reliably.

### One decision where I changed what the AI suggested
The AI initially suggested using SQLite for simplicity. I switched to 
PostgreSQL because it supports JSONB columns for storing entities and steps, 
which makes the data properly queryable rather than just a text blob. It also 
reflects a more realistic production environment.

### One thing that did not work as expected
The original LLaMA model I used (llama3-8b-8192) had been decommissioned by 
Groq and returned a 400 error. I resolved this by checking Groq's deprecations 
page and switching to llama-3.3-70b-versatile, which is the current 
recommended model and actually produces more reliable JSON output.

---

## Sample Requests to Test

- "I need to send KES 15,000 to my mother in Kisumu urgently"
- "Please verify my land title deed for the plot in Karen, Nairobi"
- "Can someone clean my apartment in Westlands this Friday"
- "I need an airport transfer from JKIA on Monday at 6am"
- "What is the status of my task VG-ABC1234"

---

## Submission Details

- Reference Number: 271
- Submission Date: May 2026
