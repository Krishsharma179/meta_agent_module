"""

hypergraph.py - Hypergraph class for sparse incidence matrix

Matrix Design:
    rows = agents, cols = meta-agents
    matrix[i,j] = 1.0 means agent i is member of meta-agent j
    
    Uses scipy.sparse.lil_matrix for efficient insertion/deletion.

"""

from scipy.sparse import lil_matrix
from typing import Any, List


class Hypergraph:
    """Sparse matrix managing agent membership in meta-agents."""
    
    def __init__(self):
        """Initialize empty sparse matrix and agent mappings."""
        self.matrix = lil_matrix((0, 0), dtype=float)
        self.agent_to_row = {}           # {agent -> row index}
        self.row_to_agent = {}           # {row index -> agent}
        self.next_agent_idx = 0          # Counter for next row index
        
        self.metaagent_id_to_name = {}   # {meta_agent_id -> name}
        self.metaagent_name_to_id = {}   # {name -> meta_agent_id}
        
    
    def register_agent(self, agent: Any) -> None:
        """Assign agent a row in the matrix."""
        if agent in self.agent_to_row:
            return  # Already registered
        
        agent_idx = self.next_agent_idx
        self.agent_to_row[agent] = agent_idx
        self.row_to_agent[agent_idx] = agent
        self.next_agent_idx += 1
        
        # Expand matrix: add new row
        new_rows = self.matrix.shape[0] + 1
        self.matrix.resize((new_rows, self.matrix.shape[1]))
        
    
    def add_member(self, agent: Any, meta_agent_id: int) -> None:
        """Set matrix[agent_idx, meta_agent_id] = 1.0"""
        # Register agent if not already registered
        if agent not in self.agent_to_row:
            self.register_agent(agent)
        
        agent_idx = self.agent_to_row[agent]
        
        # Expand matrix columns if needed
        if meta_agent_id >= self.matrix.shape[1]:
            self.matrix.resize((self.matrix.shape[0], meta_agent_id + 1))
        
        # Set membership
        self.matrix[agent_idx, meta_agent_id] = 1.0
    
    def remove_member(self, agent: Any, meta_agent_id: int) -> None:
        """Delete matrix[agent_idx, meta_agent_id]"""
        if agent not in self.agent_to_row:
            return  # Agent not registered, nothing to remove
        
        agent_idx = self.agent_to_row[agent]
        
        # Check if indices are valid
        if meta_agent_id < self.matrix.shape[1]:
            self.matrix[agent_idx, meta_agent_id] = 0
    
    def get_memberships(self, agent: Any) -> List[int]:
        """Return non-zero column indices in agent's row."""
        if agent not in self.agent_to_row:
            return []
        
        agent_idx = self.agent_to_row[agent]
        
        # Get agent's row (sparse)
        row = self.matrix.getrow(agent_idx)
        
        # Get non-zero column indices
        col_indices = row.nonzero()[1]
        
        return col_indices.tolist()
    
    def get_members(self, meta_agent_id: int) -> List[Any]:
        """Return agents (from non-zero rows) in this meta-agent column."""
        if meta_agent_id >= self.matrix.shape[1]:
            return []
        
        # Get column (sparse)
        col = self.matrix.getcol(meta_agent_id)
        
        # Get non-zero row indices
        row_indices = col.nonzero()[0]
        
        # Map row indices back to agents
        agents = [self.row_to_agent[idx] for idx in row_indices]
        
        return agents
    
    
