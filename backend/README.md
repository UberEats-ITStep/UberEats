## Quick setup

Requirements: Python 3.10+ and a running PostgreSQL server.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Update `.env` with your PostgreSQL credentials, then create the database named by `POSTGRES_DB`.

```bash
python manage.py makemigrations users restaurants orders
python manage.py migrate
python manage.py runserver
```

The API is at `http://127.0.0.1:8000/api/`.

## Restaurants backend

The restaurants app now aligns its core data model with the shared schema:

- `cuisines` are standalone and referenced by `restaurants.cuisine`
- `categories` are global and reused by `menu_items`
- restaurant detail responses group `menu_items` cleanly inside their respective `categories`

Useful commands:

```bash
python manage.py migrate
python manage.py test restaurants --keepdb
```

## Authentication endpoints

### Register

`POST /api/auth/register/`

Phone number and address are optional. New frontend registrations use the `Client` role.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "role": "Client",
    "phone_number": "+380001112233",
    "address": "Kyiv"
  }'
```

Response (`201 Created`):

```json
{
  "email": "user@example.com",
  "role": "Client"
}
```

An existing email returns `400 Bad Request`:

```json
{
  "email": ["user with this email already exists."]
}
```

### Login

`POST /api/auth/login/`

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

Response (`200 OK`):

```json
{
  "refresh": "<refresh-token>",
  "access": "<access-token>"
}
```

Unknown emails and incorrect passwords return `401 Unauthorized` with a clear `detail` message.

### Refresh access token

`POST /api/auth/refresh/`

```bash
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh-token>"}'
```

Response (`200 OK`):

```json
{
  "access": "<new-access-token>"
}
```

### Profile

`GET /api/profile/` requires an access token.

```bash
curl http://127.0.0.1:8000/api/profile/ \
  -H "Authorization: Bearer <access-token>"
```

Response (`200 OK`):

```json
{
  "phone_number": "+380001112233",
  "address": "Kyiv"
}
```

The same endpoint accepts `PUT` and `PATCH` to update these fields.

```bash
curl -X PATCH http://127.0.0.1:8000/api/profile/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"address":"Lviv"}'
```

## JWT requirements

- Send the access token as `Authorization: Bearer <access-token>`.
- Access tokens expire after 60 minutes.
- Refresh tokens expire after 7 days and are used only with `/api/auth/refresh/`.
- Registration, login, and token refresh do not require authentication.
- Profile requests require a valid access token.
- Missing, invalid, or expired access tokens return `401 Unauthorized`.

## Favorites

Apply the committed Favorites migration and run its tests:

```bash
python manage.py migrate
python manage.py test favorites --keepdb
```

All endpoints require `Authorization: Bearer <access-token>`:

- `GET /api/favorites/` lists the current user's favorites.
- `POST /api/favorites/` with `{"restaurant": <id>}` adds one.
- `DELETE /api/favorites/<id>/` removes the current user's favorite.
- `GET /api/favorites/check/?restaurant=<id>` returns favorite status.

Duplicate favorites return `400`. Favorites owned by another user are neither
listed nor removable.
