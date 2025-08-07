# ---------- Agent Manager ----------
from typing import List

from customer_issue_resolution.models import Agent


class AgentManager:
    def __init__(self):
        self.agents: List[Agent] = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def remove_agent(self, agent_id: str):
        self.agents = [a for a in self.agents if a.id != agent_id]

    def get_agents(self) -> List[Agent]:
        return self.agents
