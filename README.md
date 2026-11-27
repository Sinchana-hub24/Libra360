# Library360

FastAPI backend + React/Vite frontend + floci local GCP emulator.

## What it does

- Library management backend for students, books, borrowings, policies, fines, and digital access.
- JWT-based librarian/student authentication.
- Student profiles now use **USN** as the login identifier, while storing the generated student ID as a mapping.
- Digital book access is stored per student/book and can be granted, listed, or revoked.

## Prerequisites

- Docker
- Python 3.10+
- Node.js 18+ / npm

## Quick start

### 1. Start local GCP emulator

```bash
make floci-up
```

### One-command start

```bash
make run
```

This starts the local GCP emulator, FastAPI backend, and frontend.

### 2. Install and start backend

```bash
make backend-install
make backend-start
```

Backend: `http://127.0.0.1:8000`  
Docs: `http://127.0.0.1:8000/docs`

### 3. Install and start frontend

```bash
make frontend-install
make frontend-start
```

Frontend: `http://127.0.0.1:5173`

## Environment variables

Create `.env` in the project root:

```env
GOOGLE_CLOUD_PROJECT=floci-local
FIRESTORE_EMULATOR_HOST=localhost:4588
STORAGE_EMULATOR_HOST=http://localhost:4588
JWT_SECRET_KEY=<generated-secret>
LIBRARY360_SETUP_SECRET=library360-setup-dev
```

## Test accounts

- Librarian: `admin@library360.local` / `AdminPassword123!`
- Test student: USN `1RV21CS001` / password `Student123!`

## Notes

- Student login accepts **USN or email**.
- Student profiles store both `USN` and generated `student_id`.
- Digital access lookup accepts **student ID or USN**.
- Digital access revoke accepts **student ID or USN**.
