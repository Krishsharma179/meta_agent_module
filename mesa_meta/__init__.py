"""Mesa Meta-Agent Module"""

from mesa_meta.policy import Policy
from mesa_meta.meta_agent import Agent, MetaAgent
from mesa_meta.hypergraph import Hypergraph
from mesa_meta.facade import (
    create_group,
    add_agent_to_group,
    remove_agent_from_group,
    get_group_members,
    get_agent_groups,
    create_friends_group,
    create_company_group,
    create_family_group,
    set_global_hypergraph,
    get_global_hypergraph,
    print_group_summary
)

__all__ = [
    "Policy",
    "Agent",
    "MetaAgent",
    "Hypergraph",
    "create_group",
    "add_agent_to_group",
    "remove_agent_from_group",
    "get_group_members",
    "get_agent_groups",
    "create_friends_group",
    "create_company_group",
    "create_family_group",
    "set_global_hypergraph",
    "get_global_hypergraph",
    "print_group_summary"
]
