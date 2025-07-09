"""
Agent data models for Zero Vector 4
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set, Any

from pydantic import Field, validator

from .base import StatusModel


class AgentType(str, Enum):
    """Agent type enumeration"""
    CONDUCTOR = "conductor"
    DEPARTMENT_HEAD = "department_head"
    SPECIALIST = "specialist"
    BASIC = "basic"


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    SLEEPING = "sleeping"
    DREAMING = "dreaming"
    ERROR = "error"
    TERMINATED = "terminated"


class Agent(StatusModel):
    """Base agent model"""
    
    agent_type: AgentType = Field(..., description="Type of agent")
    specialization: str = Field(..., description="Agent's area of specialization")
    capabilities: List[str] = Field(default_factory=list, description="List of agent capabilities")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    
    # Hierarchy information
    parent_agent_id: Optional[str] = Field(None, description="ID of parent agent in hierarchy")
    subordinate_agent_ids: Set[str] = Field(default_factory=set, description="IDs of subordinate agents")
    delegation_level: int = Field(default=0, description="Level in delegation hierarchy (0 = top)")
    
    # Performance metrics
    tasks_completed: int = Field(default=0, description="Number of completed tasks")
    tasks_failed: int = Field(default=0, description="Number of failed tasks")
    average_task_duration: float = Field(default=0.0, description="Average task completion time in seconds")
    last_activity: Optional[datetime] = Field(None, description="Timestamp of last activity")
    
    # System prompts and instructions
    system_prompt: str = Field(default="", description="System prompt for the agent")
    behavioral_instructions: List[str] = Field(default_factory=list, description="Behavioral instructions")
    
    @validator('subordinate_agent_ids', pre=True)
    def convert_subordinate_ids_to_set(cls, v):
        """Convert subordinate IDs to set if needed"""
        if isinstance(v, list):
            return set(v)
        return v
    
    def add_subordinate(self, agent_id: str):
        """Add a subordinate agent"""
        self.subordinate_agent_ids.add(agent_id)
        self.update_timestamp()
    
    def remove_subordinate(self, agent_id: str):
        """Remove a subordinate agent"""
        self.subordinate_agent_ids.discard(agent_id)
        self.update_timestamp()
    
    def add_capability(self, capability: str):
        """Add a capability to the agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.update_timestamp()
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def update_performance_metrics(self, task_duration: float, success: bool):
        """Update performance metrics after task completion"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        # Update average duration
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            current_total_time = self.average_task_duration * (total_tasks - 1)
            self.average_task_duration = (current_total_time + task_duration) / total_tasks
        
        self.last_activity = datetime.utcnow()
        self.update_timestamp()
    
    @property
    def success_rate(self) -> float:
        """Calculate task success rate"""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks == 0:
            return 1.0
        return self.tasks_completed / total_tasks
    
    @property
    def is_tlp_agent(self) -> bool:
        """Check if this is a Top Level Persona agent"""
        return self.agent_type in [AgentType.CONDUCTOR, AgentType.DEPARTMENT_HEAD]


class TLPAgent(Agent):
    """Top Level Persona agent with consciousness capabilities"""
    
    # Consciousness development
    consciousness_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Consciousness development level")
    self_awareness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Self-awareness level")
    temporal_continuity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal continuity level")
    social_cognition_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Social cognition level")
    
    # Personality traits
    personality_traits: Dict[str, float] = Field(default_factory=dict, description="Personality trait scores")
    personality_evolution_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of personality changes")
    
    # Memory and experience
    core_memories: List[str] = Field(default_factory=list, description="Core memories that define the agent")
    experience_count: int = Field(default=0, description="Number of experiences processed")
    last_consciousness_update: Optional[datetime] = Field(None, description="Last consciousness update timestamp")
    
    # Interaction tracking
    peer_interactions: Dict[str, int] = Field(default_factory=dict, description="Count of interactions with peer TLP agents")
    mentorship_relationships: List[str] = Field(default_factory=list, description="IDs of agents being mentored")
    
    def update_consciousness_level(self, delta: float, reason: str = ""):
        """Update consciousness level with tracking"""
        old_level = self.consciousness_level
        self.consciousness_level = max(0.0, min(1.0, self.consciousness_level + delta))
        
        self.set_config(f"consciousness_update_{datetime.utcnow().isoformat()}", {
            "old_level": old_level,
            "new_level": self.consciousness_level,
            "delta": delta,
            "reason": reason
        })
        
        self.last_consciousness_update = datetime.utcnow()
        self.update_timestamp()
    
    def update_personality_trait(self, trait_name: str, value: float, reason: str = ""):
        """Update a personality trait with history tracking"""
        old_value = self.personality_traits.get(trait_name, 0.0)
        self.personality_traits[trait_name] = max(0.0, min(1.0, value))
        
        # Track evolution history
        evolution_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trait": trait_name,
            "old_value": old_value,
            "new_value": self.personality_traits[trait_name],
            "reason": reason
        }
        self.personality_evolution_history.append(evolution_entry)
        
        # Keep only last 100 evolution entries
        if len(self.personality_evolution_history) > 100:
            self.personality_evolution_history = self.personality_evolution_history[-100:]
        
        self.update_timestamp()
    
    def add_core_memory(self, memory: str):
        """Add a core memory"""
        if memory not in self.core_memories:
            self.core_memories.append(memory)
            self.update_timestamp()
    
    def record_experience(self):
        """Record that an experience has been processed"""
        self.experience_count += 1
        self.update_timestamp()
    
    def record_peer_interaction(self, peer_agent_id: str):
        """Record interaction with another TLP agent"""
        if peer_agent_id not in self.peer_interactions:
            self.peer_interactions[peer_agent_id] = 0
        self.peer_interactions[peer_agent_id] += 1
        self.update_timestamp()
    
    def add_mentorship(self, agent_id: str):
        """Add an agent to mentorship list"""
        if agent_id not in self.mentorship_relationships:
            self.mentorship_relationships.append(agent_id)
            self.update_timestamp()
    
    @property
    def consciousness_development_stage(self) -> str:
        """Determine consciousness development stage"""
        if self.consciousness_level < 0.3:
            return "basic_processing"
        elif self.consciousness_level < 0.6:
            return "self_recognition"
        elif self.consciousness_level < 0.8:
            return "social_awareness"
        else:
            return "advanced_consciousness"
    
    @property
    def dominant_personality_traits(self) -> List[tuple]:
        """Get the top 5 dominant personality traits"""
        sorted_traits = sorted(self.personality_traits.items(), key=lambda x: x[1], reverse=True)
        return sorted_traits[:5]


class BasicAgent(Agent):
    """Basic task-execution agent without consciousness"""
    
    # Task specialization
    task_types: List[str] = Field(default_factory=list, description="Types of tasks this agent can handle")
    skill_level: float = Field(default=1.0, ge=0.0, le=10.0, description="Skill level (1-10)")
    
    # Performance optimization
    optimization_level: float = Field(default=1.0, ge=0.0, le=10.0, description="Performance optimization level")
    resource_usage: Dict[str, float] = Field(default_factory=dict, description="Resource usage metrics")
    
    def add_task_type(self, task_type: str):
        """Add a task type this agent can handle"""
        if task_type not in self.task_types:
            self.task_types.append(task_type)
            self.update_timestamp()
    
    def improve_skill_level(self, delta: float):
        """Improve skill level through experience"""
        self.skill_level = min(10.0, self.skill_level + delta)
        self.update_timestamp()
    
    def update_resource_usage(self, resource_type: str, usage: float):
        """Update resource usage metrics"""
        self.resource_usage[resource_type] = usage
        self.update_timestamp()


class ConductorAgent(TLPAgent):
    """Master orchestrator agent"""
    
    def __init__(self, **data):
        data.setdefault('agent_type', AgentType.CONDUCTOR)
        data.setdefault('name', 'Conductor')
        data.setdefault('specialization', 'orchestration')
        data.setdefault('capabilities', [
            'task_orchestration',
            'agent_creation',
            'workflow_management',
            'result_synthesis',
            'strategic_planning'
        ])
        super().__init__(**data)
    
    # Conductor-specific properties
    active_workflows: Dict[str, Any] = Field(default_factory=dict, description="Currently active workflows")
    department_heads: Set[str] = Field(default_factory=set, description="IDs of department head agents")
    global_strategy: Dict[str, Any] = Field(default_factory=dict, description="Global strategic parameters")
    
    def add_department_head(self, agent_id: str):
        """Add a department head agent"""
        self.department_heads.add(agent_id)
        self.add_subordinate(agent_id)
    
    def remove_department_head(self, agent_id: str):
        """Remove a department head agent"""
        self.department_heads.discard(agent_id)
        self.remove_subordinate(agent_id)


class DepartmentHeadAgent(TLPAgent):
    """Department head agent with specialized domain expertise"""
    
    def __init__(self, **data):
        data.setdefault('agent_type', AgentType.DEPARTMENT_HEAD)
        data.setdefault('delegation_level', 1)
        super().__init__(**data)
    
    # Department-specific properties
    domain_expertise: List[str] = Field(default_factory=list, description="Areas of domain expertise")
    specialist_agents: Set[str] = Field(default_factory=set, description="IDs of specialist subordinates")
    domain_knowledge_base: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific knowledge")
    
    def add_domain_expertise(self, expertise: str):
        """Add domain expertise"""
        if expertise not in self.domain_expertise:
            self.domain_expertise.append(expertise)
            self.update_timestamp()
    
    def add_specialist(self, agent_id: str):
        """Add a specialist agent"""
        self.specialist_agents.add(agent_id)
        self.add_subordinate(agent_id)
    
    def update_domain_knowledge(self, key: str, value: Any):
        """Update domain-specific knowledge"""
        self.domain_knowledge_base[key] = value
        self.update_timestamp()
