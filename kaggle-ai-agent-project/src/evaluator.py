import json
from typing import Dict, Any
from agent import Agent

class EvaluatorAgent(Agent):
    """
    Evaluator agent that:
    - Scores deal quality across multiple dimensions
    - Uses Claude API for intelligent scoring (optional)
    - Falls back to deterministic scoring
    - Provides approve/revise/reject recommendations
    - Implements retry logic
    """
    
    def __init__(self, use_claude_api: bool = False, api_key: str = None):
        """
        Initialize Evaluator.
        
        Args:
            use_claude_api: Whether to use Claude API for scoring
            api_key: Anthropic API key (if using Claude)
        """
        super().__init__("Evaluator", "quality_gate")
        self.use_claude_api = use_claude_api
        self.api_key = api_key
        self.max_retries = 2
    
    def evaluate(self, 
                 deal_data: Dict[str, Any],
                 draft: Dict[str, Any],
                 risk_assessment: Dict[str, Any],
                 budget_check: Dict[str, Any],
                 timeline_check: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of deal and outputs.
        
        Args:
            deal_data: Deal snapshot from Salesforce
            draft: Generated follow-up draft
            risk_assessment: Risk score from Risk Scorer
            budget_check: Budget fit assessment
            timeline_check: Timeline feasibility assessment
            
        Returns:
            Evaluation recommendation with scores
        """
        print("[EVALUATOR] Starting comprehensive evaluation...")
        
        # Attempt scoring with retries
        evaluation = None
        for attempt in range(self.max_retries + 1):
            try:
                if self.use_claude_api and self.api_key:
                    evaluation = self._score_with_claude_api(
                        deal_data, draft, risk_assessment, 
                        budget_check, timeline_check
                    )
                else:
                    evaluation = self._score_deterministic(
                        deal_data, draft, risk_assessment,
                        budget_check, timeline_check
                    )
                
                if evaluation:
                    break
            except Exception as e:
                print(f"[EVALUATOR] Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries:
                    print("[EVALUATOR] All attempts failed, using deterministic fallback")
                    evaluation = self._score_deterministic(
                        deal_data, draft, risk_assessment,
                        budget_check, timeline_check
                    )
        
        self.log_call("evaluate", {
            "deal_id": deal_data.get("id"),
            "evaluation_type": "claude_api" if self.use_claude_api else "deterministic"
        }, evaluation)
        
        return evaluation
    
    def _score_with_claude_api(self,
                               deal_data: Dict[str, Any],
                               draft: Dict[str, Any],
                               risk_assessment: Dict[str, Any],
                               budget_check: Dict[str, Any],
                               timeline_check: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score using Gemini API (requires API key).
        
        Args:
            All assessment data
            
        Returns:
            Evaluation with Claude-generated scores
        """
        try:
            import os
            from google import genai

            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            
            prompt = f"""
You are a sales operations quality evaluator. Evaluate this deal and outputs on a scale of 0-100.

Deal Data:
- ID: {deal_data.get('id')}
- Company: {deal_data.get('company')}
- Amount: ${deal_data.get('amount')}
- Stage: {deal_data.get('stage')}
- Probability: {deal_data.get('probability')}

Risk Assessment: {json.dumps(risk_assessment, indent=2)}
Budget Fit: {json.dumps(budget_check, indent=2)}
Timeline: {json.dumps(timeline_check, indent=2)}
Draft Quality: {draft.get('quality_score', 0.75)}

Respond ONLY with JSON (no markdown, no preamble):
{{
  "deal_health_score": <0-100>,
  "draft_quality_score": <0-100>,
  "risk_score": <0-100>,
  "overall_score": <0-100>,
  "recommendation": "APPROVE" or "REVISE" or "REJECT",
  "reasoning": "<brief explanation>"
}}
            """
            
            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            # Clean markdown if present
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            scores = json.loads(response_text)
            
            return {
                "evaluation_method": "claude_api",
                "deal_health_score": scores.get("deal_health_score", 75),
                "draft_quality_score": scores.get("draft_quality_score", 80),
                "risk_score": scores.get("risk_score", 65),
                "overall_score": scores.get("overall_score", 73),
                "recommendation": scores.get("recommendation", "REVISE"),
                "reasoning": scores.get("reasoning", ""),
                "confidence": 0.95
            }
        
        except Exception as e:
            print(f"[EVALUATOR] Claude API failed: {str(e)}, falling back to deterministic")
            raise
    
    def _score_deterministic(self,
                             deal_data: Dict[str, Any],
                             draft: Dict[str, Any],
                             risk_assessment: Dict[str, Any],
                             budget_check: Dict[str, Any],
                             timeline_check: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score using deterministic logic (no API required).
        
        Args:
            All assessment data
            
        Returns:
            Evaluation with deterministic scores
        """
        # Score 1: Deal Health (based on probability and stage)
        probability = deal_data.get("probability", 0.5)
        days_in_stage = deal_data.get("days_in_stage", 30)
        
        deal_health_score = int(
            probability * 100 * 0.7 +  # 70% weight on probability
            (1 - min(days_in_stage / 90, 1)) * 100 * 0.3  # 30% weight on cycle time
        )
        deal_health_score = max(0, min(100, deal_health_score))
        
        # Score 2: Draft Quality
        draft_quality_score = int(draft.get("quality_score", 0.8) * 100)
        
        # Score 3: Risk Assessment
        risk_level = risk_assessment.get("risk_level", "MEDIUM")
        risk_score_map = {"LOW": 90, "MEDIUM": 60, "HIGH": 30}
        risk_score = risk_score_map.get(risk_level, 60)
        
        # Score 4: Overall Composite Score
        overall_score = int(
            deal_health_score * 0.35 +
            draft_quality_score * 0.25 +
            (100 - risk_score) * 0.25 +
            (100 if budget_check.get("fits_budget") else 50) * 0.10 +
            (100 if timeline_check.get("is_feasible") else 50) * 0.05
        )
        
        # Recommendation Logic
        if overall_score >= 80:
            recommendation = "APPROVE"
        elif overall_score >= 60:
            recommendation = "REVISE"
        else:
            recommendation = "REJECT"
        
        reasoning = f"Deal health: {deal_health_score}/100, Draft quality: {draft_quality_score}/100, Risk level: {risk_level}"
        
        return {
            "evaluation_method": "deterministic",
            "deal_health_score": deal_health_score,
            "draft_quality_score": draft_quality_score,
            "risk_score": risk_score,
            "overall_score": overall_score,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "confidence": 0.85,
            "budget_fit": budget_check.get("fits_budget", False),
            "timeline_feasible": timeline_check.get("is_feasible", False)
        }
    
    def score_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score quality of fetched data."""
        has_required_fields = all(
            key in data for key in ["id", "company", "amount", "stage"]
        )
        return {
            "status": "PASS" if has_required_fields else "FAIL",
            "quality_score": 0.95 if has_required_fields else 0.4,
            "feedback": "Data complete" if has_required_fields else "Missing required fields"
        }
    
    def score_draft(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Score quality of generated draft."""
        has_draft = "draft" in draft and len(draft.get("draft", "")) > 10
        return {
            "status": "PASS" if has_draft else "FAIL",
            "quality_score": draft.get("quality_score", 0.75),
            "feedback": "Draft is well-structured" if has_draft else "Draft is empty or too short"
        }