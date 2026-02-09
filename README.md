# SDLC Agent Pipeline Tool

An internal tool for deploying AI agents across the Software Development Lifecycle (SDLC), enabling automated requirement-to-release workflows.

## The 6 Agents

| Agent | Codename | Description |
|-------|----------|-------------|
| 1 | **SCRIBE** | Transforms requirements into feature documents |
| 2 | **ARCHITECT** | Converts feature docs into implementation plans |
| 3 | **FORGE** | Implements code changes, runs tests |
| 4 | **HERALD** | Creates merge requests, notifies CI/CD |
| 5 | **SENTINEL** | Reviews code quality, routes back if needed |
| 6 | **PHOENIX** | Manages releases, notifies stakeholders |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend dev server)
- RabbitMQ (for task queue)
- Redis (optional, for caching)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment (dev/prod)
set APP_ENV=dev  # Windows
export APP_ENV=dev  # Linux/Mac

# Run database migrations
python -m app.db.migrate

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Celery Workers

```bash
# Start RabbitMQ (Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Start Celery worker (in separate terminal)
cd backend
celery -A app.celery_app worker --loglevel=info --concurrency=2
```

### Frontend Setup

```bash
# For development, simply open in browser
start frontend/index.html  # Windows
open frontend/index.html   # Mac

# Or use a simple HTTP server
cd frontend
python -m http.server 3000
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **RabbitMQ Admin**: http://localhost:15672 (guest/guest)

## Environment Configuration

Create `.env` file in `backend/`:

```env
# Environment: dev | prod
APP_ENV=dev

# Database
DATABASE_URL=sqlite:///./dev.db
# DATABASE_URL=postgresql://user:pass@localhost/sdlc_agents

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Worker limits
MAX_WORKERS=5
```

## Project Structure

```
├── backend/           # FastAPI + Celery
├── frontend/          # HTML + Bootstrap + JS
├── docs/              # Architecture docs
├── docker-compose.yml # RabbitMQ + services
└── README.md
```

## Documentation

- [Architecture](docs/architecture.md) - System design and patterns
- [Agents](docs/agents.md) - Agent specifications and prompts

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

## License

Internal use only.
