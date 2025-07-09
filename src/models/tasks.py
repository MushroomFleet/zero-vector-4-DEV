"""
Task data models for Zero Vector 4
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any, Set

from pydantic import Field, validator

from .base import StatusModel


class TaskType(str, Enum):
    """Task type enumeration"""
    ORCHESTRATION = "orchestration"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    CREATION = "creation"
    COMMUNICATION = "communication"
    COMPUTATION = "computation"
    PLANNING = "planning"
    DECISION_MAKING = "decision_making"
    QUALITY_ASSURANCE = "quality_assurance"
    COORDINATION = "coordination"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_DEPENDENCIES = "waiting_for_dependencies"
    DELEGATED = "delegated"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Task(StatusModel):
    """Task model for the hierarchical agent system"""
    
    # Basic task information
    task_type: TaskType = Field(..., description="Type of task")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(..., min_length=1, description="Detailed task description")
    
    # Task execution
    assigned_agent_id: Optional[str] = Field(None, description="ID of agent assigned to this task")
    delegation_chain: List[str] = Field(default_factory=list, description="Chain of agents who delegated this task")
    delegation_level: int = Field(default=0, description="Level of delegation (0 = original task)")
    
    # Task timing
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    estimated_duration: Optional[timedelta] = Field(None, description="Estimated completion time")
    actual_duration: Optional[timedelta] = Field(None, description="Actual completion time")
    started_at: Optional[datetime] = Field(None, description="When task execution started")
    completed_at: Optional[datetime] = Field(None, description="When task was completed")
    
    # Task dependencies
    depends_on: Set[str] = Field(default_factory=set, description="Task IDs this task depends on")
    blocks: Set[str] = Field(default_factory=set, description="Task IDs that this task blocks")
    parent_task_id: Optional[str] = Field(None, description="Parent task ID if this is a subtask")
    subtask_ids: Set[str] = Field(default_factory=set, description="Subtask IDs")
    
    # Task requirements and constraints
    required_capabilities: List[str] = Field(default_factory=list, description="Required agent capabilities")
    required_tools: List[str] = Field(default_factory=list, description="Required tools")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Task constraints")
    
    # Task input/output
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the task")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data from the task")
    intermediate_results: List[Dict[str, Any]] = Field(default_factory=list, description="Intermediate results")
    
    # Task metadata
    tags: List[str] = Field(default_factory=list, description="Task tags for categorization")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context information")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    
    @validator('depends_on', 'blocks', 'subtask_ids', pre=True)
    def convert_sets(cls, v):
        """Convert lists to sets if needed"""
        if isinstance(v, list):
            return set(v)
        return v
    
    def add_dependency(self, task_id: str):
        """Add a task dependency"""
        self.depends_on.add(task_id)
        self.update_timestamp()
    
    def remove_dependency(self, task_id: str):
        """Remove a task dependency"""
        self.depends_on.discard(task_id)
        self.update_timestamp()
    
    def add_subtask(self, task_id: str):
        """Add a subtask"""
        self.subtask_ids.add(task_id)
        self.update_timestamp()
    
    def start_execution(self, agent_id: str):
        """Mark task as started"""
        self.assigned_agent_id = agent_id
        self.started_at = datetime.utcnow()
        self.update_status(TaskStatus.IN_PROGRESS, f"Started by agent {agent_id}")
    
    def complete_task(self, output_data: Dict[str, Any] = None, success: bool = True):
        """Mark task as completed"""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.actual_duration = self.completed_at - self.started_at
        
        if output_data:
            self.output_data.update(output_data)
        
        status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        self.update_status(status, f"Task {'completed' if success else 'failed'}")
    
    def fail_task(self, reason: str = ""):
        """Mark task as failed"""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.actual_duration = self.completed_at - self.started_at
        
        self.retry_count += 1
        self.update_status(TaskStatus.FAILED, f"Task failed: {reason}")
    
    def delegate_task(self, from_agent_id: str, to_agent_id: str):
        """Delegate task to another agent"""
        self.delegation_chain.append(from_agent_id)
        self.delegation_level += 1
        self.assigned_agent_id = to_agent_id
        self.update_status(TaskStatus.DELEGATED, f"Delegated from {from_agent_id} to {to_agent_id}")
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    
    def is_ready_to_execute(self) -> bool:
        """Check if task is ready for execution (all dependencies met)"""
        return len(self.depends_on) == 0 and self.status in [TaskStatus.CREATED, TaskStatus.QUEUED, TaskStatus.ASSIGNED]
    
    @property
    def is_delegated_task(self) -> bool:
        """Check if this task has been delegated"""
        return len(self.delegation_chain) > 0
    
    @property
    def has_subtasks(self) -> bool:
        """Check if task has subtasks"""
        return len(self.subtask_ids) > 0
    
    @property
    def estimated_completion_time(self) -> Optional[datetime]:
        """Calculate estimated completion time"""
        if not self.estimated_duration:
            return None
        
        if self.started_at:
            return self.started_at + self.estimated_duration
        else:
            return datetime.utcnow() + self.estimated_duration


class TaskResult(StatusModel):
    """Result of task execution"""
    
    task_id: str = Field(..., description="ID of the associated task")
    agent_id: str = Field(..., description="ID of the agent that executed the task")
    
    # Result data
    success: bool = Field(..., description="Whether the task was successful")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed error information")
    
    # Execution metrics
    execution_time: timedelta = Field(..., description="Time taken to execute the task")
    resource_usage: Dict[str, float] = Field(default_factory=dict, description="Resource usage during execution")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score of the result")
    
    # Additional metadata
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts (file paths, URLs, etc.)")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics")
    
    def add_artifact(self, artifact_path: str):
        """Add an artifact to the result"""
        self.artifacts.append(artifact_path)
        self.update_timestamp()
    
    def add_log_entry(self, log_entry: str):
        """Add a log entry"""
        timestamp = datetime.utcnow().isoformat()
        self.logs.append(f"[{timestamp}] {log_entry}")
        self.update_timestamp()
    
    def update_quality_score(self, score: float):
        """Update the quality score"""
        self.quality_score = max(0.0, min(1.0, score))
        self.update_timestamp()


class WorkflowTask(Task):
    """Extended task model for complex workflows"""
    
    # Workflow-specific properties
    workflow_id: str = Field(..., description="ID of the workflow this task belongs to")
    workflow_stage: str = Field(default="execution", description="Current workflow stage")
    parallel_execution: bool = Field(default=False, description="Whether this task can run in parallel")
    
    # Advanced coordination
    coordination_type: str = Field(default="sequential", description="Type of coordination (sequential, parallel, conditional)")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Execution conditions")
    triggers: List[str] = Field(default_factory=list, description="Event triggers for task execution")
    
    # Result aggregation
    aggregation_strategy: str = Field(default="merge", description="Strategy for aggregating subtask results")
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Result validation rules")
    
    def add_condition(self, condition_name: str, condition_value: Any):
        """Add an execution condition"""
        self.conditions[condition_name] = condition_value
        self.update_timestamp()
    
    def check_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if execution conditions are met"""
        for condition_name, expected_value in self.conditions.items():
            if context.get(condition_name) != expected_value:
                return False
        return True
    
    def validate_result(self, result_data: Dict[str, Any]) -> bool:
        """Validate result against validation rules"""
        for rule in self.validation_rules:
            # Simple validation logic - can be extended
            field = rule.get("field")
            expected_type = rule.get("type")
            required = rule.get("required", False)
            
            if required and field not in result_data:
                return False
            
            if field in result_data and expected_type:
                if not isinstance(result_data[field], eval(expected_type)):
                    return False
        
        return True
