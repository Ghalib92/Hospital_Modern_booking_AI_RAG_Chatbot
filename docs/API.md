# API Reference

Base URL: `http://localhost:8000/api/`

JSON bodies. Protected endpoints require `Authorization: Bearer <access-token>`.
Interactive docs at `/api/docs/` (Swagger) and `/api/redoc/`.

---

## Authentication (`/auth/`)

| Method | Endpoint | Body |
| --- | --- | --- |
| POST | `/auth/register/` | `username, email, password, first_name?, last_name?` |
| POST | `/auth/login/` | `username, password` → `{ access, refresh }` |
| POST | `/auth/refresh/` | `{ refresh }` → `{ access }` |
| GET/PATCH | `/auth/profile/` | current user |
| GET | `/auth/doctors/` | doctor directory (`?specialty=`); write = staff |

---

## Bookings (public submissions)

### Physical appointment
`POST /physical-appointments/`
```json
{ "name": "Sam", "email": "sam@example.com", "phone_no": "0712345678",
  "service_needed": "Dentist", "appointment_date": "2030-01-15" }
```
Sends a confirmation email. `service_needed`: `Dentist | Surgery | Consultation`.

### Emergency care
`POST /emergency-care/`
```json
{ "patient_name": "Sam", "contact_number": "0712345678",
  "condition_description": "Severe fall", "priority_level": "High", "location": "ER" }
```

### Online consultation
`POST /online-consultations/`
```json
{ "name": "Sam", "email": "sam@example.com", "phone_number": "0712345678",
  "service_type": "consultation", "date": "2030-01-15", "time": "10:00" }
```

> Listing these submissions (`GET`) requires a staff account.

---

## Typed appointments (`/appointments/`, auth required)

- `GET /appointments/types/` → `{ "types": ["Dentist", "Surgery", ...] }` (from doctor specialties)
- `GET /appointments/slots/?type=Dentist` → free vs booked weekday slots (next 5 days)
- `POST /appointments/` → `{ "appointment_type": "Dentist", "appointment_time": "2030-01-15T10:00:00" }` (emails confirmation)
- `GET /appointments/` → the patient's own appointments
- `GET /appointments/for-doctor/` → appointments matching the authenticated doctor's specialty (403 without a doctor profile)

---

## Blog & contact

- `GET /blog/`, `GET /blog/{id}/` (public); write = staff.
- `POST /contact/` → `{ "name", "email", "subject", "message" }`.

---

## Chatbot (`/chatbot/chat/`)

`POST /chatbot/chat/`
```json
{ "message": "What are the symptoms of malaria?",
  "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "Hello!"}] }
```
**200 OK**
```json
{
  "answer": "...",
  "sources": [{"source": "Medical_book.pdf", "page": 42}],
  "emergency": false,
  "disclaimer": "This is general information, not medical advice..."
}
```
Emergency-symptom messages return `"emergency": true` with urgent-care guidance and no LLM call.

| Status | Meaning |
| --- | --- |
| 400 | Validation error / empty message |
| 401 | Missing/invalid token |
| 403 | Authenticated but not permitted |
| 502 / 503 | Chatbot upstream failure / not configured |
