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