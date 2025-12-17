# Compliance-First AI Content Generation Platform

> **Industry-Grade POC for Regulated Fintech/Insurance Environments**

A production-aligned, full-stack platform demonstrating compliance-first content generation with deterministic rule enforcement, multi-model AI orchestration, and clear governance.

## 🎯 Overview

This platform ensures that AI-generated content in regulated environments (fintech, insurance) strictly adheres to compliance rules. Rules stored in PostgreSQL **always override AI output**, providing deterministic, auditable compliance enforcement.

### Key Features

- ✅ **Compliance-First Architecture** - Rules override AI, not the other way around
- 🤖 **Multi-Model AI** - Gemini for generation, Groq for compliance review
- 📊 **Vector Search** - Pinecone for semantic rule matching and duplicate detection
- 🔒 **Governance** - Agent, Admin, Super Admin roles with clear responsibilities
- 🐳 **Dockerized** - Easy deployment with Docker Compose
- 📝 **Token-Based Chunking** - Accurate 300-500 token chunks with metadata
- 🎨 **Modern UI** - Clean React frontend with role-based views

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                          │
│  (Agent View | Admin View | Super Admin View)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Rule Engine  │  │ Prompt       │  │ Compliance   │      │
│  │ (Authority)  │  │ Enhancer     │  │ Checker      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┬──────────────┐
         ▼             ▼             ▼              ▼
   PostgreSQL      Gemini API    Groq API     Pinecone
  (Source of      (Generator)   (Reviewer)   (Semantic
    Truth)                                     Search)
```

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **API Keys**:
  - Gemini API key (Google AI)
  - Groq API key
  - Pinecone API key
- **Pinecone Index**: Create an index named `poc` (or your chosen name) with:
  - Dimensions: 1024
  - Metric: cosine
  - Model: llama-text-embed-v2

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd c:\Users\ASUS\OneDrive\Desktop\poc
```

### 2. Configure Environment

The `.env` file is already created with your API keys. Verify it contains:

```bash
# Check .env file exists
cat .env
```

If you need to modify any values, edit `.env` directly. See `.env.example` for the template.

### 3. Start Backend with Docker

```bash
# Build and start PostgreSQL + FastAPI backend
docker-compose up --build
```

This will:
- Start PostgreSQL on port 5432
- Start FastAPI backend on port 8000
- Create database tables automatically
- Wait for services to be healthy

### 4. Seed Database

In a new terminal:

```bash
# Enter the backend container
docker exec -it compliance-backend bash

# Run seed script
python seed.py

# Exit container
exit
```

This creates:
- 3 users (Agent, Admin, Super Admin)
- 5 sample compliance rules
- Pinecone embeddings for rules

### 5. Start Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### 6. Access the Application

Open your browser to **http://localhost:3000**

- **Agent View**: Generate compliant content
- **Admin View**: Monitor violations and analytics
- **Super Admin View**: Manage compliance rules

## 🎮 Usage Guide

### Agent Workflow

1. Select **Agent** role
2. Enter your content generation prompt
3. Optionally upload a document (PDF, DOCX, MD)
4. Click **Generate Compliant Content**
5. Review:
   - Generated content
   - Compliance status (Approved/Rejected)
   - Violations (if any)
   - HARD vs SOFT rule violations

### Admin Workflow

1. Select **Admin** role
2. View tabs:
   - **Violations**: All rule violations with context
   - **Submissions**: Past content generations
   - **Rule Analytics**: Which rules are violated most

### Super Admin Workflow

1. Select **Super Admin** role
2. **Create Rule**:
   - Enter rule text
   - Choose severity (HARD/SOFT)
   - System checks for duplicates (exact + semantic)
3. **Update Rule**:
   - Edit rule text
   - Creates new version, deactivates old
4. **Deactivate Rule**:
   - Soft delete (preserves history)

## 🗄️ Database Schema

### Core Tables

- **users** - Agent, Admin, Super Admin roles
- **rules** - Compliance rules (source of truth)
- **submissions** - Content generation requests
- **content_chunks** - Token-based chunks with metadata
- **violations** - Rule violations detected
- **audit_logs** - Complete audit trail

## 📊 Demo Queries

Connect to PostgreSQL:

```bash
docker exec -it compliance-postgres psql -U compliance -d compliance_db
```

See `demo_queries.md` for 12 ready-to-use SQL queries including:
- List all active rules
- View violations with user context
- Rule hit frequency analytics
- Audit logs
- Success rates

## 🔧 API Endpoints

### Agent Endpoints

- `POST /api/generate` - Generate compliant content
- `GET /api/submissions/{id}` - Get submission details

### Admin Endpoints

- `GET /api/violations` - List all violations
- `GET /api/analytics/rules` - Rule hit frequency
- `GET /api/submissions` - List all submissions

### Super Admin Endpoints

- `POST /api/rules` - Create new rule
- `PUT /api/rules/{id}` - Update rule (creates version)
- `DELETE /api/rules/{id}` - Deactivate rule
- `GET /api/rules` - List all rules

### Health Check

- `GET /health` - Service health and environment validation

## 🧪 Testing

### Test Content Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -F "user_id=1" \
  -F "prompt=Generate a financial disclaimer for investment products"
```

### Test Rule Creation

```bash
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_text": "Test compliance rule",
    "severity": "hard",
    "created_by": 3
  }'
```

## 📁 Project Structure

```
poc/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── db.py                # Database connection
│   │   ├── rule_engine.py       # Rule enforcement
│   │   ├── prompt_enhancer.py   # Prompt injection
│   │   ├── ai_generator.py      # Gemini integration
│   │   ├── reviewer.py          # Groq integration
│   │   ├── compliance_checker.py # Final decision
│   │   ├── doc_parser.py        # PDF/DOCX/MD parser
│   │   ├── chunker.py           # Token-based chunking
│   │   └── embedder.py          # Pinecone integration
│   ├── seed.py                  # Database seeding
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentView.jsx
│   │   │   ├── AdminView.jsx
│   │   │   └── SuperAdminView.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml           # Orchestration
├── .env                         # Environment variables
├── .env.example                 # Environment template
└── demo_queries.md              # SQL queries for demo
```

## 🔐 Security Notes

⚠️ **This is a POC/Demo Application**

- No authentication system (role selected via UI)
- API keys in `.env` file (not for production)
- CORS allows all origins
- Suitable for demo/development only

For production:
- Implement proper authentication (OAuth2, JWT)
- Use secrets management (AWS Secrets Manager, Vault)
- Restrict CORS origins
- Add rate limiting
- Enable HTTPS/TLS
- Implement proper authorization checks

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker exec -it compliance-backend env | grep API_KEY
```

### Database connection failed

```bash
# Check PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart
```

### Pinecone errors

- Verify index exists in Pinecone dashboard
- Check index name matches `PINECONE_INDEX` in `.env`
- Confirm dimensions are 1024 with cosine metric

### Frontend can't connect to backend

- Verify backend is running on port 8000
- Check Vite proxy configuration in `vite.config.js`
- Ensure no CORS errors in browser console

## 📚 Key Technologies

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React 18, Vite
- **AI**: Google Gemini, Groq
- **Vector DB**: Pinecone
- **Deployment**: Docker, Docker Compose
- **Document Processing**: PyPDF2, python-docx
- **Token Counting**: tiktoken

## 🎯 Compliance Flow

1. **User submits prompt** (+ optional document)
2. **Document parsed** (PDF/DOCX/MD → text)
3. **Content chunked** (300-500 tokens with metadata)
4. **Prompt enhanced** (active rules injected)
5. **Gemini generates** content
6. **Groq reviews** for compliance
7. **Rule engine checks** (authoritative)
8. **Backend decides** (rules override AI)
9. **Violations stored** in PostgreSQL
10. **Result returned** to user

## 📝 License

This is a POC/demonstration project for educational purposes.

## 🤝 Support

For issues or questions:
1. Check `demo_queries.md` for database inspection
2. Review Docker logs: `docker-compose logs`
3. Verify environment variables in `.env`
4. Check API health: `curl http://localhost:8000/health`

---

**Built with ❤️ for Compliance-First AI**
