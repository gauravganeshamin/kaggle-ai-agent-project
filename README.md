# Kaggle AI Agent: Sales/Ops Workflow

## Overview
Multi-agent AI system for automating sales operations workflows using:
- Agent orchestration
- Tool-based actions
- Evaluator loops with retries
- Logging & observability

## Key Agents
- **Data Agent**: Pulls Salesforce deal data
- **Drafter Agent**: Generates follow-up actions
- **Risk Scorer Agent**: Assesses deal health
- **Evaluator Agent**: Quality gate with retry logic

## Setup
```bash
pip install -r requirements.txt
python src/orchestrator.py
```

## Project Structure
- `src/` - Core agent code
- `notebooks/` - Kaggle Notebook
- `tests/` - Unit tests
- `data/` - Sample data

## Features Demonstrated
✅ Tool use & execution
✅ Short-term memory/state management
✅ Multi-agent orchestration
✅ Evaluator loop with conditional retries
✅ Observability logging

## Submission
- Kaggle Writeup: [link]
- Public Repo: [this repo]
- Video Demo: [link]
