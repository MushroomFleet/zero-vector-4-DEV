#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError, } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
// Environment configuration
const ZV4_API_BASE_URL = process.env.ZV4_API_BASE_URL || 'http://localhost:8000';
const ZV4_API_KEY = process.env.ZV4_API_KEY;
// API Client setup
class ZV4ApiClient {
    client;
    constructor() {
        this.client = axios.create({
            baseURL: ZV4_API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
                ...(ZV4_API_KEY && { 'Authorization': `Bearer ${ZV4_API_KEY}` }),
            },
            timeout: 30000,
        });
    }
    async makeRequest(method, endpoint, data, params) {
        try {
            const response = await this.client.request({
                method,
                url: endpoint,
                data,
                params,
            });
            return response.data;
        }
        catch (error) {
            if (axios.isAxiosError(error)) {
                throw new McpError(ErrorCode.InternalError, `ZV4 API Error: ${error.response?.data?.detail || error.message}`);
            }
            throw error;
        }
    }
}
class ZeroVector4Server {
    server;
    apiClient;
    constructor() {
        this.server = new Server({
            name: 'zero-vector-4-mcp',
            version: '1.0.0',
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.apiClient = new ZV4ApiClient();
        this.setupToolHandlers();
        // Error handling
        this.server.onerror = (error) => console.error('[MCP Error]', error);
        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }
    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                // Agent Management Tools (16 tools)
                {
                    name: 'create_agent',
                    description: 'Create a new agent in the Zero Vector 4 system',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            name: { type: 'string', description: 'Agent name' },
                            agent_type: { type: 'string', description: 'Agent type (conductor, department_head, specialist, basic)' },
                            specialization: { type: 'string', description: 'Agent specialization' },
                            description: { type: 'string', description: 'Agent description' },
                            personality_traits: { type: 'object', description: 'Personality traits as key-value pairs' },
                            capabilities: { type: 'array', items: { type: 'string' }, description: 'List of capabilities' },
                            reporting_manager_id: { type: 'string', description: 'UUID of reporting manager' },
                            system_prompt: { type: 'string', description: 'System prompt for agent' }
                        },
                        required: ['name', 'agent_type', 'specialization']
                    }
                },
                {
                    name: 'get_agent',
                    description: 'Get agent details by ID',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'update_agent',
                    description: 'Update agent properties',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            name: { type: 'string', description: 'Updated agent name' },
                            description: { type: 'string', description: 'Updated description' },
                            personality_traits: { type: 'object', description: 'Updated personality traits' },
                            capabilities: { type: 'array', items: { type: 'string' }, description: 'Updated capabilities' },
                            system_prompt: { type: 'string', description: 'Updated system prompt' },
                            status: { type: 'string', description: 'Updated status' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'list_agents',
                    description: 'List agents with optional filters',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_type: { type: 'string', description: 'Filter by agent type' },
                            status: { type: 'string', description: 'Filter by status' },
                            specialization: { type: 'string', description: 'Filter by specialization' },
                            manager_id: { type: 'string', description: 'Filter by manager UUID' },
                            limit: { type: 'integer', description: 'Maximum number of results' },
                            offset: { type: 'integer', description: 'Pagination offset' }
                        }
                    }
                },
                {
                    name: 'assign_task_to_agent',
                    description: 'Assign a task to an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            task_id: { type: 'string', description: 'Task UUID' },
                            priority: { type: 'integer', description: 'Task priority' },
                            deadline: { type: 'string', description: 'Task deadline (ISO 8601)' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['agent_id', 'task_id']
                    }
                },
                {
                    name: 'recruit_subordinate',
                    description: 'Recruit a subordinate agent for a manager',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            manager_id: { type: 'string', description: 'Manager UUID' },
                            subordinate_spec: { type: 'object', description: 'Subordinate specifications' },
                            task_requirements: { type: 'object', description: 'Task requirements' }
                        },
                        required: ['manager_id', 'subordinate_spec']
                    }
                },
                {
                    name: 'get_agent_subordinates',
                    description: 'Get all subordinates of an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_agent_hierarchy',
                    description: 'Get the hierarchical view of an agent and its network',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'record_agent_interaction',
                    description: 'Record an interaction involving an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            interaction_type: { type: 'string', description: 'Type of interaction' },
                            content: { type: 'string', description: 'Interaction content' },
                            participants: { type: 'array', items: { type: 'string' }, description: 'List of participants' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['agent_id', 'interaction_type', 'content']
                    }
                },
                {
                    name: 'get_agent_performance',
                    description: 'Get agent performance metrics',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            days: { type: 'integer', description: 'Number of days for metrics' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'update_agent_relationship',
                    description: 'Update relationship between two agents',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id_1: { type: 'string', description: 'First agent UUID' },
                            agent_id_2: { type: 'string', description: 'Second agent UUID' },
                            relationship_type: { type: 'string', description: 'Type of relationship' },
                            strength: { type: 'number', description: 'Relationship strength (0-1)' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['agent_id_1', 'agent_id_2', 'relationship_type']
                    }
                },
                {
                    name: 'get_agent_relationships',
                    description: 'Get all relationships for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'deactivate_agent',
                    description: 'Deactivate an agent (soft delete)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'activate_agent',
                    description: 'Activate a deactivated agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_agent_types',
                    description: 'Get available agent types',
                    inputSchema: { type: 'object', properties: {} }
                },
                {
                    name: 'get_agent_statuses',
                    description: 'Get available agent statuses',
                    inputSchema: { type: 'object', properties: {} }
                },
                // Consciousness Tools (10 tools)
                {
                    name: 'initialize_consciousness',
                    description: 'Initialize consciousness system for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            initial_stage: { type: 'string', description: 'Initial development stage' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'update_consciousness_state',
                    description: 'Update agent consciousness state',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            new_state: { type: 'string', description: 'New consciousness state' },
                            state_data: { type: 'object', description: 'Additional state data' }
                        },
                        required: ['agent_id', 'new_state']
                    }
                },
                {
                    name: 'process_experience',
                    description: 'Process a new experience through consciousness layer',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            description: { type: 'string', description: 'Experience description' },
                            participants: { type: 'array', items: { type: 'string' }, description: 'Experience participants' },
                            location: { type: 'string', description: 'Experience location' },
                            outcome: { type: 'string', description: 'Experience outcome' },
                            emotions: { type: 'object', description: 'Emotional responses' },
                            capability_used: { type: 'string', description: 'Capability used in experience' }
                        },
                        required: ['agent_id', 'description']
                    }
                },
                {
                    name: 'initiate_sleep_cycle',
                    description: 'Initiate sleep cycle for agent consciousness',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_consciousness_status',
                    description: 'Get comprehensive consciousness status for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'evolve_personality',
                    description: 'Evolve agent personality based on accumulated experiences',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            experiences: { type: 'array', description: 'List of experiences' }
                        },
                        required: ['agent_id', 'experiences']
                    }
                },
                {
                    name: 'get_development_stages',
                    description: 'Get available consciousness development stages',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_consciousness_states',
                    description: 'Get available consciousness states',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_consciousness_metrics_history',
                    description: 'Get historical consciousness metrics for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'trigger_introspection',
                    description: 'Trigger introspection cycle for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                // Memory Tools (12 tools)
                {
                    name: 'create_memory_entry',
                    description: 'Create a new memory entry for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            memory_type: { type: 'string', description: 'Memory type (episodic, semantic, procedural, working)' },
                            content: { type: 'string', description: 'Memory content' },
                            context: { type: 'object', description: 'Memory context' },
                            emotional_valence: { type: 'number', description: 'Emotional valence (-1 to 1)' },
                            importance_score: { type: 'number', description: 'Importance score (0 to 1)' },
                            tags: { type: 'array', items: { type: 'string' }, description: 'Memory tags' },
                            associations: { type: 'array', items: { type: 'string' }, description: 'Associated memory UUIDs' }
                        },
                        required: ['agent_id', 'memory_type', 'content']
                    }
                },
                {
                    name: 'create_episodic_memory',
                    description: 'Create an episodic memory (specific event with context)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            event_description: { type: 'string', description: 'Event description' },
                            participants: { type: 'array', items: { type: 'string' }, description: 'Event participants' },
                            location: { type: 'string', description: 'Event location' },
                            outcome: { type: 'string', description: 'Event outcome' },
                            emotions: { type: 'object', description: 'Emotional responses' },
                            importance_score: { type: 'number', description: 'Importance score (0 to 1)' }
                        },
                        required: ['agent_id', 'event_description']
                    }
                },
                {
                    name: 'create_semantic_memory',
                    description: 'Create a semantic memory (general knowledge)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            knowledge: { type: 'string', description: 'Knowledge content' },
                            domain: { type: 'string', description: 'Knowledge domain' },
                            confidence_level: { type: 'number', description: 'Confidence level (0 to 1)' },
                            source: { type: 'string', description: 'Knowledge source' },
                            related_concepts: { type: 'array', items: { type: 'string' }, description: 'Related concepts' }
                        },
                        required: ['agent_id', 'knowledge', 'domain']
                    }
                },
                {
                    name: 'create_procedural_memory',
                    description: 'Create a procedural memory (skill or procedure)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            skill_name: { type: 'string', description: 'Skill name' },
                            procedure_steps: { type: 'array', items: { type: 'string' }, description: 'Procedure steps' },
                            success_rate: { type: 'number', description: 'Success rate (0 to 1)' },
                            conditions: { type: 'array', items: { type: 'string' }, description: 'Required conditions' },
                            prerequisites: { type: 'array', items: { type: 'string' }, description: 'Prerequisites' }
                        },
                        required: ['agent_id', 'skill_name', 'procedure_steps']
                    }
                },
                {
                    name: 'retrieve_memories',
                    description: 'Retrieve memories based on various criteria',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            memory_type: { type: 'string', description: 'Memory type filter' },
                            context_keywords: { type: 'array', items: { type: 'string' }, description: 'Context keywords' },
                            similarity_threshold: { type: 'number', description: 'Similarity threshold (0 to 1)' },
                            limit: { type: 'integer', description: 'Maximum results' },
                            time_range_start: { type: 'string', description: 'Start time (ISO 8601)' },
                            time_range_end: { type: 'string', description: 'End time (ISO 8601)' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_working_memory',
                    description: 'Get agent\'s current working memory',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'consolidate_memories',
                    description: 'Consolidate agent memories during sleep or background processing',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' },
                            consolidation_type: { type: 'string', description: 'Consolidation type' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'update_memory_importance',
                    description: 'Update the importance score of a memory',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            memory_id: { type: 'string', description: 'Memory UUID' },
                            new_importance: { type: 'number', description: 'New importance score (0 to 1)' },
                            reason: { type: 'string', description: 'Reason for importance update' }
                        },
                        required: ['memory_id', 'new_importance']
                    }
                },
                {
                    name: 'create_memory_association',
                    description: 'Create an association between two memories',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            memory_id_1: { type: 'string', description: 'First memory UUID' },
                            memory_id_2: { type: 'string', description: 'Second memory UUID' },
                            association_type: { type: 'string', description: 'Association type' },
                            strength: { type: 'number', description: 'Association strength (0 to 1)' }
                        },
                        required: ['memory_id_1', 'memory_id_2']
                    }
                },
                {
                    name: 'get_memory_statistics',
                    description: 'Get comprehensive memory statistics for an agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_id: { type: 'string', description: 'Agent UUID' }
                        },
                        required: ['agent_id']
                    }
                },
                {
                    name: 'get_memory_types',
                    description: 'Get available memory types',
                    inputSchema: { type: 'object', properties: {} }
                },
                {
                    name: 'delete_memory',
                    description: 'Delete a memory entry',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            memory_id: { type: 'string', description: 'Memory UUID' }
                        },
                        required: ['memory_id']
                    }
                },
                // Orchestration Tools (15 tools)
                {
                    name: 'create_workflow',
                    description: 'Create a new complex workflow',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            name: { type: 'string', description: 'Workflow name' },
                            description: { type: 'string', description: 'Workflow description' },
                            complexity: { type: 'string', description: 'Workflow complexity level' },
                            required_capabilities: { type: 'array', items: { type: 'string' }, description: 'Required capabilities' },
                            priority: { type: 'string', description: 'Workflow priority' },
                            deadline: { type: 'string', description: 'Workflow deadline (ISO 8601)' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['name', 'description']
                    }
                },
                {
                    name: 'execute_workflow',
                    description: 'Execute a complex workflow through agent hierarchy',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            workflow_id: { type: 'string', description: 'Workflow UUID' },
                            execution_mode: { type: 'string', description: 'Execution mode (parallel, sequential, adaptive)' },
                            max_agents: { type: 'integer', description: 'Maximum number of agents' },
                            timeout_minutes: { type: 'integer', description: 'Timeout in minutes' }
                        },
                        required: ['workflow_id']
                    }
                },
                {
                    name: 'delegate_task',
                    description: 'Delegate a task to another agent',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            task_id: { type: 'string', description: 'Task UUID' },
                            target_agent_id: { type: 'string', description: 'Target agent UUID' },
                            delegation_reason: { type: 'string', description: 'Reason for delegation' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['task_id', 'target_agent_id']
                    }
                },
                {
                    name: 'decompose_task',
                    description: 'Decompose a complex task into subtasks',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            task_id: { type: 'string', description: 'Task UUID' }
                        },
                        required: ['task_id']
                    }
                },
                {
                    name: 'create_subtask',
                    description: 'Create a subtask under a parent task',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            parent_task_id: { type: 'string', description: 'Parent task UUID' },
                            subtask_name: { type: 'string', description: 'Subtask name' },
                            subtask_description: { type: 'string', description: 'Subtask description' },
                            assigned_agent_id: { type: 'string', description: 'Assigned agent UUID' },
                            priority: { type: 'string', description: 'Subtask priority' },
                            dependencies: { type: 'array', items: { type: 'string' }, description: 'Dependency UUIDs' }
                        },
                        required: ['parent_task_id', 'subtask_name', 'subtask_description']
                    }
                },
                {
                    name: 'assign_agents_to_task',
                    description: 'Assign optimal agents to a task',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            task_id: { type: 'string', description: 'Task UUID' },
                            agent_specifications: { type: 'array', description: 'Agent specifications' },
                            assignment_strategy: { type: 'string', description: 'Assignment strategy' }
                        },
                        required: ['task_id', 'agent_specifications']
                    }
                },
                {
                    name: 'update_task_progress',
                    description: 'Update task progress and status',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            task_id: { type: 'string', description: 'Task UUID' },
                            progress_percentage: { type: 'number', description: 'Progress percentage (0 to 100)' },
                            status: { type: 'string', description: 'Task status' },
                            notes: { type: 'string', description: 'Progress notes' },
                            context: { type: 'object', description: 'Additional context' }
                        },
                        required: ['task_id', 'progress_percentage']
                    }
                },
                {
                    name: 'get_workflow_status',
                    description: 'Get comprehensive workflow status',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            workflow_id: { type: 'string', description: 'Workflow UUID' }
                        },
                        required: ['workflow_id']
                    }
                },
                {
                    name: 'get_task_hierarchy',
                    description: 'Get task hierarchy including subtasks and dependencies',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            task_id: { type: 'string', description: 'Task UUID' }
                        },
                        required: ['task_id']
                    }
                },
                {
                    name: 'optimize_workflow',
                    description: 'Optimize workflow execution strategy',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            workflow_id: { type: 'string', description: 'Workflow UUID' },
                            optimization_goals: { type: 'array', items: { type: 'string' }, description: 'Optimization goals' },
                            constraints: { type: 'object', description: 'Optimization constraints' }
                        },
                        required: ['workflow_id', 'optimization_goals']
                    }
                },
                {
                    name: 'get_orchestration_analytics',
                    description: 'Get orchestration performance analytics',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            time_period_days: { type: 'integer', description: 'Time period in days' }
                        }
                    }
                },
                {
                    name: 'get_agent_workload_distribution',
                    description: 'Get current workload distribution across agents',
                    inputSchema: { type: 'object', properties: {} }
                },
                {
                    name: 'synchronize_agent_coordination',
                    description: 'Synchronize coordination between multiple agents',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            agent_ids: { type: 'array', items: { type: 'string' }, description: 'Agent UUIDs' },
                            coordination_strategy: { type: 'string', description: 'Coordination strategy' }
                        },
                        required: ['agent_ids']
                    }
                },
                {
                    name: 'cancel_workflow',
                    description: 'Cancel a running workflow',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            workflow_id: { type: 'string', description: 'Workflow UUID' },
                            reason: { type: 'string', description: 'Cancellation reason' }
                        },
                        required: ['workflow_id']
                    }
                },
                {
                    name: 'get_orchestration_strategies',
                    description: 'Get available orchestration strategies',
                    inputSchema: { type: 'object', properties: {} }
                }
            ]
        }));
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            try {
                let result;
                // Ensure args is defined
                const safeArgs = args || {};
                // Agent Management Tools
                switch (name) {
                    case 'create_agent':
                        result = await this.apiClient.makeRequest('POST', '/api/agents/create', safeArgs);
                        break;
                    case 'get_agent':
                        result = await this.apiClient.makeRequest('GET', `/api/agents/${safeArgs.agent_id}`);
                        break;
                    case 'update_agent':
                        const agentId = safeArgs.agent_id;
                        const updateData = { ...safeArgs };
                        delete updateData.agent_id;
                        result = await this.apiClient.makeRequest('PATCH', `/api/agents/${agentId}`, updateData);
                        break;
                    case 'list_agents':
                        result = await this.apiClient.makeRequest('GET', '/api/agents', null, safeArgs);
                        break;
                    case 'assign_task_to_agent':
                        const agentIdForTask = safeArgs.agent_id;
                        const taskData = { ...safeArgs };
                        delete taskData.agent_id;
                        result = await this.apiClient.makeRequest('POST', `/api/agents/${agentIdForTask}/assign-task`, taskData);
                        break;
                    case 'recruit_subordinate':
                        result = await this.apiClient.makeRequest('POST', '/api/agents/recruit-subordinate', safeArgs);
                        break;
                    case 'get_agent_subordinates':
                        result = await this.apiClient.makeRequest('GET', `/api/agents/${safeArgs.agent_id}/subordinates`);
                        break;
                    case 'get_agent_hierarchy':
                        result = await this.apiClient.makeRequest('GET', `/api/agents/${safeArgs.agent_id}/hierarchy`);
                        break;
                    case 'record_agent_interaction':
                        result = await this.apiClient.makeRequest('POST', '/api/agents/interaction', safeArgs);
                        break;
                    case 'get_agent_performance':
                        const perfAgentId = safeArgs.agent_id;
                        const perfParams = { ...safeArgs };
                        delete perfParams.agent_id;
                        result = await this.apiClient.makeRequest('GET', `/api/agents/${perfAgentId}/performance`, null, perfParams);
                        break;
                    case 'update_agent_relationship':
                        result = await this.apiClient.makeRequest('POST', '/api/agents/relationship', safeArgs);
                        break;
                    case 'get_agent_relationships':
                        result = await this.apiClient.makeRequest('GET', `/api/agents/${safeArgs.agent_id}/relationships`);
                        break;
                    case 'deactivate_agent':
                        result = await this.apiClient.makeRequest('DELETE', `/api/agents/${safeArgs.agent_id}`);
                        break;
                    case 'activate_agent':
                        result = await this.apiClient.makeRequest('POST', `/api/agents/${safeArgs.agent_id}/activate`);
                        break;
                    case 'get_agent_types':
                        result = await this.apiClient.makeRequest('GET', '/api/agents/types');
                        break;
                    case 'get_agent_statuses':
                        result = await this.apiClient.makeRequest('GET', '/api/agents/statuses');
                        break;
                    // Consciousness Tools
                    case 'initialize_consciousness':
                        result = await this.apiClient.makeRequest('POST', '/api/consciousness/initialize', safeArgs);
                        break;
                    case 'update_consciousness_state':
                        const consAgentId = safeArgs.agent_id;
                        const consStateData = { ...safeArgs };
                        delete consStateData.agent_id;
                        result = await this.apiClient.makeRequest('PATCH', `/api/consciousness/${consAgentId}/state`, consStateData);
                        break;
                    case 'process_experience':
                        result = await this.apiClient.makeRequest('POST', '/api/consciousness/experience', safeArgs);
                        break;
                    case 'initiate_sleep_cycle':
                        result = await this.apiClient.makeRequest('POST', `/api/consciousness/${safeArgs.agent_id}/sleep`);
                        break;
                    case 'get_consciousness_status':
                        result = await this.apiClient.makeRequest('GET', `/api/consciousness/${safeArgs.agent_id}/status`);
                        break;
                    case 'evolve_personality':
                        result = await this.apiClient.makeRequest('POST', '/api/consciousness/personality/evolve', safeArgs);
                        break;
                    case 'get_development_stages':
                        result = await this.apiClient.makeRequest('GET', `/api/consciousness/${safeArgs.agent_id}/development-stages`);
                        break;
                    case 'get_consciousness_states':
                        result = await this.apiClient.makeRequest('GET', `/api/consciousness/${safeArgs.agent_id}/consciousness-states`);
                        break;
                    case 'get_consciousness_metrics_history':
                        result = await this.apiClient.makeRequest('GET', `/api/consciousness/${safeArgs.agent_id}/metrics/history`);
                        break;
                    case 'trigger_introspection':
                        result = await this.apiClient.makeRequest('POST', `/api/consciousness/${safeArgs.agent_id}/introspection`);
                        break;
                    // Memory Tools
                    case 'create_memory_entry':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/create', safeArgs);
                        break;
                    case 'create_episodic_memory':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/episodic', safeArgs);
                        break;
                    case 'create_semantic_memory':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/semantic', safeArgs);
                        break;
                    case 'create_procedural_memory':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/procedural', safeArgs);
                        break;
                    case 'retrieve_memories':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/retrieve', safeArgs);
                        break;
                    case 'get_working_memory':
                        result = await this.apiClient.makeRequest('GET', `/api/memory/${safeArgs.agent_id}/working-memory`);
                        break;
                    case 'consolidate_memories':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/consolidate', safeArgs);
                        break;
                    case 'update_memory_importance':
                        result = await this.apiClient.makeRequest('PATCH', '/api/memory/importance', safeArgs);
                        break;
                    case 'create_memory_association':
                        result = await this.apiClient.makeRequest('POST', '/api/memory/associate', safeArgs);
                        break;
                    case 'get_memory_statistics':
                        result = await this.apiClient.makeRequest('GET', `/api/memory/${safeArgs.agent_id}/statistics`);
                        break;
                    case 'get_memory_types':
                        result = await this.apiClient.makeRequest('GET', '/api/memory/types');
                        break;
                    case 'delete_memory':
                        result = await this.apiClient.makeRequest('DELETE', `/api/memory/${safeArgs.memory_id}`);
                        break;
                    // Orchestration Tools
                    case 'create_workflow':
                        result = await this.apiClient.makeRequest('POST', '/api/orchestration/workflow/create', safeArgs);
                        break;
                    case 'execute_workflow':
                        const execWorkflowId = safeArgs.workflow_id;
                        const execData = { ...safeArgs };
                        delete execData.workflow_id;
                        result = await this.apiClient.makeRequest('POST', `/api/orchestration/workflow/${execWorkflowId}/execute`, execData);
                        break;
                    case 'delegate_task':
                        result = await this.apiClient.makeRequest('POST', '/api/orchestration/task/delegate', safeArgs);
                        break;
                    case 'decompose_task':
                        result = await this.apiClient.makeRequest('POST', `/api/orchestration/task/decompose`, null, { task_id: safeArgs.task_id });
                        break;
                    case 'create_subtask':
                        result = await this.apiClient.makeRequest('POST', '/api/orchestration/subtask/create', safeArgs);
                        break;
                    case 'assign_agents_to_task':
                        result = await this.apiClient.makeRequest('POST', '/api/orchestration/agents/assign', safeArgs);
                        break;
                    case 'update_task_progress':
                        const progressTaskId = safeArgs.task_id;
                        const progressData = { ...safeArgs };
                        delete progressData.task_id;
                        result = await this.apiClient.makeRequest('PATCH', `/api/orchestration/task/${progressTaskId}/progress`, progressData);
                        break;
                    case 'get_workflow_status':
                        result = await this.apiClient.makeRequest('GET', `/api/orchestration/workflow/${safeArgs.workflow_id}/status`);
                        break;
                    case 'get_task_hierarchy':
                        result = await this.apiClient.makeRequest('GET', `/api/orchestration/task/${safeArgs.task_id}/hierarchy`);
                        break;
                    case 'optimize_workflow':
                        const optWorkflowId = safeArgs.workflow_id;
                        const optData = { ...safeArgs };
                        delete optData.workflow_id;
                        result = await this.apiClient.makeRequest('POST', `/api/orchestration/workflow/${optWorkflowId}/optimize`, optData);
                        break;
                    case 'get_orchestration_analytics':
                        result = await this.apiClient.makeRequest('GET', '/api/orchestration/analytics/performance', null, safeArgs);
                        break;
                    case 'get_agent_workload_distribution':
                        result = await this.apiClient.makeRequest('GET', '/api/orchestration/agents/workload');
                        break;
                    case 'synchronize_agent_coordination':
                        result = await this.apiClient.makeRequest('POST', '/api/orchestration/coordination/sync', safeArgs);
                        break;
                    case 'cancel_workflow':
                        const cancelWorkflowId = safeArgs.workflow_id;
                        const cancelData = { ...safeArgs };
                        delete cancelData.workflow_id;
                        result = await this.apiClient.makeRequest('DELETE', `/api/orchestration/workflow/${cancelWorkflowId}`, null, cancelData);
                        break;
                    case 'get_orchestration_strategies':
                        result = await this.apiClient.makeRequest('GET', '/api/orchestration/strategies');
                        break;
                    default:
                        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify(result, null, 2),
                        },
                    ],
                };
            }
            catch (error) {
                if (error instanceof McpError) {
                    throw error;
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                        },
                    ],
                    isError: true,
                };
            }
        });
    }
    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Zero Vector 4 MCP server running on stdio');
    }
}
const server = new ZeroVector4Server();
server.run().catch(console.error);
