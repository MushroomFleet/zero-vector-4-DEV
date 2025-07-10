# Zero Vector 4 - Database Setup Guide

## Prerequisites

Before setting up Zero Vector 4, you need to choose one of these database setup options:

## Option 1: Docker Setup (Recommended for Production)

### Requirements
- Docker Desktop installed and running
- At least 4GB RAM available for containers

### Steps
1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Ensure Docker is running (check system tray icon)

2. **Start all databases**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```

4. **Access the services**
   - PostgreSQL: `localhost:5432` (user: `zv4_user`, password: `zv4_dev_password_2024`, db: `zero_vector_4`)
   - Redis: `localhost:6379`
   - Weaviate: `http://localhost:8080`
   - Neo4j: `http://localhost:7474` (user: `neo4j`, password: `neo4j_dev_password`)

## Option 2: Manual Installation (Development)

### PostgreSQL Setup
1. **Install PostgreSQL**
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the superuser password
   - Default port: 5432

2. **Create database and user**
   ```sql
   -- Connect as postgres superuser
   psql -U postgres

   -- Run these commands:
   CREATE USER zv4_user WITH PASSWORD 'zv4_dev_password_2024';
   CREATE DATABASE zero_vector_4 OWNER zv4_user;
   GRANT ALL PRIVILEGES ON DATABASE zero_vector_4 TO zv4_user;
   
   -- Connect to the new database
   \c zero_vector_4;
   GRANT ALL ON SCHEMA public TO zv4_user;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

### Redis Setup
1. **Install Redis**
   - Option A: Use Windows Subsystem for Linux (WSL)
   - Option B: Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
   - Option C: Use Redis Cloud (free tier): https://redis.com/try-free/

### Weaviate Setup (Optional)
1. **Docker method** (if Docker is available)
   ```bash
   docker run -d --name weaviate -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:1.22.4
   ```

2. **Alternative**: Skip Weaviate for initial development (the app will work without it)

### Neo4j Setup (Optional)
1. **Install Neo4j Desktop**
   - Download from: https://neo4j.com/download/
   - Create a new database with password: `neo4j_dev_password`
   - Start the database on default port 7687

2. **Alternative**: Skip Neo4j for initial development

## Option 3: Cloud Databases (Production)

For production deployments, consider:
- **PostgreSQL**: AWS RDS, Google Cloud SQL, Azure Database
- **Redis**: Redis Cloud, AWS ElastiCache, Azure Redis Cache
- **Weaviate**: Weaviate Cloud Services
- **Neo4j**: Neo4j Aura

## Testing the Setup

Once your databases are running, test the Zero Vector 4 application:

```bash
# Activate virtual environment
zv4-env\Scripts\activate

# Install dependencies (if not done already)
pip install -r requirements.txt

# Start the application
python main.py
```

The application should start without database connection errors.

## Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running
- Check Docker Desktop settings (Resources > Advanced)
- Try: `docker system prune` to clean up

### PostgreSQL Issues
- Verify service is running: `services.msc` → PostgreSQL
- Check connection: `psql -U zv4_user -d zero_vector_4 -h localhost`
- Ensure Windows Firewall allows PostgreSQL

### Redis Issues
- For Windows: Use WSL or Redis for Windows
- Test connection: `redis-cli ping`

### Network Issues
- Check if ports are already in use: `netstat -an | findstr :5432`
- Disable antivirus temporarily if blocking connections

## Environment Variables

Make sure your `.env` file has the correct values:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=zero_vector_4
POSTGRES_USER=zv4_user
POSTGRES_PASSWORD=zv4_dev_password_2024

REDIS_HOST=localhost
REDIS_PORT=6379

WEAVIATE_URL=http://localhost:8080
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_dev_password
