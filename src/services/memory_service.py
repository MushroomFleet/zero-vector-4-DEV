"""
Memory service for Zero Vector 4
Handles agent memory systems, experience storage, and consolidation
"""

import asyncio
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum

from ..models.memory import (
    Memory, MemoryType, Experience, ConsciousnessState, MemoryCluster
)
from ..models.agents import Agent
from ..database.repositories import MemoryRepository, AgentRepository
from ..database.connection import get_db_session
from ..core.config import get_config
from ..core.logging import get_logger

logger = get_logger(__name__)


class ConsolidationPriority(Enum):
    """Memory consolidation priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryService:
    """Service for managing agent memory systems and consolidation"""
    
    def __init__(self):
        self.config = get_config()
        self.consolidation_interval = 3600  # 1 hour in seconds
        self.max_working_memory_size = 50
        self.consolidation_threshold = 0.7
    
    async def create_memory_entry(
        self,
        agent_id: UUID,
        memory_type: MemoryType,
        content: str,
        context: Dict[str, Any] = None,
        emotional_valence: float = 0.0,
        importance_score: float = 0.5,
        tags: List[str] = None,
        associations: List[UUID] = None
    ) -> Memory:
        """Create a new memory entry for an agent"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Create base memory entry
                memory_entry = Memory(
                    id=uuid4(),
                    name=f"memory_{uuid4().hex[:8]}",
                    agent_id=str(agent_id),
                    memory_type=memory_type,
                    content=content,
                    structured_data=context or {},
                    emotional_valence=emotional_valence,
                    importance_score=importance_score,
                    context_tags=tags or [],
                    associated_agents=[str(a) for a in (associations or [])]
                )
                
                created_memory = await memory_repo.create(memory_entry)
                
                # Add to working memory if agent is active
                await self._add_to_working_memory(agent_id, created_memory)
                
                logger.info(f"Created {memory_type.value} memory for agent {agent_id}")
                return created_memory
                
        except Exception as e:
            logger.error(f"Error creating memory entry: {e}")
            raise
    
    async def create_episodic_memory(
        self,
        agent_id: UUID,
        event_description: str,
        participants: List[str] = None,
        location: str = None,
        outcome: str = None,
        emotions: Dict[str, float] = None,
        importance_score: float = 0.5
    ) -> Memory:
        """Create an episodic memory (specific event with context)"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                context = {
                    "participants": participants or [],
                    "location": location,
                    "outcome": outcome,
                    "emotions": emotions or {}
                }
                
                episodic_memory = Memory(
                    id=uuid4(),
                    name=f"episodic_{uuid4().hex[:8]}",
                    agent_id=str(agent_id),
                    memory_type=MemoryType.EPISODIC,
                    content=event_description,
                    structured_data=context,
                    emotional_valence=self._calculate_emotional_valence(emotions or {}),
                    importance_score=importance_score,
                    context_tags=[],
                    associated_agents=participants or [],
                    location=location
                )
                
                created_memory = await memory_repo.create(episodic_memory)
                await self._add_to_working_memory(agent_id, created_memory)
                
                logger.info(f"Created episodic memory for agent {agent_id}: {event_description[:50]}...")
                return created_memory
                
        except Exception as e:
            logger.error(f"Error creating episodic memory: {e}")
            raise
    
    async def create_semantic_memory(
        self,
        agent_id: UUID,
        knowledge: str,
        domain: str,
        confidence_level: float = 0.8,
        source: str = None,
        related_concepts: List[str] = None
    ) -> Memory:
        """Create a semantic memory (general knowledge)"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                context = {
                    "domain": domain,
                    "source": source,
                    "related_concepts": related_concepts or [],
                    "confidence_level": confidence_level
                }
                
                semantic_memory = Memory(
                    id=uuid4(),
                    name=f"semantic_{uuid4().hex[:8]}",
                    agent_id=str(agent_id),
                    memory_type=MemoryType.SEMANTIC,
                    content=knowledge,
                    structured_data=context,
                    importance_score=confidence_level,
                    context_tags=[domain]
                )
                
                created_memory = await memory_repo.create(semantic_memory)
                
                logger.info(f"Created semantic memory for agent {agent_id} in domain {domain}")
                return created_memory
                
        except Exception as e:
            logger.error(f"Error creating semantic memory: {e}")
            raise
    
    async def create_procedural_memory(
        self,
        agent_id: UUID,
        skill_name: str,
        procedure_steps: List[str],
        success_rate: float = 0.0,
        conditions: List[str] = None,
        prerequisites: List[str] = None
    ) -> Memory:
        """Create a procedural memory (skill or procedure)"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                context = {
                    "conditions": conditions or [],
                    "prerequisites": prerequisites or [],
                    "skill_name": skill_name,
                    "procedure_steps": procedure_steps,
                    "success_rate": success_rate
                }
                
                procedural_memory = Memory(
                    id=uuid4(),
                    name=f"procedural_{uuid4().hex[:8]}",
                    agent_id=str(agent_id),
                    memory_type=MemoryType.PROCEDURAL,
                    content=f"Skill: {skill_name}",
                    structured_data=context,
                    importance_score=success_rate,
                    context_tags=[skill_name]
                )
                
                created_memory = await memory_repo.create(procedural_memory)
                
                logger.info(f"Created procedural memory for agent {agent_id}: {skill_name}")
                return created_memory
                
        except Exception as e:
            logger.error(f"Error creating procedural memory: {e}")
            raise
    
    async def retrieve_memories(
        self,
        agent_id: UUID,
        memory_type: Optional[MemoryType] = None,
        context_keywords: List[str] = None,
        similarity_threshold: float = 0.7,
        limit: int = 10,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Memory]:
        """Retrieve memories based on various criteria"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Build query filters
                filters = {"agent_id": agent_id}
                
                if memory_type:
                    filters["memory_type"] = memory_type.value
                
                if time_range:
                    filters["created_at_start"] = time_range[0]
                    filters["created_at_end"] = time_range[1]
                
                # Get memories from repository
                memories = await memory_repo.find_by_criteria(filters, limit=limit)
                
                # Filter by context keywords if provided
                if context_keywords:
                    relevant_memories = []
                    for memory in memories:
                        relevance_score = await self._calculate_relevance(
                            memory, context_keywords
                        )
                        if relevance_score >= similarity_threshold:
                            relevant_memories.append(memory)
                    memories = relevant_memories
                
                # Update access patterns
                for memory in memories:
                    await self._update_memory_access(memory.id)
                
                logger.info(f"Retrieved {len(memories)} memories for agent {agent_id}")
                return memories
                
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            raise
    
    async def get_working_memory(self, agent_id: UUID) -> List[Memory]:
        """Get agent's current working memory"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Get recent memories with high access frequency
                recent_cutoff = datetime.utcnow() - timedelta(hours=1)
                
                working_memories = await memory_repo.get_working_memory(
                    agent_id, 
                    since=recent_cutoff,
                    limit=self.max_working_memory_size
                )
                
                return working_memories
                
        except Exception as e:
            logger.error(f"Error getting working memory for agent {agent_id}: {e}")
            raise
    
    async def consolidate_memories(
        self,
        agent_id: UUID,
        consolidation_type: str = "sleep"
    ) -> Dict[str, Any]:
        """Consolidate agent memories during sleep or background processing"""
        try:
            logger.info(f"Starting memory consolidation for agent {agent_id}")
            
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Get recent memories for consolidation
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                recent_memories = await memory_repo.get_memories_since(agent_id, cutoff_time)
                
                consolidation_results = {
                    "agent_id": str(agent_id),
                    "consolidation_type": consolidation_type,
                    "memories_processed": len(recent_memories),
                    "patterns_identified": [],
                    "memories_consolidated": 0,
                    "memories_pruned": 0,
                    "new_associations": 0
                }
                
                if not recent_memories:
                    return consolidation_results
                
                # Identify important patterns
                important_patterns = await self._identify_memory_patterns(recent_memories)
                consolidation_results["patterns_identified"] = important_patterns
                
                # Consolidate important memories into long-term storage
                for memory in recent_memories:
                    if memory.importance_score >= self.consolidation_threshold:
                        await self._consolidate_to_longterm(memory)
                        consolidation_results["memories_consolidated"] += 1
                
                # Create associations between related memories
                new_associations = await self._create_memory_associations(recent_memories)
                consolidation_results["new_associations"] = len(new_associations)
                
                # Prune low-importance memories
                pruned_count = await self._prune_unimportant_memories(agent_id)
                consolidation_results["memories_pruned"] = pruned_count
                
                # Update consolidation timestamp
                await self._update_last_consolidation(agent_id)
                
                logger.info(f"Completed memory consolidation for agent {agent_id}")
                return consolidation_results
                
        except Exception as e:
            logger.error(f"Error consolidating memories for agent {agent_id}: {e}")
            raise
    
    async def update_memory_importance(
        self,
        memory_id: UUID,
        new_importance: float,
        reason: str = ""
    ) -> Optional[Memory]:
        """Update the importance score of a memory"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                updates = {
                    "importance_score": new_importance,
                    "updated_at": datetime.utcnow()
                }
                
                if reason:
                    # Add update reason to structured_data
                    memory = await memory_repo.get_by_id(memory_id)
                    if memory:
                        structured_data = memory.structured_data or {}
                        if "importance_updates" not in structured_data:
                            structured_data["importance_updates"] = []
                        structured_data["importance_updates"].append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "new_score": new_importance,
                            "reason": reason
                        })
                        updates["structured_data"] = structured_data
                
                updated_memory = await memory_repo.update(memory_id, updates)
                
                if updated_memory:
                    logger.info(f"Updated memory importance: {memory_id} -> {new_importance}")
                
                return updated_memory
                
        except Exception as e:
            logger.error(f"Error updating memory importance: {e}")
            raise
    
    async def create_memory_association(
        self,
        memory_id_1: UUID,
        memory_id_2: UUID,
        association_type: str = "related",
        strength: float = 0.5
    ) -> bool:
        """Create an association between two memories"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Update both memories with mutual associations
                success1 = await memory_repo.add_association(
                    memory_id_1, memory_id_2, association_type, strength
                )
                success2 = await memory_repo.add_association(
                    memory_id_2, memory_id_1, association_type, strength
                )
                
                if success1 and success2:
                    logger.info(f"Created {association_type} association between memories")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error creating memory association: {e}")
            raise
    
    async def get_memory_statistics(self, agent_id: UUID) -> Dict[str, Any]:
        """Get comprehensive memory statistics for an agent"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Get memory counts by type
                memory_counts = await memory_repo.get_memory_counts_by_type(agent_id)
                
                # Get recent activity
                recent_cutoff = datetime.utcnow() - timedelta(days=7)
                recent_memories = await memory_repo.get_memories_since(agent_id, recent_cutoff)
                
                # Calculate average importance
                all_memories = await memory_repo.get_agent_memories(agent_id)
                avg_importance = sum(m.importance_score for m in all_memories) / len(all_memories) if all_memories else 0
                
                # Get last consolidation time
                last_consolidation = await memory_repo.get_last_consolidation_time(agent_id)
                
                return {
                    "agent_id": str(agent_id),
                    "total_memories": len(all_memories),
                    "memory_counts_by_type": memory_counts,
                    "recent_memories_7_days": len(recent_memories),
                    "average_importance": avg_importance,
                    "last_consolidation": last_consolidation.isoformat() if last_consolidation else None,
                    "working_memory_size": len(await self.get_working_memory(agent_id))
                }
                
        except Exception as e:
            logger.error(f"Error getting memory statistics for agent {agent_id}: {e}")
            raise
    
    # Private helper methods
    
    async def _add_to_working_memory(self, agent_id: UUID, memory: Memory):
        """Add memory to agent's working memory"""
        try:
            # Working memory is managed through access patterns and recency
            # This is handled by the get_working_memory method
            pass
        except Exception as e:
            logger.error(f"Error adding to working memory: {e}")
    
    async def _calculate_relevance(
        self,
        memory: Memory,
        keywords: List[str]
    ) -> float:
        """Calculate relevance score between memory and keywords"""
        try:
            content_lower = memory.content.lower()
            matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            
            # Check tags and context
            tag_matches = sum(1 for keyword in keywords 
                            if any(keyword.lower() in tag.lower() for tag in memory.context_tags))
            
            context_str = str(memory.structured_data).lower()
            context_matches = sum(1 for keyword in keywords if keyword.lower() in context_str)
            
            total_matches = matches + tag_matches + context_matches
            max_possible = len(keywords) * 3  # content, tags, context
            
            return total_matches / max_possible if max_possible > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0
    
    async def _update_memory_access(self, memory_id: UUID):
        """Update memory access statistics"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                await memory_repo.increment_access_count(memory_id)
                
        except Exception as e:
            logger.error(f"Error updating memory access: {e}")
    
    async def _identify_memory_patterns(
        self,
        memories: List[Memory]
    ) -> List[Dict[str, Any]]:
        """Identify patterns in recent memories"""
        try:
            patterns = []
            
            # Group by tags
            tag_groups = {}
            for memory in memories:
                for tag in memory.context_tags:
                    if tag not in tag_groups:
                        tag_groups[tag] = []
                    tag_groups[tag].append(memory)
            
            # Identify frequent patterns
            for tag, tag_memories in tag_groups.items():
                if len(tag_memories) >= 3:  # Pattern threshold
                    patterns.append({
                        "type": "tag_frequency",
                        "pattern": tag,
                        "frequency": len(tag_memories),
                        "memories": [str(m.id) for m in tag_memories]
                    })
            
            # Identify emotional patterns
            positive_memories = [m for m in memories if m.emotional_valence > 0.5]
            negative_memories = [m for m in memories if m.emotional_valence < -0.5]
            
            if len(positive_memories) >= 3:
                patterns.append({
                    "type": "emotional_trend",
                    "pattern": "positive",
                    "frequency": len(positive_memories)
                })
            
            if len(negative_memories) >= 3:
                patterns.append({
                    "type": "emotional_trend",
                    "pattern": "negative",
                    "frequency": len(negative_memories)
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying memory patterns: {e}")
            return []
    
    async def _consolidate_to_longterm(self, memory: Memory):
        """Move important memory to long-term storage"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Mark memory as consolidated
                updates = {
                    "is_consolidated": True,
                    "consolidated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await memory_repo.update(memory.id, updates)
                
        except Exception as e:
            logger.error(f"Error consolidating memory to long-term: {e}")
    
    async def _create_memory_associations(
        self,
        memories: List[Memory]
    ) -> List[Tuple[UUID, UUID]]:
        """Create associations between related memories"""
        try:
            associations = []
            
            # Simple similarity-based association
            for i, memory1 in enumerate(memories):
                for memory2 in memories[i+1:]:
                    similarity = await self._calculate_memory_similarity(memory1, memory2)
                    
                    if similarity > 0.7:  # Similarity threshold
                        success = await self.create_memory_association(
                            memory1.id,
                            memory2.id,
                            "similarity",
                            similarity
                        )
                        if success:
                            associations.append((memory1.id, memory2.id))
            
            return associations
            
        except Exception as e:
            logger.error(f"Error creating memory associations: {e}")
            return []
    
    async def _calculate_memory_similarity(
        self,
        memory1: Memory,
        memory2: Memory
    ) -> float:
        """Calculate similarity between two memories"""
        try:
            # Simple similarity based on shared tags and content overlap
            shared_tags = set(memory1.context_tags) & set(memory2.context_tags)
            tag_similarity = len(shared_tags) / max(len(memory1.context_tags), len(memory2.context_tags), 1)
            
            # Check for common words in content
            words1 = set(memory1.content.lower().split())
            words2 = set(memory2.content.lower().split())
            shared_words = words1 & words2
            content_similarity = len(shared_words) / max(len(words1), len(words2), 1)
            
            # Combine similarities
            return (tag_similarity + content_similarity) / 2
            
        except Exception as e:
            logger.error(f"Error calculating memory similarity: {e}")
            return 0.0
    
    async def _prune_unimportant_memories(self, agent_id: UUID) -> int:
        """Prune memories with very low importance scores"""
        try:
            async with get_db_session() as session:
                memory_repo = MemoryRepository(session)
                
                # Get old, low-importance memories
                cutoff_time = datetime.utcnow() - timedelta(days=30)
                low_importance_memories = await memory_repo.get_low_importance_memories(
                    agent_id,
                    importance_threshold=0.2,
                    older_than=cutoff_time
                )
                
                pruned_count = 0
                for memory in low_importance_memories:
                    if memory.access_count == 0:  # Never accessed
                        await memory_repo.delete(memory.id)
                        pruned_count += 1
                
                return pruned_count
                
        except Exception as e:
            logger.error(f"Error pruning unimportant memories: {e}")
            return 0
    
    async def _update_last_consolidation(self, agent_id: UUID):
        """Update the last consolidation timestamp for an agent"""
        try:
            async with get_db_session() as session:
                agent_repo = AgentRepository(session)
                
                # Update agent's last consolidation time
                updates = {
                    "last_memory_consolidation": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await agent_repo.update(agent_id, updates)
                
        except Exception as e:
            logger.error(f"Error updating last consolidation time: {e}")
    
    def _calculate_emotional_valence(self, emotions: Dict[str, float]) -> float:
        """Calculate overall emotional valence from emotion scores"""
        if not emotions:
            return 0.0
        
        positive_emotions = ["joy", "happiness", "satisfaction", "pride", "excitement"]
        negative_emotions = ["sadness", "anger", "fear", "anxiety", "frustration"]
        
        positive_score = sum(emotions.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(emotions.get(emotion, 0) for emotion in negative_emotions)
        
        # Normalize to -1 to 1 range
        total_score = positive_score - negative_score
        max_possible = len(positive_emotions) + len(negative_emotions)
        
        return max(-1.0, min(1.0, total_score / max_possible)) if max_possible > 0 else 0.0
