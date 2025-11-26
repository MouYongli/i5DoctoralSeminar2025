#!/bin/bash

# ============================================
# i5agents Environment Setup Script
# ============================================
# This script helps you set up environment variables for the project

set -e

# Change to project root directory (one level up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "i5agents Environment Setup"
echo "=============================="
echo "Working directory: ${PROJECT_ROOT}"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to generate random secret
generate_secret() {
    openssl rand -base64 32
}

# Check if files already exist
if [ -f "docker/.env" ] || [ -f "backend/.env" ] || [ -f "backend/.env.docker" ] || [ -f "frontend/.env" ] || [ -f "frontend/.env.docker" ]; then
    echo -e "${YELLOW}Warning: Some .env files already exist.${NC}"
    read -p "Do you want to overwrite them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Step 1: Copying template files..."
echo ""

# Copy template files
cp backend/.env.example backend/.env
cp backend/.env.docker.example backend/.env.docker
cp frontend/.env.example frontend/.env
cp frontend/.env.docker.example frontend/.env.docker
cp docker/.env.example docker/.env

echo -e "${GREEN}[OK] Template files copied${NC}"
echo ""

echo "Step 2: Generating secrets..."
echo ""

# Generate secrets
POSTGRES_PASSWORD=$(generate_secret)
POSTGRES_TEMPORAL_PASSWORD=$(generate_secret)
NEXTAUTH_SECRET=$(generate_secret)

echo -e "${GREEN}[OK] Secrets generated${NC}"
echo ""

echo "Step 3: Updating configuration files..."
echo ""

# Update docker/.env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|" docker/.env
    sed -i '' "s|POSTGRES_TEMPORAL_PASSWORD=.*|POSTGRES_TEMPORAL_PASSWORD=${POSTGRES_TEMPORAL_PASSWORD}|" docker/.env
    sed -i '' "s|NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=${NEXTAUTH_SECRET}|" frontend/.env.docker
else
    # Linux
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|" docker/.env
    sed -i "s|POSTGRES_TEMPORAL_PASSWORD=.*|POSTGRES_TEMPORAL_PASSWORD=${POSTGRES_TEMPORAL_PASSWORD}|" docker/.env
    sed -i "s|NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=${NEXTAUTH_SECRET}|" frontend/.env.docker
fi

echo -e "${GREEN}[OK] Configuration files updated${NC}"
echo ""

echo "=============================="
echo -e "${GREEN}Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Add your OpenAI API key to backend/.env.docker:"
echo "   OPENAI_API_KEY=sk-your-actual-key-here"
echo ""
echo "2. (Optional) Review and customize the configuration files:"
echo "   - docker/.env"
echo "   - backend/.env"
echo "   - backend/.env.docker"
echo "   - frontend/.env"
echo "   - frontend/.env.docker"
echo ""
echo "3. Start the services:"
echo "   Local development:"
echo "     cd backend && python -m uvicorn main:app --reload"
echo "     cd frontend && npm run dev"
echo ""
echo "   Docker deployment:"
echo "     cd docker && docker-compose up --build"
echo ""
echo "For more information, see ENV_CONFIGURATION_GUIDE.md"
