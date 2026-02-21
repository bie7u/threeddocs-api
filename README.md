# threeddocs-api

Django REST Framework API for the [threeddocs](https://github.com/bie7u/threeddocs) frontend.

## Features

- **Authentication** via JWT access + refresh tokens stored in HTTP-only cookies
- **Projects** CRUD – store and manage 3D model project data per user

## Requirements

- Python 3.10+
- pip

## Setup

```bash
# 1. Create and activate a virtualenv
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and edit environment variables
cp .env.example .env

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (optional)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Authentication

JWT-based authentication. Tokens are stored in HTTP-only cookies – the browser sends them automatically with every request.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | `{ email, password }` → sets `access_token` + `refresh_token` HTTP-only cookies |
| POST | `/api/auth/logout` | Clears both token cookies |
| POST | `/api/auth/refresh` | Reads `refresh_token` cookie → issues new `access_token` (and rotated `refresh_token`) |
| GET | `/api/auth/me` | Returns `{ id, email, name }` for the current user |

**Token lifetimes** (configurable via `SIMPLE_JWT` in settings):
- Access token: **15 minutes**
- Refresh token: **7 days** (automatically rotated on each refresh)

**Login response**
```json
{ "id": "1", "email": "user@example.com", "name": "Jan Kowalski" }
```

**Refresh response**
```json
{ "ok": true }
```

**Error format** (all auth errors)
```json
{ "message": "Invalid email or password" }
```

### Projects

All project endpoints require authentication. Responses use the `SavedProject` envelope to match the frontend store contract.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/projects` | required | List all projects owned by the current user |
| POST | `/api/projects` | required | Create a new project (client may supply UUID; `409` if it already exists) |
| GET | `/api/projects/{id}` | required | Get a specific project |
| PUT | `/api/projects/{id}` | required | Full replace of a project |
| DELETE | `/api/projects/{id}` | required | Delete a project |
| GET | `/api/projects/{id}/public` | **none** | Public read-only view (shareable link) |

#### Project payload example

```json
{
  "project": {
    "id": "project-uuid",
    "name": "My Assembly Guide",
    "projectType": "builder",
    "projectModelUrl": null,
    "steps": [],
    "connections": [],
    "guide": []
  },
  "nodePositions": {},
  "lastModified": 1700000000000
}
```

## Running Tests

```bash
python manage.py test
```
