from customer_issue_resolution.agent_manger import AgentManager
from customer_issue_resolution.issue_assign_pattern import RoundRobinStrategy, LeastLoadedStrategy
from customer_issue_resolution.issue_manager import IssueFactory
from customer_issue_resolution.models import Agent
from customer_issue_resolution.notifer import IssueNotifier, EmailNotifier, LoggingService


def test_system():
    # Register Observers
    IssueNotifier.register(EmailNotifier())
    IssueNotifier.register(LoggingService())

    # Create Agent Manager and Agents
    manager = AgentManager()
    a1 = Agent("Alice")
    a2 = Agent("Bob")
    a3 = Agent("Charlie")
    manager.add_agent(a1)
    manager.add_agent(a2)
    manager.add_agent(a3)

    # Create Issues
    issue1 = IssueFactory.create_issue("Login", "User unable to login")
    issue2 = IssueFactory.create_issue("Payment", "Payment not processing")
    issue3 = IssueFactory.create_issue("UI", "Button not working")

    # Strategy Assignment
    strategy = RoundRobinStrategy()
    print(f"\n[Round Robin]")
    strategy.assign(manager.get_agents(), issue1)
    strategy.assign(manager.get_agents(), issue2)

    strategy = LeastLoadedStrategy()
    print(f"\n[Least Loaded]")
    strategy.assign(manager.get_agents(), issue3)

    # Simulate Resolution
    issue1.state.next()  # Move to resolved
    issue2.state.next()  # Move to resolved

    # Agent availability
    print("\n[Agent Status]")
    for agent in manager.get_agents():
        print(f"{agent.name} - Assigned: {len(agent.assigned_issues)}, Available: {agent.is_available}")


if __name__ == "__main__":
    test_system()
