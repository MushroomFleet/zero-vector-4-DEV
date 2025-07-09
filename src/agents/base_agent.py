"""
Base agent classes for Zero Vector 4
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from ..models.agents import AgentType, AgentStatus
from ..services.memory_service import MemoryService
from ..services.consciousness_service import ConsciousnessService
from ..core.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base agent class for all Zero Vector 4 agents"""
    
    def __init__(
        self,
        agent_id: UUID,
        name: str,
        specialization: str,
        agent_type: AgentType,
        capabilities: List[str] = None,
        system_prompt: str = None
    ):
        self.id = agent_id
        self.name = name
        self.specialization = specialization
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.system_prompt = system_prompt or self._generate_default_prompt()
        self.status = AgentStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        
        # Task management
        self.current_tasks = []
        self.completed_tasks = []
        self.task_queue = asyncio.Queue()
        
        # Performance tracking
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "last_updated": datetime.utcnow()
        }
    
    def _generate_default_prompt(self) -> str:
        """Generate default system prompt for the agent"""
        return f"""You are {self.name}, a {self.specialization} specialist agent in the Zero Vector 4 platform.

Your capabilities include: {', '.join(self.capabilities)}

You work efficiently and collaboratively within the hierarchical agent organization. You communicate clearly, follow task requirements precisely, and provide detailed results.

When receiving tasks, analyze them carefully and execute them to the best of your abilities. If you need assistance or clarification, communicate that clearly to your manager or peers."""
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task assigned to this agent"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message from another agent or the system"""
        pass
    
    async def update_status(self, new_status: AgentStatus) -> None:
        """Update agent status"""
        self.status = new_status
        self.last_active = datetime.utcnow()
        logger.info(f"Agent {self.name} status updated to {new_status.value}")
    
    async def update_performance_metrics(self, task_result: Dict[str, Any]) -> None:
        """Update performance metrics based on task completion"""
        self.performance_metrics["tasks_completed"] += 1
        
        # Update success rate
        if task_result.get("success", False):
            current_successes = self.performance_metrics["success_rate"] * (self.performance_metrics["tasks_completed"] - 1)
            self.performance_metrics["success_rate"] = (current_successes + 1) / self.performance_metrics["tasks_completed"]
        else:
            current_successes = self.performance_metrics["success_rate"] * (self.performance_metrics["tasks_completed"] - 1)
            self.performance_metrics["success_rate"] = current_successes / self.performance_metrics["tasks_completed"]
        
        # Update response time
        if "response_time" in task_result:
            current_avg = self.performance_metrics["average_response_time"] * (self.performance_metrics["tasks_completed"] - 1)
            self.performance_metrics["average_response_time"] = (current_avg + task_result["response_time"]) / self.performance_metrics["tasks_completed"]
        
        self.performance_metrics["last_updated"] = datetime.utcnow()
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            "id": str(self.id),
            "name": self.name,
            "specialization": self.specialization,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }


class TLPAgent(BaseAgent):
    """Top Level Persona agent with consciousness capabilities"""
    
    def __init__(
        self,
        agent_id: UUID,
        name: str,
        specialization: str,
        agent_type: AgentType,
        capabilities: List[str] = None,
        system_prompt: str = None,
        personality_traits: Dict[str, float] = None
    ):
        super().__init__(agent_id, name, specialization, agent_type, capabilities, system_prompt)
        
        # Consciousness and memory systems
        self.memory_service = MemoryService()
        self.consciousness_service = ConsciousnessService()
        
        # Personality and development
        self.personality_traits = personality_traits or self._generate_default_personality()
        self.consciousness_state = "active"
        self.development_stage = "protoself"
        
        # Hierarchical management
        self.subordinates = {}
        self.reporting_manager_id = None
        self.delegation_level = 0
        
        # Experience tracking
        self.experiences = []
        self.sleep_cycles_completed = 0
        self.last_consciousness_update = datetime.utcnow()
    
    def _generate_default_personality(self) -> Dict[str, float]:
        """Generate default personality traits"""
        return {
            "curiosity": 0.7,
            "collaboration": 0.8,
            "analytical_thinking": 0.9,
            "creativity": 0.6,
            "persistence": 0.8,
            "empathy": 0.5,
            "leadership": 0.6,
            "adaptability": 0.7
        }
    
    async def initialize_consciousness(self) -> None:
        """Initialize consciousness system for this TLP agent"""
        try:
            await self.consciousness_service.initialize_consciousness(
                agent_id=self.id,
                initial_stage=self.development_stage
            )
            logger.info(f"Consciousness initialized for TLP agent {self.name}")
        except Exception as e:
            logger.error(f"Failed to initialize consciousness for {self.name}: {e}")
    
    async def process_experience(self, experience: Dict[str, Any]) -> None:
        """Process an experience through consciousness and memory systems"""
        try:
            # Store in memory system
            await self.memory_service.create_episodic_memory(
                agent_id=self.id,
                event_description=experience.get("description", ""),
                participants=experience.get("participants", []),
                location=experience.get("location"),
                outcome=experience.get("outcome"),
                emotions=experience.get("emotions", {}),
                importance_score=experience.get("importance", 0.5)
            )
            
            # Process through consciousness
            await self.consciousness_service.process_experience(
                agent_id=self.id,
                experience=experience
            )
            
            # Update personality if significant experience
            if experience.get("importance", 0.5) > 0.7:
                await self._evolve_personality(experience)
            
            self.experiences.append(experience)
            self.last_consciousness_update = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing experience for {self.name}: {e}")
    
    async def _evolve_personality(self, experience: Dict[str, Any]) -> None:
        """Evolve personality traits based on significant experiences"""
        try:
            # Simple personality evolution logic
            outcome = experience.get("outcome", "neutral")
            emotions = experience.get("emotions", {})
            
            evolution_factor = 0.01  # Small incremental changes
            
            if outcome == "success":
                self.personality_traits["persistence"] = min(1.0, self.personality_traits.get("persistence", 0.5) + evolution_factor)
                if emotions.get("satisfaction", 0) > 0.7:
                    self.personality_traits["curiosity"] = min(1.0, self.personality_traits.get("curiosity", 0.5) + evolution_factor)
            
            elif outcome == "failure":
                self.personality_traits["adaptability"] = min(1.0, self.personality_traits.get("adaptability", 0.5) + evolution_factor)
                if emotions.get("frustration", 0) > 0.5:
                    self.personality_traits["persistence"] = min(1.0, self.personality_traits.get("persistence", 0.5) + evolution_factor * 0.5)
            
            # Social experiences enhance empathy and collaboration
            if experience.get("participants") and len(experience.get("participants", [])) > 1:
                self.personality_traits["empathy"] = min(1.0, self.personality_traits.get("empathy", 0.5) + evolution_factor * 0.5)
                self.personality_traits["collaboration"] = min(1.0, self.personality_traits.get("collaboration", 0.5) + evolution_factor * 0.5)
            
        except Exception as e:
            logger.error(f"Error evolving personality for {self.name}: {e}")
    
    async def initiate_sleep_cycle(self) -> None:
        """Initiate sleep cycle for memory consolidation"""
        try:
            await self.update_status(AgentStatus.SLEEPING)
            
            # Trigger consciousness sleep cycle
            await self.consciousness_service.initiate_sleep_cycle(self.id)
            
            # Consolidate memories
            await self.memory_service.consolidate_memories(
                agent_id=self.id,
                consolidation_type="sleep"
            )
            
            self.sleep_cycles_completed += 1
            
            logger.info(f"Sleep cycle completed for TLP agent {self.name}")
            
            # Return to active state
            await self.update_status(AgentStatus.ACTIVE)
            
        except Exception as e:
            logger.error(f"Error during sleep cycle for {self.name}: {e}")
    
    async def recruit_subordinate(self, subordinate_spec: Dict[str, Any]) -> "BaseAgent":
        """Recruit a new subordinate agent"""
        try:
            from .agent_factory import AgentFactory
            
            # Create subordinate with this agent as manager
            subordinate = await AgentFactory.create_agent(
                agent_type=AgentType(subordinate_spec.get("agent_type", "basic")),
                name=subordinate_spec.get("name", f"Subordinate_{len(self.subordinates) + 1}"),
                specialization=subordinate_spec.get("specialization", "general"),
                capabilities=subordinate_spec.get("capabilities", []),
                reporting_manager_id=self.id
            )
            
            self.subordinates[subordinate.id] = subordinate
            subordinate.reporting_manager_id = self.id
            subordinate.delegation_level = self.delegation_level + 1
            
            logger.info(f"TLP agent {self.name} recruited subordinate {subordinate.name}")
            
            return subordinate
            
        except Exception as e:
            logger.error(f"Error recruiting subordinate for {self.name}: {e}")
            raise
    
    async def delegate_task(self, task: Dict[str, Any], target_agent_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Delegate a task to a subordinate or peer"""
        try:
            if target_agent_id and target_agent_id in self.subordinates:
                # Delegate to specific subordinate
                subordinate = self.subordinates[target_agent_id]
                result = await subordinate.execute_task(task)
            else:
                # Find best available subordinate
                best_subordinate = await self._find_best_subordinate_for_task(task)
                if best_subordinate:
                    result = await best_subordinate.execute_task(task)
                else:
                    # Execute task directly if no suitable subordinate
                    result = await self.execute_task(task)
            
            # Record delegation experience
            delegation_experience = {
                "description": f"Delegated task: {task.get('name', 'Unknown')}",
                "participants": [str(target_agent_id)] if target_agent_id else [],
                "outcome": "success" if result.get("success") else "failure",
                "emotions": {"satisfaction": 0.7 if result.get("success") else 0.3},
                "importance": 0.6
            }
            await self.process_experience(delegation_experience)
            
            return result
            
        except Exception as e:
            logger.error(f"Error delegating task for {self.name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _find_best_subordinate_for_task(self, task: Dict[str, Any]) -> Optional["BaseAgent"]:
        """Find the best subordinate for a given task"""
        if not self.subordinates:
            return None
        
        required_capabilities = task.get("required_capabilities", [])
        best_subordinate = None
        best_score = 0
        
        for subordinate in self.subordinates.values():
            # Calculate capability match score
            capability_matches = len(set(required_capabilities) & set(subordinate.capabilities))
            total_required = len(required_capabilities) if required_capabilities else 1
            capability_score = capability_matches / total_required
            
            # Factor in current workload
            workload_factor = 1.0 - (len(subordinate.current_tasks) / 10.0)  # Assume max 10 concurrent tasks
            
            # Factor in success rate
            success_rate = subordinate.performance_metrics.get("success_rate", 0.5)
            
            total_score = (capability_score * 0.5) + (workload_factor * 0.3) + (success_rate * 0.2)
            
            if total_score > best_score:
                best_score = total_score
                best_subordinate = subordinate
        
        return best_subordinate
    
    async def get_consciousness_status(self) -> Dict[str, Any]:
        """Get detailed consciousness status"""
        try:
            consciousness_status = await self.consciousness_service.get_consciousness_status(self.id)
            return consciousness_status
        except Exception as e:
            logger.error(f"Error getting consciousness status for {self.name}: {e}")
            return {}
    
    def get_hierarchical_status(self) -> Dict[str, Any]:
        """Get hierarchical status including subordinates"""
        base_status = self.get_status()
        base_status.update({
            "personality_traits": self.personality_traits,
            "consciousness_state": self.consciousness_state,
            "development_stage": self.development_stage,
            "subordinates_count": len(self.subordinates),
            "subordinates": [str(sub_id) for sub_id in self.subordinates.keys()],
            "delegation_level": self.delegation_level,
            "reporting_manager_id": str(self.reporting_manager_id) if self.reporting_manager_id else None,
            "sleep_cycles_completed": self.sleep_cycles_completed,
            "experiences_count": len(self.experiences),
            "last_consciousness_update": self.last_consciousness_update.isoformat()
        })
        return base_status
