# Vunoh Diaspora Assistant

An AI-powered web application that helps Kenyans living abroad initiate and track
services back home — money transfers, local service hires, and document verification.

Built for the Vunoh Global AI Internship Practical Test 2026.
Reference Number: 271

---


### Completed 14/05/2026:
- Created project folder structure
- Set up Python virtual environment
- Installed dependencies: Flask, Groq, python-dotenv, psycopg2-binary
- Created and connected PostgreSQL database `vunoh_db`
- Designed database schema with two tables: `tasks` and `status_history`
- Successfully initialized database

### Coming tomorrow:
- Flask app and API routes (`app.py`)
- Groq AI integration for intent extraction
- Risk scoring engine
- Three-format message generation (WhatsApp, Email, SMS)
- Task dashboard frontend
- SQL dump with 5 sample tasks

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Backend | Python + Flask | Lightweight, easy to understand and explain |
| Database | PostgreSQL | Relational structure, supports JSONB for entities |
| AI | Groq (LLaMA 3) | Free tier, fast response, reliable JSON output |
| Frontend | Vanilla HTML/CSS/JS | Required by brief |

---

## Project Structure
