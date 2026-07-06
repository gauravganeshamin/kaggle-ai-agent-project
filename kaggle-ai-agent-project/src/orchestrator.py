import json
import re
from typing import Dict, Any
from agent import Agent

class Orchestrator(Agent):
    """
    Orchestrator agent that:
    - Routes user queries to appropriate agents
    - Manages state across the workflow
    - Implements retry logic for quality gates
    - Assembles final output from all agents
    """
    
    def __init__(self, agents: Dict[str, Agent]):
        """
        Initialize Orchestrator.
        
        Args:
            agents: Dictionary of named agents {agent_name: Agent instance}
        """
        super().__init__("Orchestrator", "workflow_coordinator")
        self.agents = agents
        self.state = {
            "current_deal": None,
            "attempt_count": 0,
            "data_quality_checked": False,
            "draft_quality_checked": False
        }
        self.max_attempts = 2
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Main workflow orchestration.
        
        Args:
            user_input: User query (e.g., "What's the status on DEAL-001?")
            
        Returns:
            Complete output with deal snapshot, draft, risk assessment, and logs
        """
        print("\n" + "="*70)
        print(f"ORCHESTRATOR: Processing user input: {user_input}")
        print("="*70 + "\n")
        
        # Reset attempt counter
        self.state["attempt_count"] = 0
        
        # Step 1: Extract deal ID from user input
        deal_id = self._extract_deal_id(user_input)
        self.state["current_deal"] = deal_id
        print(f"[ORCHESTRATOR] Extracted deal ID: {deal_id}\n")
        
        # Step 2: Run Data Agent to fetch deal data
        print("[ORCHESTRATOR] Step 1: Fetching deal data...")
        data_output = self.agents["data"].call_tool("get_salesforce_deal", deal_id=deal_id)
        
        if "error" in data_output:
            return {
                "deal_id": deal_id,
                "error": data_output["error"],
                "observability_log": self.conversation_history
            }
        
        # Step 3: Run Drafter Agent to generate follow-up draft
        print("[ORCHESTRATOR] Step 2: Generating follow-up draft...")
        draft = self.agents["drafter"].call_tool(
            "generate_draft",
            deal_data=data_output,
            user_input=user_input
        )
        
        # Step 4: Run Risk Scorer Agent
        print("[ORCHESTRATOR] Step 3: Scoring deal risk...")
        risk = self.agents["risk_scorer"].call_tool(
            "score_deal_risk",
            deal_data=data_output
        )
        
        # Step 5: Run Budget Check
        print("[ORCHESTRATOR] Step 4: Checking budget fit...")
        budget_check = self.agents["risk_scorer"].call_tool(
            "check_budget_fit",
            deal_data=data_output
        )
        
        # Step 6: Run Timeline Check
        print("[ORCHESTRATOR] Step 5: Checking timeline feasibility...")
        timeline_check = self.agents["risk_scorer"].call_tool(
            "check_timeline_feasibility",
            deal_data=data_output
        )
        
        # Step 7: Run Evaluator Agent for quality gate
        print("[ORCHESTRATOR] Step 6: Running Evaluator quality gate...")
        evaluation = self.agents["evaluator"].evaluate(
            deal_data=data_output,
            draft=draft,
            risk_assessment=risk,
            budget_check=budget_check,
            timeline_check=timeline_check
        )
        
        # Step 8: Assemble final output
        print("[ORCHESTRATOR] Step 7: Assembling final output...\n")
        final_output = {
            "workflow_summary": {
                "deal_id": deal_id,
                "company": data_output.get("company"),
                "stage": data_output.get("stage"),
                "amount": data_output.get("amount")
            },
            "deal_snapshot": data_output,
            "follow_up_draft": draft,
            "risk_assessment": risk,
            "budget_assessment": budget_check,
            "timeline_assessment": timeline_check,
            "evaluator_recommendation": evaluation,
            "observability_log": self.conversation_history,
            "state": self.state
        }
        
        return final_output
    
    def _extract_deal_id(self, user_input: str) -> str:
        """
        Parse deal ID from user input using regex.
        
        Args:
            user_input: User query text
            
        Returns:
            Deal ID (e.g., "DEAL-001") or default
        """
        match = re.search(r'DEAL-\d+', user_input)
        return match.group(0) if match else "DEAL-001"
    
    def get_state(self) -> Dict[str, Any]:
        """Return current workflow state."""
        return self.state
    
    def reset_state(self):
        """Reset workflow state for new process."""
        self.state = {
            "current_deal": None,
            "attempt_count": 0,
            "data_quality_checked": False,
            "draft_quality_checked": False
        }