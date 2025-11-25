@echo off
setlocal enabledelayedexpansion

echo =========================================
echo Docker Cleanup Script
echo =========================================

set COMPOSE_FILE=docker-compose.yml

echo.
echo 1. Stopping all containers...
docker-compose -f %COMPOSE_FILE% down --volumes

echo.
echo 2. Removing images...
docker-compose -f %COMPOSE_FILE% down --rmi all

echo.
echo 3. Removing dangling images...
docker image prune -f

echo.
echo 4. Removing unused volumes...
docker volume prune -f

echo.
echo 5. Removing unused networks...
docker network prune -f

echo.
echo 6. Current containers:
docker ps -a

echo.
echo 7. Current images:
docker images | findstr smchitfund
if errorlevel 1 echo No smchitfund images found

echo.
echo =========================================
echo Cleanup completed!
echo =========================================
pause
