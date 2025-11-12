#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${GREEN}Starting deployment to ${ENVIRONMENT}...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your configuration before continuing.${NC}"
        exit 1
    else
        echo -e "${RED}Error: .env.example file not found.${NC}"
        exit 1
    fi
fi

# Pull latest images
echo -e "${GREEN}Pulling latest images...${NC}"
docker-compose -f ${COMPOSE_FILE} pull

# Build images
echo -e "${GREEN}Building images...${NC}"
docker-compose -f ${COMPOSE_FILE} build

# Stop existing containers
echo -e "${GREEN}Stopping existing containers...${NC}"
docker-compose -f ${COMPOSE_FILE} down

# Start containers
echo -e "${GREEN}Starting containers...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d

# Wait for services to be healthy
echo -e "${GREEN}Waiting for services to be healthy...${NC}"
sleep 10

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
docker-compose -f ${COMPOSE_FILE} exec -T backend alembic upgrade head

# Check service health
echo -e "${GREEN}Checking service health...${NC}"
services=("backend" "frontend" "postgres" "redis")
for service in "${services[@]}"; do
    if docker-compose -f ${COMPOSE_FILE} ps | grep -q "${service}.*Up"; then
        echo -e "${GREEN}✓ ${service} is running${NC}"
    else
        echo -e "${RED}✗ ${service} is not running${NC}"
    fi
done

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}Services are available at:${NC}"
echo -e "  Frontend: http://localhost:3000"
echo -e "  Backend API: http://localhost:8000"
echo -e "  API Docs: http://localhost:8000/docs"

