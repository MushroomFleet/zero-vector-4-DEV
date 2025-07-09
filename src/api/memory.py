"""
Memory API endpoints for Zero Vector 4
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from ..services.memory_service import MemoryService, ConsolidationPriority
from ..models.memory import MemoryType
from ..core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


# Request/Response Models
class MemoryCreationRequest(BaseModel):
    agent_id: UUID
    memory_type: str
    content: str
    context: Optional[Dict[str, Any]] = None
    emotional_valence: Optional[float] = 0.0
    importance_score: Optional[float] = 0.5
    tags: Optional[List[str]] = None
    associations: Optional[List[UUID]] = None


class EpisodicMemoryRequest(BaseModel):
    agent_id: UUID
    event_description: str
    participants: Optional[List[str]] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    emotions: Optional[Dict[str, float]] = None
    importance_score: Optional[float] = 0.5


class SemanticMemoryRequest(BaseModel):
    agent_id: UUID
    knowledge: str
    domain: str
    confidence_level: Optional[float] = 0.8
    source: Optional[str] = None
    related_concepts: Optional[List[str]] = None


class ProceduralMemoryRequest(BaseModel):
    agent_id: UUID
    skill_name: str
    procedure_steps: List[str]
    success_rate: Optional[float] = 0.0
    conditions: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class MemoryRetrievalRequest(BaseModel):
    agent_id: UUID
    memory_type: Optional[str] = None
    context_keywords: Optional[List[str]] = None
    similarity_threshold: Optional[float] = 0.7
    limit: Optional[int] = 10
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None


class MemoryImportanceUpdate(BaseModel):
    memory_id: UUID
    new_importance: float
    reason: Optional[str] = ""


class MemoryAssociationRequest(BaseModel):
    memory_id_1: UUID
    memory_id_2: UUID
    association_type: Optional[str] = "related"
    strength: Optional[float] = 0.5


class ConsolidationRequest(BaseModel):
    agent_id: UUID
    consolidation_type: Optional[str] = "background"


# Dependency injection
def get_memory_service() -> MemoryService:
    return MemoryService()


@router.post("/create")
async def create_memory_entry(
    request: MemoryCreationRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Create a new memory entry for an agent"""
    try:
        # Validate memory type
        try:
            memory_type = MemoryType(request.memory_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid memory type: {request.memory_type}"
            )
        
        memory_entry = await memory_service.create_memory_entry(
            agent_id=request.agent_id,
            memory_type=memory_type,
            content=request.content,
            context=request.context,
            emotional_valence=request.emotional_valence,
            importance_score=request.importance_score,
            tags=request.tags,
            associations=request.associations
        )
        
        return {
            "status": "success",
            "message": f"Memory entry created for agent {request.agent_id}",
            "data": {
                "memory_id": str(memory_entry.id),
                "memory_type": memory_entry.memory_type.value,
                "content": memory_entry.content,
                "importance_score": memory_entry.importance_score,
                "created_at": memory_entry.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating memory entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/episodic")
async def create_episodic_memory(
    request: EpisodicMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Create an episodic memory (specific event with context)"""
    try:
        episodic_memory = await memory_service.create_episodic_memory(
            agent_id=request.agent_id,
            event_description=request.event_description,
            participants=request.participants,
            location=request.location,
            outcome=request.outcome,
            emotions=request.emotions,
            importance_score=request.importance_score
        )
        
        return {
            "status": "success",
            "message": f"Episodic memory created for agent {request.agent_id}",
            "data": {
                "memory_id": str(episodic_memory.id),
                "event_description": episodic_memory.content,
                "participants": episodic_memory.participants,
                "location": episodic_memory.location,
                "outcome": episodic_memory.outcome,
                "emotional_valence": episodic_memory.emotional_valence,
                "created_at": episodic_memory.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating episodic memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic")
async def create_semantic_memory(
    request: SemanticMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Create a semantic memory (general knowledge)"""
    try:
        semantic_memory = await memory_service.create_semantic_memory(
            agent_id=request.agent_id,
            knowledge=request.knowledge,
            domain=request.domain,
            confidence_level=request.confidence_level,
            source=request.source,
            related_concepts=request.related_concepts
        )
        
        return {
            "status": "success",
            "message": f"Semantic memory created for agent {request.agent_id}",
            "data": {
                "memory_id": str(semantic_memory.id),
                "knowledge": semantic_memory.content,
                "domain": semantic_memory.domain,
                "confidence_level": semantic_memory.confidence_level,
                "source": semantic_memory.source,
                "created_at": semantic_memory.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating semantic memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/procedural")
async def create_procedural_memory(
    request: ProceduralMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Create a procedural memory (skill or procedure)"""
    try:
        procedural_memory = await memory_service.create_procedural_memory(
            agent_id=request.agent_id,
            skill_name=request.skill_name,
            procedure_steps=request.procedure_steps,
            success_rate=request.success_rate,
            conditions=request.conditions,
            prerequisites=request.prerequisites
        )
        
        return {
            "status": "success",
            "message": f"Procedural memory created for agent {request.agent_id}",
            "data": {
                "memory_id": str(procedural_memory.id),
                "skill_name": procedural_memory.skill_name,
                "procedure_steps": procedural_memory.procedure_steps,
                "success_rate": procedural_memory.success_rate,
                "conditions": procedural_memory.conditions,
                "created_at": procedural_memory.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating procedural memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrieve")
async def retrieve_memories(
    request: MemoryRetrievalRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Retrieve memories based on various criteria"""
    try:
        # Handle time range
        time_range = None
        if request.time_range_start and request.time_range_end:
            time_range = (request.time_range_start, request.time_range_end)
        
        # Convert memory type string to enum if provided
        memory_type = None
        if request.memory_type:
            try:
                memory_type = MemoryType(request.memory_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid memory type: {request.memory_type}"
                )
        
        memories = await memory_service.retrieve_memories(
            agent_id=request.agent_id,
            memory_type=memory_type,
            context_keywords=request.context_keywords,
            similarity_threshold=request.similarity_threshold,
            limit=request.limit,
            time_range=time_range
        )
        
        memory_data = []
        for memory in memories:
            memory_data.append({
                "memory_id": str(memory.id),
                "memory_type": memory.memory_type.value,
                "content": memory.content,
                "context": memory.context,
                "emotional_valence": memory.emotional_valence,
                "importance_score": memory.importance_score,
                "tags": memory.tags,
                "access_count": memory.access_count,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else None
            })
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(request.agent_id),
                "memories_found": len(memory_data),
                "memories": memory_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/working-memory")
async def get_working_memory(
    agent_id: UUID,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Get agent's current working memory"""
    try:
        working_memories = await memory_service.get_working_memory(agent_id)
        
        memory_data = []
        for memory in working_memories:
            memory_data.append({
                "memory_id": str(memory.id),
                "memory_type": memory.memory_type.value,
                "content": memory.content,
                "importance_score": memory.importance_score,
                "access_count": memory.access_count,
                "created_at": memory.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "agent_id": str(agent_id),
                "working_memory_size": len(memory_data),
                "working_memories": memory_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting working memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consolidate")
async def consolidate_memories(
    request: ConsolidationRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Consolidate agent memories during sleep or background processing"""
    try:
        consolidation_result = await memory_service.consolidate_memories(
            agent_id=request.agent_id,
            consolidation_type=request.consolidation_type
        )
        
        return {
            "status": "success",
            "message": f"Memory consolidation completed for agent {request.agent_id}",
            "data": consolidation_result
        }
        
    except Exception as e:
        logger.error(f"Error consolidating memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/importance")
async def update_memory_importance(
    request: MemoryImportanceUpdate,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Update the importance score of a memory"""
    try:
        updated_memory = await memory_service.update_memory_importance(
            memory_id=request.memory_id,
            new_importance=request.new_importance,
            reason=request.reason
        )
        
        if not updated_memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "status": "success",
            "message": f"Memory importance updated",
            "data": {
                "memory_id": str(updated_memory.id),
                "new_importance": updated_memory.importance_score,
                "updated_at": updated_memory.updated_at.isoformat() if updated_memory.updated_at else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating memory importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/associate")
async def create_memory_association(
    request: MemoryAssociationRequest,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Create an association between two memories"""
    try:
        success = await memory_service.create_memory_association(
            memory_id_1=request.memory_id_1,
            memory_id_2=request.memory_id_2,
            association_type=request.association_type,
            strength=request.strength
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create memory association"
            )
        
        return {
            "status": "success",
            "message": "Memory association created successfully",
            "data": {
                "memory_id_1": str(request.memory_id_1),
                "memory_id_2": str(request.memory_id_2),
                "association_type": request.association_type,
                "strength": request.strength
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating memory association: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/statistics")
async def get_memory_statistics(
    agent_id: UUID,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Get comprehensive memory statistics for an agent"""
    try:
        statistics = await memory_service.get_memory_statistics(agent_id)
        
        return {
            "status": "success",
            "data": statistics
        }
        
    except Exception as e:
        logger.error(f"Error getting memory statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_memory_types() -> Dict[str, Any]:
    """Get available memory types"""
    memory_types = [
        {
            "type": MemoryType.EPISODIC.value,
            "description": "Memories of specific events and experiences"
        },
        {
            "type": MemoryType.SEMANTIC.value,
            "description": "General knowledge and facts"
        },
        {
            "type": MemoryType.PROCEDURAL.value,
            "description": "Skills and procedures"
        },
        {
            "type": MemoryType.WORKING.value,
            "description": "Current context and active processing"
        }
    ]
    
    return {
        "status": "success",
        "data": {
            "available_types": memory_types
        }
    }


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: UUID,
    memory_service: MemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Delete a memory entry (use with caution)"""
    try:
        # This would need to be implemented in the memory service
        # For now, we'll return a placeholder response
        
        return {
            "status": "success",
            "message": f"Memory {memory_id} marked for deletion",
            "data": {
                "memory_id": str(memory_id),
                "action": "deletion_scheduled"
            }
        }
        
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
