# Docker Setup Guide

This directory contains all configuration files for Docker deployment.

## Files

- **`.env.example`** - Environment variable template  
- **`.env`** - Actual environment file (copy from `.env.example` and edit)  
- **`docker-compose.yml`** - Docker Compose definition  

## Usage

### 1. Create the env file

```bash
cp .env.example .env
```

### 2. Edit `.env`

Fill required values:

```env
# Database password (change this)
POSTGRES_PASSWORD=your-secure-password

# LLM API key
OPENAI_API_KEY=sk-xxx

# Auth secret (change this; at least 32 chars)
NEXTAUTH_SECRET=your-nextauth-secret-at-least-32-chars
```

### 3. Start services

```bash
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Stop services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Environment Variables

### PostgreSQL
- `POSTGRES_HOST`: database host (inside containers use `postgresql`)  
- `POSTGRES_PORT`: database port (default 5432)  
- `POSTGRES_DB`: app database name  
- `POSTGRES_USER`: database user  
- `POSTGRES_PASSWORD`: database password  

### Backend
- `OPENAI_API_KEY`: OpenAI API key (required)  
- `APP_ENV`: environment (`production`/`development`)  
- `DEBUG`: debug mode (`true`/`false`)  

### Frontend
- `NEXT_PUBLIC_API_URL`: backend API URL (inside Docker use `http://backend:8000`)  
- `NEXTAUTH_SECRET`: NextAuth secret (required)  

## Service Ports

After startup:

- **Frontend**: http://localhost:3000  
- **Backend API**: http://localhost:8000  
- **PostgreSQL**: localhost:5432  
- **Temporal**: localhost:7233  
- **Temporal UI**: http://localhost:8080  

## Data Persistence

Persisted volumes:

- `postgres_data`: PostgreSQL data  
- `backend_uploads`: backend uploads  

## Common Commands

```bash
# Restart a single service
docker-compose restart backend

# Tail logs for a service
docker-compose logs -f backend

# Enter a container
docker-compose exec backend sh

# Clean all containers and data
docker-compose down -v
docker system prune -a
```

## Notes

1. Never commit `.env` files to version control.  
2. In production, change all passwords and secrets.  
3. `docker-compose.yml` automatically reads `.env` in the same directory.  
4. To apply config changes, edit `.env` and restart: `docker-compose up -d`.  
