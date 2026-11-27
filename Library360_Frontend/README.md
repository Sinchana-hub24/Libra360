# Library360 Frontend

A React + Vite frontend for the existing Library360 FastAPI backend.

## Requirements

- Python backend running at `http://127.0.0.1:8000`
- Node.js LTS (18 or newer recommended)
- npm

## Run it on Windows

1. Extract this folder into your `LIBRA360` project folder (or keep it separate).
2. Open a **new PowerShell terminal** in this `Library360_Frontend` folder.
3. Run:

```powershell
npm install
npm run dev
```

4. Open the local URL Vite prints (normally `http://127.0.0.1:5173`).

Keep the backend/Uvicorn terminal running. The Vite development server proxies `/api` requests to `http://127.0.0.1:8000`, so local browser CORS configuration should not be needed.

## Login

- Select Librarian or Student on the login screen.
- Librarian login uses the librarian email and password.
- Student login accepts the student ID or email and password.
- The frontend stores the JWT in browser local storage and sends it as `Authorization: Bearer <token>`.
- Signing out removes the saved token.

## Important notes about the current backend

This UI only calls endpoints present in the supplied OpenAPI specification. It does not add backend functionality.

- The API has no endpoint to list all students. Student management therefore provides profile registration and lookup by student ID.
- Fine records are loaded for a specific student, because there is no all-fines endpoint.
- Book search uses the existing book list endpoint and filters the returned list in the browser.
- Some endpoints in the supplied API are not JWT-protected. The frontend's hidden/visible navigation is not a security boundary. Add server-side role checks before production use.
- The digital read endpoint response is shown as returned by the API because its response format is not specified in OpenAPI.
- Student profile creation and student login-account creation are two separate operations. Create the student profile first, then create the login account using its returned student ID.
- Digital book access is permanent until revoked, as implemented by the backend.

## Build

```powershell
npm run build
```

The production build is generated in `dist`.
