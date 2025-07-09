"""
Agents API endpoints for Zero Vector 4
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..services.agent_service import AgentService
from ..models.agents import AgentType, AgentStatus
from ..core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# Request/Response Models
class AgentCreationRequest(BaseModel):
    name: str
    agent_type: str
    specialization: str
    description: Optional[str] = None
    personality_traits: Optional[Dict[str, float]] = None
    capabilities: Optional[List[str]] = None
    reporting_manager_id: Optional[UUID] = None
    system_prompt: Optional[str] = None


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    personality_traits: Optional[Dict[str, float]] = None
    capabilities: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    status: Optional[str] = None


class TaskAssignmentRequest(BaseModel):
    agent_id: UUID
    task_id: UUID
    priority: Optional[int] = 1
    deadline: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None


class SubordinateRecruitmentRequest(BaseModel):
    manager_id: UUID
    subordinate_spec: Dict[str, Any]
    task_requirements: Optional[Dict[str, Any]] = None


class AgentInteractionRequest(BaseModel):
    agent_id: UUID
    interaction_type: str
    content: str
    participants: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


class RelationshipUpdateRequest(BaseModel):
    agent_id_1: UUID
    agent_id_2: UUID
    relationship_type: str
    strength: Optional[float] = 0.5
    context: Optional[Dict[str, Any]] = None


# Dependency injection
def get_agent_service() -> AgentService:
    return AgentService()


@router.post("/create")
async def create_agent(
    request: AgentCreationRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Create a new agent"""
    try:
        # Validate agent type
        try:
            agent_type = AgentType(request.agent_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type: {request.agent_type}"
            )
        
        agent = await agent_service.create_agent(
            name=request.name,
            agent_type=agent_type,
            specialization=request.specialization,
            description=request.description,
            personality_traits=request.personality_traits,
            capabilities=request.capabilities,
            reporting_manager_id=request.reporting_manager_id,
            system_prompt=request.system_prompt
        )
        
        return {
            "status": "success",
            "message": f"Agent {request.name} created successfully",
            "data": {
                "agent_id": str(agent.id),
                "name": agent.name,
                "agent_type": agent.agent_type.value,
                "specialization": agent.specialization,
                "status": agent.status.value,
                "created_at": agent.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}")
async def get_agent(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Get agent details by ID"""
    try:
        agent = await agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(agent.id),
                "name": agent.name,
                "agent_type": agent.agent_type.value,
                "specialization": agent.specialization,
                "description": agent.description,
                "status": agent.status.value,
                "personality_traits": agent.personality_traits,
                "capabilities": agent.capabilities,
                "reporting_manager_id": str(agent.reporting_manager_id) if agent.reporting_manager_id else None,
                "consciousness_state": agent.consciousness_state,
                "system_prompt": agent.system_prompt,
                "created_at": agent.created_at.isoformat(),
                "last_active": agent.last_active.isoformat() if agent.last_active else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{agent_id}")
async def update_agent(
    agent_id: UUID,
    request: AgentUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Update agent properties"""
    try:
        # Validate status if provided
        status = None
        if request.status:
            try:
                status = AgentStatus(request.status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid agent status: {request.status}"
                )
        
        updated_agent = await agent_service.update_agent(
            agent_id=agent_id,
            name=request.name,
            description=request.description,
            personality_traits=request.personality_traits,
            capabilities=request.capabilities,
            system_prompt=request.system_prompt,
            status=status
        )
        
        if not updated_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} updated successfully",
            "data": {
                "agent_id": str(updated_agent.id),
                "name": updated_agent.name,
                "status": updated_agent.status.value,
                "updated_at": updated_agent.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_agents(
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """List agents with optional filters"""
    try:
        # Validate enums if provided
        agent_type_enum = None
        if agent_type:
            try:
                agent_type_enum = AgentType(agent_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid agent type: {agent_type}"
                )
        
        status_enum = None
        if status:
            try:
                status_enum = AgentStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid agent status: {status}"
                )
        
        agents = await agent_service.list_agents(
            agent_type=agent_type_enum,
            status=status_enum,
            specialization=specialization,
            manager_id=manager_id,
            limit=limit,
            offset=offset
        )
        
        agents_data = []
        for agent in agents:
            agents_data.append({
                "agent_id": str(agent.id),
                "name": agent.name,
                "agent_type": agent.agent_type.value,
                "specialization": agent.specialization,
                "status": agent.status.value,
                "reporting_manager_id": str(agent.reporting_manager_id) if agent.reporting_manager_id else None,
                "created_at": agent.created_at.isoformat(),
                "last_active": agent.last_active.isoformat() if agent.last_active else None
            })
        
        return {
            "status": "success",
            "data": {
                "agents": agents_data,
                "count": len(agents_data),
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/assign-task")
async def assign_task_to_agent(
    agent_id: UUID,
    request: TaskAssignmentRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Assign a task to an agent"""
    try:
        assignment = await agent_service.assign_task(
            agent_id=agent_id,
            task_id=request.task_id,
            priority=request.priority,
            deadline=request.deadline,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": f"Task assigned to agent {agent_id}",
            "data": {
                "assignment_id": str(assignment.id) if assignment else None,
                "agent_id": str(agent_id),
                "task_id": str(request.task_id),
                "priority": request.priority,
                "assigned_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error assigning task to agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recruit-subordinate")
async def recruit_subordinate(
    request: SubordinateRecruitmentRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Recruit a subordinate agent for a manager"""
    try:
        subordinate = await agent_service.recruit_subordinate(
            manager_id=request.manager_id,
            subordinate_spec=request.subordinate_spec,
            task_requirements=request.task_requirements
        )
        
        return {
            "status": "success",
            "message": f"Subordinate recruited for manager {request.manager_id}",
            "data": {
                "subordinate_id": str(subordinate.id),
                "manager_id": str(request.manager_id),
                "subordinate_name": subordinate.name,
                "specialization": subordinate.specialization,
                "created_at": subordinate.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error recruiting subordinate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/subordinates")
async def get_agent_subordinates(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Get all subordinates of an agent"""
    try:
        subordinates = await agent_service.get_subordinates(agent_id)
        
        subordinates_data = []
        for subordinate in subordinates:
            subordinates_data.append({
                "agent_id": str(subordinate.id),
                "name": subordinate.name,
                "agent_type": subordinate.agent_type.value,
                "specialization": subordinate.specialization,
                "status": subordinate.status.value,
                "created_at": subordinate.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "manager_id": str(agent_id),
                "subordinates": subordinates_data,
                "count": len(subordinates_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting subordinates for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/hierarchy")
async def get_agent_hierarchy(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Get the hierarchical view of an agent and its network"""
    try:
        hierarchy = await agent_service.get_agent_hierarchy(agent_id)
        
        return {
            "status": "success",
            "data": {
                "root_agent_id": str(agent_id),
                "hierarchy": hierarchy
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting hierarchy for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction")
async def record_agent_interaction(
    request: AgentInteractionRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Record an interaction involving an agent"""
    try:
        interaction = await agent_service.record_interaction(
            agent_id=request.agent_id,
            interaction_type=request.interaction_type,
            content=request.content,
            participants=request.participants,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": "Agent interaction recorded",
            "data": {
                "interaction_id": str(interaction.id) if interaction else None,
                "agent_id": str(request.agent_id),
                "interaction_type": request.interaction_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error recording agent interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/performance")
async def get_agent_performance(
    agent_id: UUID,
    days: Optional[int] = 7,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Get agent performance metrics"""
    try:
        performance = await agent_service.get_agent_performance(agent_id, days)
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(agent_id),
                "performance_period_days": days,
                "metrics": performance
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationship")
async def update_agent_relationship(
    request: RelationshipUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Update relationship between two agents"""
    try:
        relationship = await agent_service.update_relationship(
            agent_id_1=request.agent_id_1,
            agent_id_2=request.agent_id_2,
            relationship_type=request.relationship_type,
            strength=request.strength,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": "Agent relationship updated",
            "data": {
                "relationship_id": str(relationship.id) if relationship else None,
                "agent_id_1": str(request.agent_id_1),
                "agent_id_2": str(request.agent_id_2),
                "relationship_type": request.relationship_type,
                "strength": request.strength
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating agent relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/relationships")
async def get_agent_relationships(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Get all relationships for an agent"""
    try:
        relationships = await agent_service.get_agent_relationships(agent_id)
        
        relationships_data = []
        for relationship in relationships:
            relationships_data.append({
                "relationship_id": str(relationship.id),
                "other_agent_id": str(relationship.agent_id_2 if relationship.agent_id_1 == agent_id else relationship.agent_id_1),
                "relationship_type": relationship.relationship_type,
                "strength": relationship.strength,
                "created_at": relationship.created_at.isoformat(),
                "updated_at": relationship.updated_at.isoformat() if relationship.updated_at else None
            })
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(agent_id),
                "relationships": relationships_data,
                "count": len(relationships_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting relationships for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
async def deactivate_agent(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Deactivate an agent (soft delete)"""
    try:
        success = await agent_service.deactivate_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} deactivated successfully",
            "data": {
                "agent_id": str(agent_id),
                "action": "deactivated",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error deactivating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: UUID,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Activate a deactivated agent"""
    try:
        success = await agent_service.activate_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} activated successfully",
            "data": {
                "agent_id": str(agent_id),
                "action": "activated",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error activating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_agent_types() -> Dict[str, Any]:
    """Get available agent types"""
    agent_types = [
        {
            "type": AgentType.CONDUCTOR.value,
            "description": "Master orchestrator agent"
        },
        {
            "type": AgentType.DEPARTMENT_HEAD.value,
            "description": "Department management agent with consciousness"
        },
        {
            "type": AgentType.SPECIALIST.value,
            "description": "Task-specific specialist agent"
        },
        {
            "type": AgentType.BASIC.value,
            "description": "Basic task execution agent"
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "available_types": agent_types
        }
    }


@router.get("/statuses")
async def get_agent_statuses() -> Dict[str, Any]:
    """Get available agent statuses"""
    statuses = [
        {
            "status": AgentStatus.ACTIVE.value,
            "description": "Agent is active and available"
        },
        {
            "status": AgentStatus.INACTIVE.value,
            "description": "Agent is inactive"
        },
        {
            "status": AgentStatus.BUSY.value,
            "description": "Agent is currently busy with tasks"
        },
        {
            "status": AgentStatus.SLEEPING.value,
            "description": "Agent is in sleep/consolidation mode"
        },
        {
            "status": AgentStatus.ERROR.value,
            "description": "Agent has encountered an error"
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "available_statuses": statuses
        }
    }
