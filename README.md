# Satryawiguna API

Professional RESTful API built with FastAPI, following best practices with layered architecture.

## Features

- ✅ FastAPI with async support
- ✅ Layered architecture (Controller → Service → Repository)
- ✅ MySQL database with SQLAlchemy ORM
- ✅ Alembic for database migrations
- ✅ Pydantic for data validation
- ✅ Swagger documentation (Basic Auth protected)
- ✅ Standardized response format
- ✅ Pagination support
- ✅ Database seeders

## Project Structure

```
api.satryawiguna.me/
├── app/
│   ├── api/            # API routes/controllers
│   ├── core/           # Core configuration
│   ├── models/         # Database models
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic layer
│   └── utils/          # Utilities
├── alembic/            # Database migrations
├── seeders/            # Database seeders
├── .env.example
├── main.py
└── requirements.txt
```

## Setup

1. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Generate a strong JWT secret:

   ```bash
   openssl rand -hex 32
   ```

3. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations:**

   ```bash
   # Create the MySQL database first
   createdb satryawiguna
   ```

   ```bash
   python manage.py migrate
   ```

5. **Seed database:**

   ```bash
   python manage.py seed
   ```

6. **Run server:**
   ```bash
   python manage.py runserver
   # or
   uvicorn main:app --reload
   ```

## Available Commands

```bash
# Run migrations
python manage.py migrate

# Fresh migration (drop all tables and recreate)
python manage.py migrate:fresh

# Rollback last migration
python manage.py migrate:rollback

# Seed database
python manage.py seed

# Create new migration
python manage.py make:migration <migration_name>

# Run development server
python manage.py runserver
```

## API Documentation

Access Swagger documentation at: `http://localhost:8000/docs`

**Credentials:**

- Username: `admin`
- Password: `admin123`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. The authentication system includes:

- **Login**: Email/password authentication with JWT tokens
- **Refresh Token**: Long-lived tokens for obtaining new access tokens
- **Protected Endpoints**: Require valid JWT access token
- **Password Management**: Change password, forgot password, reset password

### Authentication Flow

1. **Login** to get access token and refresh token
2. **Use access token** in Authorization header for protected endpoints
3. **Refresh** access token when it expires using refresh token
4. **Logout** to revoke refresh token

### Endpoints

#### POST `/api/v1/auth/login`

Login with email and password.

**Request Body:**

```json
{
  "email": "admin@satryawiguna.me",
  "password": "admin123"
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...",
    "tokenType": "Bearer",
    "expiresIn": "15m",
    "refreshExpiresIn": "7d",
    "user": {
      "id": 1,
      "name": "Admin User",
      "email": "admin@satryawiguna.me",
      "isActive": true,
      "roles": [
        {
          "id": 1,
          "name": "Admin",
          "slug": "admin"
        }
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST `/api/v1/auth/refresh`

Refresh access token using refresh token.

**Request Body:**

```json
{
  "refreshToken": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6..."
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Token refreshed successfully",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6...",
    "tokenType": "Bearer",
    "expiresIn": "15m",
    "refreshExpiresIn": "7d",
    "user": {...}
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

#### GET `/api/v1/auth/me`

Get current authenticated user information.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@satryawiguna.me",
    "isActive": true,
    "roles": [
      {
        "id": 1,
        "name": "Admin",
        "slug": "admin"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST `/api/v1/auth/logout`

Logout by revoking refresh token.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "refreshToken": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6..."
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Logout successful",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

#### POST `/api/v1/auth/change-password`

Change user password (requires authentication).

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "currentPassword": "admin123",
  "newPassword": "newpassword123",
  "newPasswordConfirmation": "newpassword123"
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Password changed successfully",
  "timestamp": "2024-01-15T11:15:00Z"
}
```

#### POST `/api/v1/auth/forgot-password`

Request password reset email.

**Request Body:**

```json
{
  "email": "admin@satryawiguna.me"
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Password reset email sent (not implemented)",
  "timestamp": "2024-01-15T11:20:00Z"
}
```

#### POST `/api/v1/auth/reset-password`

Reset password with token from email.

**Request Body:**

```json
{
  "token": "reset_token_from_email",
  "password": "newpassword123",
  "passwordConfirmation": "newpassword123"
}
```

**Response:**

```json
{
  "success": true,
  "status": 200,
  "message": "Password reset successful (not implemented)",
  "timestamp": "2024-01-15T11:25:00Z"
}
```

### Using Authentication in Your Requests

**Example with cURL:**

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@satryawiguna.me","password":"admin123"}'

# Use access token for protected endpoints
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

**Example with JavaScript (fetch):**

```javascript
// Login
const loginResponse = await fetch("http://localhost:8000/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "admin@satryawiguna.me",
    password: "admin123",
  }),
});
const { data } = await loginResponse.json();
const { accessToken, refreshToken } = data;

// Use access token for protected endpoints
const userResponse = await fetch("http://localhost:8000/api/v1/auth/me", {
  headers: { Authorization: `Bearer ${accessToken}` },
});
```

### Token Expiration

- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days

When the access token expires, use the refresh token to obtain a new one without requiring the user to log in again.

### Test Users

The following test users are available after seeding:

| Email                 | Password    | Role   |
| --------------------- | ----------- | ------ |
| admin@satryawiguna.me | admin123    | Admin  |
| john@example.com      | password123 | Author |
| jane@example.com      | password123 | User   |

## Pagination

List endpoints support both paginated and non-paginated responses:

**With Pagination (default):**

```
GET /api/v1/admin/users?page=1&limit=10
```

Response includes `pagination` metadata:

```json
{
  "success": true,
  "status": 200,
  "message": "Users retrieved successfully",
  "data": [...],
  "pagination": {
    "total": 25,
    "page": 1,
    "limit": 10,
    "totalPages": 3,
    "hasNextPage": true,
    "hasPreviousPage": false
  },
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Without Pagination:**
Set `limit` to `null` or omit it to get all records:

```
GET /api/v1/admin/users?limit=null
```

Response without pagination metadata:

```json
{
  "success": true,
  "status": 200,
  "message": "Users retrieved successfully",
  "data": [...],
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Query Parameters:**

- `page`: Page number (default: 1, only used with pagination)
- `limit`: Items per page (default: 10, set to `null` for all records)
- `sortBy`: Field to sort by (default: `created_at`)
- `sortOrder`: Sort order - `ASC` or `DESC` (default: `DESC`)
- `keyword`: Search keyword (optional)

## Response Format

All API responses follow a standardized format:

**Success (no data):**

```json
{
  "success": true,
  "status": 200,
  "message": "Success",
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Success (single item):**

```json
{
  "success": true,
  "status": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@satryawiguna.me",
    "created_at": "2026-03-15T22:22:19",
    "updated_at": "2026-03-15T22:22:19"
  },
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Success (list without pagination):**

```json
{
  "success": true,
  "status": 200,
  "message": "Users retrieved successfully",
  "data": [
    {...},
    {...}
  ],
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Success (list with pagination):**

```json
{
  "success": true,
  "status": 200,
  "message": "Users retrieved successfully",
  "data": [
    {...},
    {...}
  ],
  "pagination": {
    "total": 25,
    "page": 1,
    "limit": 10,
    "totalPages": 3,
    "hasNextPage": true,
    "hasPreviousPage": false
  },
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

**Error:**

```json
{
  "success": false,
  "status": 404,
  "message": "User not found",
  "timestamp": "2026-03-16T00:00:00.000Z"
}
```

## License

MIT
