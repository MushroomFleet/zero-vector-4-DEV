"""
Base data models for Zero Vector 4
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

# SQLAlchemy Base
SQLAlchemyBase = declarative_base()


class BaseModel(PydanticBaseModel):
    """Base Pydantic model with common configuration"""
    
    model_config = ConfigDict(
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Allow extra fields for flexibility
        extra='allow',
        # Validate on assignment
        validate_assignment=True,
        # Use JSON encoders for datetime and UUID
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class TimestampedModel(BaseModel):
    """Model with automatic timestamp tracking"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()


class TimestampedSQLModel(SQLAlchemyBase):
    """SQLAlchemy base model with timestamps"""
    
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    metadata_json = Column(JSON, default=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def update_metadata(self, key: str, value: Any):
        """Update metadata JSON field"""
        if self.metadata_json is None:
            self.metadata_json = {}
        self.metadata_json[key] = value


class IdentifiableModel(TimestampedModel):
    """Model with UUID identification"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class ConfigurableModel(IdentifiableModel):
    """Model with flexible configuration storage"""
    
    config: Dict[str, Any] = Field(default_factory=dict)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.update_timestamp()
    
    def update_config(self, config_dict: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(config_dict)
        self.update_timestamp()


class VersionedModel(ConfigurableModel):
    """Model with version tracking"""
    
    version: str = Field(default="1.0.0")
    schema_version: str = Field(default="1.0.0")
    
    def increment_version(self, version_type: str = "patch"):
        """Increment version number"""
        major, minor, patch = map(int, self.version.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        self.version = f"{major}.{minor}.{patch}"
        self.update_timestamp()


class StatusModel(VersionedModel):
    """Model with status tracking"""
    
    status: str = Field(default="created")
    status_message: Optional[str] = Field(None)
    status_details: Dict[str, Any] = Field(default_factory=dict)
    
    def update_status(self, status: str, message: Optional[str] = None, **details):
        """Update status with optional message and details"""
        self.status = status
        self.status_message = message
        if details:
            self.status_details.update(details)
        self.update_timestamp()
    
    def is_active(self) -> bool:
        """Check if the model is in an active state"""
        return self.status in ["active", "running", "processing", "ready"]
    
    def is_inactive(self) -> bool:
        """Check if the model is in an inactive state"""
        return self.status in ["inactive", "stopped", "paused", "sleeping"]
    
    def is_error(self) -> bool:
        """Check if the model is in an error state"""
        return self.status in ["error", "failed", "crashed"]
