import pytest

from mesa_meta.hypergraph import Hypergraph
from mesa_meta.meta_agent import Agent


def test_hypergraph_add_remove_member_roundtrip():
    hg = Hypergraph()
    a1 = Agent(1)
    a2 = Agent(2)

    hg.add_member(a1, meta_agent_id=0)
    hg.add_member(a2, meta_agent_id=0)
    hg.add_member(a2, meta_agent_id=2)

    assert sorted(hg.get_members(meta_agent_id=0), key=lambda a: a.unique_id) == [a1, a2]
    assert hg.get_members(meta_agent_id=1) == []
    assert sorted(hg.get_memberships(a2)) == [0, 2]

    hg.remove_member(a2, meta_agent_id=0)
    assert hg.get_memberships(a2) == [2]
    assert hg.get_members(meta_agent_id=0) == [a1]
