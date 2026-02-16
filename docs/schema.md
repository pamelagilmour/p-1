# Data schema

## Objective

Two table schema for storing users and their entries.

## Tables

### users

Stores user auth and profile info.

```sql
CREATE TABLE users {
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    pass_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
}
```

Fields:
+ `id`: auto-incrementing primary key
+ `email`: unique user email for logging in
+ `pass_hash`: hashed password
+ `created_at`: account creation timestamp
+ `updated_at`: last updated timestamp 

### entries
