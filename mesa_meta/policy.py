"""


policy.py - Policy class for Meta-Agent module

Overview:
    The Policy class defines the rules that govern how agents
    join and leave a MetaAgent group. It acts as a configuration
    object that is passed to a MetaAgent at creation time.

    Instead of hardcoding group behaviors (like Family, Company,
    Alliance), users configure a single Policy object with
    parameters that express any group dynamic.

Parameters:
    join_rule (str or callable):
        Controls how agents enter the group.
        "free"     — any agent can join without approval
        "approval" — meta-agent's assess_member() must return True

    leave_rule (str or callable):
        Controls how agents exit the group.
        "free"     — any agent can leave without approval
        "approval" — meta-agent's approve_exit() must return True

    exclusivity (str):
        Controls whether an agent can belong to multiple groups.
        "multiple"  — agent can belong to many groups at once
        "exclusive" — agent can only belong to one group at a time

    authority (str):
        The name of the authority/relationship type this group represents.
        Used to identify which column in the incidence matrix
        belongs to this meta-agent.
        Examples: "alliance", "family", "employer"

Usage:
    # open group — anyone can join and leave freely
    friends_policy = Policy(
        join_rule="free",
        leave_rule="free",
        exclusivity="multiple",
        authority="friends"
    )

    # approval group — meta-agent decides who joins
    squad_policy = Policy(
        join_rule="approval",
        leave_rule="approval",
        exclusivity="multiple",
        authority="alliance"
    )

    # exclusive group — agent can only be in one
    family_policy = Policy(
        join_rule="approval",
        leave_rule="free",
        exclusivity="exclusive",
        authority="family"
    )

Note:
    Policy does not contain any logic itself.
    It is just a configuration object.
    The actual join/leave logic lives in MetaAgent.add()
    and MetaAgent.remove().


"""


class Policy:
    def __init__(self,join_rule:str,leave_rule:str,exclusivity:str,authority:str,join_approval_func=None,leave_approval_func=None):
        self.join_rule=join_rule
        self.leave_rule=leave_rule
        self.exclusivity=exclusivity
        self.authority=authority
        self.join_approval_func=join_approval_func
        self.leave_approval_func=leave_approval_func

        if join_rule not in ["free", "approval"]:
            """If the join rule is approval then approcal fucntion is required """
            raise ValueError(f"Invalid join_rule: {join_rule}")
        elif self.join_rule == "approval" and join_approval_func is None:
            raise ValueError("join_rule='approval' requires join_approval function")



        if leave_rule not in ["free", "approval"]:
            """if the leave rule is approval then it need to have a approval fucntion""" 
            raise ValueError(f"Invalid leave_rule: {leave_rule}")
        elif self.leave_rule == "approval" and leave_approval_func is None:
            raise ValueError("leave_rule='approval' requires leave_approval_func")
        

        if exclusivity not in ["multiple", "exclusive"]:
            """agent can be part of only single """
            raise ValueError(f"Invalid exclusivity: {exclusivity}")       


