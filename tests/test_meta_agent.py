from mesa_meta.hypergraph import Hypergraph
from mesa_meta.meta_agent import Agent, MetaAgent
from mesa_meta.policy import Policy


class OptOutAgent(Agent):
    def wants_to_join(self, meta_agent):
        return False


def test_metaagent_add_respects_agent_opt_in():
    hg = Hypergraph()
    policy = Policy(join_rule="free", leave_rule="free", exclusivity="multiple", authority="test")
    group = MetaAgent(policy, hg, meta_agent_id=0)

    a = OptOutAgent(1)
    assert group.add(a) is False
    assert hg.get_members(meta_agent_id=0) == []


def test_metaagent_join_leave_approval_funcs_gate_membership():
    hg = Hypergraph()

    def join_approval(agent):
        return agent.unique_id % 2 == 0

    def leave_approval(agent):
        return False

    policy = Policy(join_rule="approval", leave_rule="approval", exclusivity="multiple", authority="test")
    group = MetaAgent(policy, hg, meta_agent_id=0, join_approval_func=join_approval, leave_approval_func=leave_approval)

    a1 = Agent(1)
    a2 = Agent(2)

    assert group.add(a1) is False
    assert group.add(a2) is True
    assert hg.get_memberships(a2) == [0]

    assert group.remove(a2) is False
    assert hg.get_memberships(a2) == [0]


def test_exclusive_policy_blocks_multiple_memberships():
    hg = Hypergraph()

    exclusive = Policy(join_rule="free", leave_rule="free", exclusivity="exclusive", authority="exclusive")
    g1 = MetaAgent(exclusive, hg, meta_agent_id=0)
    g2 = MetaAgent(exclusive, hg, meta_agent_id=1)

    a = Agent(1)
    assert g1.add(a) is True
    assert g2.add(a) is False
    assert hg.get_memberships(a) == [0]
