# HRMS Lite – Backend (Django)

REST API for Employee and Attendance management. Uses Django + Django REST Framework and **Swagger** for documentation.

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Optional (ASGI):** `uvicorn main:app --host 127.0.0.1 --port 8000`  
On Windows, avoid `--reload` with uvicorn to prevent a harmless subprocess traceback on file change; use `runserver` for auto-reload instead.

- **API base:** http://127.0.0.1:8000/api/
- **Swagger UI:** http://127.0.0.1:8000/swagger/
- **ReDoc:** http://127.0.0.1:8000/redoc/

## Endpoints

### Auth (token-based)
| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register/ | Sign up. Body: `{ "name", "email", "password" }`. Returns `{ "token", "user" }`. |
| POST | /api/auth/login/ | Log in. Body: `{ "email", "password" }`. Returns `{ "token", "user" }`. |

Use the token in requests: `Authorization: Token <token>`.

### Employees & Attendance
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/employees/ | List all employees |
| POST | /api/employees/ | Create employee (body: employee_id, full_name, email, department) |
| GET | /api/employees/<id>/ | Get one employee |
| PUT | /api/employees/<id>/ | Update employee (body: same as POST) |
| DELETE | /api/employees/<id>/ | Delete employee |
| GET | /api/attendance/?date=YYYY-MM-DD&employee_id=... | List attendance (optional filters) |
| POST | /api/attendance/ | Mark attendance (body: employee_id, date, status) |

## Deploy on Render

Migrations must run so `auth_user` and other tables exist. In Render → your service → **Settings** → **Build & Deploy** set **Start Command** to one of:

**If Root Directory is the folder that contains `manage.py` (e.g. `backend`):**
```bash
python manage.py migrate --noinput && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**If Root Directory is repo root and the app is in a `backend` subfolder:**
```bash
cd backend && python manage.py migrate --noinput && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Or use `sh start.sh` (or `cd backend && sh start.sh`) if that script is next to `manage.py`. Then **Manual Deploy** so the service restarts. After that, signup/login and employees/attendance should work (no more "no such table: auth_user").

## Connect frontend

In the **frontend** folder create `.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

Restart the frontend dev server. The app will use this backend instead of localStorage.

## Database

- **Default:** **SQLite**. No extra install; data is stored in a single file.
- **File:** `backend/db.sqlite3` (created when you run `python manage.py migrate`).
- **Tables:** Django creates tables for `api.Employee`, `api.Attendance`, auth, admin, and sessions. Migrations are in `api/migrations/`.

**Models:**

| Model      | Purpose |
|-----------|---------|
| **Employee** | employee_id (unique), full_name, email, department |
| **Attendance** | employee (FK), date, status (Present/Absent). One record per employee per date (unique constraint). |

**Use PostgreSQL (e.g. for deployment):** In `hrms/settings.py`, replace the `DATABASES` entry with:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'hrms'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Add `psycopg2-binary` to `requirements.txt`, then run `migrate` again.

## Tech stack

- Django 4.x
- Django REST Framework
- drf-yasg (Swagger/OpenAPI)
- django-cors-headers (CORS for frontend)
- SQLite (default); PostgreSQL optional for production
