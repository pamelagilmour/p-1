# API Endpoints

## Base URL

`http://localhost:8000` (development)

## Authentication

All endpoints except

`/auth/register`, 

`/auth/login`, and 

`/health` 

require authentication token in header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Create a New User

```
POST /api/auth/register

Request body:
{
    "email": "user@email.com",
    "password": "xxxxxxxxxxx"
}

Response (201 Created):
{
    "id": 0,
    "email": "user@email.com",
    "created_at": "2025-02-17T10:30:00Z"
}
```

#### Login

```
POST /api/auth/login

Request Body:
{
    "email": "user@email.com",
    "password": "xxxxxxxxxxx"
}

Response (200 OK):
{
  "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_type": "bearer"
}
```


#### Get Current User
```
GET /api/auth/me

Response (200 OK):
{
    "id": 0,
    "email": "user@email.com",
    "created_at": "2025-02-17T10:30:00Z"
}
```

### Knowledge Entries

#### Get All Entries
```
GET /api/entries

Response (200 OK):
{
  "entries": [
    {
      "id": 0,
      "title": "React Hooks Guide",
      "content": "useState and useEffect are...",
      "tags": ["React", "JavaScript"],
      "created_at": "2025-02-17T10:30:00Z",
      "updated_at": "2025-02-17T10:30:00Z"
    }
  ]
}
```

#### Get Single Entry
```
GET /api/entries/{id}

Response (200 OK):
{
  "id": 1,
  "title": "React Hooks Guide",
  "content": "useState and useEffect are...",
  "tags": ["React", "JavaScript"],
  "created_at": "2025-02-17T10:30:00Z",
  "updated_at": "2025-02-17T10:30:00Z"
}
```

#### Create Entry
```
POST /api/entries

Request Body:
{
  "title": "Python Decorators",
  "content": "Decorators are functions that...",
  "tags": ["Python"]
}

Response (201 Created):
{
  "id": 3,
  "title": "Python Decorators",
  "content": "Decorators are functions that...",
  "tags": ["Python"],
  "created_at": "2025-02-17T11:00:00Z",
  "updated_at": "2025-02-17T11:00:00Z"
}
```

#### Update Entry
```
PUT /api/entries/{id}

Request Body:
{
  "title": "Python Decorators (Updated)",
  "content": "Updated content...",
  "tags": ["Python", "Advanced"]
}

Response (200 OK):
{
  "id": 4,
  "title": "Python Decorators (Updated)",
  "content": "Updated content...",
  "tags": ["Python", "Advanced"],
  "created_at": "2025-02-17T11:00:00Z",
  "updated_at": "2025-02-17T11:15:00Z"
}
```

#### Delete Entry
```
DELETE /api/entries/{id}

Response (204 No Content):
(empty response)
```

#### Search Entries
```
GET /api/entries/search?q=react hooks

Response (200 OK):
{
  "results": [
    {
      "id": 1,
      "title": "React Hooks Guide",
      "content": "useState and useEffect are...",
      "tags": ["React", "JavaScript"]
    }
  ]
}
```


### Chat

#### Ask Agent a Question
```
POST /api/chat

Request Body:
{
  "message": "What do I know about React hooks?"
}

Response (200 OK):
{
  "response": "Based on your knowledge base, you have notes about...",
  "sources": [1, 3]  // IDs of entries used to answer
}
```

---

### Utility

#### Health Check
```
GET /api/health

Response (200 OK):
{
  "status": "healthy",
  "database": "connected"
}
```

#### Get All Tags
```
GET /api/tags

Response (200 OK):
{
  "tags": ["React", "Python", "TypeScript", "JavaScript"]
}
```

## Rate Limiting

All protected endpoints are rate limited to **100 requests per minute per user**.

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1708197123
```

**Rate Limit Exceeded (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 42 seconds."
}
```

**Headers on 429:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1708197123
Retry-After: 42
```

## Design Decisions

**RESTful conventions:**
- GET = retrieve data
- POST = create new resource
- PUT = update existing resource
- DELETE = remove resource

**Status codes:**
- 200 OK = successful request
- 201 Created = new resource created
- 204 No Content = successful delete
- 400 Bad Request = invalid input
- 401 Unauthorized = not logged in
- 404 Not Found = resource doesn't exist
- 500 Server Error = something broke

**Authentication:**
- JWT tokens in Authorization header
- Token expires after 24 hours (configurable)

**Pagination (future):**
- Can add `?page=1&limit=20` to `/api/entries` later