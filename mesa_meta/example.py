try:
    from .policy import Policy
    from .hypergraph import Hypergraph
    from .meta_agent import MetaAgent
except ImportError:  # Support running as a script from within mesa_meta/
    from policy import Policy
    from hypergraph import Hypergraph
    from meta_agent import MetaAgent
from mesa import Model, Agent
from random import randint


class Agent_std(Agent):
    def __init__(self, unique_id, model, iq_level, past_qualification, entrance_marks):
        super().__init__(model)
        self.unique_id = unique_id
        self.iq_level = iq_level
        self.past_qualification = past_qualification
        self.entrance_marks = entrance_marks

    def wants_to_join(self, meta_agent):
        if "rank" in meta_agent.attributes and meta_agent.attributes["rank"] < 10:
            return True
        elif "distance" in meta_agent.attributes: # Assuming it's the gym instead
            return True 
        else:
            return False
    def wants_to_join_gym(self,meta_agent):
        if meta_agent.attributes["distance"]<=5:
            return True
        else:
            return False
        
        
class College(MetaAgent):
    """MetaAgent for college with approval functions."""
    
    def assess_join(self, agent):
        """
        Approve if:
        - student's iq_level >= 120
        - past_qualification == "graduate"
        - entrance_marks >= 120
        """
        return (agent.iq_level >= 120 and 
                agent.past_qualification == "graduate" and 
                agent.entrance_marks >= 120)
    
    def assess_leave(self,agent):
        """Always approve leaving"""
        return True

def join_approval(agent):
    return (agent.iq_level >= 120 and 
                agent.past_qualification == "graduate" and 
                agent.entrance_marks >= 120)

def leave_approval(agent):
    return True



class Gym(MetaAgent):
    """MetaAgent for gym with free join/leave."""
    pass


class Model_institute(Model):
    def __init__(self, n_agents):
        super().__init__()
        self.n_agents = n_agents
        self.agen = []
        self.hypergraph = Hypergraph()
        
        for i in range(self.n_agents):
            a = Agent_std(unique_id=i, model=self, iq_level=130, 
                         past_qualification="graduate", 
                         entrance_marks=randint(120, 200))
            self.agen.append(a)
            
        policy = Policy(
            join_rule="approval",
            leave_rule="approval",
            authority="hierarchy",
            exclusivity="multiple"
        )

        students = MetaAgent(policy, self.hypergraph, meta_agent_id=0, join_approval_func=join_approval, leave_approval_func=leave_approval)
        
        attribute = {"rank": 3}
        students.add_attribute(attribute)
        
        for agent in self.agen:
            students.add(agent)
        
        # Create Gym meta-agent with free join/leave
        gym_policy = Policy(
            join_rule="free",
            leave_rule="free",
            authority="none",
            exclusivity="multiple",
        )
        
        gym = Gym(gym_policy, self.hypergraph, meta_agent_id=1)
        gym.add_attribute({"name": "City Gym", "cost": 50,"distance":5})
        
        # Add agents to gym (all can join freely)
        for agent in self.agen:
            gym.add(agent)
        
        # Print incidence matrix
        print("\n" + "="*50)
        print("INCIDENCE MATRIX")
        print("="*50)
        print(f"Rows: Agents, Columns: Meta-agents (0=College, 1=Gym)")
        print(self.hypergraph.matrix.toarray())
        print("="*50 + "\n")
        
model=Model_institute(3)

        
