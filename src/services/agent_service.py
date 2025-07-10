"""
Agent service for Zero Vector 4
Handles agent lifecycle management and operations
"""

import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from ..models.agents import Agent, TLPAgent, BasicAgent, AgentType
from ..models.memory import Memory, MemoryType
from ..models.relationships import AgentRelationship, RelationshipType
from ..database.repositories import AgentRepository, MemoryRepository, RelationshipRepository
from ..database.connection import get_db_session
from ..core.config import get_config
from ..core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    """Service for managing agent operations"""
    
    def __init__(self):
        self.config = get_config()
    
    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        specialization: str,
        description: str = "",
        parent_agent_id: Optional[UUID] = None,
        capabilities: List[str] = None,
        personality_traits: Optional[Dict[str, float]] = None,
        core_memories: Optional[List[str]] = None
    ) -> Agent:
        """Create a new agent with specified configuration"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                memory_repo = MemoryRepository(session)
                
                # Create agent based on type
                if agent_type in [AgentType.CONDUCTOR, AgentType.DEPARTMENT_HEAD]:
                    agent = TLPAgent(
                        id=uuid4(),
                        name=name,
                        description=description,
                        agent_type=agent_type,
                        specialization=specialization,
                        parent_agent_id=parent_agent_id,
                        capabilities=capabilities or [],
                        personality_traits=personality_traits or {},
                        core_memories=core_memories or [],
                        consciousness_level=0.1,  # Start with basic consciousness
                        self_awareness_score=0.0,
                        temporal_continuity_score=0.0,
                        social_cognition_score=0.0,
                        experience_count=0
                    )
                else:
                    agent = BasicAgent(
                        id=uuid4(),
                        name=name,
                        description=description,
                        agent_type=agent_type,
                        specialization=specialization,
                        parent_agent_id=parent_agent_id,
                        capabilities=capabilities or []
                    )
                
                # Save agent to database
                created_agent = await agent_repo.create(agent)
                
                # Create core memories if provided
                if core_memories:
                    await self._create_core_memories(memory_repo, created_agent.id, core_memories)
                
                # Establish relationship with parent if specified
                if parent_agent_id:
                    await self._establish_parent_relationship(session, parent_agent_id, created_agent.id)
                
                logger.info(f"Created agent {created_agent.name} ({created_agent.id}) of type {agent_type}")
                return created_agent
                
        except Exception as e:
            logger.error(f"Error creating agent {name}: {e}")
            raise
    
    async def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get agent by ID"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.get_by_id(agent_id)
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            raise
    
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.get_by_name(name)
        except Exception as e:
            logger.error(f"Error getting agent by name {name}: {e}")
            raise
    
    async def list_agents(
        self,
        agent_type: Optional[AgentType] = None,
        status: Optional[str] = None,
        specialization: Optional[str] = None,
        manager_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Agent]:
        """List agents with optional filtering"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                
                # If no filters, use simple list_all
                if not any([agent_type, status, specialization, manager_id]):
                    return await agent_repo.list_all(limit=limit, offset=offset)
                
                # Apply filters
                agents = []
                
                if agent_type:
                    agents = await agent_repo.get_by_type(agent_type)
                else:
                    agents = await agent_repo.list_all(limit=1000, offset=0)  # Get all for filtering
                
                # Apply additional filters
                if status:
                    agents = [agent for agent in agents if agent.status.value == status]
                
                if specialization:
                    agents = [agent for agent in agents if agent.specialization == specialization]
                
                if manager_id:
                    agents = [agent for agent in agents if agent.parent_agent_id == manager_id]
                
                # Apply pagination
                start_idx = offset
                end_idx = offset + limit
                return agents[start_idx:end_idx]
                
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of specified type"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.get_by_type(agent_type)
        except Exception as e:
            logger.error(f"Error getting agents by type {agent_type}: {e}")
            raise
    
    async def get_conductor_agent(self) -> Optional[Agent]:
        """Get the conductor agent"""
        try:
            agents = await self.get_agents_by_type(AgentType.CONDUCTOR)
            return agents[0] if agents else None
        except Exception as e:
            logger.error(f"Error getting conductor agent: {e}")
            raise
    
    async def get_department_heads(self) -> List[Agent]:
        """Get all department head agents"""
        try:
            return await self.get_agents_by_type(AgentType.DEPARTMENT_HEAD)
        except Exception as e:
            logger.error(f"Error getting department heads: {e}")
            raise
    
    async def get_subordinates(self, parent_agent_id: UUID) -> List[Agent]:
        """Get subordinate agents of a parent agent"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.get_subordinates(parent_agent_id)
        except Exception as e:
            logger.error(f"Error getting subordinates for agent {parent_agent_id}: {e}")
            raise
    
    async def update_agent_status(self, agent_id: UUID, status: str, message: str = "") -> Optional[Agent]:
        """Update agent status"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                updates = {
                    "status": status,
                    "status_message": message,
                    "last_activity": datetime.utcnow()
                }
                return await agent_repo.update(agent_id, updates)
        except Exception as e:
            logger.error(f"Error updating agent status for {agent_id}: {e}")
            raise
    
    async def update_performance_metrics(self, agent_id: UUID, task_duration: float, success: bool):
        """Update agent performance metrics after task completion"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.update_performance_metrics(agent_id, task_duration, success)
        except Exception as e:
            logger.error(f"Error updating performance metrics for agent {agent_id}: {e}")
            raise
    
    async def recruit_subordinate(
        self,
        recruiting_agent_id: UUID,
        specialization: str,
        task_requirements: Dict[str, Any],
        agent_name: Optional[str] = None
    ) -> Agent:
        """Dynamically recruit a subordinate agent for specific task requirements"""
        try:
            # Get recruiting agent to determine hierarchy level
            recruiting_agent = await self.get_agent(recruiting_agent_id)
            if not recruiting_agent:
                raise ValueError(f"Recruiting agent {recruiting_agent_id} not found")
            
            # Generate subordinate specifications
            subordinate_spec = await self._analyze_subordinate_requirements(task_requirements)
            
            # Create subordinate agent
            subordinate_name = agent_name or f"specialist_{specialization}_{uuid4().hex[:8]}"
            subordinate = await self.create_agent(
                name=subordinate_name,
                agent_type=AgentType.SPECIALIST,
                specialization=specialization,
                description=f"Dynamically recruited specialist for {specialization}",
                parent_agent_id=recruiting_agent_id,
                capabilities=subordinate_spec.get("capabilities", []),
                personality_traits=subordinate_spec.get("personality_traits"),
                core_memories=subordinate_spec.get("core_memories")
            )
            
            logger.info(f"Agent {recruiting_agent.name} recruited subordinate {subordinate.name} for {specialization}")
            return subordinate
            
        except Exception as e:
            logger.error(f"Error recruiting subordinate for agent {recruiting_agent_id}: {e}")
            raise
    
    async def evolve_agent_personality(self, agent_id: UUID, personality_changes: Dict[str, float]):
        """Evolve agent personality based on experiences"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                
                agent = await agent_repo.get_by_id(agent_id)
                if not agent or not hasattr(agent, 'personality_traits'):
                    return None
                
                # Apply personality changes
                current_traits = agent.personality_traits or {}
                for trait, change in personality_changes.items():
                    current_value = current_traits.get(trait, 0.0)
                    new_value = max(-1.0, min(1.0, current_value + change))
                    current_traits[trait] = new_value
                
                # Update agent
                updates = {"personality_traits": current_traits}
                updated_agent = await agent_repo.update(agent_id, updates)
                
                logger.info(f"Evolved personality for agent {agent_id}: {personality_changes}")
                return updated_agent
                
        except Exception as e:
            logger.error(f"Error evolving personality for agent {agent_id}: {e}")
            raise
    
    async def establish_relationship(
        self,
        agent_a_id: UUID,
        agent_b_id: UUID,
        relationship_type: RelationshipType,
        context: str = ""
    ) -> AgentRelationship:
        """Establish a relationship between two agents"""
        try:
            async with get_db_session() as session:
                relationship_repo = RelationshipRepository(session)
                
                # Check if relationship already exists
                existing = await relationship_repo.get_relationship(agent_a_id, agent_b_id)
                if existing:
                    return existing
                
                # Create new relationship
                relationship = AgentRelationship(
                    id=uuid4(),
                    name=f"relationship_{agent_a_id}_{agent_b_id}",
                    agent_a_id=agent_a_id,
                    agent_b_id=agent_b_id,
                    relationship_type=relationship_type,
                    formation_context=context
                )
                
                # Set hierarchical properties if needed
                if relationship_type == RelationshipType.HIERARCHICAL:
                    relationship.is_directional = True
                    relationship.dominant_agent_id = agent_a_id  # First agent is dominant
                
                created_relationship = await relationship_repo.create(relationship)
                logger.info(f"Established {relationship_type} relationship between {agent_a_id} and {agent_b_id}")
                return created_relationship
                
        except Exception as e:
            logger.error(f"Error establishing relationship between {agent_a_id} and {agent_b_id}: {e}")
            raise
    
    async def get_agent_relationships(self, agent_id: UUID) -> List[AgentRelationship]:
        """Get all relationships for an agent"""
        try:
            async with get_db_session() as session:
                relationship_repo = RelationshipRepository(session)
                return await relationship_repo.get_agent_relationships(agent_id)
        except Exception as e:
            logger.error(f"Error getting relationships for agent {agent_id}: {e}")
            raise
    
    async def find_agents_by_capability(self, capability: str) -> List[Agent]:
        """Find agents with specific capability"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                return await agent_repo.get_by_capability(capability)
        except Exception as e:
            logger.error(f"Error finding agents by capability {capability}: {e}")
            raise
    
    async def get_agent_hierarchy(self, root_agent_id: UUID) -> Dict[str, Any]:
        """Get hierarchical structure starting from root agent"""
        try:
            hierarchy = {}
            
            async def build_hierarchy(agent_id: UUID, level: int = 0):
                agent = await self.get_agent(agent_id)
                if not agent:
                    return None
                
                subordinates = await self.get_subordinates(agent_id)
                agent_info = {
                    "agent": agent,
                    "level": level,
                    "subordinates": []
                }
                
                for subordinate in subordinates:
                    sub_hierarchy = await build_hierarchy(subordinate.id, level + 1)
                    if sub_hierarchy:
                        agent_info["subordinates"].append(sub_hierarchy)
                
                return agent_info
            
            hierarchy = await build_hierarchy(root_agent_id)
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error building hierarchy for agent {root_agent_id}: {e}")
            raise
    
    async def deactivate_agent(self, agent_id: UUID, reason: str = "") -> bool:
        """Deactivate an agent and handle cleanup"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                
                # Update agent status
                await agent_repo.update(agent_id, {
                    "status": "deactivated",
                    "status_message": f"Deactivated: {reason}",
                    "last_activity": datetime.utcnow()
                })
                
                # TODO: Handle task reassignment, relationship cleanup, etc.
                
                logger.info(f"Deactivated agent {agent_id}: {reason}")
                return True
                
        except Exception as e:
            logger.error(f"Error deactivating agent {agent_id}: {e}")
            raise
    
    async def _create_core_memories(self, memory_repo: MemoryRepository, agent_id: UUID, core_memories: List[str]):
        """Create core memories for an agent"""
        for memory_content in core_memories:
            memory = Memory(
                id=uuid4(),
                name=f"core_memory_{uuid4().hex[:8]}",
                memory_type=MemoryType.CORE,
                agent_id=agent_id,
                content=memory_content,
                importance_score=1.0,  # Core memories have maximum importance
                consolidation_level=1.0  # Fully consolidated
            )
            await memory_repo.create(memory)
    
    async def _establish_parent_relationship(self, session, parent_id: UUID, child_id: UUID):
        """Establish hierarchical relationship with parent"""
        relationship_repo = RelationshipRepository(session)
        
        relationship = AgentRelationship(
            id=uuid4(),
            name=f"hierarchy_{parent_id}_{child_id}",
            agent_a_id=parent_id,
            agent_b_id=child_id,
            relationship_type=RelationshipType.HIERARCHICAL,
            is_directional=True,
            dominant_agent_id=parent_id,
            formation_context="Parent-child hierarchy established at creation"
        )
        
        await relationship_repo.create(relationship)
    
    async def _analyze_subordinate_requirements(self, task_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task requirements to determine subordinate specifications"""
        # This would typically involve more sophisticated analysis
        # For now, provide basic specifications based on requirements
        
        capabilities = []
        personality_traits = {}
        core_memories = []
        
        # Extract capabilities from requirements
        if "required_capabilities" in task_requirements:
            capabilities = task_requirements["required_capabilities"]
        
        # Generate personality traits optimized for the task
        if "complexity" in task_requirements:
            complexity = task_requirements["complexity"]
            if complexity == "high":
                personality_traits["analytical_thinking"] = 0.8
                personality_traits["attention_to_detail"] = 0.9
            elif complexity == "creative":
                personality_traits["creativity"] = 0.9
                personality_traits["innovation"] = 0.8
        
        # Create relevant core memories
        if "domain" in task_requirements:
            domain = task_requirements["domain"]
            core_memories.append(f"I am specialized in {domain} and committed to excellence in this field.")
            core_memories.append(f"My purpose is to contribute effectively to {domain}-related tasks.")
        
        return {
            "capabilities": capabilities,
            "personality_traits": personality_traits,
            "core_memories": core_memories
        }
