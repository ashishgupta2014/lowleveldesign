# ---------- Factory Pattern ----------
from customer_issue_resolution.models import Issue


class IssueFactory:
    @staticmethod
    def create_issue(issue_type: str, description: str) -> Issue:
        return Issue(issue_type, description)