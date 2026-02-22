# threeddocs-api

Django REST Framework backend for the [threeddocs](https://github.com/bie7u/threeddocs) 3D docs editor.

- **JWT authentication** via HTTP-only cookies (no `Authorization` header needed)
- **Projects CRUD** – store and manage 3D model projects per user
- **Public shareable links** – read-only access without authentication

---

## Table of Contents

1. [Setup](#setup)
2. [Authentication](#authentication)
   - [POST /api/auth/login](#post-apiauthlogin)
   - [POST /api/auth/logout](#post-apiauthlogout)
   - [POST /api/auth/refresh](#post-apiauthrefresh)
   - [GET /api/auth/me](#get-apiauthme)
3. [Projects](#projects)
   - [Project object](#project-object)
   - [GET /api/projects](#get-apiprojects)
   - [POST /api/projects](#post-apiprojects)
   - [GET /api/projects/{id}](#get-apiprojectsid)
   - [PUT /api/projects/{id}](#put-apiprojectsid)
   - [DELETE /api/projects/{id}](#delete-apiprojectsid)
   - [GET /api/projects/{id}/public](#get-apiprojectsidpublic)
4. [Data types](#data-types)
5. [Error format](#error-format)
6. [CORS & cookies](#cors--cookies)

---

## Setup

### Requirements

- Python 3.10+

### Install & run

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Open .env and set at least DJANGO_SECRET_KEY in production

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) create a superuser for the /admin panel
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API is available at **`http://localhost:8000/api`**.

### Environment variables

| Variable | Default | Required in prod | Description |
|----------|---------|-----------------|-------------|
| `DJANGO_SECRET_KEY` | insecure built-in | **yes** | Django secret key |
| `DJANGO_DEBUG` | `True` | – | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | **yes** | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | **yes** | Comma-separated frontend origins |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5173,...` | **yes** | Comma-separated trusted origins |

### Running tests

```bash
python manage.py test
```

---

## Authentication

The API uses **JWT tokens stored in HTTP-only cookies**. The browser attaches the `access_token` cookie automatically on every request – no `Authorization` header is required and JavaScript cannot read the cookie (XSS protection).

### Token lifetimes

| Cookie | Lifetime | Description |
|--------|----------|-------------|
| `access_token` | **15 minutes** | Short-lived JWT; sent with every API call |
| `refresh_token` | **7 days** | Long-lived token; used only to issue a new access token |

Both cookies are set with `HttpOnly`, `SameSite=Lax`, and `Secure` (production only).

### Automatic refresh flow

```
Client                            Server
  │──── GET /api/projects ──────────▶│  401 Unauthorized
  │◀─── 401 ────────────────────────│
  │──── POST /api/auth/refresh ─────▶│  200 OK  (new cookies set)
  │◀─── 200 ────────────────────────│
  │──── GET /api/projects (retry) ──▶│  200 OK
```

If `/api/auth/refresh` also returns `401` the frontend redirects to the login page.

---

### `POST /api/auth/login`

Authenticate with email and password. Sets both token cookies on success.

**No auth required.**

**Request**

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "jan@example.com",
  "password": "secret123"
}
```

**curl example**

```bash
curl -s -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jan@example.com","password":"secret123"}'
```

**Response `200 OK`**

```json
{
  "id": "1",
  "email": "jan@example.com",
  "name": "Jan Kowalski"
}
```

> `name` is `first_name + last_name`; falls back to `username` when blank.

**Response `401 Unauthorized`**

```json
{ "message": "Invalid email or password" }
```

**Response `400 Bad Request`** – missing or invalid fields

```json
{ "message": "Invalid email or password" }
```

---

### `POST /api/auth/logout`

Clears both token cookies. **Requires a valid `access_token` cookie.**

**curl example**

```bash
curl -s -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/auth/logout
```

**Response `204 No Content`** – cookies cleared, empty body.

**Response `401 Unauthorized`** – access token missing or expired.

---

### `POST /api/auth/refresh`

Issues a new `access_token` (and rotates the `refresh_token`) using the `refresh_token` cookie. No request body needed. **No access token required.**

**curl example**

```bash
curl -s -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/auth/refresh
```

**Response `200 OK`**

```json
{ "ok": true }
```

New `access_token` and `refresh_token` cookies are set in the response headers.

**Response `401 Unauthorized`** – refresh token missing, expired or tampered.

```json
{ "message": "Invalid or expired refresh token." }
```

---

### `GET /api/auth/me`

Returns the currently authenticated user. **Requires `access_token` cookie.**

**curl example**

```bash
curl -s -b cookies.txt http://localhost:8000/api/auth/me
```

**Response `200 OK`**

```json
{
  "id": "1",
  "email": "jan@example.com",
  "name": "Jan Kowalski"
}
```

**Response `401 Unauthorized`** – triggers the automatic refresh flow on the frontend.

---

## Projects

All project endpoints except `/public` require a valid `access_token` cookie. Every user can only access their **own** projects.

### Project object

All project endpoints send and receive the same flat JSON object:

```json
{
  "id": 42,
  "name": "Assembly Guide v1",
  "projectType": "builder",
  "projectModelUrl": null,
  "steps": [
    {
      "id": "step-abc",
      "title": "Attach the base plate",
      "description": "<p>Place the base plate on a flat surface.</p>",
      "modelPath": "box",
      "cameraPosition": { "x": 5, "y": 5, "z": 5 },
      "shapeType": "cube",
      "highlightColor": "#ff0000",
      "annotations": [],
      "modelScale": 1
    }
  ],
  "connections": [
    { "id": "e1-2", "source": "step-abc", "target": "step-def" }
  ],
  "guide": [
    { "stepId": "step-abc", "label": "Step 1" }
  ],
  "nodePositions": {
    "step-abc": { "x": 100, "y": 200 }
  },
  "lastModified": 1700000000000
}
```

#### Field reference

| Field | Type | Access | Description |
|-------|------|--------|-------------|
| `id` | `integer` | **read-only** | Server-assigned primary key. |
| `name` | `string` | read/write | Human-readable project title (max 255 chars). |
| `projectType` | `"builder" \| "upload"` | read/write | Editor mode. Defaults to `"builder"`. |
| `projectModelUrl` | `string \| null` | read/write | Remote URL or base64 data-URL of an uploaded GLB/GLTF model (e.g. `"data:model/gltf-binary;base64,…"`). `null` for builder projects without a custom model. |
| `steps` | `InstructionStep[]` | read/write | Ordered list of instruction steps. See [InstructionStep](#instructionstep). |
| `connections` | `Edge[]` | read/write | ReactFlow edges between steps. See [Edge](#edge). |
| `guide` | `GuideStep[]` | read/write | Ordered guide entries. See [GuideStep](#guidestep). |
| `nodePositions` | `Record<string, {x,y}>` | read/write | Map of step `id` → canvas position used by the node editor. |
| `lastModified` | `integer` | **read-only** | Unix timestamp in **milliseconds** of the last server save. Set automatically; omit in requests. |

---

### `GET /api/projects`

Returns all projects owned by the authenticated user, ordered by most recently modified first.

**curl example**

```bash
curl -s -b cookies.txt http://localhost:8000/api/projects
```

**Response `200 OK`** – array of [Project](#project-object) objects (may be empty):

```json
[
  {
    "id": 42,
    "name": "Assembly Guide v1",
    "projectType": "builder",
    "projectModelUrl": null,
    "steps": [],
    "connections": [],
    "guide": [],
    "nodePositions": {},
    "lastModified": 1700000000000
  },
  {
    "id": 7,
    "name": "Turbine exploded view",
    "projectType": "upload",
    "projectModelUrl": "https://cdn.example.com/turbine.glb",
    "steps": [],
    "connections": [],
    "guide": [],
    "nodePositions": {},
    "lastModified": 1699000000000
  }
]
```

**Response `401 Unauthorized`**

---

### `POST /api/projects`

Creates a new project. The server assigns the `id` and `lastModified`.

**curl example**

```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Guide",
    "projectType": "builder",
    "projectModelUrl": null,
    "steps": [],
    "connections": [],
    "guide": [],
    "nodePositions": {}
  }'
```

**Response `201 Created`** – the saved [Project](#project-object) with server-assigned `id`:

```json
{
  "id": 43,
  "name": "My First Guide",
  "projectType": "builder",
  "projectModelUrl": null,
  "steps": [],
  "connections": [],
  "guide": [],
  "nodePositions": {},
  "lastModified": 1700001000000
}
```

**Response `400 Bad Request`** – `name` is missing:

```json
{ "name": ["This field is required."] }
```

**Response `401 Unauthorized`**

---

### `GET /api/projects/{id}`

Returns a single project by its integer `id`. The project must belong to the authenticated user.

**curl example**

```bash
curl -s -b cookies.txt http://localhost:8000/api/projects/43
```

**Response `200 OK`** – [Project](#project-object).

**Response `404 Not Found`** – project does not exist or belongs to another user.

---

### `PUT /api/projects/{id}`

Fully replaces a project. **All writable fields must be supplied** (this is a full replace, not a partial patch).

**curl example**

```bash
curl -s -b cookies.txt -X PUT http://localhost:8000/api/projects/43 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Guide – updated",
    "projectType": "builder",
    "projectModelUrl": null,
    "steps": [
      {
        "id": "step-1",
        "title": "Step one",
        "description": "Do this first.",
        "modelPath": "box",
        "cameraPosition": { "x": 5, "y": 5, "z": 5 },
        "shapeType": "cube"
      }
    ],
    "connections": [],
    "guide": [{ "stepId": "step-1", "label": "1" }],
    "nodePositions": { "step-1": { "x": 200, "y": 100 } }
  }'
```

**Response `200 OK`** – the updated [Project](#project-object).

**Response `400 Bad Request`** – validation error (e.g. invalid `projectType`).

**Response `404 Not Found`** – project does not exist or belongs to another user.

**Response `401 Unauthorized`**

---

### `DELETE /api/projects/{id}`

Permanently deletes a project.

**curl example**

```bash
curl -s -b cookies.txt -X DELETE http://localhost:8000/api/projects/43
```

**Response `204 No Content`** – project deleted, empty body.

**Response `404 Not Found`** – project does not exist or belongs to another user.

**Response `401 Unauthorized`**

---

### `GET /api/projects/{id}/public`

Returns a project **without any authentication**. Used by the shareable `/view/:projectId` link in the frontend. Anyone with the URL can read the project.

**curl example**

```bash
curl -s http://localhost:8000/api/projects/43/public
```

**Response `200 OK`** – [Project](#project-object).

**Response `404 Not Found`** – project does not exist.

---

## Data types

### `InstructionStep`

Each element of the `steps` array:

```json
{
  "id": "step-abc",
  "title": "Attach the base plate",
  "description": "<p>Sanitized HTML from the rich-text editor.</p>",
  "modelPath": "box",
  "cameraPosition": { "x": 5, "y": 5, "z": 5 },
  "shapeType": "cube",
  "highlightColor": "#ff0000",
  "annotations": [],
  "customModelUrl": null,
  "modelScale": 1,
  "focusMeshName": null,
  "focusPoint": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Client-generated UUID for the step |
| `title` | `string` | Short step title |
| `description` | `string` | Sanitized HTML content from the rich-text editor |
| `modelPath` | `string` | Built-in shape name (`"box"`, `"sphere"`, …) or mesh identifier |
| `cameraPosition` | `{x,y,z}` | Three.js camera position for this step |
| `shapeType` | `"cube" \| "sphere" \| "cylinder" \| "cone" \| "custom"` | Shape of the highlight annotation |
| `highlightColor` | `string` | CSS colour string, e.g. `"#ff0000"` |
| `annotations` | `Annotation[]` | In-scene text labels |
| `customModelUrl` | `string \| null` | Base64 data-URL of an embedded GLB/GLTF for this step |
| `modelScale` | `number` | Scale multiplier for the step model |
| `focusMeshName` | `string \| null` | Upload-type: mesh name to highlight |
| `focusPoint` | `[x, y, z] \| null` | World-space point the camera focuses on |

### `Edge`

Each element of the `connections` array (ReactFlow edge):

```json
{
  "id": "e-step-abc-step-def",
  "source": "step-abc",
  "target": "step-def"
}
```

Additional ReactFlow edge properties (`type`, `label`, `data`, etc.) are stored as-is.

### `GuideStep`

Each element of the `guide` array:

```json
{
  "stepId": "step-abc",
  "label": "1"
}
```

---

## Error format

All error responses (auth and validation) use the same JSON shape:

```json
{ "message": "Human-readable description of the error" }
```

**Common status codes**

| Status | When |
|--------|------|
| `400 Bad Request` | Missing required field or invalid value |
| `401 Unauthorized` | Missing, expired or invalid access token |
| `404 Not Found` | Resource does not exist or belongs to another user |

---

## CORS & cookies

### CORS

The backend allows cross-origin requests only from the origins listed in `CORS_ALLOWED_ORIGINS` with `Access-Control-Allow-Credentials: true`. The wildcard `*` is never used when credentials are enabled (browsers block this).

### Cookie attributes

| Attribute | Value | Reason |
|-----------|-------|--------|
| `HttpOnly` | `true` | JavaScript cannot read the cookie (XSS protection) |
| `SameSite` | `Lax` | Sent on same-site requests and top-level navigations (CSRF protection) |
| `Secure` | `true` in production | Cookie is only transmitted over HTTPS |
| `Path` | `/` | Cookie is sent with every request to the server |
| `Max-Age` | 900 / 604800 | Access: 15 min; Refresh: 7 days |

