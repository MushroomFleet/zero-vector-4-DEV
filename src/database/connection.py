"""
Database connection management for Zero Vector 4
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg
import redis.asyncio as redis
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
import weaviate

from ..core.config import get_config
from ..core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Centralized database connection manager"""
    
    def __init__(self):
        self.config = get_config()
        self._postgres_engine = None
        self._async_postgres_engine = None
        self._session_factory = None
        self._async_session_factory = None
        self._redis_pool = None
        self._weaviate_client = None
        self._neo4j_driver = None
    
    async def initialize(self):
        """Initialize all database connections"""
        logger.info("Initializing database connections")
        
        # PostgreSQL connections
        await self._init_postgres()
        
        # Redis connection
        await self._init_redis()
        
        # Weaviate connection
        await self._init_weaviate()
        
        # Neo4j connection (optional)
        await self._init_neo4j()
        
        logger.info("All database connections initialized")
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connections"""
        try:
            # Sync engine for migrations and admin tasks
            self._postgres_engine = create_engine(
                self.config.postgres_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                echo=self.config.debug
            )
            
            # Async engine for application use
            async_url = self.config.postgres_url.replace("postgresql://", "postgresql+asyncpg://")
            self._async_postgres_engine = create_async_engine(
                async_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                echo=self.config.debug
            )
            
            # Session factories
            self._session_factory = sessionmaker(
                bind=self._postgres_engine,
                expire_on_commit=False
            )
            
            self._async_session_factory = async_sessionmaker(
                bind=self._async_postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("PostgreSQL connections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self._redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=20,
                retry_on_timeout=True
            )
            
            # Test connection
            redis_client = redis.Redis(connection_pool=self._redis_pool)
            await redis_client.ping()
            await redis_client.close()
            
            logger.info("Redis connection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def _init_weaviate(self):
        """Initialize Weaviate connection"""
        try:
            auth_config = None
            if self.config.database.weaviate_api_key:
                auth_config = weaviate.AuthApiKey(
                    api_key=self.config.database.weaviate_api_key
                )
            
            self._weaviate_client = weaviate.Client(
                url=self.config.database.weaviate_url,
                auth_client_secret=auth_config
            )
            
            # Test connection
            if self._weaviate_client.is_ready():
                logger.info("Weaviate connection initialized")
            else:
                raise Exception("Weaviate is not ready")
                
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            # Don't raise - Weaviate is optional for basic functionality
            self._weaviate_client = None
    
    async def _init_neo4j(self):
        """Initialize Neo4j connection (optional)"""
        try:
            from neo4j import AsyncGraphDatabase
            
            self._neo4j_driver = AsyncGraphDatabase.driver(
                self.config.database.neo4j_uri,
                auth=(self.config.database.neo4j_user, self.config.database.neo4j_password)
            )
            
            # Test connection
            async with self._neo4j_driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
            
            logger.info("Neo4j connection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            # Don't raise - Neo4j is optional
            self._neo4j_driver = None
    
    async def close(self):
        """Close all database connections"""
        logger.info("Closing database connections")
        
        if self._async_postgres_engine:
            await self._async_postgres_engine.dispose()
        
        if self._postgres_engine:
            self._postgres_engine.dispose()
        
        if self._redis_pool:
            await self._redis_pool.disconnect()
        
        if self._neo4j_driver:
            await self._neo4j_driver.close()
        
        logger.info("All database connections closed")
    
    def get_sync_session(self) -> Session:
        """Get synchronous PostgreSQL session"""
        if not self._session_factory:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    def get_async_session(self) -> AsyncSession:
        """Get asynchronous PostgreSQL session"""
        if not self._async_session_factory:
            raise RuntimeError("Database not initialized")
        return self._async_session_factory()
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis client"""
        if not self._redis_pool:
            raise RuntimeError("Redis not initialized")
        return redis.Redis(connection_pool=self._redis_pool)
    
    def get_weaviate(self) -> Optional[weaviate.Client]:
        """Get Weaviate client"""
        return self._weaviate_client
    
    def get_neo4j(self):
        """Get Neo4j driver"""
        return self._neo4j_driver
    
    async def health_check(self) -> dict:
        """Perform health check on all databases"""
        health = {
            "postgres": False,
            "redis": False,
            "weaviate": False,
            "neo4j": False
        }
        
        # PostgreSQL health check
        try:
            async with self.get_async_session() as session:
                result = await session.execute("SELECT 1")
                await result.fetchone()
            health["postgres"] = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
        
        # Redis health check
        try:
            redis_client = await self.get_redis()
            await redis_client.ping()
            await redis_client.close()
            health["redis"] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
        
        # Weaviate health check
        try:
            if self._weaviate_client and self._weaviate_client.is_ready():
                health["weaviate"] = True
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
        
        # Neo4j health check
        try:
            if self._neo4j_driver:
                async with self._neo4j_driver.session() as session:
                    result = await session.run("RETURN 1")
                    await result.single()
                health["neo4j"] = True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
        
        return health


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def init_database() -> DatabaseManager:
    """Initialize global database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    return _db_manager


async def close_database():
    """Close global database manager"""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager"""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions"""
    db_manager = get_db_manager()
    async with db_manager.get_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Context manager for Redis client"""
    db_manager = get_db_manager()
    client = await db_manager.get_redis()
    try:
        yield client
    finally:
        await client.close()


# Database lifecycle management for FastAPI
@asynccontextmanager
async def database_lifespan():
    """Database lifespan context manager for FastAPI"""
    await init_database()
    try:
        yield
    finally:
        await close_database()
