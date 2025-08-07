# ---------- State Pattern ----------
from abc import ABC, abstractmethod


class IssueState(ABC):
    def __init__(self, issue):
        self.issue = issue

    @abstractmethod
    def next(self):
        pass


class NewState(IssueState):
    def next(self):
        self.issue.change_state(AssignedState(self.issue))


class AssignedState(IssueState):
    def next(self):
        self.issue.change_state(ResolvedState(self.issue))


class ResolvedState(IssueState):
    def next(self):
        print("Issue is already resolved.")
