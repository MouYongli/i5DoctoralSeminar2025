## Toy Agent

## Project structure

```
toyagent/
├── backend/              # Python backend
│   ├── .env.example     # Local development environment variables example
│   ├── Dockerfile       # Backend Docker image
│   └── src/
├── frontend/            # Next.js frontend
│   ├── .env.local.example     # Local development environment variables example
│   ├── Dockerfile       # Frontend Docker image
│   └── src/
└── docker/              # Docker orchestration configuration
    ├── .env.example     # Docker environment variables example
    └── docker-compose.yml
```

---

## Quick Start

Copy `.env.example` or `.env.local.example` to `.env` or `.env.local` and configure credential environment variables

```bash
make setup

make install

make docker-local-up && make db-init

make dev-back

# New terminal
make dev-worker

# New terminal
make dev-front
```



## Development Guide

We provide this guide to introduce how to configure and start the i5 Agents system, including both local testing and Docker deployment methods.

<!-- ### Stage 0: Setup Environment Variables
```bash
chmod +x scripts/setup-env.sh
bash scripts/setup-env.s
``` 
-->

### Stage 1: Local Development

In local development mode, backend and frontend run locally, while database services use Docker.

#### 1. Start Database Services

```bash
cd docker

# 1. Start services
docker-compose up postgresql temporal temporal-ui -d

# 2. Wait for services to start
sleep 30

# 3. Check service status
docker-compose ps

# 4. Verify databases were created
docker exec i5-postgresql psql -U postgres -c "\l"

# 5. Verify user configuration
docker exec i5-postgresql psql -U postgres -c "\du"

# 6. Check Temporal logs
docker-compose logs temporal --tail 20

# Expected results:
# - Both services show (healthy) status
# - Databases: i5agents, temporal, temporal_visibility
# - Single user: postgres

# 7. Clean up when necessary
docker-compose down -v --remove-orphans --rmi all
```

#### 2. Configure and Start Backend

```bash
cd backend
# Edit .env file to set OPENAI_API_KEY, etc.

# Install dependencies
uv venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

# Start development server
uv run uvicorn i5_agents.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Configure and Start Frontend

```bash
cd frontend
# Edit .env.local file

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

#### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Temporal Server: localhost:7233 (gRPC endpoint)

**Note**: Temporal Web UI is not included in the basic setup. To add it, you can deploy `temporalio/ui` separately.

---

### Stage 2: Docker Deployment

In Docker mode, all services run in containers.

#### 1. Configure Environment Variables

```bash
cd docker
# Edit .env file to set all necessary environment variables
```

**Note**: docker-compose.yml automatically reads all environment variables from the `docker/.env` file.

#### 2. Build and Start All Services

```bash
cd docker
docker-compose up --build -d
```

#### 3. Check Service Status

```bash
docker-compose ps
docker-compose logs -f  # View logs
```

#### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Temporal Server: localhost:7233 (gRPC endpoint)

**Note**: Temporal Web UI is not included in the basic setup. To add it, you can deploy `temporalio/ui` separately.

#### 5. Stop Services

```bash
docker-compose down          # Stop services
docker-compose down -v       # Stop and remove data volumes (clear data)
```