"""
Relationship models for Zero Vector 4
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any

from pydantic import Field

from .base import StatusModel


class RelationshipType(str, Enum):
    """Relationship type enumeration"""
    HIERARCHICAL = "hierarchical"
    PEER = "peer"
    COLLABORATION = "collaboration"
    MENTORSHIP = "mentorship"
    DEPENDENCY = "dependency"
    CONFLICT = "conflict"
    ALLIANCE = "alliance"


class RelationshipStatus(str, Enum):
    """Relationship status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class AgentRelationship(StatusModel):
    """Model for relationships between agents"""
    
    # Relationship participants
    agent_a_id: str = Field(..., description="ID of first agent in relationship")
    agent_b_id: str = Field(..., description="ID of second agent in relationship")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    
    # Relationship properties
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Strength of relationship (0-1)")
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Trust level between agents (0-1)")
    collaboration_frequency: int = Field(default=0, description="Number of collaborations")
    
    # Relationship directionality (for hierarchical relationships)
    is_directional: bool = Field(default=False, description="Whether relationship has direction")
    dominant_agent_id: Optional[str] = Field(None, description="Dominant agent ID for directional relationships")
    
    # Relationship history
    interaction_count: int = Field(default=0, description="Total number of interactions")
    successful_collaborations: int = Field(default=0, description="Number of successful collaborations")
    failed_collaborations: int = Field(default=0, description="Number of failed collaborations")
    last_interaction: Optional[datetime] = Field(None, description="Last interaction timestamp")
    
    # Relationship metadata
    formation_context: str = Field(default="", description="Context in which relationship was formed")
    shared_experiences: List[str] = Field(default_factory=list, description="Shared experience IDs")
    relationship_tags: List[str] = Field(default_factory=list, description="Tags describing the relationship")
    
    # Dynamic properties
    compatibility_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Compatibility between agents")
    conflict_resolution_ability: float = Field(default=0.5, ge=0.0, le=1.0, description="Ability to resolve conflicts")
    
    def record_interaction(self, successful: bool = True, context: str = ""):
        """Record an interaction between the agents"""
        self.interaction_count += 1
        self.last_interaction = datetime.utcnow()
        
        if successful:
            self.successful_collaborations += 1
            # Strengthen relationship on successful interaction
            self.strength = min(1.0, self.strength + 0.01)
            self.trust_level = min(1.0, self.trust_level + 0.005)
        else:
            self.failed_collaborations += 1
            # Weaken relationship on failed interaction
            self.strength = max(0.0, self.strength - 0.02)
            self.trust_level = max(0.0, self.trust_level - 0.01)
        
        if context:
            self.set_config(f"interaction_{datetime.utcnow().isoformat()}", {
                "successful": successful,
                "context": context,
                "strength_after": self.strength,
                "trust_after": self.trust_level
            })
        
        self.update_timestamp()
    
    def add_shared_experience(self, experience_id: str):
        """Add a shared experience"""
        if experience_id not in self.shared_experiences:
            self.shared_experiences.append(experience_id)
            # Shared experiences strengthen bonds
            self.strength = min(1.0, self.strength + 0.05)
            self.update_timestamp()
    
    def update_compatibility(self, new_score: float):
        """Update compatibility score"""
        self.compatibility_score = max(0.0, min(1.0, new_score))
        self.update_timestamp()
    
    def set_hierarchical_relationship(self, dominant_agent_id: str):
        """Set as hierarchical relationship with dominant agent"""
        self.relationship_type = RelationshipType.HIERARCHICAL
        self.is_directional = True
        self.dominant_agent_id = dominant_agent_id
        self.update_timestamp()
    
    @property
    def success_rate(self) -> float:
        """Calculate collaboration success rate"""
        total = self.successful_collaborations + self.failed_collaborations
        if total == 0:
            return 1.0
        return self.successful_collaborations / total
    
    @property
    def relationship_health(self) -> float:
        """Calculate overall relationship health"""
        return (self.strength * 0.4 + 
                self.trust_level * 0.3 + 
                self.success_rate * 0.2 + 
                self.compatibility_score * 0.1)
    
    @property
    def is_healthy_relationship(self) -> bool:
        """Check if relationship is healthy"""
        return self.relationship_health > 0.6 and self.status == "active"


class TaskDependency(StatusModel):
    """Model for task dependencies"""
    
    # Dependency specification
    dependent_task_id: str = Field(..., description="ID of task that depends on another")
    dependency_task_id: str = Field(..., description="ID of task that is depended upon")
    dependency_type: str = Field(..., description="Type of dependency")
    
    # Dependency properties
    is_blocking: bool = Field(default=True, description="Whether this dependency blocks execution")
    is_critical: bool = Field(default=False, description="Whether this is a critical dependency")
    satisfaction_criteria: Dict[str, Any] = Field(default_factory=dict, description="Criteria for dependency satisfaction")
    
    # Dependency status
    is_satisfied: bool = Field(default=False, description="Whether dependency is satisfied")
    satisfaction_timestamp: Optional[datetime] = Field(None, description="When dependency was satisfied")
    
    # Dependency metadata
    creation_reason: str = Field(default="", description="Reason for creating this dependency")
    estimated_wait_time: Optional[float] = Field(None, description="Estimated wait time in seconds")
    actual_wait_time: Optional[float] = Field(None, description="Actual wait time in seconds")
    
    def satisfy_dependency(self, context: Dict[str, Any] = None):
        """Mark dependency as satisfied"""
        if not self.is_satisfied:
            self.is_satisfied = True
            self.satisfaction_timestamp = datetime.utcnow()
            
            if self.created_at and self.satisfaction_timestamp:
                self.actual_wait_time = (self.satisfaction_timestamp - self.created_at).total_seconds()
            
            if context:
                self.set_config("satisfaction_context", context)
            
            self.update_status("satisfied", "Dependency has been satisfied")
    
    def check_satisfaction_criteria(self, task_result: Dict[str, Any]) -> bool:
        """Check if satisfaction criteria are met"""
        if not self.satisfaction_criteria:
            return True
        
        for criterion, expected_value in self.satisfaction_criteria.items():
            if task_result.get(criterion) != expected_value:
                return False
        
        return True
    
    @property
    def wait_time_accuracy(self) -> Optional[float]:
        """Calculate accuracy of wait time estimation"""
        if self.estimated_wait_time and self.actual_wait_time:
            error = abs(self.estimated_wait_time - self.actual_wait_time)
            return max(0.0, 1.0 - (error / max(self.estimated_wait_time, self.actual_wait_time)))
        return None


class AgentNetwork(StatusModel):
    """Model for agent network topology"""
    
    # Network identification
    network_name: str = Field(..., description="Name of the agent network")
    conductor_agent_id: str = Field(..., description="ID of the conductor agent")
    
    # Network structure
    agent_ids: List[str] = Field(default_factory=list, description="All agent IDs in the network")
    tlp_agent_ids: List[str] = Field(default_factory=list, description="TLP agent IDs")
    relationship_ids: List[str] = Field(default_factory=list, description="Relationship IDs in the network")
    
    # Network properties
    network_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Network density (0-1)")
    average_path_length: float = Field(default=0.0, description="Average path length in network")
    clustering_coefficient: float = Field(default=0.0, ge=0.0, le=1.0, description="Clustering coefficient")
    
    # Network dynamics
    formation_strategy: str = Field(default="hierarchical", description="Network formation strategy")
    adaptation_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Rate of network adaptation")
    stability_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Network stability score")
    
    # Network metrics
    total_interactions: int = Field(default=0, description="Total interactions in network")
    successful_collaborations: int = Field(default=0, description="Successful collaborations")
    network_efficiency: float = Field(default=0.0, ge=0.0, le=1.0, description="Network efficiency")
    
    def add_agent(self, agent_id: str, is_tlp: bool = False):
        """Add an agent to the network"""
        if agent_id not in self.agent_ids:
            self.agent_ids.append(agent_id)
            if is_tlp:
                self.tlp_agent_ids.append(agent_id)
            self.update_timestamp()
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the network"""
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)
            if agent_id in self.tlp_agent_ids:
                self.tlp_agent_ids.remove(agent_id)
            self.update_timestamp()
    
    def add_relationship(self, relationship_id: str):
        """Add a relationship to the network"""
        if relationship_id not in self.relationship_ids:
            self.relationship_ids.append(relationship_id)
            self.update_timestamp()
    
    def record_interaction(self, successful: bool = True):
        """Record a network interaction"""
        self.total_interactions += 1
        if successful:
            self.successful_collaborations += 1
        
        # Update network efficiency
        self.network_efficiency = self.successful_collaborations / self.total_interactions if self.total_interactions > 0 else 0.0
        self.update_timestamp()
    
    def calculate_network_metrics(self):
        """Calculate network topology metrics"""
        num_agents = len(self.agent_ids)
        num_relationships = len(self.relationship_ids)
        
        if num_agents > 1:
            max_possible_relationships = num_agents * (num_agents - 1) / 2
            self.network_density = num_relationships / max_possible_relationships if max_possible_relationships > 0 else 0.0
        else:
            self.network_density = 0.0
        
        self.update_timestamp()
    
    @property
    def network_size(self) -> int:
        """Get network size (number of agents)"""
        return len(self.agent_ids)
    
    @property
    def tlp_agent_ratio(self) -> float:
        """Get ratio of TLP agents to total agents"""
        if len(self.agent_ids) == 0:
            return 0.0
        return len(self.tlp_agent_ids) / len(self.agent_ids)
    
    @property
    def is_well_connected(self) -> bool:
        """Check if network is well connected"""
        return self.network_density > 0.3 and self.network_efficiency > 0.7


class CollaborationPattern(StatusModel):
    """Model for tracking collaboration patterns"""
    
    # Pattern identification
    pattern_name: str = Field(..., description="Name of the collaboration pattern")
    participating_agents: List[str] = Field(..., description="Agents participating in this pattern")
    
    # Pattern characteristics
    pattern_type: str = Field(..., description="Type of collaboration pattern")
    frequency: int = Field(default=1, description="How often this pattern occurs")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate of this pattern")
    
    # Pattern dynamics
    typical_duration: float = Field(default=0.0, description="Typical duration in seconds")
    resource_requirements: Dict[str, float] = Field(default_factory=dict, description="Resource requirements")
    coordination_complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Coordination complexity")
    
    # Pattern evolution
    emergence_context: str = Field(..., description="Context in which pattern emerged")
    evolution_stages: List[Dict[str, Any]] = Field(default_factory=list, description="Pattern evolution stages")
    adaptation_triggers: List[str] = Field(default_factory=list, description="Triggers for pattern adaptation")
    
    # Pattern effectiveness
    effectiveness_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Overall effectiveness")
    efficiency_metrics: Dict[str, float] = Field(default_factory=dict, description="Efficiency metrics")
    
    def record_execution(self, duration: float, successful: bool):
        """Record pattern execution"""
        self.frequency += 1
        
        # Update typical duration (moving average)
        if self.typical_duration == 0.0:
            self.typical_duration = duration
        else:
            self.typical_duration = (self.typical_duration * 0.9) + (duration * 0.1)
        
        # Update success rate
        total_executions = self.frequency
        current_successes = self.success_rate * (total_executions - 1)
        if successful:
            current_successes += 1
        self.success_rate = current_successes / total_executions
        
        self.update_timestamp()
    
    def add_evolution_stage(self, stage_description: str, metrics: Dict[str, Any]):
        """Add a pattern evolution stage"""
        stage = {
            "timestamp": datetime.utcnow().isoformat(),
            "description": stage_description,
            "metrics": metrics
        }
        self.evolution_stages.append(stage)
        
        # Keep only last 20 evolution stages
        if len(self.evolution_stages) > 20:
            self.evolution_stages = self.evolution_stages[-20:]
        
        self.update_timestamp()
    
    @property
    def is_stable_pattern(self) -> bool:
        """Check if pattern is stable"""
        return (self.frequency >= 5 and 
                self.success_rate > 0.7 and 
                self.effectiveness_score > 0.6)
    
    @property
    def participant_count(self) -> int:
        """Get number of participating agents"""
        return len(self.participating_agents)
