# Zero Vector 4 MCP Server

A comprehensive Model Context Protocol (MCP) server that provides access to Zero Vector 4's advanced agent orchestration, consciousness simulation, and memory management capabilities.

## Overview

This MCP server exposes 53 tools organized into 4 main categories:

- **Agent Management** (16 tools) - Create, manage, and coordinate AI agents
- **Consciousness** (10 tools) - Handle agent consciousness states and development  
- **Memory** (12 tools) - Manage different types of agent memories
- **Orchestration** (15 tools) - Handle complex workflows and task coordination

## Installation

1. Install dependencies:
```bash
npm install
```

2. Build the server:
```bash
npm run build
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Zero Vector 4 API configuration
```

## Configuration

Set the following environment variables:

- `ZV4_API_BASE_URL`: Base URL for Zero Vector 4 API (default: http://localhost:8000)
- `ZV4_API_KEY`: API key for authentication (optional)

## Available Tools

### Agent Management Tools (16 tools)

1. **create_agent** - Create a new agent with specified capabilities
2. **get_agent** - Retrieve agent details by ID
3. **update_agent** - Update agent properties and configuration
4. **list_agents** - List agents with optional filters
5. **assign_task_to_agent** - Assign tasks to specific agents
6. **recruit_subordinate** - Recruit subordinate agents for managers
7. **get_agent_subordinates** - Get all subordinates of an agent
8. **get_agent_hierarchy** - View agent hierarchical relationships
9. **record_agent_interaction** - Record interactions between agents
10. **get_agent_performance** - Get performance metrics for agents
11. **update_agent_relationship** - Manage relationships between agents
12. **get_agent_relationships** - View all relationships for an agent
13. **deactivate_agent** - Deactivate an agent (soft delete)
14. **activate_agent** - Reactivate a deactivated agent
15. **get_agent_types** - Get available agent types
16. **get_agent_statuses** - Get available agent statuses

### Consciousness Tools (10 tools)

1. **initialize_consciousness** - Initialize consciousness system for an agent
2. **update_consciousness_state** - Update agent consciousness state
3. **process_experience** - Process new experiences through consciousness layer
4. **initiate_sleep_cycle** - Start sleep cycle for memory consolidation
5. **get_consciousness_status** - Get comprehensive consciousness status
6. **evolve_personality** - Evolve agent personality based on experiences
7. **get_development_stages** - Get available consciousness development stages
8. **get_consciousness_states** - Get available consciousness states
9. **get_consciousness_metrics_history** - Get historical consciousness metrics
10. **trigger_introspection** - Trigger introspection cycle for self-reflection

### Memory Tools (12 tools)

1. **create_memory_entry** - Create a new memory entry
2. **create_episodic_memory** - Create episodic memory (specific events)
3. **create_semantic_memory** - Create semantic memory (general knowledge)
4. **create_procedural_memory** - Create procedural memory (skills/procedures)
5. **retrieve_memories** - Retrieve memories with various criteria
6. **get_working_memory** - Get agent's current working memory
7. **consolidate_memories** - Consolidate memories during sleep
8. **update_memory_importance** - Update memory importance scores
9. **create_memory_association** - Create associations between memories
10. **get_memory_statistics** - Get comprehensive memory statistics
11. **get_memory_types** - Get available memory types
12. **delete_memory** - Delete a memory entry

### Orchestration Tools (15 tools)

1. **create_workflow** - Create complex multi-agent workflows
2. **execute_workflow** - Execute workflows through agent hierarchy
3. **delegate_task** - Delegate tasks between agents
4. **decompose_task** - Break complex tasks into subtasks
5. **create_subtask** - Create subtasks under parent tasks
6. **assign_agents_to_task** - Assign optimal agents to tasks
7. **update_task_progress** - Update task progress and status
8. **get_workflow_status** - Get comprehensive workflow status
9. **get_task_hierarchy** - View task hierarchy and dependencies
10. **optimize_workflow** - Optimize workflow execution strategies
11. **get_orchestration_analytics** - Get performance analytics
12. **get_agent_workload_distribution** - View agent workload distribution
13. **synchronize_agent_coordination** - Synchronize multi-agent coordination
14. **cancel_workflow** - Cancel running workflows
15. **get_orchestration_strategies** - Get available orchestration strategies

## Usage Examples

### Creating an Agent
```typescript
// Create a new specialist agent
await use_mcp_tool("zero-vector-4-mcp", "create_agent", {
  "name": "Data Analyst",
  "agent_type": "specialist", 
  "specialization": "data_analysis",
  "description": "Specialized in data analysis and visualization",
  "capabilities": ["python", "pandas", "matplotlib", "sql"],
  "personality_traits": {
    "analytical": 0.9,
    "detail_oriented": 0.8,
    "collaborative": 0.7
  }
});
```

### Processing an Experience
```typescript
// Process a learning experience
await use_mcp_tool("zero-vector-4-mcp", "process_experience", {
  "agent_id": "agent-uuid-here",
  "description": "Successfully completed data analysis project",
  "participants": ["user", "other-agent-uuid"],
  "location": "virtual_workspace",
  "outcome": "positive",
  "emotions": {
    "satisfaction": 0.8,
    "confidence": 0.7
  },
  "capability_used": "data_analysis"
});
```

### Creating a Workflow
```typescript
// Create a complex workflow
await use_mcp_tool("zero-vector-4-mcp", "create_workflow", {
  "name": "Data Processing Pipeline",
  "description": "End-to-end data processing and analysis workflow",
  "complexity": "high",
  "required_capabilities": ["data_extraction", "data_cleaning", "analysis", "visualization"],
  "priority": "high",
  "deadline": "2024-01-15T23:59:59Z"
});
```

### Retrieving Memories
```typescript
// Retrieve memories by context
await use_mcp_tool("zero-vector-4-mcp", "retrieve_memories", {
  "agent_id": "agent-uuid-here",
  "memory_type": "episodic",
  "context_keywords": ["data", "analysis", "success"],
  "similarity_threshold": 0.7,
  "limit": 10
});
```

## Integration with Cline

To use this MCP server with Cline:

1. Add to your MCP configuration:
```json
{
  "mcpServers": {
    "zero-vector-4-mcp": {
      "command": "node",
      "args": ["C:/Projects/zero-vector-4-dev/MCP/zero-vector-4-mcp/build/index.js"],
      "env": {
        "ZV4_API_BASE_URL": "http://localhost:8000",
        "ZV4_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

2. The tools will be available as:
```typescript
use_mcp_tool("zero-vector-4-mcp", "tool_name", { parameters })
```

## API Endpoints Mapping

The MCP server maps to these Zero Vector 4 API endpoints:

### Agent Management
- `/api/agents/create` - Agent creation
- `/api/agents/{id}` - Agent CRUD operations
- `/api/agents` - Agent listing and filtering
- `/api/agents/{id}/subordinates` - Hierarchy management
- `/api/agents/interaction` - Interaction recording

### Consciousness
- `/api/consciousness/initialize` - Consciousness initialization
- `/api/consciousness/{id}/state` - State management
- `/api/consciousness/experience` - Experience processing
- `/api/consciousness/{id}/sleep` - Sleep cycles

### Memory
- `/api/memory/create` - Memory creation
- `/api/memory/episodic` - Episodic memories
- `/api/memory/semantic` - Semantic memories
- `/api/memory/procedural` - Procedural memories
- `/api/memory/retrieve` - Memory retrieval

### Orchestration
- `/api/orchestration/workflow/create` - Workflow creation
- `/api/orchestration/workflow/{id}/execute` - Workflow execution
- `/api/orchestration/task/delegate` - Task delegation
- `/api/orchestration/agents/assign` - Agent assignment

## Error Handling

The server includes comprehensive error handling:

- API connection errors are properly formatted
- Invalid tool names return appropriate error messages
- Missing parameters are handled gracefully
- Authentication errors are passed through from the API

## Development

To modify or extend the server:

1. Edit `src/index.ts`
2. Run `npm run build` to compile
3. Test with your MCP client

## License

This MCP server is part of the Zero Vector 4 project.
