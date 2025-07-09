"""
Orchestration API endpoints for Zero Vector 4
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..services.orchestration_service import OrchestrationService
from ..models.tasks import TaskStatus, TaskPriority
from ..core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


# Request/Response Models
class WorkflowCreationRequest(BaseModel):
    name: str
    description: str
    complexity: Optional[str] = "medium"
    required_capabilities: Optional[List[str]] = None
    priority: Optional[str] = "normal"
    deadline: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None


class TaskDelegationRequest(BaseModel):
    task_id: UUID
    target_agent_id: UUID
    delegation_reason: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class SubtaskCreationRequest(BaseModel):
    parent_task_id: UUID
    subtask_name: str
    subtask_description: str
    assigned_agent_id: Optional[UUID] = None
    priority: Optional[str] = "normal"
    dependencies: Optional[List[UUID]] = None


class WorkflowExecutionRequest(BaseModel):
    workflow_id: UUID
    execution_mode: Optional[str] = "parallel"
    max_agents: Optional[int] = 10
    timeout_minutes: Optional[int] = 60


class TaskProgressUpdate(BaseModel):
    task_id: UUID
    progress_percentage: float
    status: Optional[str] = None
    notes: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentAssignmentRequest(BaseModel):
    task_id: UUID
    agent_specifications: List[Dict[str, Any]]
    assignment_strategy: Optional[str] = "optimal_match"


class WorkflowOptimizationRequest(BaseModel):
    workflow_id: UUID
    optimization_goals: List[str]
    constraints: Optional[Dict[str, Any]] = None


# Dependency injection
def get_orchestration_service() -> OrchestrationService:
    return OrchestrationService()


@router.post("/workflow/create")
async def create_workflow(
    request: WorkflowCreationRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Create a new complex workflow"""
    try:
        # Validate priority
        priority = None
        if request.priority:
            try:
                priority = TaskPriority(request.priority)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority: {request.priority}"
                )
        
        workflow = await orchestration_service.create_workflow(
            name=request.name,
            description=request.description,
            complexity=request.complexity,
            required_capabilities=request.required_capabilities,
            priority=priority,
            deadline=request.deadline,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": f"Workflow '{request.name}' created successfully",
            "data": {
                "workflow_id": str(workflow.id),
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "complexity": request.complexity,
                "created_at": workflow.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: UUID,
    request: WorkflowExecutionRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Execute a complex workflow through agent hierarchy"""
    try:
        execution_result = await orchestration_service.execute_workflow(
            workflow_id=workflow_id,
            execution_mode=request.execution_mode,
            max_agents=request.max_agents,
            timeout_minutes=request.timeout_minutes
        )
        
        return {
            "status": "success",
            "message": f"Workflow execution initiated",
            "data": {
                "workflow_id": str(workflow_id),
                "execution_id": execution_result.get("execution_id"),
                "assigned_agents": execution_result.get("assigned_agents", []),
                "estimated_completion": execution_result.get("estimated_completion"),
                "execution_mode": request.execution_mode
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task/delegate")
async def delegate_task(
    request: TaskDelegationRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Delegate a task to another agent"""
    try:
        delegation_result = await orchestration_service.delegate_task(
            task_id=request.task_id,
            target_agent_id=request.target_agent_id,
            delegation_reason=request.delegation_reason,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": "Task delegated successfully",
            "data": {
                "task_id": str(request.task_id),
                "target_agent_id": str(request.target_agent_id),
                "delegation_id": delegation_result.get("delegation_id"),
                "delegation_timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error delegating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task/decompose")
async def decompose_task(
    task_id: UUID,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Decompose a complex task into subtasks"""
    try:
        decomposition_result = await orchestration_service.decompose_task(task_id)
        
        subtasks_data = []
        for subtask in decomposition_result.get("subtasks", []):
            subtasks_data.append({
                "subtask_id": str(subtask.get("id")),
                "name": subtask.get("name"),
                "description": subtask.get("description"),
                "priority": subtask.get("priority"),
                "estimated_duration": subtask.get("estimated_duration")
            })
        
        return {
            "status": "success",
            "message": f"Task decomposed into {len(subtasks_data)} subtasks",
            "data": {
                "parent_task_id": str(task_id),
                "subtasks_created": len(subtasks_data),
                "subtasks": subtasks_data,
                "decomposition_strategy": decomposition_result.get("strategy")
            }
        }
        
    except Exception as e:
        logger.error(f"Error decomposing task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subtask/create")
async def create_subtask(
    request: SubtaskCreationRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Create a subtask under a parent task"""
    try:
        # Validate priority
        priority = None
        if request.priority:
            try:
                priority = TaskPriority(request.priority)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority: {request.priority}"
                )
        
        subtask = await orchestration_service.create_subtask(
            parent_task_id=request.parent_task_id,
            subtask_name=request.subtask_name,
            subtask_description=request.subtask_description,
            assigned_agent_id=request.assigned_agent_id,
            priority=priority,
            dependencies=request.dependencies
        )
        
        return {
            "status": "success",
            "message": "Subtask created successfully",
            "data": {
                "subtask_id": str(subtask.id),
                "parent_task_id": str(request.parent_task_id),
                "name": subtask.name,
                "assigned_agent_id": str(request.assigned_agent_id) if request.assigned_agent_id else None,
                "created_at": subtask.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating subtask: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/assign")
async def assign_agents_to_task(
    request: AgentAssignmentRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Assign optimal agents to a task"""
    try:
        assignment_result = await orchestration_service.assign_optimal_agents(
            task_id=request.task_id,
            agent_specifications=request.agent_specifications,
            assignment_strategy=request.assignment_strategy
        )
        
        assignments_data = []
        for assignment in assignment_result.get("assignments", []):
            assignments_data.append({
                "agent_id": str(assignment.get("agent_id")),
                "agent_name": assignment.get("agent_name"),
                "specialization": assignment.get("specialization"),
                "match_score": assignment.get("match_score"),
                "role": assignment.get("role")
            })
        
        return {
            "status": "success",
            "message": f"Assigned {len(assignments_data)} agents to task",
            "data": {
                "task_id": str(request.task_id),
                "assignments": assignments_data,
                "assignment_strategy": request.assignment_strategy,
                "total_agents_assigned": len(assignments_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error assigning agents to task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/task/{task_id}/progress")
async def update_task_progress(
    task_id: UUID,
    request: TaskProgressUpdate,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Update task progress and status"""
    try:
        # Validate status if provided
        status = None
        if request.status:
            try:
                status = TaskStatus(request.status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid task status: {request.status}"
                )
        
        updated_task = await orchestration_service.update_task_progress(
            task_id=task_id,
            progress_percentage=request.progress_percentage,
            status=status,
            notes=request.notes,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": "Task progress updated",
            "data": {
                "task_id": str(task_id),
                "progress_percentage": request.progress_percentage,
                "status": updated_task.status.value if updated_task else request.status,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating task progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: UUID,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Get comprehensive workflow status"""
    try:
        workflow_status = await orchestration_service.get_workflow_status(workflow_id)
        
        return {
            "status": "success",
            "data": workflow_status
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}/hierarchy")
async def get_task_hierarchy(
    task_id: UUID,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Get task hierarchy including subtasks and dependencies"""
    try:
        hierarchy = await orchestration_service.get_task_hierarchy(task_id)
        
        return {
            "status": "success",
            "data": {
                "root_task_id": str(task_id),
                "hierarchy": hierarchy
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting task hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/optimize")
async def optimize_workflow(
    workflow_id: UUID,
    request: WorkflowOptimizationRequest,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Optimize workflow execution strategy"""
    try:
        optimization_result = await orchestration_service.optimize_workflow(
            workflow_id=workflow_id,
            optimization_goals=request.optimization_goals,
            constraints=request.constraints
        )
        
        return {
            "status": "success",
            "message": "Workflow optimization completed",
            "data": {
                "workflow_id": str(workflow_id),
                "optimization_goals": request.optimization_goals,
                "improvements": optimization_result.get("improvements", []),
                "estimated_time_savings": optimization_result.get("time_savings"),
                "resource_efficiency": optimization_result.get("resource_efficiency")
            }
        }
        
    except Exception as e:
        logger.error(f"Error optimizing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/performance")
async def get_orchestration_analytics(
    time_period_days: Optional[int] = 7,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Get orchestration performance analytics"""
    try:
        analytics = await orchestration_service.get_performance_analytics(time_period_days)
        
        return {
            "status": "success",
            "data": {
                "time_period_days": time_period_days,
                "analytics": analytics
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting orchestration analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/workload")
async def get_agent_workload_distribution(
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Get current workload distribution across agents"""
    try:
        workload_data = await orchestration_service.get_agent_workload_distribution()
        
        return {
            "status": "success",
            "data": {
                "workload_distribution": workload_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent workload distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coordination/sync")
async def synchronize_agent_coordination(
    agent_ids: List[UUID],
    coordination_strategy: Optional[str] = "consensus",
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Synchronize coordination between multiple agents"""
    try:
        sync_result = await orchestration_service.synchronize_agents(
            agent_ids=agent_ids,
            coordination_strategy=coordination_strategy
        )
        
        return {
            "status": "success",
            "message": f"Synchronized {len(agent_ids)} agents",
            "data": {
                "synchronized_agents": [str(aid) for aid in agent_ids],
                "coordination_strategy": coordination_strategy,
                "sync_result": sync_result
            }
        }
        
    except Exception as e:
        logger.error(f"Error synchronizing agent coordination: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: UUID,
    reason: Optional[str] = "User cancellation",
    orchestration_service: OrchestrationService = Depends(get_orchestration_service)
) -> Dict[str, Any]:
    """Cancel a running workflow"""
    try:
        cancellation_result = await orchestration_service.cancel_workflow(
            workflow_id=workflow_id,
            reason=reason
        )
        
        return {
            "status": "success",
            "message": f"Workflow {workflow_id} cancelled",
            "data": {
                "workflow_id": str(workflow_id),
                "cancellation_reason": reason,
                "cancelled_tasks": cancellation_result.get("cancelled_tasks", 0),
                "cancelled_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error cancelling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_orchestration_strategies() -> Dict[str, Any]:
    """Get available orchestration strategies"""
    strategies = {
        "execution_modes": [
            {"mode": "parallel", "description": "Execute tasks in parallel when possible"},
            {"mode": "sequential", "description": "Execute tasks one after another"},
            {"mode": "adaptive", "description": "Dynamically choose optimal execution pattern"}
        ],
        "assignment_strategies": [
            {"strategy": "optimal_match", "description": "Assign agents with best capability match"},
            {"strategy": "load_balance", "description": "Distribute tasks evenly across agents"},
            {"strategy": "specialization_priority", "description": "Prioritize specialized agents"}
        ],
        "coordination_strategies": [
            {"strategy": "consensus", "description": "Agents reach consensus before proceeding"},
            {"strategy": "hierarchy", "description": "Follow hierarchical decision making"},
            {"strategy": "democracy", "description": "Majority vote determines decisions"}
        ],
        "optimization_goals": [
            "minimize_time",
            "minimize_resources",
            "maximize_quality",
            "balance_workload",
            "minimize_cost"
        ]
    }
    
    return {
        "status": "success",
        "data": strategies
    }
