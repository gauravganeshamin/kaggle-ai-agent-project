import json
from typing import Dict, Any

# ============================================================================
# TOOL 1: Get Salesforce Deal (Mock Data)
# ============================================================================

def get_salesforce_deal(deal_id: str) -> Dict[str, Any]:
    """
    Fetch deal data from Salesforce.
    (Mock implementation for demo)
    
    Args:
        deal_id: Deal identifier (e.g., "DEAL-001")
        
    Returns:
        Deal data dictionary
    """
    mock_deals = {
        "DEAL-001": {
            "id": "DEAL-001",
            "company": "TechCorp Inc",
            "amount": 150000,
            "stage": "Negotiation",
            "probability": 0.75,
            "days_in_stage": 32,
            "owner": "John Smith",
            "next_step": "Legal review",
            "expected_close": "2026-08-15",
            "budget_available": 200000
        },
        "DEAL-002": {
            "id": "DEAL-002",
            "company": "CloudStart LLC",
            "amount": 75000,
            "stage": "Proposal",
            "probability": 0.60,
            "days_in_stage": 14,
            "owner": "Sarah Johnson",
            "next_step": "Pricing discussion",
            "expected_close": "2026-07-30",
            "budget_available": 100000
        }
    }
    
    return mock_deals.get(deal_id, {
        "error": f"Deal {deal_id} not found",
        "available_deals": list(mock_deals.keys())
    })

# ============================================================================
# TOOL 2: Generate Draft Follow-up Action
# ============================================================================

def generate_draft(deal_data: Dict[str, Any], user_input: str = None) -> Dict[str, Any]:
    """
    Generate a follow-up action draft based on deal data.
    
    Args:
        deal_data: Deal information from Salesforce
        user_input: Optional context from user
        
    Returns:
        Draft action dictionary
    """
    deal_id = deal_data.get("id", "UNKNOWN")
    company = deal_data.get("company", "Unknown")
    stage = deal_data.get("stage", "Unknown")
    owner = deal_data.get("owner", "Sales Rep")
    
    # Generate contextual draft
    if stage == "Negotiation":
        draft_text = f"""
Follow-up Action: {deal_id} - {company}

Owner: {owner}
Priority: High (in negotiation for 32 days)

Suggested Action:
1. Schedule legal review meeting with {company}
2. Prepare contract redlines
3. Brief Finance on budget requirements

Timeline: This week
Status: Action Required
        """
    elif stage == "Proposal":
        draft_text = f"""
Follow-up Action: {deal_id} - {company}

Owner: {owner}
Priority: Medium (proposal sent)

Suggested Action:
1. Initiate pricing discussion
2. Provide product demo if needed
3. Address any technical questions

Timeline: Next 3 days
Status: Follow-up Needed
        """
    else:
        draft_text = f"""
Follow-up Action: {deal_id} - {company}

Owner: {owner}
Current Stage: {stage}

Suggested Action:
1. Review deal progress
2. Plan next steps

Timeline: As needed
Status: Monitor
        """
    
    return {
        "deal_id": deal_id,
        "draft": draft_text.strip(),
        "quality_score": 0.85,
        "tone": "professional",
        "revision_count": 0
    }

# ============================================================================
# TOOL 3: Score Deal Risk
# ============================================================================

def score_deal_risk(deal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate risk score for a deal.
    
    Args:
        deal_data: Deal information from Salesforce
        
    Returns:
        Risk assessment dictionary
    """
    amount = deal_data.get("amount", 0)
    probability = deal_data.get("probability", 0)
    days_in_stage = deal_data.get("days_in_stage", 0)
    stage = deal_data.get("stage", "Unknown")
    
    # Risk calculation logic
    risk_factors = {
        "low_probability": probability < 0.5,
        "long_cycle": days_in_stage > 60,
        "large_amount": amount > 100000,
        "early_stage": stage in ["Prospecting", "Qualification"]
    }
    
    risk_score = sum(risk_factors.values()) / len(risk_factors)
    
    if risk_score < 0.25:
        risk_level = "LOW"
    elif risk_score < 0.6:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return {
        "deal_id": deal_data.get("id"),
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "factors": risk_factors,
        "confidence": 0.90,
        "recommendations": [
            "Monitor deal progress weekly" if risk_level != "LOW" else "Standard monitoring",
            "Escalate if timeline extends" if days_in_stage > 45 else "On track"
        ]
    }

# ============================================================================
# TOOL 4: Check Budget Fit
# ============================================================================

def check_budget_fit(deal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate deal against budget constraints.
    
    Args:
        deal_data: Deal information
        
    Returns:
        Budget fit assessment
    """
    amount = deal_data.get("amount", 0)
    budget_available = deal_data.get("budget_available", 0)
    
    fits = amount <= budget_available
    utilization = (amount / budget_available * 100) if budget_available > 0 else 0
    
    return {
        "deal_id": deal_data.get("id"),
        "deal_amount": amount,
        "available_budget": budget_available,
        "fits_budget": fits,
        "utilization_percent": round(utilization, 1),
        "remaining_after": max(0, budget_available - amount)
    }

# ============================================================================
# TOOL 5: Check Timeline Feasibility
# ============================================================================

def check_timeline_feasibility(deal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess timeline feasibility for deal closure.
    
    Args:
        deal_data: Deal information
        
    Returns:
        Timeline assessment
    """
    from datetime import datetime, timedelta
    
    expected_close = deal_data.get("expected_close", "2026-12-31")
    days_in_stage = deal_data.get("days_in_stage", 0)
    stage = deal_data.get("stage", "Unknown")
    
    try:
        close_date = datetime.fromisoformat(expected_close)
        days_until_close = (close_date - datetime.now()).days
    except:
        days_until_close = 30  # Default
    
    # Feasibility logic
    stage_duration_map = {
        "Prospecting": 14,
        "Qualification": 21,
        "Proposal": 30,
        "Negotiation": 45,
        "Closed Won": 0
    }
    
    typical_duration = stage_duration_map.get(stage, 30)
    is_feasible = days_until_close >= typical_duration
    
    return {
        "deal_id": deal_data.get("id"),
        "current_stage": stage,
        "expected_close_date": expected_close,
        "days_until_close": days_until_close,
        "typical_stage_duration": typical_duration,
        "is_feasible": is_feasible,
        "confidence": 0.85,
        "note": "Timeline is realistic" if is_feasible else "Timeline may be tight"
    }