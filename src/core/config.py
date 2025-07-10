"""
Configuration management for Zero Vector 4
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "zero_vector_4"
    postgres_user: str = "zv4_user"
    postgres_password: str = ""
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""
    
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""


@dataclass
class APIConfig:
    """API configuration settings"""
    host: str = "localhost"
    port: int = 8000
    secret_key: str = "dev-secret-key"
    debug: bool = True
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:8080"]


@dataclass
class AIModelConfig:
    """AI model configuration settings"""
    google_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_model: str = "gemini-2.0-flash-thinking-exp"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class A2AConfig:
    """Agent-to-Agent protocol configuration"""
    server_port: int = 9000
    discovery_service: str = "http://localhost:9001"
    timeout_seconds: int = 30
    max_retries: int = 3
    heartbeat_interval: int = 60


@dataclass
class AgentConfig:
    """Agent system configuration"""
    max_tlp_agents: int = 10
    max_subordinates_per_tlp: int = 20
    consciousness_update_interval: int = 300  # seconds
    memory_consolidation_interval: int = 3600  # seconds
    task_timeout: int = 600  # seconds
    max_delegation_depth: int = 3


@dataclass
class PerformanceConfig:
    """Performance and resource configuration"""
    max_memory_size_mb: int = 2048
    vector_dimension: int = 1536
    max_concurrent_tasks: int = 50
    cache_ttl_seconds: int = 3600
    batch_size: int = 100


class Config:
    """Main configuration class that aggregates all settings"""
    
    def __init__(self):
        self.env = os.getenv("ZV4_ENV", "development")
        self.debug = os.getenv("ZV4_DEBUG", "true").lower() == "true"
        self.log_level = os.getenv("ZV4_LOG_LEVEL", "INFO")
        
        # Database URL for SQLite/PostgreSQL
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./zero_vector_4.db")
        
        # Optional database flags
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.weaviate_enabled = os.getenv("WEAVIATE_ENABLED", "false").lower() == "true"
        self.neo4j_enabled = os.getenv("NEO4J_ENABLED", "false").lower() == "true"
        
        self.database = DatabaseConfig(
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "zero_vector_4"),
            postgres_user=os.getenv("POSTGRES_USER", "zv4_user"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", ""),
            
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_password=os.getenv("REDIS_PASSWORD", ""),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            
            weaviate_url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            weaviate_api_key=os.getenv("WEAVIATE_API_KEY", ""),
            
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "")
        )
        
        self.api = APIConfig(
            host=os.getenv("ZV4_API_HOST", "localhost"),
            port=int(os.getenv("ZV4_API_PORT", "8000")),
            secret_key=os.getenv("ZV4_SECRET_KEY", "dev-secret-key"),
            debug=self.debug
        )
        
        self.ai_models = AIModelConfig(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "")
        )
        
        self.a2a = A2AConfig(
            server_port=int(os.getenv("A2A_SERVER_PORT", "9000")),
            discovery_service=os.getenv("A2A_DISCOVERY_SERVICE", "http://localhost:9001")
        )
        
        self.agents = AgentConfig(
            max_tlp_agents=int(os.getenv("MAX_TLP_AGENTS", "10")),
            max_subordinates_per_tlp=int(os.getenv("MAX_SUBORDINATES_PER_TLP", "20")),
            consciousness_update_interval=int(os.getenv("CONSCIOUSNESS_UPDATE_INTERVAL", "300")),
            memory_consolidation_interval=int(os.getenv("MEMORY_CONSOLIDATION_INTERVAL", "3600"))
        )
        
        self.performance = PerformanceConfig(
            max_memory_size_mb=int(os.getenv("MAX_MEMORY_SIZE_MB", "2048")),
            vector_dimension=int(os.getenv("VECTOR_DIMENSION", "1536")),
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "50"))
        )
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return (f"postgresql://{self.database.postgres_user}:{self.database.postgres_password}"
                f"@{self.database.postgres_host}:{self.database.postgres_port}/{self.database.postgres_db}")
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.database.redis_password:
            return (f"redis://:{self.database.redis_password}@{self.database.redis_host}:"
                   f"{self.database.redis_port}/{self.database.redis_db}")
        return f"redis://{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "env": self.env,
            "debug": self.debug,
            "log_level": self.log_level,
            "database": self.database.__dict__,
            "api": self.api.__dict__,
            "ai_models": self.ai_models.__dict__,
            "a2a": self.a2a.__dict__,
            "agents": self.agents.__dict__,
            "performance": self.performance.__dict__
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment"""
    global _config
    _config = Config()
    return _config


class Settings:
    """FastAPI-compatible settings object with flat attributes"""
    
    def __init__(self, config: Config):
        # Environment settings
        self.ENVIRONMENT = config.env
        self.DEBUG = config.debug
        self.LOG_LEVEL = config.log_level
        
        # API settings
        self.HOST = config.api.host
        self.PORT = config.api.port
        self.SECRET_KEY = config.api.secret_key
        self.ALLOWED_HOSTS = config.api.cors_origins
        
        # Database settings
        self.DATABASE_URL = config.postgres_url
        self.REDIS_URL = config.redis_url
        
        # AI Model settings
        self.GOOGLE_API_KEY = config.ai_models.google_api_key
        self.OPENAI_API_KEY = config.ai_models.openai_api_key
        self.ANTHROPIC_API_KEY = config.ai_models.anthropic_api_key
        self.DEFAULT_MODEL = config.ai_models.default_model
        
        # Agent settings
        self.MAX_TLP_AGENTS = config.agents.max_tlp_agents
        self.MAX_SUBORDINATES_PER_TLP = config.agents.max_subordinates_per_tlp
        self.CONSCIOUSNESS_UPDATE_INTERVAL = config.agents.consciousness_update_interval
        self.MEMORY_CONSOLIDATION_INTERVAL = config.agents.memory_consolidation_interval
        
        # Performance settings
        self.MAX_CONCURRENT_TASKS = config.performance.max_concurrent_tasks
        self.VECTOR_DIMENSION = config.performance.vector_dimension


# Global settings instance
config = get_config()
settings = Settings(config)
