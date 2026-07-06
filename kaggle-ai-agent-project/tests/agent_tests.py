import pytest
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import Agent
from tools import get_salesforce_deal, generate_draft, score_deal_risk

class TestAgent:
    """Test Agent class functionality."""
    
    def test_agent_initialization(self):
        """Test Agent can be initialized with name, role, and tools."""
        def dummy_tool():
            return {"result": "success"}
        
        agent = Agent(
            name="TestAgent",
            role="test_role",
            tools={"dummy": dummy_tool}
        )
        
        assert agent.name == "TestAgent"
        assert agent.role == "test_role"
        assert "dummy" in agent.tools
        assert agent.conversation_history == []
    
    def test_call_tool_success(self):
        """Test calling a tool successfully."""
        def test_tool(x: int, y: int):
            return {"result": x + y}
        
        agent = Agent(
            name="MathAgent",
            role="calculator",
            tools={"add": test_tool}
        )
        
        result = agent.call_tool("add", x=5, y=3)
        
        assert result["result"] == 8
        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0]["tool"] == "add"
    
    def test_call_tool_not_found(self):
        """Test calling a non-existent tool."""
        agent = Agent(
            name="TestAgent",
            role="test",
            tools={}
        )
        
        result = agent.call_tool("nonexistent", param="value")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_conversation_history_logging(self):
        """Test that tool calls are logged to conversation history."""
        def greet(name: str):
            return {"greeting": f"Hello, {name}!"}
        
        agent = Agent(
            name="Greeter",
            role="greets_users",
            tools={"greet": greet}
        )
        
        agent.call_tool("greet", name="Alice")
        agent.call_tool("greet", name="Bob")
        
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["inputs"]["name"] == "Alice"
        assert agent.conversation_history[1]["inputs"]["name"] == "Bob"
    
    def test_clear_history(self):
        """Test clearing conversation history."""
        agent = Agent(
            name="TestAgent",
            role="test",
            tools={"dummy": lambda: "result"}
        )
        
        agent.call_tool("dummy")
        assert len(agent.conversation_history) == 1
        
        agent.clear_history()
        assert len(agent.conversation_history) == 0

class TestTools:
    """Test tool functions."""
    
    def test_get_salesforce_deal_valid(self):
        """Test fetching a valid deal."""
        result = get_salesforce_deal("DEAL-001")
        
        assert result["id"] == "DEAL-001"
        assert result["company"] == "TechCorp Inc"
        assert result["amount"] == 150000
        assert "stage" in result
    
    def test_get_salesforce_deal_invalid(self):
        """Test fetching an invalid deal."""
        result = get_salesforce_deal("DEAL-999")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_generate_draft(self):
        """Test generating a follow-up draft."""
        deal_data = {
            "id": "DEAL-001",
            "company": "TechCorp Inc",
            "stage": "Negotiation",
            "owner": "John Smith"
        }
        
        result = generate_draft(deal_data)
        
        assert "deal_id" in result
        assert "draft" in result
        assert len(result["draft"]) > 0
        assert "quality_score" in result
    
    def test_score_deal_risk(self):
        """Test risk scoring."""
        deal_data = {
            "id": "DEAL-001",
            "amount": 150000,
            "probability": 0.75,
            "days_in_stage": 32,
            "stage": "Negotiation"
        }
        
        result = score_deal_risk(deal_data)
        
        assert "risk_level" in result
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert "risk_score" in result
        assert 0 <= result["risk_score"] <= 1
        assert "factors" in result

class TestIntegration:
    """Integration tests for multiple agents."""
    
    def test_data_and_drafter_workflow(self):
        """Test workflow: Data Agent → Drafter Agent."""
        from tools import get_salesforce_deal, generate_draft
        
        # Step 1: Data Agent fetches deal
        data_agent = Agent(
            name="DataAgent",
            role="fetcher",
            tools={"get_deal": get_salesforce_deal}
        )
        
        deal = data_agent.call_tool("get_deal", deal_id="DEAL-001")
        
        # Step 2: Drafter uses that data
        drafter_agent = Agent(
            name="DrafterAgent",
            role="writer",
            tools={"generate": generate_draft}
        )
        
        draft = drafter_agent.call_tool("generate", deal_data=deal)
        
        # Verify
        assert "error" not in deal
        assert "draft" in draft
        assert "error" not in draft

if __name__ == "__main__":
    pytest.main([__file__, "-v"])