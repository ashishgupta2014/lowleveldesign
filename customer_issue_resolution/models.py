# ---------- Agent and Issue Models ----------
import uuid

from customer_issue_resolution.issue_states import NewState


class Agent:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.is_available = True
        self.assigned_issues = []

    def assign_issue(self, issue):
        self.assigned_issues.append(issue)
        self.is_available = False

    def resolve_issue(self, issue):
        self.assigned_issues.remove(issue)
        if not self.assigned_issues:
            self.is_available = True

    def __str__(self):
        return f"Agent({self.name}, Available: {self.is_available})"


class Issue:
    def __init__(self, issue_type, description):
        self.id = str(uuid.uuid4())
        self.type = issue_type
        self.description = description
        self.state = NewState(self)
        self.assigned_agent = None

    def change_state(self, new_state):
        self.state = new_state
        self.notify_observers()

    def set_agent(self, agent):
        self.assigned_agent = agent

    def notify_observers(self):
        from customer_issue_resolution.notifer import IssueNotifier
        IssueNotifier.notify_all(self)
