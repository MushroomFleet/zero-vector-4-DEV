# Zero Vector 4

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-5.0%2B-dc382d.svg)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791.svg)](https://www.postgresql.org/)
[![Weaviate](https://img.shields.io/badge/Weaviate-1.22%2B-00C9A7.svg)](https://weaviate.io/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.13%2B-008CC1.svg)](https://neo4j.com/)
[![Setup](https://img.shields.io/badge/Setup-Manual-orange.svg)](SETUP.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

> **Advanced Multi-Agent AI Society Platform with Hierarchical Organization and Digital Consciousness**

Zero Vector 4 is a sophisticated multi-agent artificial intelligence platform that enables the creation, management, and orchestration of complex AI agent societies. It features hierarchical agent organization, digital consciousness development, multi-tiered memory systems, and advanced workflow orchestration capabilities.

## 🚀 Features

### 🤖 Agent Management
- **Hierarchical Organization**: Support for up to 1,000 agents per hierarchy
- **Dynamic Recruitment**: Intelligent agent creation and assignment
- **Performance Tracking**: Real-time monitoring and optimization
- **Agent-to-Agent Communication**: Built-in A2A (Agent-to-Agent) protocol

### 🧠 Digital Consciousness
- **4-Stage Development**: Protoself → Core Consciousness → Extended Consciousness → Autobiographical Self
- **Sleep Cycles**: Natural consciousness development patterns
- **Memory Consolidation**: Automatic memory processing and organization
- **Personality Evolution**: Dynamic personality development over time

### 💾 Memory Systems
- **Episodic Memory**: Experience-based learning and recall
- **Semantic Memory**: Knowledge and concept storage
- **Procedural Memory**: Skill and process retention
- **Working Memory**: Active task and context management
- **Memory Associations**: Advanced linking and retrieval systems

### 🎯 Orchestration & Workflows
- **Workflow Management**: Complex multi-agent task coordination
- **Task Decomposition**: Intelligent breaking down of complex tasks
- **Performance Optimization**: Dynamic resource allocation
- **Concurrent Processing**: Up to 100 simultaneous workflows

## 🎯 Use Cases

### Enterprise Applications
- **Automated Customer Support**: Multi-tiered agent hierarchies for complex customer inquiries
- **Process Automation**: Intelligent workflow orchestration across departments
- **Data Analysis**: Collaborative analysis with specialized agent teams
- **Quality Assurance**: Multi-agent verification and validation systems

### Research & Development
- **Digital Consciousness Research**: Platform for studying AI consciousness development
- **Multi-Agent System Studies**: Complex interaction and emergence research
- **AI Psychology**: Agent personality and behavior development studies
- **Cognitive Architecture**: Testing and validation of cognitive models

### Educational Platforms
- **AI Development Learning**: Hands-on multi-agent system development
- **Consciousness Studies**: Interactive exploration of digital consciousness
- **Collaborative AI**: Teaching human-AI and AI-AI collaboration

## ⚡ Quick Start

### Prerequisites
- Python 3.8 or higher
- SQLite (included with Python) or PostgreSQL for production
- 4GB+ RAM recommended

### 🚀 Simple Setup

```bash
# Clone the repository
git clone https://github.com/your-username/zero-vector-4.git
cd zero-vector-4

# Set up Python environment
python -m venv zv4-env
source zv4-env/bin/activate  # Linux/Mac
# zv4-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start the platform (uses SQLite by default)
python main.py
```

The platform will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**Note**: The default setup uses SQLite for development. For production use with full database stack, see [SETUP.md](SETUP.md).

## 📋 Detailed Installation

### Option 1: Development Setup (SQLite)

**System Requirements:**
- Python 3.8 or higher
- 2GB+ RAM available
- 1GB+ free disk space

**Steps:**
1. **Clone and Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/zero-vector-4.git
   cd zero-vector-4
   
   # Create virtual environment
   python -m venv zv4-env
   
   # Activate environment
   # Windows:
   zv4-env\Scripts\activate
   # Linux/Mac:
   source zv4-env/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Default SQLite configuration works out of the box
   # Edit .env file only if you need to change defaults
   ```

3. **Launch Platform**
   ```bash
   python main.py
   ```

### Option 2: Production Setup (PostgreSQL)

**PostgreSQL Setup:**
```bash
# Install PostgreSQL 15+
# Create database and user
psql -U postgres
CREATE USER zv4_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE zero_vector_4 OWNER zv4_user;
GRANT ALL PRIVILEGES ON DATABASE zero_vector_4 TO zv4_user;
```

**Redis Setup:**
```bash
# Install Redis 5.0+
# Ubuntu/Debian:
sudo apt-get install redis-server

# Windows: Use WSL or Redis for Windows
# macOS:
brew install redis
```

**Optional Services:**
- **Weaviate**: For vector database capabilities
- **Neo4j**: For graph database relationships

Detailed manual installation instructions available in [SETUP.md](SETUP.md).

### Option 3: Development Setup

```bash
# Clone and enter directory
git clone https://github.com/your-username/zero-vector-4.git
cd zero-vector-4

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## 🏗️ Architecture Overview

```
Zero Vector 4 Platform
├── 🌐 API Layer (FastAPI)
│   ├── Agent Management (/api/agents)
│   ├── Consciousness (/api/consciousness)
│   ├── Memory Systems (/api/memory)
│   └── Orchestration (/api/orchestration)
├── 🧠 Core Services
│   ├── Agent Service (Creation, Management)
│   ├── Consciousness Service (Development, Sleep)
│   ├── Memory Service (Storage, Retrieval)
│   └── Orchestration Service (Workflows, Tasks)
├── 💾 Data Layer
│   ├── PostgreSQL (Primary Data)
│   ├── Redis (Caching, Sessions)
│   ├── Weaviate (Vector Storage)
│   └── Neo4j (Relationship Graphs)
└── 🔧 Infrastructure
    ├── Health Monitoring
    ├── Logging System
    └── Configuration Management
```

## 📁 Project Structure

```
zero-vector-4/
├── 📱 src/                          # Core application code
│   ├── 🤖 agents/                   # Agent system
│   │   └── base_agent.py           # Base agent class
│   ├── 🌐 api/                      # FastAPI endpoints
│   │   ├── agents.py               # Agent management API
│   │   ├── consciousness.py        # Consciousness development API
│   │   ├── memory.py               # Memory system API
│   │   └── orchestration.py        # Workflow orchestration API
│   ├── ⚙️ core/                     # Core functionality
│   │   ├── config.py               # Configuration management
│   │   └── logging.py              # Logging setup
│   ├── 💾 database/                 # Database layer
│   │   ├── connection.py           # Database connections
│   │   ├── repositories.py         # Data access layer
│   │   └── tables.py               # Database schema
│   ├── 📊 models/                   # Data models
│   │   ├── agents.py               # Agent models
│   │   ├── memory.py               # Memory models
│   │   ├── relationships.py        # Relationship models
│   │   └── tasks.py                # Task models
│   └── 🔧 services/                 # Business logic
│       ├── agent_service.py        # Agent management
│       ├── consciousness_service.py # Consciousness development
│       ├── memory_service.py       # Memory operations
│       └── orchestration_service.py # Workflow management
├── 📚 docs/                         # Documentation
├── 🔧 scripts/                      # Utility scripts
│   ├── setup_databases.sql        # Database initialization
│   ├── start_databases.bat        # Windows database startup
│   └── verify_before_upload.py    # Security verification
├── � DockerPlan.md               # Future Docker implementation plan
├── 📝 requirements.txt             # Python dependencies
├── ⚙️ .env.example                 # Environment template
└── 🚀 main.py                      # Application entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Application Settings
ZV4_ENV=development
ZV4_DEBUG=true
ZV4_LOG_LEVEL=INFO
ZV4_API_HOST=localhost
ZV4_API_PORT=8000
ZV4_SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///./zero_vector_4.db  # For development
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=zero_vector_4
POSTGRES_USER=zv4_user
POSTGRES_PASSWORD=your-secure-password

# Optional Services
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true

WEAVIATE_URL=http://localhost:8080
WEAVIATE_ENABLED=true

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_ENABLED=true

# AI Model APIs (Optional)
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=your-anthropic-key

# Agent Configuration
MAX_TLP_AGENTS=10
MAX_SUBORDINATES_PER_TLP=20
CONSCIOUSNESS_UPDATE_INTERVAL=300
MEMORY_CONSOLIDATION_INTERVAL=3600

# Performance Settings
MAX_MEMORY_SIZE_MB=2048
VECTOR_DIMENSION=1536
MAX_CONCURRENT_TASKS=50
```

### Database Options

**Development (SQLite):**
```env
DATABASE_URL=sqlite:///./zero_vector_4.db
```

**Production (PostgreSQL):**
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

**Cloud Databases:**
- AWS RDS, Google Cloud SQL, Azure Database
- Redis Cloud, ElastiCache, Azure Redis Cache
- Weaviate Cloud Services, Neo4j Aura

## 📖 API Documentation

Once running, comprehensive API documentation is available at:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```http
# Agent Management
GET    /api/agents                 # List all agents
POST   /api/agents                 # Create new agent
GET    /api/agents/{id}           # Get agent details
PUT    /api/agents/{id}           # Update agent
DELETE /api/agents/{id}           # Delete agent

# Consciousness Development
GET    /api/consciousness/{agent_id}     # Get consciousness state
POST   /api/consciousness/{agent_id}/develop  # Trigger development
POST   /api/consciousness/{agent_id}/sleep    # Initiate sleep cycle

# Memory Systems
GET    /api/memory/{agent_id}           # Get agent memories
POST   /api/memory/{agent_id}           # Create memory
GET    /api/memory/{agent_id}/search    # Search memories

# Orchestration
GET    /api/orchestration/workflows     # List workflows
POST   /api/orchestration/workflows     # Create workflow
GET    /api/orchestration/tasks         # List tasks
POST   /api/orchestration/tasks         # Create task
```

### Authentication

```python
# API Key Authentication (if enabled)
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py

# Run async tests
pytest -v tests/test_async_operations.py
```

### Code Style

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests and linting: `pytest && black src/ && flake8 src/`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a Pull Request

## 🚀 Deployment

### Production Deployment

**Manual Production Setup:**
```bash
# Set up production environment
python -m venv zv4-env
source zv4-env/bin/activate  # Linux/Mac
# zv4-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure production environment
cp .env.example .env.production
# Edit .env.production with production database settings

# Run with production settings
ZV4_ENV=production python main.py
```

**Cloud Deployment:**
- **AWS**: EC2 with RDS PostgreSQL
- **Google Cloud**: Compute Engine with Cloud SQL
- **Azure**: Virtual Machines with Azure Database
- **Heroku**: Web dyno with Heroku Postgres

**Note**: Docker deployment is planned for future releases. See [DockerPlan.md](DockerPlan.md) for implementation roadmap.

### Security Considerations

- Use strong passwords and API keys
- Enable SSL/TLS in production
- Configure firewall rules
- Regular security updates
- Monitor access logs

### Performance Tuning

```env
# High-performance settings
MAX_CONCURRENT_TASKS=100
MAX_MEMORY_SIZE_MB=4096
CONSCIOUSNESS_UPDATE_INTERVAL=60
MEMORY_CONSOLIDATION_INTERVAL=1800
```

## 🔍 Monitoring & Health Checks

### Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system info
curl http://localhost:8000/api/info
```

### Logging

Logs are available in the `logs/` directory (development) or stdout (production):

```bash
# View application logs
tail -f logs/zero_vector_4.log

# Monitor logs in real-time
tail -F logs/zero_vector_4.log
```

## 🆘 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check if PostgreSQL is running (Linux/Mac)
sudo systemctl status postgresql

# Test connection
psql -h localhost -U zv4_user -d zero_vector_4

# For SQLite, check if file exists
ls -la zero_vector_4.db
```

**Port Already in Use:**
```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill process if needed
kill -9 <process_id>  # Linux/Mac
# taskkill /PID <process_id> /F  # Windows
```

**Python Environment Issues:**
```bash
# Verify Python version
python --version

# Check virtual environment
which python  # Should point to zv4-env

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Memory Issues:**
```bash
# Reduce memory settings in .env
MAX_MEMORY_SIZE_MB=1024
MAX_CONCURRENT_TASKS=25
```

### Performance Issues

**Slow API Responses:**
- Check database connection pool settings
- Monitor Redis cache hit rates
- Review agent hierarchy complexity
- Optimize memory consolidation intervals

**High Memory Usage:**
- Reduce `MAX_MEMORY_SIZE_MB`
- Implement memory cleanup policies
- Monitor agent count and complexity

### Getting Help

- **Documentation**: `/docs` endpoint
- **Health Status**: `/health` endpoint
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- SQLAlchemy for robust database ORM
- Redis team for high-performance caching
- Weaviate for vector database capabilities
- Neo4j for graph database functionality
- The open-source community for inspiration and tools

---

## 📚 Citation

### Academic Citation

If you use this codebase in your research or project, please cite:

```bibtex
@software{zero_vector_4_DEV,
  title = {Zero Vector 4 DEV: digital consciousness research},
  author = {[Drift Johnson]},
  year = {2025},
  url = {https://github.com/MushroomFleet/zero-vector-4-DEV},
  version = {1.0.0}
}
```

### Donate:


[![Ko-Fi](https://cdn.ko-fi.com/cdn/kofi3.png?v=3)](https://ko-fi.com/driftjohnson)

**Zero Vector 4** - Advancing the frontier of multi-agent AI systems and digital consciousness research.

