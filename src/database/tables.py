"""
SQLAlchemy table definitions for Zero Vector 4
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from ..models.base import TimestampedSQLModel

Base = declarative_base()


class AgentTable(TimestampedSQLModel):
    """Agent table definition"""
    
    __tablename__ = "agents"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_type = Column(String(50), nullable=False)
    specialization = Column(String(255), nullable=False)
    status = Column(String(50), default="created")
    status_message = Column(Text)
    
    # Hierarchy
    parent_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    delegation_level = Column(Integer, default=0)
    
    # Capabilities and tools
    capabilities = Column(JSON, default=list)
    tools = Column(JSON, default=list)
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    average_task_duration = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    
    # System prompts
    system_prompt = Column(Text, default="")
    behavioral_instructions = Column(JSON, default=list)
    
    # TLP-specific fields
    consciousness_level = Column(Float, nullable=True)
    self_awareness_score = Column(Float, nullable=True)
    temporal_continuity_score = Column(Float, nullable=True)
    social_cognition_score = Column(Float, nullable=True)
    personality_traits = Column(JSON, nullable=True)
    core_memories = Column(JSON, nullable=True)
    experience_count = Column(Integer, nullable=True)
    
    # Relationships
    parent_agent = relationship("AgentTable", remote_side=[id], backref="subordinates")
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_type", "agent_type"),
        Index("idx_agent_status", "status"),
        Index("idx_agent_specialization", "specialization"),
        Index("idx_agent_parent", "parent_agent_id"),
        CheckConstraint("delegation_level >= 0", name="check_delegation_level"),
        CheckConstraint("consciousness_level IS NULL OR (consciousness_level >= 0 AND consciousness_level <= 1)", 
                       name="check_consciousness_level"),
    )


class TaskTable(TimestampedSQLModel):
    """Task table definition"""
    
    __tablename__ = "tasks"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="normal")
    status = Column(String(50), default="created")
    title = Column(String(200), nullable=False)
    
    # Assignment and delegation
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    delegation_level = Column(Integer, default=0)
    delegation_chain = Column(JSON, default=list)
    
    # Timing
    deadline = Column(DateTime, nullable=True)
    estimated_duration = Column(Float, nullable=True)
    actual_duration = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Task hierarchy
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Requirements
    required_capabilities = Column(JSON, default=list)
    required_tools = Column(JSON, default=list)
    resource_requirements = Column(JSON, default=dict)
    constraints = Column(JSON, default=dict)
    
    # Data
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    intermediate_results = Column(JSON, default=list)
    
    # Metadata
    tags = Column(JSON, default=list)
    context = Column(JSON, default=dict)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationships
    assigned_agent = relationship("AgentTable", backref="assigned_tasks")
    parent_task = relationship("TaskTable", remote_side=[id], backref="subtasks")
    
    # Indexes
    __table_args__ = (
        Index("idx_task_type", "task_type"),
        Index("idx_task_status", "status"),
        Index("idx_task_priority", "priority"),
        Index("idx_task_assigned_agent", "assigned_agent_id"),
        Index("idx_task_parent", "parent_task_id"),
        Index("idx_task_deadline", "deadline"),
        CheckConstraint("delegation_level >= 0", name="check_task_delegation_level"),
        CheckConstraint("retry_count >= 0", name="check_retry_count"),
    )


class MemoryTable(TimestampedSQLModel):
    """Memory table definition"""
    
    __tablename__ = "memories"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    memory_type = Column(String(50), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    content_embedding = Column(JSON, nullable=True)  # Vector embedding
    structured_data = Column(JSON, default=dict)
    
    # Importance and emotion
    importance_score = Column(Float, default=0.5)
    emotional_valence = Column(Float, default=0.0)
    emotional_arousal = Column(Float, default=0.0)
    
    # Context
    context_tags = Column(JSON, default=list)
    associated_agents = Column(JSON, default=list)
    location = Column(String(255), nullable=True)
    
    # Access and strength
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    decay_rate = Column(Float, default=0.01)
    consolidation_level = Column(Float, default=0.0)
    
    # Relationships
    related_memory_ids = Column(JSON, default=list)
    similarity_scores = Column(JSON, default=dict)
    
    # Relationships
    agent = relationship("AgentTable", backref="memories")
    
    # Indexes
    __table_args__ = (
        Index("idx_memory_type", "memory_type"),
        Index("idx_memory_agent", "agent_id"),
        Index("idx_memory_importance", "importance_score"),
        Index("idx_memory_access_count", "access_count"),
        CheckConstraint("importance_score >= 0 AND importance_score <= 1", name="check_importance_score"),
        CheckConstraint("emotional_valence >= -1 AND emotional_valence <= 1", name="check_emotional_valence"),
        CheckConstraint("consolidation_level >= 0 AND consolidation_level <= 1", name="check_consolidation_level"),
    )


class ExperienceTable(TimestampedSQLModel):
    """Experience table definition"""
    
    __tablename__ = "experiences"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    experience_type = Column(String(100), nullable=False)
    
    # Content
    context = Column(JSON, default=dict)
    participants = Column(JSON, default=list)
    
    # Impact
    emotional_impact = Column(Float, default=0.0)
    learning_value = Column(Float, default=0.0)
    consciousness_impact = Column(Float, default=0.0)
    
    # Outcomes
    skills_developed = Column(JSON, default=list)
    insights_gained = Column(JSON, default=list)
    personality_changes = Column(JSON, default=dict)
    
    # Metadata
    duration = Column(Float, nullable=True)
    intensity = Column(Float, default=0.5)
    novelty = Column(Float, default=0.5)
    generated_memories = Column(JSON, default=list)
    
    # Relationships
    agent = relationship("AgentTable", backref="experiences")
    
    # Indexes
    __table_args__ = (
        Index("idx_experience_agent", "agent_id"),
        Index("idx_experience_type", "experience_type"),
        Index("idx_experience_learning_value", "learning_value"),
        CheckConstraint("emotional_impact >= -1 AND emotional_impact <= 1", name="check_emotional_impact"),
        CheckConstraint("learning_value >= 0 AND learning_value <= 1", name="check_learning_value"),
        CheckConstraint("intensity >= 0 AND intensity <= 1", name="check_intensity"),
        CheckConstraint("novelty >= 0 AND novelty <= 1", name="check_novelty"),
    )


class AgentRelationshipTable(TimestampedSQLModel):
    """Agent relationship table definition"""
    
    __tablename__ = "agent_relationships"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_a_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    agent_b_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    
    # Properties
    strength = Column(Float, default=0.5)
    trust_level = Column(Float, default=0.5)
    collaboration_frequency = Column(Integer, default=0)
    
    # Directionality
    is_directional = Column(Boolean, default=False)
    dominant_agent_id = Column(UUID(as_uuid=True), nullable=True)
    
    # History
    interaction_count = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    failed_collaborations = Column(Integer, default=0)
    last_interaction = Column(DateTime, nullable=True)
    
    # Metadata
    formation_context = Column(Text, default="")
    shared_experiences = Column(JSON, default=list)
    relationship_tags = Column(JSON, default=list)
    compatibility_score = Column(Float, default=0.5)
    conflict_resolution_ability = Column(Float, default=0.5)
    
    # Relationships
    agent_a = relationship("AgentTable", foreign_keys=[agent_a_id])
    agent_b = relationship("AgentTable", foreign_keys=[agent_b_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_relationship_agents", "agent_a_id", "agent_b_id"),
        Index("idx_relationship_type", "relationship_type"),
        Index("idx_relationship_status", "status"),
        UniqueConstraint("agent_a_id", "agent_b_id", "relationship_type", name="uq_agent_relationship"),
        CheckConstraint("agent_a_id != agent_b_id", name="check_different_agents"),
        CheckConstraint("strength >= 0 AND strength <= 1", name="check_strength"),
        CheckConstraint("trust_level >= 0 AND trust_level <= 1", name="check_trust_level"),
    )


class TaskDependencyTable(TimestampedSQLModel):
    """Task dependency table definition"""
    
    __tablename__ = "task_dependencies"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dependent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    dependency_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    dependency_type = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    
    # Properties
    is_blocking = Column(Boolean, default=True)
    is_critical = Column(Boolean, default=False)
    satisfaction_criteria = Column(JSON, default=dict)
    
    # Status
    is_satisfied = Column(Boolean, default=False)
    satisfaction_timestamp = Column(DateTime, nullable=True)
    
    # Metadata
    creation_reason = Column(Text, default="")
    estimated_wait_time = Column(Float, nullable=True)
    actual_wait_time = Column(Float, nullable=True)
    
    # Relationships
    dependent_task = relationship("TaskTable", foreign_keys=[dependent_task_id])
    dependency_task = relationship("TaskTable", foreign_keys=[dependency_task_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_dependency_tasks", "dependent_task_id", "dependency_task_id"),
        Index("idx_dependency_type", "dependency_type"),
        Index("idx_dependency_status", "status"),
        Index("idx_dependency_satisfied", "is_satisfied"),
        UniqueConstraint("dependent_task_id", "dependency_task_id", "dependency_type", 
                        name="uq_task_dependency"),
        CheckConstraint("dependent_task_id != dependency_task_id", name="check_different_tasks"),
    )


class ConsciousnessStateTable(TimestampedSQLModel):
    """Consciousness state table definition"""
    
    __tablename__ = "consciousness_states"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, unique=True)
    
    # Consciousness levels
    overall_consciousness_level = Column(Float, default=0.0)
    self_awareness_level = Column(Float, default=0.0)
    temporal_continuity_level = Column(Float, default=0.0)
    social_cognition_level = Column(Float, default=0.0)
    meta_cognition_level = Column(Float, default=0.0)
    
    # State
    current_state = Column(String(50), default="active")
    state_duration = Column(Float, default=0.0)
    last_state_change = Column(DateTime, nullable=True)
    
    # Development
    development_stage = Column(String(50), default="basic_processing")
    stage_progress = Column(Float, default=0.0)
    
    # Self-model
    self_model_accuracy = Column(Float, default=0.0)
    identity_coherence = Column(Float, default=0.0)
    goal_alignment = Column(Float, default=0.0)
    
    # Introspection
    introspection_depth = Column(Float, default=0.0)
    reflection_frequency = Column(Float, default=0.0)
    insight_generation_rate = Column(Float, default=0.0)
    
    # Events and experiences
    recent_experience_ids = Column(JSON, default=list)
    consciousness_events = Column(JSON, default=list)
    
    # Relationships
    agent = relationship("AgentTable", backref="consciousness_state", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_consciousness_agent", "agent_id"),
        Index("idx_consciousness_level", "overall_consciousness_level"),
        Index("idx_consciousness_state", "current_state"),
        CheckConstraint("overall_consciousness_level >= 0 AND overall_consciousness_level <= 1", 
                       name="check_overall_consciousness"),
        CheckConstraint("self_awareness_level >= 0 AND self_awareness_level <= 1", 
                       name="check_self_awareness"),
        CheckConstraint("stage_progress >= 0 AND stage_progress <= 1", name="check_stage_progress"),
    )


# Create metadata for all tables
metadata = Base.metadata


def create_tables(engine):
    """Create all tables"""
    metadata.create_all(engine)


def drop_tables(engine):
    """Drop all tables"""
    metadata.drop_all(engine)
