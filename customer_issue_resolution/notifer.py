# ---------- Observer Pattern ----------
from abc import ABC, abstractmethod
from typing import List

from customer_issue_resolution.models import Issue


class IssueObserver(ABC):
    @abstractmethod
    def update(self, issue):
        pass


class EmailNotifier(IssueObserver):
    def update(self, issue):
        print(f"[Email] Issue {issue.id} is now in state: {type(issue.state).__name__}")


class LoggingService(IssueObserver):
    def update(self, issue):
        print(f"[Log] Issue {issue.id} with type {issue.type} is now in state: {type(issue.state).__name__}")


class IssueNotifier:
    _observers: List[IssueObserver] = []

    @classmethod
    def register(cls, observer: IssueObserver):
        cls._observers.append(observer)

    @classmethod
    def notify_all(cls, issue: Issue):
        for observer in cls._observers:
            observer.update(issue)
