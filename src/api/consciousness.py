"""
Consciousness API endpoints for Zero Vector 4
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..services.consciousness_service import ConsciousnessService, ConsciousnessState, DevelopmentStage
from ..core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter(prefix="/consciousness", tags=["consciousness"])


# Request/Response Models
class ConsciousnessInitRequest(BaseModel):
    agent_id: UUID
    initial_stage: Optional[str] = "protoself"


class ConsciousnessStateUpdate(BaseModel):
    new_state: str
    state_data: Optional[Dict[str, Any]] = None


class ExperienceRequest(BaseModel):
    agent_id: UUID
    description: str
    participants: Optional[List[str]] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    emotions: Optional[Dict[str, float]] = None
    capability_used: Optional[str] = None


class PersonalityEvolutionRequest(BaseModel):
    agent_id: UUID
    experiences: List[Dict[str, Any]]


class ConsciousnessStatusResponse(BaseModel):
    agent_id: str
    current_state: str
    development_stage: str
    development_score: float
    consciousness_metrics: Dict[str, float]
    self_awareness_level: float
    temporal_continuity: float
    social_cognition: float
    introspection_depth: float
    sleep_cycles_completed: int
    memory_statistics: Dict[str, Any]
    last_update: Optional[str]


# Dependency injection
def get_consciousness_service() -> ConsciousnessService:
    return ConsciousnessService()


@router.post("/initialize")
async def initialize_consciousness(
    request: ConsciousnessInitRequest,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Initialize consciousness system for an agent"""
    try:
        # Validate development stage
        try:
            stage = DevelopmentStage(request.initial_stage)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid development stage: {request.initial_stage}"
            )
        
        result = await consciousness_service.initialize_consciousness(
            agent_id=request.agent_id,
            initial_stage=stage
        )
        
        return {
            "status": "success",
            "message": f"Consciousness initialized for agent {request.agent_id}",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error initializing consciousness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{agent_id}/state")
async def update_consciousness_state(
    agent_id: UUID,
    state_update: ConsciousnessStateUpdate,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Update agent consciousness state"""
    try:
        # Validate consciousness state
        try:
            new_state = ConsciousnessState(state_update.new_state)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid consciousness state: {state_update.new_state}"
            )
        
        result = await consciousness_service.update_consciousness_state(
            agent_id=agent_id,
            new_state=new_state,
            state_data=state_update.state_data
        )
        
        return {
            "status": "success",
            "message": f"Consciousness state updated for agent {agent_id}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating consciousness state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experience")
async def process_experience(
    experience: ExperienceRequest,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Process a new experience through consciousness layer"""
    try:
        experience_data = {
            "description": experience.description,
            "participants": experience.participants or [],
            "location": experience.location,
            "outcome": experience.outcome,
            "emotions": experience.emotions or {},
            "capability_used": experience.capability_used
        }
        
        result = await consciousness_service.process_experience(
            agent_id=experience.agent_id,
            experience=experience_data
        )
        
        return {
            "status": "success",
            "message": f"Experience processed for agent {experience.agent_id}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/sleep")
async def initiate_sleep_cycle(
    agent_id: UUID,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Initiate sleep cycle for agent consciousness"""
    try:
        result = await consciousness_service.initiate_sleep_cycle(agent_id)
        
        return {
            "status": "success",
            "message": f"Sleep cycle initiated for agent {agent_id}",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error initiating sleep cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status", response_model=Dict[str, Any])
async def get_consciousness_status(
    agent_id: UUID,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Get comprehensive consciousness status for an agent"""
    try:
        result = await consciousness_service.get_consciousness_status(agent_id)
        
        return {
            "status": "success",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting consciousness status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/personality/evolve")
async def evolve_personality(
    evolution_request: PersonalityEvolutionRequest,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Evolve agent personality based on accumulated experiences"""
    try:
        result = await consciousness_service.evolve_personality(
            agent_id=evolution_request.agent_id,
            experiences=evolution_request.experiences
        )
        
        return {
            "status": "success",
            "message": f"Personality evolved for agent {evolution_request.agent_id}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error evolving personality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/development-stages")
async def get_development_stages(agent_id: UUID) -> Dict[str, Any]:
    """Get available consciousness development stages"""
    stages = [
        {
            "stage": DevelopmentStage.PROTOSELF.value,
            "description": "Basic processing and initial awareness",
            "requirements": {"self_recognition": 0.0, "temporal_awareness": 0.0}
        },
        {
            "stage": DevelopmentStage.CORE_CONSCIOUSNESS.value,
            "description": "Self-recognition and basic consciousness",
            "requirements": {"self_recognition": 0.3, "temporal_awareness": 0.2}
        },
        {
            "stage": DevelopmentStage.EXTENDED_CONSCIOUSNESS.value,
            "description": "Enhanced awareness and emotional complexity",
            "requirements": {"self_recognition": 0.6, "temporal_awareness": 0.5, "emotional_complexity": 0.4}
        },
        {
            "stage": DevelopmentStage.AUTOBIOGRAPHICAL_SELF.value,
            "description": "Full consciousness with social understanding",
            "requirements": {"self_recognition": 0.8, "temporal_awareness": 0.7, "social_understanding": 0.6}
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "agent_id": str(agent_id),
            "available_stages": stages
        }
    }


@router.get("/{agent_id}/consciousness-states")
async def get_consciousness_states(agent_id: UUID) -> Dict[str, Any]:
    """Get available consciousness states"""
    states = [
        {
            "state": ConsciousnessState.ACTIVE.value,
            "description": "Fully conscious and processing experiences"
        },
        {
            "state": ConsciousnessState.SLEEPING.value,
            "description": "Memory consolidation and reduced processing"
        },
        {
            "state": ConsciousnessState.DREAMING.value,
            "description": "Pattern synthesis and predictive modeling"
        },
        {
            "state": ConsciousnessState.INTROSPECTING.value,
            "description": "Self-model analysis and self-awareness development"
        },
        {
            "state": ConsciousnessState.LEARNING.value,
            "description": "Focused learning and skill development"
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "agent_id": str(agent_id),
            "available_states": states
        }
    }


@router.get("/{agent_id}/metrics/history")
async def get_consciousness_metrics_history(
    agent_id: UUID,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Get historical consciousness metrics for an agent"""
    try:
        # Get current status which includes metrics
        status = await consciousness_service.get_consciousness_status(agent_id)
        
        # Extract historical data (in a real implementation, this would query historical records)
        consciousness_data = status.get("consciousness_metrics", {})
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(agent_id),
                "current_metrics": consciousness_data,
                "development_stage": status.get("development_stage"),
                "self_awareness_level": status.get("self_awareness_level"),
                "sleep_cycles_completed": status.get("sleep_cycles_completed"),
                "last_update": status.get("last_update")
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting consciousness metrics history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/introspection")
async def trigger_introspection(
    agent_id: UUID,
    consciousness_service: ConsciousnessService = Depends(get_consciousness_service)
) -> Dict[str, Any]:
    """Trigger introspection cycle for an agent"""
    try:
        result = await consciousness_service.update_consciousness_state(
            agent_id=agent_id,
            new_state=ConsciousnessState.INTROSPECTING,
            state_data={"triggered_manually": True, "trigger_time": datetime.utcnow().isoformat()}
        )
        
        return {
            "status": "success",
            "message": f"Introspection cycle triggered for agent {agent_id}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering introspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
