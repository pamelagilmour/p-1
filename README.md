# AI-Powered Knowledge Base

> A full-stack application that lets users store knowledge entries and ask AI questions about their data using a custom MCP server and Claude API.

## 🚀 Status: Core Features Complete

Core functionality is working! Currently adding system design elements (caching, rate limiting).

## ✨ Demo

**Storing Knowledge:**
- Create, edit, and delete knowledge entries with tags
- Organized personal knowledge base

**AI Chat:**
- Ask Claude questions about your knowledge base
- Claude uses custom MCP tools to search your database
- Agentic loop - Claude decides which tools to call

Example queries:
- "What do I know about React?"
- "Show me all my entries tagged with TypeScript"
- "Summarize everything in my knowledge base"

## 📋 Overview

This project demonstrates:
- Full-stack development (Next.js + FastAPI)
- Custom MCP server integration
- AI agent implementation with Claude API
- JWT authentication and protected routes
- PostgreSQL database design with relationships
- Production-grade API design (validation, error handling, status codes)
- System design patterns (caching, message queues - in progress)

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Context (auth state management)

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication (python-jose)
- Password hashing (passlib/bcrypt)

**AI/MCP:**
- Anthropic Claude API
- Custom MCP Server (FastMCP)
- Agentic tool loop

**Infrastructure:**
- Redis (caching - in progress)
- Docker Compose (in progress)

## 🏗️ Architecture
```
User
  ↓
Frontend (Next.js)
  ↓
Backend API (FastAPI)
  ↓         ↓
Database   Claude API
(PostgreSQL)   ↓
  ↑       MCP Server
  └───────────┘
  (Claude searches DB
   via MCP tools)
```

**AI Flow:**
1. User asks question in chat interface
2. Frontend sends request to FastAPI backend
3. Backend calls Claude API with MCP tools attached
4. Claude decides which tools to use
5. MCP tools query PostgreSQL database
6. Claude synthesizes results into natural language
7. Response returned to user

## 🗄️ Database Schema
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge entries table
CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 MCP Server Tools

Custom MCP server exposes 4 tools to Claude:

| Tool | Description |
|------|-------------|
| `search_knowledge` | Search entries by keyword in title/content |
| `get_all_entries` | Get all entries for a user |
| `get_entry_by_id` | Get specific entry by ID |
| `search_by_tag` | Filter entries by tag |

## 🔒 API Endpoints

**Authentication:**
```
POST /api/auth/register   - Create account
POST /api/auth/login      - Login, get JWT token
GET  /api/auth/me         - Get current user (protected)
```

**Knowledge Entries (all protected):**
```
GET    /api/entries        - List all entries
POST   /api/entries        - Create entry
GET    /api/entries/{id}   - Get single entry
PUT    /api/entries/{id}   - Update entry
DELETE /api/entries/{id}   - Delete entry
```

**AI Chat (protected):**
```
POST /api/chat             - Send message to Claude
```

## 📊 Features

**Complete ✅**
- [x] User registration and login
- [x] JWT authentication with protected routes
- [x] Full CRUD for knowledge entries
- [x] Tag support for entries
- [x] Custom MCP server with 4 tools
- [x] Claude API integration
- [x] Agentic loop (Claude decides which tools to use)
- [x] Chat interface in dashboard

**In Progress ⏳**
- [ ] Redis caching for API responses
- [ ] Rate limiting (token bucket algorithm)
- [ ] Background job processing
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Deployment (Vercel + Railway)

**Planned 📋**
- [ ] Search endpoint with full-text search
- [ ] Pagination for large entry lists
- [ ] Entry categories
- [ ] Export knowledge base

## 🚦 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 15+

### Database Setup
```sql
CREATE DATABASE knowledge_base;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_entries_user_id ON knowledge_entries(user_id);
CREATE INDEX idx_knowledge_entries_tags ON knowledge_entries USING GIN(tags);
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### MCP Server Setup
```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python knowledge_base_server.py
```

### Environment Variables

**backend/.env**
```
DATABASE_URL=postgresql://localhost:5432/knowledge_base
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## 🧪 Testing
```bash
# Backend tests (coming soon)
pytest

# Test MCP server
mcp dev mcp-server/knowledge_base_server.py

# API docs (auto-generated)
http://localhost:8000/docs
```

## 📈 System Design Highlights

**Current:**
- RESTful API with proper status codes and error handling
- JWT authentication with 24hr token expiration
- Password hashing with bcrypt
- Database indexes for query performance
- Input validation with Pydantic models
- CORS configuration
- Agentic AI loop with tool orchestration

**Coming Soon:**
- Redis caching (target: 80%+ cache hit rate)
- Rate limiting (token bucket: 100 req/min per user)
- Background job processing for long AI tasks
- Horizontal scaling strategy

## 🚀 Deployment

- Frontend: Vercel (coming soon)
- Backend: Railway (coming soon)
- Database: Railway PostgreSQL (coming soon)

[Live Demo](#) - Coming soon!

## 📝 Documentation

- [Architecture Overview](./docs/architecture.md)
- [Database Schema](./docs/database-schema.md)
- [API Endpoints](./docs/api-endpoints.md)
- [MCP Server Documentation](./mcp-server/README.md)

## 🎯 What I Learned

- How MCP protocol works and how to build custom servers
- Agentic AI loops (Claude decides which tools to call)
- JWT authentication implementation from scratch
- FastAPI with PostgreSQL (SQLAlchemy, psycopg2)
- Full-stack TypeScript with Next.js App Router
- System design patterns for scalable applications

---

Built as part of my software engineering portfolio | [View Other Projects](https://github.com/pamelagilmour)
