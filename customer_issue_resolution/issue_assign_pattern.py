# ---------- Strategy Pattern ----------
from abc import ABC, abstractmethod
from typing import List

from customer_issue_resolution.issue_states import AssignedState
from customer_issue_resolution.models import Agent, Issue


class AssignmentStrategy(ABC):
    @abstractmethod
    def assign(self, agents: List[Agent], issue: Issue):
        pass


class RoundRobinStrategy(AssignmentStrategy):
    def __init__(self):
        self.index = 0

    def assign(self, agents: List[Agent], issue: Issue):
        if not agents:
            raise Exception("No agents available")

        start_index = self.index
        while True:
            agent = agents[self.index % len(agents)]
            self.index += 1
            if agent.is_available:
                agent.assign_issue(issue)
                issue.set_agent(agent)
                issue.change_state(AssignedState(issue))
                return agent

            if self.index % len(agents) == start_index:
                raise Exception("No agents currently available")


class LeastLoadedStrategy(AssignmentStrategy):
    def assign(self, agents: List[Agent], issue: Issue):
        if not agents:
            raise Exception("No agents available")

        sorted_agents = sorted(agents, key=lambda a: len(a.assigned_issues))
        for agent in sorted_agents:
            if agent.is_available:
                agent.assign_issue(issue)
                issue.set_agent(agent)
                issue.change_state(AssignedState(issue))
                return agent
        raise Exception("No agents currently available")
