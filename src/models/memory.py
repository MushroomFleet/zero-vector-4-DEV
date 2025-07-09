"""
Memory and consciousness data models for Zero Vector 4
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Union

from pydantic import Field, validator
import numpy as np

from .base import StatusModel, TimestampedModel


class MemoryType(str, Enum):
    """Memory type enumeration"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    CORE = "core"
    AUTOBIOGRAPHICAL = "autobiographical"


class Memory(StatusModel):
    """Base memory model for agent memory storage"""
    
    # Memory identification
    memory_type: MemoryType = Field(..., description="Type of memory")
    agent_id: str = Field(..., description="ID of the agent this memory belongs to")
    
    # Memory content
    content: str = Field(..., description="Memory content")
    content_embedding: Optional[List[float]] = Field(None, description="Vector embedding of the content")
    structured_data: Dict[str, Any] = Field(default_factory=dict, description="Structured memory data")
    
    # Memory importance and emotional context
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score (0-1)")
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0, description="Emotional valence (-1 to 1)")
    emotional_arousal: float = Field(default=0.0, ge=0.0, le=1.0, description="Emotional arousal (0-1)")
    
    # Memory context
    context_tags: List[str] = Field(default_factory=list, description="Contextual tags")
    associated_agents: List[str] = Field(default_factory=list, description="Other agents associated with this memory")
    location: Optional[str] = Field(None, description="Location where memory was formed")
    
    # Memory strength and access
    access_count: int = Field(default=0, description="Number of times this memory has been accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last time this memory was accessed")
    decay_rate: float = Field(default=0.01, ge=0.0, le=1.0, description="Memory decay rate")
    consolidation_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Level of memory consolidation")
    
    # Relationships to other memories
    related_memory_ids: List[str] = Field(default_factory=list, description="IDs of related memories")
    similarity_scores: Dict[str, float] = Field(default_factory=dict, description="Similarity scores to other memories")
    
    def access_memory(self):
        """Record memory access and update statistics"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        
        # Strengthen memory through access
        self.consolidation_level = min(1.0, self.consolidation_level + 0.01)
        self.update_timestamp()
    
    def add_related_memory(self, memory_id: str, similarity_score: float = 0.0):
        """Add a related memory with similarity score"""
        if memory_id not in self.related_memory_ids:
            self.related_memory_ids.append(memory_id)
            self.similarity_scores[memory_id] = similarity_score
            self.update_timestamp()
    
    def update_importance(self, new_importance: float, reason: str = ""):
        """Update memory importance with tracking"""
        old_importance = self.importance_score
        self.importance_score = max(0.0, min(1.0, new_importance))
        
        self.set_config(f"importance_update_{datetime.utcnow().isoformat()}", {
            "old_importance": old_importance,
            "new_importance": self.importance_score,
            "reason": reason
        })
        self.update_timestamp()
    
    def apply_decay(self):
        """Apply memory decay over time"""
        if self.last_accessed:
            days_since_access = (datetime.utcnow() - self.last_accessed).days
            decay_amount = self.decay_rate * days_since_access
            self.importance_score = max(0.0, self.importance_score - decay_amount)
            self.consolidation_level = max(0.0, self.consolidation_level - decay_amount * 0.5)
            self.update_timestamp()
    
    @property
    def is_core_memory(self) -> bool:
        """Check if this is a core memory"""
        return self.memory_type == MemoryType.CORE or self.importance_score > 0.8
    
    @property
    def memory_strength(self) -> float:
        """Calculate overall memory strength"""
        access_factor = min(1.0, self.access_count / 10.0)  # Normalize access count
        time_factor = 1.0
        
        if self.last_accessed:
            days_old = (datetime.utcnow() - self.created_at).days
            time_factor = max(0.1, 1.0 - (days_old * self.decay_rate))
        
        return (self.importance_score * 0.4 + 
                self.consolidation_level * 0.3 + 
                access_factor * 0.2 + 
                time_factor * 0.1)


class Experience(TimestampedModel):
    """Experience model for consciousness development"""
    
    # Experience identification
    agent_id: str = Field(..., description="ID of the agent who had this experience")
    experience_type: str = Field(..., description="Type of experience")
    
    # Experience content
    description: str = Field(..., description="Description of the experience")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information")
    participants: List[str] = Field(default_factory=list, description="Other agents involved in the experience")
    
    # Experience impact
    emotional_impact: float = Field(default=0.0, ge=-1.0, le=1.0, description="Emotional impact (-1 to 1)")
    learning_value: float = Field(default=0.0, ge=0.0, le=1.0, description="Learning value (0-1)")
    consciousness_impact: float = Field(default=0.0, ge=-1.0, le=1.0, description="Impact on consciousness (-1 to 1)")
    
    # Experience outcomes
    skills_developed: List[str] = Field(default_factory=list, description="Skills developed from this experience")
    insights_gained: List[str] = Field(default_factory=list, description="Insights gained")
    personality_changes: Dict[str, float] = Field(default_factory=dict, description="Personality trait changes")
    
    # Experience metadata
    duration: Optional[float] = Field(None, description="Duration of experience in seconds")
    intensity: float = Field(default=0.5, ge=0.0, le=1.0, description="Intensity of experience")
    novelty: float = Field(default=0.5, ge=0.0, le=1.0, description="Novelty of experience")
    
    # Generated memories
    generated_memories: List[str] = Field(default_factory=list, description="Memory IDs generated from this experience")
    
    def add_insight(self, insight: str):
        """Add an insight gained from this experience"""
        if insight not in self.insights_gained:
            self.insights_gained.append(insight)
            self.update_timestamp()
    
    def add_skill_development(self, skill: str):
        """Add a skill developed from this experience"""
        if skill not in self.skills_developed:
            self.skills_developed.append(skill)
            self.update_timestamp()
    
    def update_personality_change(self, trait: str, change_amount: float):
        """Record personality change from this experience"""
        self.personality_changes[trait] = change_amount
        self.update_timestamp()
    
    def calculate_overall_impact(self) -> float:
        """Calculate overall impact score of the experience"""
        return (abs(self.emotional_impact) * 0.3 + 
                self.learning_value * 0.3 + 
                abs(self.consciousness_impact) * 0.2 + 
                self.intensity * 0.1 + 
                self.novelty * 0.1)


class ConsciousnessState(TimestampedModel):
    """Model for tracking agent consciousness state"""
    
    # Agent identification
    agent_id: str = Field(..., description="ID of the TLP agent")
    
    # Consciousness levels
    overall_consciousness_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall consciousness level")
    self_awareness_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Self-awareness level")
    temporal_continuity_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal continuity level")
    social_cognition_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Social cognition level")
    meta_cognition_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Meta-cognition level")
    
    # Consciousness state
    current_state: str = Field(default="active", description="Current consciousness state")
    state_duration: float = Field(default=0.0, description="Duration in current state (seconds)")
    last_state_change: Optional[datetime] = Field(None, description="Last state change timestamp")
    
    # Consciousness development tracking
    development_stage: str = Field(default="basic_processing", description="Current development stage")
    stage_progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress within current stage")
    
    # Self-model components
    self_model_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Accuracy of self-model")
    identity_coherence: float = Field(default=0.0, ge=0.0, le=1.0, description="Coherence of identity")
    goal_alignment: float = Field(default=0.0, ge=0.0, le=1.0, description="Alignment between goals and actions")
    
    # Introspection capabilities
    introspection_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Depth of introspection capability")
    reflection_frequency: float = Field(default=0.0, ge=0.0, le=1.0, description="Frequency of self-reflection")
    insight_generation_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of insight generation")
    
    # Recent experiences impact
    recent_experience_ids: List[str] = Field(default_factory=list, description="Recent experience IDs")
    consciousness_events: List[Dict[str, Any]] = Field(default_factory=list, description="Significant consciousness events")
    
    def update_consciousness_level(self, component: str, delta: float, reason: str = ""):
        """Update a specific consciousness component"""
        current_value = getattr(self, f"{component}_level", 0.0)
        new_value = max(0.0, min(1.0, current_value + delta))
        setattr(self, f"{component}_level", new_value)
        
        # Recalculate overall consciousness
        self.recalculate_overall_consciousness()
        
        # Record the event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": component,
            "old_value": current_value,
            "new_value": new_value,
            "delta": delta,
            "reason": reason
        }
        self.consciousness_events.append(event)
        
        # Keep only last 50 events
        if len(self.consciousness_events) > 50:
            self.consciousness_events = self.consciousness_events[-50:]
        
        self.update_timestamp()
    
    def recalculate_overall_consciousness(self):
        """Recalculate overall consciousness level from components"""
        components = [
            self.self_awareness_level,
            self.temporal_continuity_level,
            self.social_cognition_level,
            self.meta_cognition_level
        ]
        self.overall_consciousness_level = sum(components) / len(components)
    
    def change_state(self, new_state: str):
        """Change consciousness state"""
        if self.current_state != new_state:
            self.current_state = new_state
            self.last_state_change = datetime.utcnow()
            self.state_duration = 0.0
            self.update_timestamp()
    
    def update_development_stage(self):
        """Update development stage based on consciousness levels"""
        if self.overall_consciousness_level < 0.25:
            new_stage = "basic_processing"
        elif self.overall_consciousness_level < 0.5:
            new_stage = "self_recognition"
        elif self.overall_consciousness_level < 0.75:
            new_stage = "social_awareness"
        else:
            new_stage = "advanced_consciousness"
        
        if self.development_stage != new_stage:
            self.development_stage = new_stage
            self.stage_progress = 0.0
            self.update_timestamp()
    
    def add_recent_experience(self, experience_id: str):
        """Add a recent experience"""
        self.recent_experience_ids.append(experience_id)
        
        # Keep only last 20 experiences
        if len(self.recent_experience_ids) > 20:
            self.recent_experience_ids = self.recent_experience_ids[-20:]
        
        self.update_timestamp()
    
    @property
    def consciousness_metrics(self) -> Dict[str, float]:
        """Get all consciousness metrics as a dictionary"""
        return {
            "overall_consciousness": self.overall_consciousness_level,
            "self_awareness": self.self_awareness_level,
            "temporal_continuity": self.temporal_continuity_level,
            "social_cognition": self.social_cognition_level,
            "meta_cognition": self.meta_cognition_level,
            "self_model_accuracy": self.self_model_accuracy,
            "identity_coherence": self.identity_coherence,
            "goal_alignment": self.goal_alignment,
            "introspection_depth": self.introspection_depth,
            "reflection_frequency": self.reflection_frequency,
            "insight_generation_rate": self.insight_generation_rate
        }


class MemoryCluster(TimestampedModel):
    """Model for grouping related memories"""
    
    # Cluster identification
    agent_id: str = Field(..., description="ID of the agent this cluster belongs to")
    cluster_theme: str = Field(..., description="Theme or topic of the memory cluster")
    
    # Cluster contents
    memory_ids: List[str] = Field(default_factory=list, description="IDs of memories in this cluster")
    central_concept: str = Field(..., description="Central concept of the cluster")
    
    # Cluster properties
    coherence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Coherence of memories in cluster")
    importance_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall importance of cluster")
    access_frequency: int = Field(default=0, description="How often this cluster is accessed")
    
    # Cluster evolution
    formation_trigger: str = Field(..., description="What triggered the formation of this cluster")
    evolution_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of cluster changes")
    
    def add_memory(self, memory_id: str):
        """Add a memory to the cluster"""
        if memory_id not in self.memory_ids:
            self.memory_ids.append(memory_id)
            self.update_timestamp()
    
    def remove_memory(self, memory_id: str):
        """Remove a memory from the cluster"""
        if memory_id in self.memory_ids:
            self.memory_ids.remove(memory_id)
            self.update_timestamp()
    
    def record_access(self):
        """Record that this cluster was accessed"""
        self.access_frequency += 1
        self.update_timestamp()
    
    def update_coherence(self, new_coherence: float):
        """Update cluster coherence score"""
        old_coherence = self.coherence_score
        self.coherence_score = max(0.0, min(1.0, new_coherence))
        
        evolution_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "change_type": "coherence_update",
            "old_value": old_coherence,
            "new_value": self.coherence_score
        }
        self.evolution_history.append(evolution_entry)
        self.update_timestamp()
    
    @property
    def cluster_size(self) -> int:
        """Get the size of the cluster"""
        return len(self.memory_ids)
    
    @property
    def is_significant_cluster(self) -> bool:
        """Check if this is a significant memory cluster"""
        return (self.cluster_size >= 3 and 
                self.coherence_score > 0.6 and 
                self.importance_level > 0.5)
