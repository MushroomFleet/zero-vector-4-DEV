"""
Repository pattern implementations for Zero Vector 4
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ..models.agents import Agent, TLPAgent, BasicAgent, AgentType
from ..models.tasks import Task, TaskStatus, TaskResult
from ..models.memory import Memory, Experience, ConsciousnessState, MemoryType
from ..models.relationships import AgentRelationship, TaskDependency
from .tables import (
    AgentTable, TaskTable, MemoryTable, ExperienceTable,
    AgentRelationshipTable, TaskDependencyTable, ConsciousnessStateTable
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base repository with common operations"""
    
    def __init__(self, session: AsyncSession, table_class, model_class):
        self.session = session
        self.table_class = table_class
        self.model_class = model_class
    
    async def create(self, model: Any) -> Any:
        """Create a new record"""
        try:
            data = model.dict()
            db_obj = self.table_class(**data)
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return self._to_model(db_obj)
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    async def get_by_id(self, id: UUID) -> Optional[Any]:
        """Get record by ID"""
        try:
            result = await self.session.execute(
                select(self.table_class).where(self.table_class.id == id)
            )
            db_obj = result.scalar_one_or_none()
            return self._to_model(db_obj) if db_obj else None
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {e}")
            raise
    
    async def update(self, id: UUID, updates: Dict[str, Any]) -> Optional[Any]:
        """Update record by ID"""
        try:
            await self.session.execute(
                update(self.table_class)
                .where(self.table_class.id == id)
                .values(**updates)
            )
            return await self.get_by_id(id)
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__} {id}: {e}")
            raise
    
    async def delete(self, id: UUID) -> bool:
        """Delete record by ID"""
        try:
            result = await self.session.execute(
                delete(self.table_class).where(self.table_class.id == id)
            )
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__} {id}: {e}")
            raise
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        """List all records with pagination"""
        try:
            result = await self.session.execute(
                select(self.table_class)
                .limit(limit)
                .offset(offset)
                .order_by(self.table_class.created_at.desc())
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error listing {self.model_class.__name__}: {e}")
            raise
    
    def _to_model(self, db_obj) -> Any:
        """Convert database object to Pydantic model"""
        if db_obj is None:
            return None
        return self.model_class.parse_obj(db_obj.to_dict())


class AgentRepository(BaseRepository):
    """Repository for agent operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AgentTable, Agent)
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        try:
            result = await self.session.execute(
                select(AgentTable).where(AgentTable.name == name)
            )
            db_obj = result.scalar_one_or_none()
            return self._to_model(db_obj) if db_obj else None
        except Exception as e:
            logger.error(f"Error getting agent by name {name}: {e}")
            raise
    
    async def get_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get agents by type"""
        try:
            result = await self.session.execute(
                select(AgentTable).where(AgentTable.agent_type == agent_type.value)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting agents by type {agent_type}: {e}")
            raise
    
    async def get_tlp_agents(self) -> List[Agent]:
        """Get all TLP agents (Conductor and Department Heads)"""
        try:
            result = await self.session.execute(
                select(AgentTable).where(
                    AgentTable.agent_type.in_([AgentType.CONDUCTOR, AgentType.DEPARTMENT_HEAD])
                )
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting TLP agents: {e}")
            raise
    
    async def get_subordinates(self, parent_agent_id: UUID) -> List[Agent]:
        """Get subordinate agents"""
        try:
            result = await self.session.execute(
                select(AgentTable).where(AgentTable.parent_agent_id == parent_agent_id)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting subordinates for agent {parent_agent_id}: {e}")
            raise
    
    async def get_by_capability(self, capability: str) -> List[Agent]:
        """Get agents with specific capability"""
        try:
            result = await self.session.execute(
                select(AgentTable).where(
                    AgentTable.capabilities.op('@>')([capability])
                )
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting agents by capability {capability}: {e}")
            raise
    
    async def update_performance_metrics(self, agent_id: UUID, task_duration: float, success: bool):
        """Update agent performance metrics"""
        try:
            agent = await self.get_by_id(agent_id)
            if not agent:
                return None
            
            new_total = agent.tasks_completed + agent.tasks_failed + 1
            current_total_time = agent.average_task_duration * (new_total - 1)
            new_average = (current_total_time + task_duration) / new_total
            
            updates = {
                "tasks_completed": agent.tasks_completed + (1 if success else 0),
                "tasks_failed": agent.tasks_failed + (0 if success else 1),
                "average_task_duration": new_average,
                "last_activity": datetime.utcnow()
            }
            
            return await self.update(agent_id, updates)
        except Exception as e:
            logger.error(f"Error updating performance metrics for agent {agent_id}: {e}")
            raise


class TaskRepository(BaseRepository):
    """Repository for task operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, TaskTable, Task)
    
    async def get_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        try:
            result = await self.session.execute(
                select(TaskTable).where(TaskTable.status == status.value)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting tasks by status {status}: {e}")
            raise
    
    async def get_assigned_tasks(self, agent_id: UUID) -> List[Task]:
        """Get tasks assigned to an agent"""
        try:
            result = await self.session.execute(
                select(TaskTable).where(TaskTable.assigned_agent_id == agent_id)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting assigned tasks for agent {agent_id}: {e}")
            raise
    
    async def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready for execution (no unsatisfied dependencies)"""
        try:
            # Get tasks that have no dependencies or all dependencies are satisfied
            result = await self.session.execute(
                select(TaskTable).where(
                    and_(
                        TaskTable.status.in_(['created', 'queued', 'assigned']),
                        ~TaskTable.id.in_(
                            select(TaskDependencyTable.dependent_task_id).where(
                                TaskDependencyTable.is_satisfied == False
                            )
                        )
                    )
                )
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting ready tasks: {e}")
            raise
    
    async def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        try:
            result = await self.session.execute(
                select(TaskTable).where(
                    and_(
                        TaskTable.deadline < datetime.utcnow(),
                        TaskTable.status.in_(['created', 'queued', 'assigned', 'in_progress'])
                    )
                )
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting overdue tasks: {e}")
            raise
    
    async def get_subtasks(self, parent_task_id: UUID) -> List[Task]:
        """Get subtasks of a parent task"""
        try:
            result = await self.session.execute(
                select(TaskTable).where(TaskTable.parent_task_id == parent_task_id)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting subtasks for task {parent_task_id}: {e}")
            raise


class MemoryRepository(BaseRepository):
    """Repository for memory operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, MemoryTable, Memory)
    
    async def get_agent_memories(self, agent_id: UUID, memory_type: Optional[MemoryType] = None) -> List[Memory]:
        """Get memories for an agent, optionally filtered by type"""
        try:
            query = select(MemoryTable).where(MemoryTable.agent_id == agent_id)
            if memory_type:
                query = query.where(MemoryTable.memory_type == memory_type.value)
            
            result = await self.session.execute(query.order_by(MemoryTable.importance_score.desc()))
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting memories for agent {agent_id}: {e}")
            raise
    
    async def get_core_memories(self, agent_id: UUID) -> List[Memory]:
        """Get core memories for an agent"""
        try:
            result = await self.session.execute(
                select(MemoryTable).where(
                    and_(
                        MemoryTable.agent_id == agent_id,
                        or_(
                            MemoryTable.memory_type == MemoryType.CORE,
                            MemoryTable.importance_score > 0.8
                        )
                    )
                ).order_by(MemoryTable.importance_score.desc())
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting core memories for agent {agent_id}: {e}")
            raise
    
    async def search_memories(self, agent_id: UUID, query: str, limit: int = 10) -> List[Memory]:
        """Search memories by content"""
        try:
            result = await self.session.execute(
                select(MemoryTable).where(
                    and_(
                        MemoryTable.agent_id == agent_id,
                        MemoryTable.content.ilike(f"%{query}%")
                    )
                ).order_by(MemoryTable.importance_score.desc())
                .limit(limit)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error searching memories for agent {agent_id}: {e}")
            raise
    
    async def update_access(self, memory_id: UUID):
        """Update memory access statistics"""
        try:
            await self.session.execute(
                update(MemoryTable)
                .where(MemoryTable.id == memory_id)
                .values(
                    access_count=MemoryTable.access_count + 1,
                    last_accessed=datetime.utcnow(),
                    consolidation_level=func.least(1.0, MemoryTable.consolidation_level + 0.01)
                )
            )
        except Exception as e:
            logger.error(f"Error updating memory access for {memory_id}: {e}")
            raise


class ExperienceRepository(BaseRepository):
    """Repository for experience operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ExperienceTable, Experience)
    
    async def get_agent_experiences(self, agent_id: UUID, limit: int = 50) -> List[Experience]:
        """Get recent experiences for an agent"""
        try:
            result = await self.session.execute(
                select(ExperienceTable)
                .where(ExperienceTable.agent_id == agent_id)
                .order_by(ExperienceTable.created_at.desc())
                .limit(limit)
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting experiences for agent {agent_id}: {e}")
            raise
    
    async def get_high_impact_experiences(self, agent_id: UUID, threshold: float = 0.7) -> List[Experience]:
        """Get high-impact experiences for consciousness development"""
        try:
            result = await self.session.execute(
                select(ExperienceTable).where(
                    and_(
                        ExperienceTable.agent_id == agent_id,
                        or_(
                            func.abs(ExperienceTable.emotional_impact) > threshold,
                            ExperienceTable.learning_value > threshold,
                            func.abs(ExperienceTable.consciousness_impact) > threshold
                        )
                    )
                ).order_by(ExperienceTable.created_at.desc())
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting high-impact experiences for agent {agent_id}: {e}")
            raise


class RelationshipRepository(BaseRepository):
    """Repository for relationship operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AgentRelationshipTable, AgentRelationship)
    
    async def get_agent_relationships(self, agent_id: UUID) -> List[AgentRelationship]:
        """Get all relationships for an agent"""
        try:
            result = await self.session.execute(
                select(AgentRelationshipTable).where(
                    or_(
                        AgentRelationshipTable.agent_a_id == agent_id,
                        AgentRelationshipTable.agent_b_id == agent_id
                    )
                )
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting relationships for agent {agent_id}: {e}")
            raise
    
    async def get_relationship(self, agent_a_id: UUID, agent_b_id: UUID) -> Optional[AgentRelationship]:
        """Get specific relationship between two agents"""
        try:
            result = await self.session.execute(
                select(AgentRelationshipTable).where(
                    or_(
                        and_(
                            AgentRelationshipTable.agent_a_id == agent_a_id,
                            AgentRelationshipTable.agent_b_id == agent_b_id
                        ),
                        and_(
                            AgentRelationshipTable.agent_a_id == agent_b_id,
                            AgentRelationshipTable.agent_b_id == agent_a_id
                        )
                    )
                )
            )
            db_obj = result.scalar_one_or_none()
            return self._to_model(db_obj) if db_obj else None
        except Exception as e:
            logger.error(f"Error getting relationship between {agent_a_id} and {agent_b_id}: {e}")
            raise


class ConsciousnessRepository(BaseRepository):
    """Repository for consciousness state operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConsciousnessStateTable, ConsciousnessState)
    
    async def get_by_agent_id(self, agent_id: UUID) -> Optional[ConsciousnessState]:
        """Get consciousness state for an agent"""
        try:
            result = await self.session.execute(
                select(ConsciousnessStateTable).where(ConsciousnessStateTable.agent_id == agent_id)
            )
            db_obj = result.scalar_one_or_none()
            return self._to_model(db_obj) if db_obj else None
        except Exception as e:
            logger.error(f"Error getting consciousness state for agent {agent_id}: {e}")
            raise
    
    async def get_conscious_agents(self, min_level: float = 0.5) -> List[ConsciousnessState]:
        """Get agents with consciousness above threshold"""
        try:
            result = await self.session.execute(
                select(ConsciousnessStateTable).where(
                    ConsciousnessStateTable.overall_consciousness_level >= min_level
                ).order_by(ConsciousnessStateTable.overall_consciousness_level.desc())
            )
            db_objs = result.scalars().all()
            return [self._to_model(obj) for obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting conscious agents with level >= {min_level}: {e}")
            raise
    
    async def update_consciousness_level(self, agent_id: UUID, component: str, delta: float):
        """Update specific consciousness component"""
        try:
            consciousness = await self.get_by_agent_id(agent_id)
            if not consciousness:
                return None
            
            # Update specific component
            current_value = getattr(consciousness, f"{component}_level", 0.0)
            new_value = max(0.0, min(1.0, current_value + delta))
            
            # Recalculate overall consciousness
            components = [
                consciousness.self_awareness_level,
                consciousness.temporal_continuity_level,
                consciousness.social_cognition_level,
                consciousness.meta_cognition_level
            ]
            
            # Update the specific component in the list
            if component == "self_awareness":
                components[0] = new_value
            elif component == "temporal_continuity":
                components[1] = new_value
            elif component == "social_cognition":
                components[2] = new_value
            elif component == "meta_cognition":
                components[3] = new_value
            
            overall_level = sum(components) / len(components)
            
            updates = {
                f"{component}_level": new_value,
                "overall_consciousness_level": overall_level
            }
            
            await self.session.execute(
                update(ConsciousnessStateTable)
                .where(ConsciousnessStateTable.agent_id == agent_id)
                .values(**updates)
            )
            
            return await self.get_by_agent_id(agent_id)
        except Exception as e:
            logger.error(f"Error updating consciousness for agent {agent_id}: {e}")
            raise
