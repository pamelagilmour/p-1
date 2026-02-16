# AI-Powered Developer Knowledge Base

> A full-stack application that helps developers manage and query their technical knowledge using AI agents and custom MCP servers.

## 🚀 Status: In Development

Currently building core functionality. Check back for updates!

## 📋 Overview

This project demonstrates:
- Full-stack development (Next.js + FastAPI)
- Custom MCP server integration
- AI agent implementation with Claude API
- Modern system design patterns (caching, message queues, distributed systems)
- Production-grade authentication and API design

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (TBD)

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL

**Infrastructure:**
- Redis (caching & message queue)
- Docker Compose (local development)

**AI/MCP:**
- Anthropic Claude API
- Custom MCP Server (Python SDK)

## 🏗️ Architecture
```
┌─────────────────────────────────────────────┐
│                    User                      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│          Frontend (Next.js)                  │
│  - UI for creating/viewing knowledge entries│
│  - Chat interface for AI questions          │
└─────────────────┬───────────────────────────┘
                  ↓ (HTTP requests)
┌─────────────────────────────────────────────┐
│       Backend API (FastAPI)                  │
│  - Handle CRUD operations                    │
│  - Coordinate AI requests                    │
│  - Call Claude API when user asks questions │
└──────┬──────────────────┬───────────────────┘
       │                  │
       ↓                  ↓
┌──────────────┐   ┌─────────────────────────┐
│  PostgreSQL  │   │    Claude API           │
│   Database   │   │  (with MCP integration) │
│              │   └──────────┬──────────────┘
│ - Users      │              │
│ - Knowledge  │              │ (calls when needed)
│   Entries    │              ↓
└──────┬───────┘   ┌─────────────────────────┐
       │           │   MCP Server (Python)   │
       │           │  - search_knowledge()   │
       │           │  - get_entry()          │
       └───────────┤  - list_entries()       │
         (queries) └─────────────────────────┘
```

**Key Components:**
- REST API with authentication
- MCP server for GitHub/code repository integration
- AI agent with multi-step reasoning
- Redis caching layer
- Background job processing

## 🚦 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis (optional for local dev)

### Installation

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Environment Variables:**
```bash
# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ANTHROPIC_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
```

## 📊 Features

- [ ] User authentication (JWT)
- [ ] Knowledge base CRUD operations
- [ ] AI-powered search and Q&A
- [ ] Custom MCP server for code analysis
- [ ] Real-time updates via WebSockets
- [ ] Redis caching layer
- [ ] Background job processing
- [ ] Rate limiting and API security

## 🧪 Testing
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## 📈 System Design Highlights

- **Caching Strategy:** Redis with 15-minute TTL for frequently accessed data
- **Rate Limiting:** Token bucket algorithm (100 req/min per user)
- **Database Optimization:** Indexed queries, connection pooling
- **Scalability:** Designed to handle 10k+ concurrent users (documented in ARCHITECTURE.md)

## 🚀 Deployment

- Frontend: Vercel
- Backend: Railway
- Database: Railway PostgreSQL
- Redis: Upstash

[Live Demo](https://your-demo-link.com) (Coming soon)

## 📝 Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [API Documentation](./API.md)
- [MCP Server Documentation](./backend/mcp/README.md)

## 🎯 Learning Goals

This project demonstrates:
- System design principles at scale
- Integration of modern AI tooling (MCP, Claude API)
- Production-grade code quality and testing
- DevOps and deployment practices

## 📧 Contact

Questions or feedback? Open an issue or reach out on [LinkedIn/Twitter/Email].

---

Built as part of my software engineering portfolio | [View Other Projects](link-to-portfolio)
