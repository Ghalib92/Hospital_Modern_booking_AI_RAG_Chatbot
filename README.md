# Hospital System API

A Django REST Framework API for a hospital booking platform: patients book
**physical appointments, emergency care, online consultations** and **typed
time-slot appointments**; doctors have profiles and see appointments matching
their specialty; plus a blog, contact form, and a **RAG medical-assistant
chatbot**. JWT-authenticated, documented with OpenAPI/Swagger, and containerised.

> ⚠️ Portfolio/demo. The chatbot provides general information only and is **not**
> a medical device or a substitute for professional care.

## Tech Stack

Python 3.12 · Django 5.2 · Django REST Framework · PostgreSQL / SQLite ·
JWT (simplejwt) · LangChain (Pinecone + OpenAI + HuggingFace) · drf-spectacular ·
Gunicorn · WhiteNoise · Docker.

## Apps

| App | Responsibility |
| --- | --- |
| `accounts` | JWT auth (register / login / refresh / profile) + doctor directory |
| `appointments` | physical / emergency / online / typed bookings, slots, blog, contact |
| `chatbot` | RAG medical-assistant endpoint (lazy-loaded, with an emergency-safety nudge) |

## Features

- **JWT auth** — patient registration, login/refresh, profile.
- **Bookings** — public physical-appointment, emergency-care and online-consultation submissions (with email confirmations); authenticated patients book typed appointments against free weekday time-slots.
- **Doctor view** — a doctor sees appointments matching their specialty; doctor directory is public to read, staff-managed.
- **RAG chatbot** — history-aware retrieval (Pinecone + OpenAI), MMR, source citations, and a deterministic emergency-symptom nudge to urgent care; lazy-loaded so the app boots without keys (`503` until configured).
- **Secure config** — all secrets from the environment; production security headers when `DEBUG=0`.
- **Docs** — Swagger UI at `/api/docs/`.

## Quick Start (Docker)

```bash
git clone <repo-url>
cd HospitalSystem_Modern_booking-chatbot_
cp .env.example .env          # set a real SECRET_KEY & DB_PASSWORD
docker compose up --build
```

- API root: <http://localhost:8000/api/>
- Swagger UI: <http://localhost:8000/api/docs/>
- Admin: <http://localhost:8000/admin/>

## Local Development

```bash
cd HospitalSystem_Modern_booking-chatbot_/Hospital_System
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env     # SQLite by default; set DATABASE_URL for Postgres
python manage.py migrate
python manage.py runserver
python manage.py test
```

## Key Endpoints

| Method | Endpoint | Notes |
| --- | --- | --- |
| POST | `/api/auth/register/` · `/api/auth/login/` · `/api/auth/refresh/` | JWT |
| GET/PATCH | `/api/auth/profile/` | current user |
| GET | `/api/auth/doctors/` | doctor directory (write = staff) |
| POST | `/api/physical-appointments/` | book a physical appointment (public) |
| POST | `/api/emergency-care/` | emergency booking (public) |
| POST | `/api/online-consultations/` | online consultation (public) |
| GET/POST | `/api/appointments/` | a patient's typed appointments |
| GET | `/api/appointments/types/` · `/api/appointments/slots/?type=` | types & free slots |
| GET | `/api/appointments/for-doctor/` | appointments for the doctor's specialty |
| GET/POST | `/api/blog/` | blog (write = staff) |
| POST | `/api/contact/` | contact form |
| POST | `/api/chatbot/chat/` | RAG assistant (`message`, optional `history`) |

Full reference: [docs/API.md](docs/API.md) or the live Swagger UI.

## Project Layout

```
Hospital_System/
├── Hospital_System/   # project config (settings, urls, wsgi)
├── accounts/          # auth + doctor profiles
├── appointments/      # bookings, slots, blog, contact
├── chatbot/           # RAG endpoint (chatbot/rag.py)
├── src/               # RAG helpers (PDF load, chunk, embeddings)
├── manage.py
└── requirements.txt
```

## Enabling the Chatbot

1. Set `OPENAI_API_KEY` and `PINECONE_API_KEY` in `.env` (it queries a medical
   knowledge-base Pinecone index, default name `medicalbot`).
2. `POST /api/chatbot/chat/`. Until configured it returns `503`; the rest of the
   API and the emergency-safety nudge work regardless.

## Security

- `.env` is git-ignored; all secrets read from the environment.
- JWT auth; booking submissions are public but only staff can list them.
- Production security headers auto-enable when `DEBUG=0`.
