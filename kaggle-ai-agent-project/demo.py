from src.agent import Agent
from src.orchestrator import Orchestrator
from src.evaluator import EvaluatorAgent
from src.tools import (
    get_salesforce_deal, 
    generate_draft, 
    score_deal_risk,
    check_budget_fit,
    check_timeline_feasibility
)

# Initialize agents
data_agent = Agent(
    name="DataAgent",
    role="pulls_salesforce_data",
    tools={"get_salesforce_deal": get_salesforce_deal}
)

drafter_agent = Agent(
    name="DrafterAgent",
    role="writes_follow_ups",
    tools={"generate_draft": generate_draft}
)

risk_agent = Agent(
    name="RiskScorerAgent",
    role="scores_deal_health",
    tools={
        "score_deal_risk": score_deal_risk,
        "check_budget_fit": check_budget_fit,
        "check_timeline_feasibility": check_timeline_feasibility
    }
)

evaluator_agent = EvaluatorAgent(use_claude_api=False)  # Set True if using Claude API

# Create orchestrator
orchestrator = Orchestrator({
    "data": data_agent,
    "drafter": drafter_agent,
    "risk_scorer": risk_agent,
    "evaluator": evaluator_agent
})

# Process a user query
result = orchestrator.process("What's the status on DEAL-001? Should I follow up?")

# Print results
import json
print(json.dumps(result, indent=2))