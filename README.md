# Dev Notes AI

A full-stack application that helps developers organize and query their technical knowledge using AI. Built with custom MCP server integration, Redis caching, and background job processing.

![Screenshot](./screenshots/main-interface.png)

## Key Features

- **AI-powered search and knowledge retrieval** - Natural language queries across your knowledge base
- **Custom MCP server for tool integration** - Extensible architecture for adding new capabilities
- **Redis caching** - Fast query responses and optimized performance
- **Background job processing** - Async indexing and data processing
- **Modern tech stack** - Next.js, TypeScript, FastAPI, PostgreSQL

## Demo

- **[Live Demo](your-deployed-url)** - Try it out (rate-limited for security)
- **[Video Walkthrough](youtube-link)** - 2-minute feature overview

## Tech Stack

**Frontend:**
- Next.js 14
- TypeScript
- React
- [Any UI library you're using - Tailwind? shadcn?]

**Backend:**
- FastAPI (Python)
- PostgreSQL
- Redis
- [Other backend tools]

**AI/Integration:**
- Claude API
- Custom MCP Protocol implementation

## Architecture

- User submits query through Next.js frontend
- Request hits FastAPI backend
- Redis cache checked for existing results
- If cache miss, MCP server processes query with Claude API
- Background jobs handle indexing and data updates
- Results returned and cached for future queries

## Local Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL
- Redis

### Setup

1. Clone the repository
\`\`\`bash
git clone https://github.com/pamelagilmour/dev-notes-ai.git
cd dev-notes-ai
\`\`\`

2. [Rest of your current setup instructions]

## Security Features

- Rate limiting on AI queries
- API key management
- [Whatever app sec you implement]

## Roadmap

- [ ] Additional MCP tool integrations
- [ ] Export/import knowledge base
- [ ] Team collaboration features

## License

MIT

---

Built by [Pam Gilmour](https://my-next-app.sodalitemix.workers.dev/) | [LinkedIn](https://www.linkedin.com/in/pamela-gilmour/) | [GitHub](https://github.com/pamelagilmour)
```

## Don't Forget to Update Your Portfolio

Once this is all done, update your portfolio project section to:
```
Dev Notes AI
A full-stack knowledge management system with AI-powered search, custom MCP server integration, and production-grade caching and background job processing.

Tech: Next.js, TypeScript, FastAPI, PostgreSQL, Redis, Claude API

[View Demo] [View Code] [Watch Video]
