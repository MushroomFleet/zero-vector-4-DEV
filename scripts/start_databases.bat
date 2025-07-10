@echo off
echo Starting Zero Vector 4 Databases...
echo.

echo Checking if Docker is running...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo Docker is available. Starting database containers...
echo.

echo Starting all database services...
docker-compose up -d

echo.
echo Waiting for databases to be ready...
timeout /t 30 /nobreak

echo.
echo Checking database health...
docker-compose ps

echo.
echo Database setup complete!
echo.
echo Services available at:
echo - PostgreSQL: localhost:5432 (user: zv4_user, db: zero_vector_4)
echo - Redis: localhost:6379
echo - Weaviate: http://localhost:8080
echo - Neo4j: http://localhost:7474 (user: neo4j)
echo.
echo You can now run: python main.py
echo.
pause
