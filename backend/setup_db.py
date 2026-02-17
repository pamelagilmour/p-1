import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_user_id ON knowledge_entries(user_id);
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_tags ON knowledge_entries USING GIN(tags);
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Database setup complete!")