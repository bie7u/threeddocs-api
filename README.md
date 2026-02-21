# threeddocs-api

Django REST Framework API for the [threeddocs](https://github.com/bie7u/threeddocs) frontend.

## Features

- **Authentication** via HTTP-only session cookies (login / logout / me)
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Log in with `{ email, password }` → sets session cookie |
| POST | `/api/auth/logout/` | Log out (clears session) |
| GET | `/api/auth/me/` | Return current user info |

### Projects

All project endpoints require authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List all projects owned by the current user |
| POST | `/api/projects/` | Create a new project |
| GET | `/api/projects/{id}/` | Get a specific project |
| PUT | `/api/projects/{id}/` | Replace a project |
| PATCH | `/api/projects/{id}/` | Partially update a project |
| DELETE | `/api/projects/{id}/` | Delete a project |

#### Project payload example

```json
{
  "name": "My Assembly Guide",
  "project_type": "builder",
  "project_model_url": "",
  "steps": [],
  "connections": [],
  "guide": [],
  "node_positions": {}
}
```

## Running Tests

```bash
python manage.py test
```
