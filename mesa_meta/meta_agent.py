"""

meta_agent.py - MetaAgent and Agent classes for Meta-Agent module

Overview:
    This module defines two core classes:
    
    Agent: A simple wrapper around a unique identifier. Agents are the atomic
    units that can join/leave MetaAgent groups.
    
    MetaAgent: A group that agents can join/leave according to a Policy.
    MetaAgent stores membership in a sparse incidence matrix (not a set).
    Membership changes go through a decision pipeline before being applied.

Agent:
    Represents an individual entity in the simulation.
    
    Parameters:
        unique_id (int or str): Unique identifier for the agent
    
    Attributes:
        unique_id: Immutable identifier
    
    Usage:
        agent = Agent(1)
        agent2 = Agent("agent_002")

MetaAgent:
    A group governed by a Policy. Agents can join/leave based on the policy rules.
    
    Parameters:
        policy (Policy): Configuration for join/leave/exclusivity rules
        hypergraph: The sparse matrix backend that stores membership
        meta_agent_id (int or str): Unique identifier for this meta-agent
    
    Core Methods:
        add(agent) -> bool:
            Attempt to add agent to this group.
            Pipeline: agent decision → policy check → exclusivity check
            Returns True if successful, False if rejected.
        
        remove(agent) -> bool:
            Attempt to remove agent from this group.
            Pipeline: agent decision → policy check
            Returns True if successful, False if rejected.
        
        members (property):
            Returns list of agents currently in this group.
            Reads directly from sparse matrix, not a set.
    
    Approval Methods (override in subclass for custom logic):
        assess_join(agent) -> bool:
            Called only if policy.join_rule == "approval"
            Return True to approve, False to reject.
        
        assess_leave(agent) -> bool:
            Called only if policy.leave_rule == "approval"
            Return True to approve, False to reject.

Matrix Design:
    rows = agents (indexed 0..N-1)
    cols = meta-agents (indexed 0..M-1)
    matrix[i,j] = 1.0 means agent i is member of meta-agent j
    matrix[i,j] = 0.0 (or missing) means agent i is NOT member of meta-agent j

Usage:
    from mesa_meta.policy import Policy
    from mesa_meta.meta_agent import Agent, MetaAgent
    from mesa_meta.hypergraph import Hypergraph
    
    # Create policy: free to join, free to leave, multiple membership
    policy = Policy(
        join_rule="free",
        leave_rule="free",
        exclusivity="multiple",
        authority="friends"
    )
    
    # Create hypergraph and meta-agent
    hg = Hypergraph()
    friends_group = MetaAgent(policy, hg, meta_agent_id=0)
    
    # Create agents and add to group
    agent1 = Agent(1)
    agent2 = Agent(2)
    
    friends_group.add(agent1)  # True
    friends_group.add(agent2)  # True
    
    # Check members
    print(friends_group.members)  # [agent1, agent2]
    
    # Remove agent
    friends_group.remove(agent1)  # True

Notes:
    - MetaAgent does NOT store membership in a set; uses sparse matrix only
    - Policy is immutable configuration; MetaAgent is the behavior
    - Exclusivity is checked at add() time based on matrix state
    - Approval functions (assess_join, assess_leave) must return bool

"""

try:
    from .policy import Policy
except ImportError:  # Support running as a script from within mesa_meta/
    from policy import Policy
from typing import Any, Iterable

class Agent:
    """
    Atomic unit that can join/leave meta-agent groups.
    """
    def __init__(self, unique_id):
        self.unique_id = unique_id
    
    def on_join(self,meta_agent):
        pass

    def on_leave(self,meat_agent):
        pass



    def __repr__(self):
        return f"Agent({self.unique_id})"
    
    def __eq__(self, other):
        if isinstance(other, Agent):
            return self.unique_id == other.unique_id
        return False
    
    def __hash__(self):
        return hash(self.unique_id)
    
    def on_join(self, meta_agent):
        """Called when agent successfully joins a meta-agent. Override to customize."""
        pass
    
    def on_leave(self, meta_agent):
        """Called when agent successfully leaves a meta-agent. Override to customize."""
        pass


class MetaAgent:
    """
    A group governed by a Policy. Agents/MetaAgents join/leave through a decision pipeline.
    Membership stored in sparse matrix (not a set).
    
    Now supports hierarchical nesting: MetaAgent can contain other MetaAgents.
    """
    def __init__(self, policy: Policy, hypergraph, meta_agent_id, join_approval_func=None, leave_approval_func=None):
        self.policy = policy
        self.hypergraph = hypergraph
        self.meta_agent_id = meta_agent_id
        self.attributes = {}  # Store meta-agent attributes
        self.join_approval_func = join_approval_func
        self.leave_approval_func = leave_approval_func
        
        
        # Eagerly register this meta-agent's column in the hypergraph
        self.hypergraph.register_meta_agent_column(self.meta_agent_id)
        
        # This meta-agent is NOT registered as an entity (row) yet.
        # It will only get a row if it is added as a member to another meta-agent.
        
        # Hierarchical support
        self.parent = None  # Parent meta-agent (if this is nested)
        self.children = []  # Child meta-agents (if this contains other meta-agents)
        
        # Note: This meta-agent is NOT registered in hypergraph yet
        # It only gets a row when it's added as member of another meta-agent
        # (See add() method for registration logic)
    
    def add_attribute(self, meta_attributes: dict) -> None:
        """
        Add attributes to this meta-agent from a dictionary.
        
        Args:
            meta_attributes: Dictionary of {key: value} pairs to set as attributes
        
        Example:
            meta_agent.add_attribute({"rank": 5, "tier": "elite"})
        """
        if meta_attributes is not None:
            for key, value in meta_attributes.items():
                setattr(self, key, value)
                self.attributes[key] = value
    
    
    
    def on_member_join(self, agent):
        """will be overridden by the user Called when an agent successfully joins this meta-agent. Override to customize."""
        pass
    
    def on_member_leave(self, agent):
        """Will be overidden by the user Called when an agent successfully leaves this meta-agent. Override to customize."""
        pass    
    
    def assess_join(self, agent: Agent) -> bool:
        """
        This is the helper function for add method to assess that join function is True or false,
        or use the function passed in at initialization or in the policy.
        """
        if self.join_approval_func is not None:
            return self.join_approval_func(agent)
        
        
    
    def assess_leave(self, agent: Agent) -> bool:
        """
        This is the helper function of remove method it is to assess if the leave func is True/false
        """
        # First check if function was passed directly to MetaAgent
        if self.leave_approval_func is not None:
            return self.leave_approval_func(agent)
            
        
    
    def add(self, entity, role: str = "member",wants_to_join:callable=None) :
        """
        Attempt to add entity (Agent or MetaAgent) to this group with a specific role.
        
        Pipeline:
            1. Entity check (wants_to_join if Agent)
            2. Policy check (join_rule)
            3. Exclusivity check
            4. Register meta-agent as row if needed
            5. Add to matrix with role
            6. Set parent if entity is MetaAgent
        
        Args:
            entity: Agent or MetaAgent to add
            role: Role of entity in this group (default: "member")
        
        Returns:
            True if added, False if rejected
        """
        # Determine entity type
        is_meta_agent = isinstance(entity, MetaAgent)
        entity_type = "meta-agent" if is_meta_agent else "agent"
        
        # Gate 0: Check if agent wants to join (only for agents)
        if not is_meta_agent and wants_to_join is not None:
            if not wants_to_join(self):
                return False
                
        # Gate 1: Policy check (join_rule) - approval logic only applies to agents
        if not is_meta_agent and self.policy.join_rule == "approval":
            if not self.assess_join(entity):
                return False  # Approval rejected
        
        # Gate 2: Exclusivity check
        if self.policy.exclusivity == "exclusive":
            existing_memberships = self.hypergraph.get_memberships(entity)
            if len(existing_memberships) > 0:
                return False  # Entity already in another exclusive group
        
        # Gate 3: Register meta-agent as row only when it becomes a member
        # (Agents are registered automatically when first added)
        if is_meta_agent and entity not in self.hypergraph.entity_to_row:
            self.hypergraph.register_entity(entity, entity_type="meta-agent")
        
        # Gate 4: Add to hypergraph WITH ROLE
        self.hypergraph.add_member(entity, self.meta_agent_id, entity_type=entity_type, role=role)
        
        # Gate 5: If entity is a MetaAgent, set parent and track as child
        if is_meta_agent:
            entity.parent = self
            self.children.append(entity)
        
        # Trigger callbacks for bidirectional influence
        if not is_meta_agent and hasattr(entity, "on_join"):
            entity.on_join(self)
        self.on_member_join(entity)
        
        return True        

            
    
    def remove(self, entity,wants_to_leave:callable=None) -> bool:
        """
        Attempt to remove entity (Agent or MetaAgent) from this group.
        
        Pipeline:
            1. Policy check (leave_rule)
            2. Remove from matrix
            3. Clear parent if entity is MetaAgent
        
        Args:
            entity: Agent or MetaAgent to remove
        
        Returns:
            True if removed, False if rejected
        """
        is_meta_agent = isinstance(entity, MetaAgent)
        #Gate 0 :wants to leave
        if not is_meta_agent and wants_to_leave is not None:
            if not wants_to_leave(self):
                return False 
        
        # Gate 1: Policy check (leave_rule)
        if self.policy.leave_rule == "approval":
            if not self.assess_leave(entity):
                return False  # Approval rejected
        
        # Gate 2: Remove from hypergraph
        self.hypergraph.remove_member(entity, self.meta_agent_id)
        
        # Gate 3: If entity is a MetaAgent, clear parent and remove from children
        if is_meta_agent:
            entity.parent = None
            if entity in self.children:
                self.children.remove(entity)
        
        # Trigger callbacks for bidirectional influence
        if not is_meta_agent and hasattr(entity, "on_leave"):
            entity.on_leave(self)
        self.on_member_leave(entity)
        
        return True
        
    @property
    def members(self):
        """
        Return list of all entities (agents and meta-agents) currently in this group.
        Reads from sparse matrix, not a set.
        """
        return self.hypergraph.get_members(self.meta_agent_id)
    
    def get_agents(self):
        """Return only agents (not meta-agents) in this group."""
        return self.hypergraph.get_agents(self.meta_agent_id)
    
    def get_leaders(self) -> list:
        """Return all entities with 'leader' role in this group."""
        return self.hypergraph.get_members(self.meta_agent_id, role="leader")
    
    def get_members_by_role(self, role: str) -> list:
        """Return all entities with specific role in this group."""
        return self.hypergraph.get_members(self.meta_agent_id, role=role)

    def activate(self, entity: Any) -> None:
        """Set an entity's state to 'active' in this group."""
        self.hypergraph.set_member_state(entity, self.meta_agent_id, "active")
        
    def deactivate(self, entity: Any) -> None:
        """Set an entity's state to 'dormant' in this group."""
        self.hypergraph.set_member_state(entity, self.meta_agent_id, "dormant")
        
    def get_active_members(self) -> list:
        """Return all active members of this group."""
        return self.hypergraph.get_members(self.meta_agent_id, state="active")
        
    def get_dormant_members(self) -> list:
        """Return all dormant members of this group."""
        return self.hypergraph.get_members(self.meta_agent_id, state="dormant")

    def get_meta_agents(self):
        """Return only meta-agents (not agents) directly in this group."""
        return self.hypergraph.get_meta_agents(self.meta_agent_id)
    
    def get_all_members_recursive(self):
        """
        Return all agents recursively, including agents nested in child meta-agents.
        
        Example:
            company.get_all_members_recursive() returns all soldiers in all platoons
        
        Returns:
            List of all agents at any depth in the hierarchy
        """
        all_agents = []
        
        # Add direct agents
        all_agents.extend(self.get_agents())
        
        # Add agents from child meta-agents (recursive)
        for child_meta in self.get_meta_agents():
            all_agents.extend(child_meta.get_all_members_recursive())
        
        return all_agents
