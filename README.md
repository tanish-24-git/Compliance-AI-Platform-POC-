# Compliance AI Platform (POC)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/frontend-React-blue)
![Docker](https://img.shields.io/badge/deployment-Docker-blue)

**Automated Compliance & Content Generation for the Insurance Industry**

This Proof of Concept (POC) demonstrates an AI-powered platform that enables insurance agents to generate marketing content that is automatically validated against strictly enforced compliance rules (IRDAI/Brand Guidelines).

## 🚀 Key Features

- **Compliance-Aware Generation**: Generates content that inherently understands regulatory context using RAG (Retrieval Augmented Generation).
- **Automated Verification**: Checks generated content against a database of rules using both deterministic and AI-based methods.
- **Rule Extraction**: Automatically ingests PDF regulatory documents and extracts executable compliance rules.
- **Tech Stack Switch**: Configurable LLM backend (Switch between Groq and Gemini).

## 🏗 Architecture

The system relies on a Microservices-ready architecture:

- **Frontend**: React + TypeScript (User Interface)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Relational Data)
- **Vector DB**: Pinecone (Semantic Search for Rules)
- **LLM Provider**: Groq (Llama 3.3) / Google Gemini

For detailed architecture documentation, see [docs/](docs/).

### Services
- **[Content Service](docs/backend/content_service.md)**: Generates and purifies content.
- **[Compliance Service](docs/backend/compliance_service.md)**: Checks existing documents.
- **[Rule Service](docs/backend/rule_service.md)**: Manages rule lifecycle.

## 🛠 Prerequisites

- **Docker** & **Docker Compose**
- **Pinecone API Key** (Vector DB)
- **Groq API Key** (Primary LLM)
- **Gemini API Key** (Fallback/Embeddings)

## ⚡ Getting Started

1.  **Clone the repository**
    ```bash
    git clone <repo-url>
    cd poc
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory (copy from `.env.example`):
    ```bash
    cp .env.example .env
    ```
    Populate the keys:
    ```ini
    DATABASE_URL=postgresql://postgres:postgres@compliance-db:5432/compliance_db
    PINECONE_API_KEY=your_key
    PINECONE_ENV=your_env
    GROQ_API_KEY=your_key
    GEMINI_API_KEY=your_key
    DEFAULT_LLM_PROVIDER=groq
    ```

3.  **Run with Docker**
    ```bash
    docker compose up -d --build
    ```

4.  **Access the Application**
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📝 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_LLM_PROVIDER` | Primary LLM for generation | `groq` |
| `REVIEWER_LLM_PROVIDER` | LLM for compliance auditing | `groq` |
| `SEMANTIC_SIMILARITY_THRESHOLD` | Threshold for duplicate rule detection | `0.85` |

## 📚 Documentation

Detailed documentation for each service is available in the `docs/` directory:

- [Backend Content Service](docs/backend/content_service.md)
- [Backend Compliance Service](docs/backend/compliance_service.md)
- [Backend Rule Service](docs/backend/rule_service.md)
- [Frontend Architecture](docs/frontend/architecture.md)

## 📄 License

This project is licensed under the MIT License.
