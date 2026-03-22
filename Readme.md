# Meta-Agent Prototype (GSoC)

This repository is a prototype for a GSoC project exploring meta-agents and group membership in agent-based models.

**What it does:**
- Models agents and groups (meta-agents) with flexible join/leave rules.
- Uses a sparse matrix to efficiently track which agents belong to which groups.
- Supports custom approval logic for joining/leaving groups.

**How to run:**
- From the repo root: `python -m mesa_meta.example`

**Code structure:**
- `Agent`: Represents an individual entity.
- `MetaAgent`: Represents a group; manages membership and rules.
- `Policy`: Configures join/leave/exclusivity logic.
- `Hypergraph`: Sparse matrix backend for group membership.
- `example.py`: Shows how to use the system.

This is a starting point for more advanced agent-based modeling and group dynamics.

---

**Lifecycle:**
1. Agents and meta-agents are created.
2. Agents decide to join or leave a group (meta-agent) based on the meta-agent's attributes (e.g., `rank`, `distance`).
3. Agents apply to join or leave the meta-agent.
4. Meta-agents apply policy and approval logic to accept or reject requests.
5. Membership is updated in the sparse matrix.
6. Both agents and meta-agents can react to membership changes (customizable).

incidence matrix:
![alt text](image.png)

This is the incidence matrix when every agents want to join the school and gym
and cleared the criteria 

![alt text](image-1.png)

This is the incidence martix when the agent didnt wanted to join the school but wanted to join the gym