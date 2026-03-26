"""

hypergraph.py - Hypergraph class for sparse incidence matrix

Matrix Design:
    rows = entities (agents + meta-agents), cols = meta-agents
    matrix[i,j] = 1.0 means entity i is member of meta-agent j
    
    This supports multi-level adaptive networks:
    - Agents can be members of meta-agents
    - Meta-agents can be members of other meta-agents (hierarchical)
    
    Uses scipy.sparse.lil_matrix for efficient insertion/deletion.

"""

from scipy.sparse import lil_matrix
from typing import Any, List, Dict


class Hypergraph:
    """Sparse matrix managing membership in meta-agents (agents and meta-agents both as rows)."""
    
    def __init__(self):
        """Initialize empty sparse matrix and entity mappings."""
        self.matrix = lil_matrix((0, 0), dtype=float)
        self.entity_to_row = {}           # {entity (agent or meta-agent) -> row index}
        self.row_to_entity = {}           # {row index -> entity}
        self.entity_type = {}             # {entity -> "agent" | "meta-agent"}
        self.next_entity_idx = 0          # Counter for next row index
        
        self.metaagent_id_to_name = {}   # {meta_agent_id -> name}
        self.metaagent_name_to_id = {}   # {name -> meta_agent_id}
        
        # Role tracking: {meta_agent_id: {role: set(entities)}}
        self.relationships = {}           # Track which entities have which roles
        
        # Active/Dormant state tracking: {meta_agent_id: {entity: "active" | "dormant"}}
        self.member_states = {}
        
    
    def register_entity(self, entity: Any, entity_type: str = "agent") -> None:
        """
        Assign entity (agent or meta-agent) a row in the matrix.
        
        Args:
            entity: Agent or MetaAgent to register
            entity_type: "agent" or "meta-agent"
        """
        if entity in self.entity_to_row:
            return  # Already registered
        
        entity_idx = self.next_entity_idx
        self.entity_to_row[entity] = entity_idx
        self.row_to_entity[entity_idx] = entity
        self.entity_type[entity] = entity_type
        self.next_entity_idx += 1
        
        # Expand matrix: add new row
        new_rows = self.matrix.shape[0] + 1
        self.matrix.resize((new_rows, self.matrix.shape[1]))
    
    def register_meta_agent_column(self, meta_agent_id: int) -> None:
        """
        Ensure a column exists for a meta-agent.
        
        Args:
            meta_agent_id: The ID of the meta-agent to ensure a column for.
        """
        if meta_agent_id >= self.matrix.shape[1]:
            self.matrix.resize((self.matrix.shape[0], meta_agent_id + 1))
    
    
    def add_member(self, entity: Any, meta_agent_id: int, entity_type: str = "agent", role: str = "member") -> None:
        """
        Set matrix[entity_idx, meta_agent_id] = 1.0 and track the role.
        
        Args:
            entity: Agent or MetaAgent to add
            meta_agent_id: Column index (which meta-agent)
            entity_type: "agent" or "meta-agent"
            role: Role of entity in this meta-agent (default: "member")
        """
        # Register entity if not already registered
        if entity not in self.entity_to_row:
            self.register_entity(entity, entity_type=entity_type)
        
        entity_idx = self.entity_to_row[entity]
        
        # Set membership in matrix
        self.matrix[entity_idx, meta_agent_id] = 1.0
        
        # Track role: {meta_agent_id: {role: set(entities)}}
        if meta_agent_id not in self.relationships:
            self.relationships[meta_agent_id] = {}
        
        if role not in self.relationships[meta_agent_id]:
            self.relationships[meta_agent_id][role] = set()
        
        self.relationships[meta_agent_id][role].add(entity)
        
        # Set default state to "active"
        if meta_agent_id not in self.member_states:
            self.member_states[meta_agent_id] = {}
        self.member_states[meta_agent_id][entity] = "active"
    
    def remove_member(self, entity: Any, meta_agent_id: int) -> None:
        """Delete matrix[entity_idx, meta_agent_id] and clean up role tracking"""
        if entity not in self.entity_to_row:
            return  # Entity not registered, nothing to remove
        
        entity_idx = self.entity_to_row[entity]
        
        # Check if indices are valid
        if meta_agent_id < self.matrix.shape[1]:
            self.matrix[entity_idx, meta_agent_id] = 0
        
        # Clean up role tracking
        if meta_agent_id in self.relationships:
            for role_set in self.relationships[meta_agent_id].values():
                if entity in role_set:
                    role_set.discard(entity)
        
        # Clean up state tracking
        if meta_agent_id in self.member_states and entity in self.member_states[meta_agent_id]:
            del self.member_states[meta_agent_id][entity]
    
    def get_memberships(self, entity: Any) -> List[int]:
        """Return non-zero column indices in entity's row."""
        if entity not in self.entity_to_row:
            return []
        
        entity_idx = self.entity_to_row[entity]
        
        # Get entity's row (sparse)
        row = self.matrix.getrow(entity_idx)
        
        # Get non-zero column indices
        col_indices = row.nonzero()[1]
        
        return col_indices.tolist()
    
    def get_role(self, entity: Any, meta_agent_id: int) -> str:
        """
        Get the role of an entity in a specific meta-agent.
        
        Args:
            entity: Agent or MetaAgent
            meta_agent_id: Which meta-agent
        
        Returns:
            Role string (e.g., "leader", "member", "observer") or None if not member
        """
        if meta_agent_id not in self.relationships:
            return None
        
        for role, entities in self.relationships[meta_agent_id].items():
            if entity in entities:
                return role
        
        return None
    
    def set_member_state(self, entity: Any, meta_agent_id: int, state: str) -> None:
        """
        Set the state of a member in a specific meta-agent.
        
        Args:
            entity: Agent or MetaAgent
            meta_agent_id: Which meta-agent
            state: "active" or "dormant"
        """
        if meta_agent_id in self.member_states:
            self.member_states[meta_agent_id][entity] = state
            
    def get_member_state(self, entity: Any, meta_agent_id: int) -> str:
        """
        Get the state of a member in a specific meta-agent.
        
        Args:
            entity: Agent or MetaAgent
            meta_agent_id: Which meta-agent
        
        Returns:
            State string ("active" or "dormant") or None if not member
        """
        if meta_agent_id in self.member_states:
            return self.member_states[meta_agent_id].get(entity)
        return None

    def get_members(self, meta_agent_id: int, entity_type: str = None, role: str = None, state: str = None) -> List[Any]:
        """
        Return entities in this meta-agent column, optionally filtered by type, role, and/or state.
        
        Args:
            meta_agent_id: Column index (which meta-agent)
            entity_type: Filter by type ("agent", "meta-agent", or None for all)
            role: Filter by role ("leader", "member", "observer", or None for all roles)
            state: Filter by state ("active", "dormant", or None for all states)
        
        Returns:
            List of entities (agents or meta-agents or both)
        """
        # Start with all members from the matrix
        if meta_agent_id >= self.matrix.shape[1]:
            return []
        col = self.matrix.getcol(meta_agent_id)
        row_indices = col.nonzero()[0]
        entities = {self.row_to_entity[idx] for idx in row_indices}
        
        # Filter by role
        if role is not None:
            if meta_agent_id in self.relationships:
                role_entities = self.relationships[meta_agent_id].get(role, set())
                entities &= role_entities
        
        # Filter by state
        if state is not None:
            if meta_agent_id in self.member_states:
                state_entities = {e for e, s in self.member_states[meta_agent_id].items() if s == state}
                entities &= state_entities
        
        # Filter by entity type
        if entity_type is not None:
            type_entities = {e for e in entities if self.entity_type.get(e) == entity_type}
            entities &= type_entities
            
        return list(entities)
    
    def get_agents(self, meta_agent_id: int) -> List[Any]:
        """Convenience method: return only agents (not meta-agents) in this meta-agent."""
        return self.get_members(meta_agent_id, entity_type="agent")
    
    def get_meta_agents(self, meta_agent_id: int) -> List[Any]:
        """Convenience method: return only meta-agents (not agents) in this meta-agent."""
        return self.get_members(meta_agent_id, entity_type="meta-agent")
    
    
