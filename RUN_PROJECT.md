# NLTK Toolkit — Beginner's Project Run Guide

A step-by-step, copy-paste friendly guide to running the NLTK Toolkit full-stack project on Windows using PowerShell.

---

## 1. Project Location

The project is located at:
```text
D:\NLTK Kit
```

Always open your Windows PowerShell terminal in this folder before executing commands:
```powershell
cd "D:\NLTK Kit"
```

---

## 2. First-Time Setup & Prerequisites

Before starting, verify your system tools:
```powershell
python --version
node --version
npm --version
```
- **Python:** Tested on Python 3.13 (3.10+ supported)
- **Node.js:** Tested on Node.js v22 (18+ supported)

---

## 3. Virtual Environment

The project provides a virtual environment containing all required Python libraries.
A project-root directory junction `.venv` points directly to `backend\venv`.

### Activate the Virtual Environment:
Run from `D:\NLTK Kit`:
```powershell
cd "D:\NLTK Kit"
.\.venv\Scripts\Activate.ps1
```
*(Alternative: `.\backend\venv\Scripts\Activate.ps1` works identically).*

> **Tip:** If PowerShell gives an execution policy warning (`running scripts is disabled`), run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 4. Backend Dependencies Installation

With the environment activated or using the direct Python executable:
```powershell
cd "D:\NLTK Kit"
python -m pip install -r backend\requirements.txt
```

Verify that essential NLTK corpora are downloaded:
```powershell
.\.venv\Scripts\python.exe backend\scripts\download_nltk_data.py
```

---

## 5. Frontend Dependencies Installation

Install frontend packages:
```powershell
cd "D:\NLTK Kit\frontend"
npm install
cd "D:\NLTK Kit"
```

---

## 6. Environment Variables Configuration

The project uses three coordinated `.env` files:

1. **`D:\NLTK Kit\.env`** (Root configuration):
   - `VITE_GOOGLE_CLIENT_ID` (Google Client ID for frontend)
   - `GOOGLE_CLIENT_ID` (Google Client ID for backend)
   - `PORT=5001`

2. **`D:\NLTK Kit\backend\.env`** (Flask API backend configuration):
   - `PORT=5001`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174`
   - `GOOGLE_CLIENT_ID`
   - `DATABASE_URL=sqlite:///instance/nltk_toolkit.db`

3. **`D:\NLTK Kit\frontend\.env`** (Vite frontend configuration):
   - `VITE_GOOGLE_CLIENT_ID`
   - `PORT=5001`

> **Security Note:** The Google Client ID uses Google Identity Services client-side ID-token verification. No Google Client Secret is needed or stored.

---

## 7. How to Start the Backend (Terminal 1)

1. Open a Windows PowerShell window and navigate to the project root:
   ```powershell
   cd "D:\NLTK Kit"
   ```
2. Activate virtual environment and start the Flask backend:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m backend.app
   ```
   *(Or direct one-line command: `.\.venv\Scripts\python.exe -m backend.app`)*

**Expected Terminal 1 Output:**
```text
Google Client ID configured: True
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.1.69:5001
```

> **Crucial Rule:** Always start the backend from `D:\NLTK Kit` using `python -m backend.app`. Do not `cd backend` and run `python app.py` as that causes `ModuleNotFoundError: No module named 'backend'`.

---

## 8. How to Start the Frontend (Terminal 2)

1. Open a **second** Windows PowerShell window and navigate to the project root:
   ```powershell
   cd "D:\NLTK Kit"
   ```
2. Start the Vite development server:
   ```powershell
   npm run dev
   ```

**Expected Terminal 2 Output:**
```text
  VITE v8.3.0  ready in ... ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

3. Open your browser and navigate to:
   ```text
   http://localhost:5173/
   ```

---

## 9. Backend Health Check Command

To verify that the Flask backend is operational and all NLTK corpora are ready:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5001/api/v1/health" | ConvertTo-Json
```

Or test through the Vite development proxy:
```powershell
Invoke-RestMethod -Uri "http://localhost:5173/api/v1/health" | ConvertTo-Json
```

**Expected Response:**
```json
{
  "data": {
    "api_version": "v1.0.0",
    "nltk_resources": {
      "punkt": true,
      "stopwords": true,
      "vader_lexicon": true,
      "wordnet": true
    },
    "service": "NLTK Toolkit Backend",
    "status": "healthy"
  },
  "success": true
}
```

---

## 10. Email / Password Login Test

The application automatically seeds a demo user account into SQLite (`backend/instance/nltk_toolkit.db`):
- **Email:** `demo@nltk.org`
- **Password:** `DemoPassword123!`

You can also create a new account anytime by clicking **"Create an account"** on the `/login` page.

---

## 11. Google Sign-In Test Checklist

1. Open `http://localhost:5173/` in your browser. (Unauthenticated users are automatically sent to `/login`).
2. Under **"or continue with"**, click the **Google** button.
3. The official Google Identity popup will open. Select your Google account.
4. Google issues an ID token credential to the browser.
5. The frontend sends this credential to `POST /api/v1/auth/google`.
6. Flask verifies the ID token with Google's public certificates using `google.oauth2.id_token`.
7. Your Google profile is saved/updated in `backend/instance/nltk_toolkit.db`.
8. A JWT session token is returned and stored in `localStorage`.
9. The browser automatically navigates to the main dashboard.
10. To sign out, click the profile avatar / logout button in the top right.

---

## 12. Stopping the Servers

To stop either server:
1. Click in that terminal window.
2. Press `Ctrl + C`.
3. If prompted `Terminate batch job (Y/N)?`, type `Y` and press Enter.

---

## 13. Complete Troubleshooting Guide

| Issue / Error | Cause | Exact Fix / Command |
| :--- | :--- | :--- |
| `[vite] http proxy error: /api/v1/...` | Flask backend is not running on port 5001 when frontend makes an API call. | Open Terminal 1, run `cd "D:\NLTK Kit"`, then `python -m backend.app`. Keep this terminal open! |
| `ECONNREFUSED 127.0.0.1:5001` | Connection refused because Flask is offline or listening on a different port. | Verify Flask started on port 5001. Check with: `Invoke-RestMethod http://127.0.0.1:5001/api/v1/health`. |
| `ModuleNotFoundError: No module named 'backend'` | Running `python app.py` from inside `D:\NLTK Kit\backend\` instead of running as a module from root. | Always run from project root: `cd "D:\NLTK Kit"` followed by `python -m backend.app`. |
| `ModuleNotFoundError: No module named 'flask_sqlalchemy'` | Python packages are missing in the current Python environment. | Run `cd "D:\NLTK Kit"`, then `python -m pip install -r backend\requirements.txt`. |
| `.\.venv\Scripts\Activate.ps1 : The term is not recognized` | PowerShell cannot find the virtual environment path. | Ensure you are in `cd "D:\NLTK Kit"`. The junction `.venv` points to `backend\venv`. Both `.\.venv\Scripts\Activate.ps1` and `.\backend\venv\Scripts\Activate.ps1` are valid. |
| `Google sign-in prompt was suppressed` | Google One Tap prompt was minimized, closed, or suppressed by browser settings. | Non-fatal browser notice. Simply click the visible **Google** button to open the account chooser popup directly. |
| `Google Client ID is not configured` | Missing `VITE_GOOGLE_CLIENT_ID` in `frontend/.env` or `GOOGLE_CLIENT_ID` in `backend/.env`. | Verify that `VITE_GOOGLE_CLIENT_ID` in `D:\NLTK Kit\frontend\.env` and `GOOGLE_CLIENT_ID` in `D:\NLTK Kit\backend\.env` are set to your Google OAuth Web Client ID. |
| `CORS error in browser console` | Origin mismatch between frontend and backend. | Verify `FRONTEND_ORIGINS` in `D:\NLTK Kit\backend\.env` contains `http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174`. |
| `Port 5173 occupied` / `Port 5174 used` | Another process is already running on port 5173. | Backend CORS supports both 5173 and 5174. To free port 5173: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess -Force`. |
| `Backend not reachable from frontend` | Vite proxy misconfigured or target port incorrect. | Inspect `frontend/vite.config.ts`. The proxy target must be `'http://127.0.0.1:5001'`. |
| `npm package missing` / `Cannot find module ...` | Node dependencies incomplete in `frontend`. | Run `cd "D:\NLTK Kit\frontend"` followed by `npm install`. |
