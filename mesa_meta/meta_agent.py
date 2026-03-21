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

from mesa_meta.policy import Policy
from typing import Any, Iterable

class Agent:
    """
    Atomic unit that can join/leave meta-agent groups.
    """
    def __init__(self, unique_id):
        self.unique_id = unique_id
    
    def __repr__(self):
        return f"Agent({self.unique_id})"
    
    def __eq__(self, other):
        if isinstance(other, Agent):
            return self.unique_id == other.unique_id
        return False
    
    def __hash__(self):
        return hash(self.unique_id)


class MetaAgent:
    """
    A group governed by a Policy. Agents join/leave through a decision pipeline.
    Membership stored in sparse matrix (not a set).
    """
    def __init__(self, policy: Policy, hypergraph, meta_agent_id):
        self.policy = policy
        self.hypergraph = hypergraph
        self.meta_agent_id = meta_agent_id
    
    @staticmethod
    def create_meta_agent(policy: Policy, hypergraph, meta_agent_id, agents: Iterable[Agent] = None):
        """
        Factory method to create a MetaAgent and optionally populate it with agents.
        
        Args:
            policy: Policy governing join/leave/exclusivity
            hypergraph: Sparse matrix backend
            meta_agent_id: Unique identifier for this meta-agent
            agents: Optional iterable of agents to add on creation
        
        Returns:
            MetaAgent instance with agents added (if provided)
        """
        meta = MetaAgent(policy, hypergraph, meta_agent_id)
        if agents:
            for agent in agents:
                meta.add(agent)
        if agents:
            for agent in agents:
                meta.add(agent)
        return meta    
    
    def assess_join(self, agent: Agent) -> bool:
        """
        Override this to implement approval logic for join_rule="approval".
        Return True to approve, False to reject.
        """
        return True
    
    def assess_leave(self, agent: Agent) -> bool:
        """
        Override this to implement approval logic for leave_rule="approval".
        Return True to approve, False to reject.
        """
        return True
    
    def add(self, agent: Agent) -> bool:
        """
        Attempt to add agent to this group.
        
        Pipeline:
            1. Policy check (join_rule)
            2. Exclusivity check
            3. Add to matrix
        
        Args:
            agent: Agent to add
        
        Returns:
            True if added, False if rejected
        """
        # Gate 1: Policy check (join_rule)
        if self.policy.join_rule == "approval":
            if not self.assess_join(agent):
                return False  # Approval rejected
        
        # Gate 2: Exclusivity check
        if self.policy.exclusivity == "exclusive":
            existing_memberships = self.hypergraph.get_memberships(agent)
            if len(existing_memberships) > 0:
                return False  # Agent already in another exclusive group
        
        # Gate 3: Add to hypergraph
        self.hypergraph.add_member(agent, self.meta_agent_id)
        return True        

            
    
    def remove(self, agent: Agent) -> bool:
        """
        Attempt to remove agent from this group.
        
        Pipeline:
            1. Policy check (leave_rule)
            2. Remove from matrix
        
        Args:
            agent: Agent to remove
        
        Returns:
            True if removed, False if rejected
        """
        # Gate 1: Policy check (leave_rule)
        
        # Gate 2: Remove from hypergraph
        self.hypergraph.remove_member(agent, self.meta_agent_id)
        return True
        if self.policy.leave_rule == "approval":
            if not self.assess_leave(agent):
                return False  # Approval rejected
        
        # Gate 2: Remove from hypergraph
        self.hypergraph.remove_member(agent, self.meta_agent_id)
        return True
        
    @property
    def members(self):
        """
        Return list of agents currently in this group.
        Reads from sparse matrix, not a set.
        """
        return self.hypergraph.get_members(self.meta_agent_id)    
    
    
