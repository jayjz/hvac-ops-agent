# AGENTS.md - hvac-ops-agent

## Project Overview
hvac-ops-agent is a multi-agent system designed for HVAC operations. It handles inventory forecasting, parts availability checking, accounts receivable (AR) follow-ups, job closeout procedures, and predictive reordering.

## Architecture
- **Lead Architect + Specialist Agents** pattern
- Lead Architect coordinates specialized agents
- Persistent state and data managed via MongoDB
- Clean Architecture principles strictly followed (entities, use cases, interfaces, infrastructure layers)

## Tech Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: MongoDB
- **Containerization**: Docker + docker-compose
- **AI Layer**: Hermes Agent (multi-agent orchestration)
- Additional: Nginx, Python, GitHub Actions

## Agent Roster
- **LeadArchitect**: Coordinates all agents and maintains system state
- **InventoryForecaster**: Handles inventory forecasting and predictive reordering
- **PartsAvailabilityChecker**: Checks supplier availability and pricing
- **ARFollowUp**: Manages accounts receivable follow-ups and collections
- **JobCloseout**: Handles job completion, documentation, and financial reconciliation
- **PredictiveReordering**: Specialized agent for automated reorder optimization

## Core Rules
- **Strict TDD**: All code changes must follow Red → Green → Refactor cycle
- **Clean Architecture**: Strict separation of concerns across layers
- **Branch Isolation**: Work exclusively on `dev/ai-integration` branch. Never commit directly to `main`
- All development must maintain production-grade standards (logging, error handling, testing, observability)

---
**This file is the portable source of truth for all agents working on this project.**
**Last Updated:** June 5, 2026
