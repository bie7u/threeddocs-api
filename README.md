# threeddocs-api

Django REST Framework backend for the [threeddocs](https://github.com/bie7u/threeddocs) frontend.

## Features

- JWT authentication via **HTTP-only cookies** (access + refresh token)
- Full CRUD for **3D model projects** with owner-scoped access
- Public shareable link endpoint (no auth required)

---

## Setup

### Requirements

- Python 3.10+

### Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment variables
cp .env.example .env
# Edit .env – set DJANGO_SECRET_KEY, CORS_ALLOWED_ORIGINS, etc.

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) Create a superuser for the admin panel
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API is available at `http://localhost:8000/api`.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | insecure default (dev only) | Django secret key – **required in production** |
| `DJANGO_DEBUG` | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | Comma-separated frontend origins |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5173,...` | Comma-separated trusted origins for CSRF |

### Running tests

```bash
python manage.py test
```

---

## Authentication

All protected endpoints read the `access_token` from an **HTTP-only cookie** that is set automatically on login. JavaScript cannot read these cookies (XSS protection).

### Cookie specification

| Cookie | TTL | Description |
|--------|-----|-------------|
| `access_token` | 15 min | Short-lived JWT sent with every API request |
| `refresh_token` | 7 days | Long-lived token used to obtain a new access token |

Both cookies are set with `HttpOnly=true`, `SameSite=Lax`, and `Secure=true` in production.

### Automatic token refresh

When the frontend receives a `401` response it automatically calls `POST /api/auth/refresh`, replaces the access token cookie, and retries the original request. If the refresh also returns `401` the user is redirected to the login page.

---

## API Reference

### Base URL

```
http://localhost:8000/api
```

---

### Auth endpoints

#### `POST /api/auth/login`

Authenticate with email and password. On success the server sets `access_token` and `refresh_token` cookies.

**Request body**
```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

**`200 OK`**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Jan Kowalski"
}
```

**`401 Unauthorized`**
```json
{ "message": "Invalid email or password" }
```

---

#### `POST /api/auth/logout`

Clears both token cookies. Requires a valid access token.

**`204 No Content`** – cookies cleared, no body.

**`401 Unauthorized`** – access token missing or expired.

---

#### `POST /api/auth/refresh`

Issues a new `access_token` (and rotates the `refresh_token`) using the refresh token cookie. No request body needed.

**`200 OK`**
```json
{ "ok": true }
```

**`401 Unauthorized`** – refresh token is missing, expired or invalid.

---

#### `GET /api/auth/me`

Returns the currently authenticated user.

**`200 OK`**
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "Jan Kowalski"
}
```

**`401 Unauthorized`** – triggers the automatic token refresh flow on the frontend.

---

### Project endpoints

All project endpoints (except `/public`) require a valid `access_token` cookie. Users can only access their own projects.

#### Data shape – `Project`

Every project endpoint sends and receives a single flat object:

```json
{
  "id": 42,
  "name": "My Assembly Guide",
  "projectType": "builder",
  "projectModelUrl": null,
  "steps": [],
  "connections": [],
  "guide": [],
  "nodePositions": {
    "step-1": { "x": 100, "y": 200 }
  },
  "lastModified": 1700000000000
}
```

| Field | Type | Read/Write | Description |
|-------|------|-----------|-------------|
| `id` | integer | **read-only** | Server-assigned primary key |
| `name` | string | read/write | Human-readable project name |
| `projectType` | `"builder"` \| `"upload"` | read/write | Editor mode |
| `projectModelUrl` | string \| null | read/write | URL or data-URL of an uploaded GLB/GLTF model |
| `steps` | array | read/write | List of `InstructionStep` objects |
| `connections` | array | read/write | List of `Edge` (ReactFlow) objects |
| `guide` | array | read/write | Ordered list of `GuideStep` objects |
| `nodePositions` | object | read/write | Map of step-id → `{ x, y }` canvas positions |
| `lastModified` | integer | **read-only** | Unix timestamp in **milliseconds** (set by the server on every save) |

---

#### `GET /api/projects`

Returns all projects owned by the authenticated user, ordered by most recently updated.

**`200 OK`** – array of `Project` objects:
```json
[
  { "id": 42, "name": "...", "projectType": "builder", "nodePositions": {}, "lastModified": 1700000000000, ... }
]
```

---

#### `POST /api/projects`

Creates a new project. The server assigns the `id`.

**Request body** – `Project` (without `id`/`lastModified`):
```json
{
  "name": "My 3D Model",
  "projectType": "builder",
  "projectModelUrl": null,
  "steps": [],
  "connections": [],
  "guide": [],
  "nodePositions": {}
}
```

**`201 Created`** – the saved `Project` including the server-assigned `id` and `lastModified`.

**`400 Bad Request`**
```json
{ "message": "This field is required." }
```

---

#### `GET /api/projects/{id}`

Returns a single project by its integer `id`.

**`200 OK`** – `Project`.

**`404 Not Found`** – project does not exist or belongs to another user.

---

#### `PUT /api/projects/{id}`

Fully replaces a project. All writable fields must be supplied.

**Request body** – same shape as `POST /api/projects`.

**`200 OK`** – updated `Project`.

**`400 Bad Request`** – validation error.

**`404 Not Found`** – project does not exist or belongs to another user.

---

#### `DELETE /api/projects/{id}`

Deletes a project permanently.

**`204 No Content`** – deleted, no body.

**`404 Not Found`** – project does not exist or belongs to another user.

---

#### `GET /api/projects/{id}/public`

Returns a project **without authentication**. Used by the shareable `/view/:projectId` link in the frontend.

**`200 OK`** – `Project`.

**`404 Not Found`** – project does not exist.

---

## Error format

All error responses follow the same shape:

```json
{ "message": "Human-readable description of the error" }
```

---

## CORS

The backend allows cross-origin requests from the origins listed in `CORS_ALLOWED_ORIGINS` with credentials enabled (`Access-Control-Allow-Credentials: true`). The wildcard `*` is never used for origins when credentials are present (browsers block this).

