"""
Task service for Zero Vector 4
Handles task lifecycle management, assignment, and coordination
"""

import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from ..models.tasks import Task, TaskStatus, TaskResult, TaskPriority
from ..models.agents import Agent, AgentType
from ..models.relationships import TaskDependency
from ..database.repositories import TaskRepository, AgentRepository, RelationshipRepository
from ..database.connection import get_db_session
from ..core.config import get_config
from ..core.logging import get_logger

logger = get_logger(__name__)


class TaskService:
    """Service for managing task operations and lifecycle"""
    
    def __init__(self):
        self.config = get_config()
    
    async def create_task(
        self,
        name: str,
        description: str,
        task_type: str = "general",
        priority: TaskPriority = TaskPriority.NORMAL,
        assigned_agent_id: Optional[UUID] = None,
        parent_task_id: Optional[UUID] = None,
        required_capabilities: List[str] = None,
        deadline: Optional[datetime] = None,
        estimated_duration: Optional[float] = None,
        input_data: Dict[str, Any] = None,
        constraints: Dict[str, Any] = None
    ) -> Task:
        """Create a new task"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                # Determine delegation level based on parent task
                delegation_level = 0
                delegation_chain = []
                
                if parent_task_id:
                    parent_task = await task_repo.get_by_id(parent_task_id)
                    if parent_task:
                        delegation_level = parent_task.delegation_level + 1
                        delegation_chain = parent_task.delegation_chain + [str(parent_task_id)]
                
                # Create task
                task = Task(
                    id=uuid4(),
                    name=name,
                    description=description,
                    title=name,  # Using name as title for now
                    task_type=task_type,
                    priority=priority,
                    status=TaskStatus.CREATED,
                    assigned_agent_id=assigned_agent_id,
                    parent_task_id=parent_task_id,
                    delegation_level=delegation_level,
                    delegation_chain=delegation_chain,
                    required_capabilities=required_capabilities or [],
                    deadline=deadline,
                    estimated_duration=estimated_duration,
                    input_data=input_data or {},
                    constraints=constraints or {}
                )
                
                created_task = await task_repo.create(task)
                logger.info(f"Created task {created_task.name} ({created_task.id})")
                return created_task
                
        except Exception as e:
            logger.error(f"Error creating task {name}: {e}")
            raise
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                return await task_repo.get_by_id(task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            raise
    
    async def assign_task(self, task_id: UUID, agent_id: UUID) -> Optional[Task]:
        """Assign task to an agent"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                agent_repo = AgentRepository(session)
                
                # Verify agent exists and is available
                agent = await agent_repo.get_by_id(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found")
                
                if agent.status != "active":
                    raise ValueError(f"Agent {agent_id} is not active (status: {agent.status})")
                
                # Update task assignment
                updates = {
                    "assigned_agent_id": agent_id,
                    "status": TaskStatus.ASSIGNED.value,
                    "updated_at": datetime.utcnow()
                }
                
                updated_task = await task_repo.update(task_id, updates)
                
                if updated_task:
                    logger.info(f"Assigned task {task_id} to agent {agent_id}")
                
                return updated_task
                
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to agent {agent_id}: {e}")
            raise
    
    async def start_task(self, task_id: UUID) -> Optional[Task]:
        """Start task execution"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                updates = {
                    "status": TaskStatus.IN_PROGRESS.value,
                    "started_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                updated_task = await task_repo.update(task_id, updates)
                
                if updated_task:
                    logger.info(f"Started task {task_id}")
                
                return updated_task
                
        except Exception as e:
            logger.error(f"Error starting task {task_id}: {e}")
            raise
    
    async def complete_task(
        self,
        task_id: UUID,
        result: TaskResult,
        output_data: Dict[str, Any] = None
    ) -> Optional[Task]:
        """Complete a task with results"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                agent_repo = AgentRepository(session)
                
                task = await task_repo.get_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                # Calculate actual duration
                actual_duration = None
                if task.started_at:
                    actual_duration = (datetime.utcnow() - task.started_at).total_seconds()
                
                # Update task
                updates = {
                    "status": result.status.value if hasattr(result, 'status') else TaskStatus.COMPLETED.value,
                    "completed_at": datetime.utcnow(),
                    "actual_duration": actual_duration,
                    "output_data": output_data or {},
                    "updated_at": datetime.utcnow()
                }
                
                updated_task = await task_repo.update(task_id, updates)
                
                # Update agent performance metrics
                if task.assigned_agent_id and actual_duration:
                    success = updates["status"] == TaskStatus.COMPLETED.value
                    await agent_repo.update_performance_metrics(
                        task.assigned_agent_id,
                        actual_duration,
                        success
                    )
                
                # Check and update dependent tasks
                await self._check_task_dependencies(session, task_id)
                
                logger.info(f"Completed task {task_id} with status {updates['status']}")
                return updated_task
                
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            raise
    
    async def fail_task(self, task_id: UUID, error_message: str = "") -> Optional[Task]:
        """Mark task as failed"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                task = await task_repo.get_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                # Calculate actual duration if started
                actual_duration = None
                if task.started_at:
                    actual_duration = (datetime.utcnow() - task.started_at).total_seconds()
                
                updates = {
                    "status": TaskStatus.FAILED.value,
                    "completed_at": datetime.utcnow(),
                    "actual_duration": actual_duration,
                    "retry_count": task.retry_count + 1,
                    "updated_at": datetime.utcnow()
                }
                
                # Add error message to output data
                output_data = task.output_data or {}
                output_data["error_message"] = error_message
                output_data["failure_timestamp"] = datetime.utcnow().isoformat()
                updates["output_data"] = output_data
                
                updated_task = await task_repo.update(task_id, updates)
                
                # Update agent performance metrics
                if task.assigned_agent_id and actual_duration:
                    agent_repo = AgentRepository(session)
                    await agent_repo.update_performance_metrics(
                        task.assigned_agent_id,
                        actual_duration,
                        False  # Failed task
                    )
                
                logger.warning(f"Failed task {task_id}: {error_message}")
                return updated_task
                
        except Exception as e:
            logger.error(f"Error failing task {task_id}: {e}")
            raise
    
    async def retry_task(self, task_id: UUID) -> Optional[Task]:
        """Retry a failed task if under retry limit"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                task = await task_repo.get_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                if task.retry_count >= task.max_retries:
                    raise ValueError(f"Task {task_id} has exceeded retry limit ({task.max_retries})")
                
                if task.status != TaskStatus.FAILED:
                    raise ValueError(f"Task {task_id} is not in failed state")
                
                # Reset task for retry
                updates = {
                    "status": TaskStatus.QUEUED.value,
                    "started_at": None,
                    "completed_at": None,
                    "actual_duration": None,
                    "updated_at": datetime.utcnow()
                }
                
                updated_task = await task_repo.update(task_id, updates)
                
                logger.info(f"Retrying task {task_id} (attempt {task.retry_count + 1})")
                return updated_task
                
        except Exception as e:
            logger.error(f"Error retrying task {task_id}: {e}")
            raise
    
    async def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready for execution (no unsatisfied dependencies)"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                return await task_repo.get_ready_tasks()
        except Exception as e:
            logger.error(f"Error getting ready tasks: {e}")
            raise
    
    async def get_agent_tasks(self, agent_id: UUID, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get tasks assigned to an agent"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                if status:
                    # Get tasks with specific status
                    all_tasks = await task_repo.get_assigned_tasks(agent_id)
                    return [task for task in all_tasks if task.status == status]
                else:
                    return await task_repo.get_assigned_tasks(agent_id)
                    
        except Exception as e:
            logger.error(f"Error getting tasks for agent {agent_id}: {e}")
            raise
    
    async def get_subtasks(self, parent_task_id: UUID) -> List[Task]:
        """Get subtasks of a parent task"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                return await task_repo.get_subtasks(parent_task_id)
        except Exception as e:
            logger.error(f"Error getting subtasks for task {parent_task_id}: {e}")
            raise
    
    async def create_task_dependency(
        self,
        dependent_task_id: UUID,
        dependency_task_id: UUID,
        dependency_type: str = "finish_to_start",
        is_blocking: bool = True,
        is_critical: bool = False
    ) -> TaskDependency:
        """Create a dependency between tasks"""
        try:
            async with get_db_session() as session:
                relationship_repo = RelationshipRepository(session)
                
                dependency = TaskDependency(
                    id=uuid4(),
                    name=f"dependency_{dependent_task_id}_{dependency_task_id}",
                    dependent_task_id=dependent_task_id,
                    dependency_task_id=dependency_task_id,
                    dependency_type=dependency_type,
                    is_blocking=is_blocking,
                    is_critical=is_critical
                )
                
                created_dependency = await relationship_repo.create(dependency)
                logger.info(f"Created dependency: task {dependent_task_id} depends on {dependency_task_id}")
                return created_dependency
                
        except Exception as e:
            logger.error(f"Error creating task dependency: {e}")
            raise
    
    async def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                return await task_repo.get_overdue_tasks()
        except Exception as e:
            logger.error(f"Error getting overdue tasks: {e}")
            raise
    
    async def decompose_task(
        self,
        task_id: UUID,
        subtask_specs: List[Dict[str, Any]]
    ) -> List[Task]:
        """Decompose a task into subtasks"""
        try:
            subtasks = []
            
            for spec in subtask_specs:
                subtask = await self.create_task(
                    name=spec.get("name"),
                    description=spec.get("description"),
                    task_type=spec.get("task_type", "subtask"),
                    priority=spec.get("priority", TaskPriority.NORMAL),
                    parent_task_id=task_id,
                    required_capabilities=spec.get("required_capabilities"),
                    estimated_duration=spec.get("estimated_duration"),
                    input_data=spec.get("input_data"),
                    constraints=spec.get("constraints")
                )
                subtasks.append(subtask)
                
                # Create dependencies if specified
                if "dependencies" in spec:
                    for dep_spec in spec["dependencies"]:
                        dependency_task_id = dep_spec.get("task_id")
                        if dependency_task_id:
                            await self.create_task_dependency(
                                subtask.id,
                                dependency_task_id,
                                dep_spec.get("type", "finish_to_start"),
                                dep_spec.get("is_blocking", True),
                                dep_spec.get("is_critical", False)
                            )
            
            logger.info(f"Decomposed task {task_id} into {len(subtasks)} subtasks")
            return subtasks
            
        except Exception as e:
            logger.error(f"Error decomposing task {task_id}: {e}")
            raise
    
    async def get_task_progress(self, task_id: UUID) -> Dict[str, Any]:
        """Get comprehensive task progress information"""
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                
                task = await task_repo.get_by_id(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                subtasks = await task_repo.get_subtasks(task_id)
                
                # Calculate progress metrics
                total_subtasks = len(subtasks)
                completed_subtasks = len([t for t in subtasks if t.status == TaskStatus.COMPLETED])
                failed_subtasks = len([t for t in subtasks if t.status == TaskStatus.FAILED])
                in_progress_subtasks = len([t for t in subtasks if t.status == TaskStatus.IN_PROGRESS])
                
                progress_percentage = 0.0
                if total_subtasks > 0:
                    progress_percentage = (completed_subtasks / total_subtasks) * 100
                
                # Calculate estimated completion
                estimated_completion = None
                if task.estimated_duration and task.started_at:
                    estimated_completion = task.started_at + timedelta(seconds=task.estimated_duration)
                
                return {
                    "task_id": task_id,
                    "status": task.status,
                    "progress_percentage": progress_percentage,
                    "total_subtasks": total_subtasks,
                    "completed_subtasks": completed_subtasks,
                    "failed_subtasks": failed_subtasks,
                    "in_progress_subtasks": in_progress_subtasks,
                    "started_at": task.started_at,
                    "estimated_completion": estimated_completion,
                    "actual_duration": task.actual_duration,
                    "delegation_level": task.delegation_level
                }
                
        except Exception as e:
            logger.error(f"Error getting task progress for {task_id}: {e}")
            raise
    
    async def _check_task_dependencies(self, session, completed_task_id: UUID):
        """Check and update dependent tasks when a task completes"""
        try:
            # This would typically query the task_dependencies table
            # For now, we'll implement basic logic
            # TODO: Implement full dependency resolution
            pass
        except Exception as e:
            logger.error(f"Error checking task dependencies for {completed_task_id}: {e}")
