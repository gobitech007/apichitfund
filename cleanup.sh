#!/bin/bash

echo "========================================="
echo "Docker Cleanup Script"
echo "========================================="

COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. Stopping all containers...${NC}"
docker-compose -f ${COMPOSE_FILE} down --volumes

echo -e "${YELLOW}2. Removing images...${NC}"
docker-compose -f ${COMPOSE_FILE} down --rmi all

echo -e "${YELLOW}3. Removing dangling images...${NC}"
docker image prune -f

echo -e "${YELLOW}4. Removing unused volumes...${NC}"
docker volume prune -f

echo -e "${YELLOW}5. Removing unused networks...${NC}"
docker network prune -f

echo -e "${YELLOW}6. Current containers:${NC}"
docker ps -a

echo -e "${YELLOW}7. Current images:${NC}"
docker images | grep smchitfund || echo "No smchitfund images found"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Cleanup completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
