# Data schema

## Objective

Two table schema for storing users and their entries.

## Tables

### users

Stores user auth and profile info.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    pass_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Fields:
+ `id`: auto-incrementing primary key
+ `email`: unique user email for logging in
+ `pass_hash`: hashed password
+ `created_at`: account creation timestamp
+ `updated_at`: last updated timestamp 

### entries

Stores user's knowledge content. Things like notes, code snippets, docs.

```sql
CREATE TABLE entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    context TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Create an index for faster search, by user, by tags
CREATE INDEX idx_entries_user_id ON entries(user_id);
CREATE INDEX inx_entries_tags ON entries USING GIN(tags);
```

fields:
+ `id`: Auto-incrementing primary key
+ `user_id`: Foreign key to users table
+ `title`: Entry title
+ `content`: text content
+ `tags`: aaray of tags to categorize entries
+ `created_at`: Entry creation timestamp
+ `updated_at`: Last edit timestamp
