# HVAC OpsForge Agent - Codex / Agent Guidelines

**Project Name:** HVAC OpsForge (HVAC OpsForge Agent)  
**Branding:** "HVAC OpsForge – Autonomous AI Operations Co-Pilot for HVAC & Trade Services"  
**Tagline:** Transform reactive HVAC operations into proactive, data-driven workflows with intelligent multi-agent orchestration.  
**Version:** 0.3.0-alpha (Active Development)  
**Primary Goal:** Production-ready multi-agent system for inventory, scheduling, AR, and risk management in HVAC/trades businesses. Human-in-the-loop always.

## Current Status
- **Maturity:** Hackathon MVP → Production polish phase. Core orchestration works; UI (Streamlit) functional but needs premium demo UX.
- **Key Strengths:** Modular agents, MongoDB integration, Docker, synthetic data support.
- **Priority Focus (Next 2-4 weeks):** 
  1. Polished, shareable Streamlit demo UI/UX (highest signal for GitHub, users, opportunities).
  2. Enhanced agent reliability, testing, and visualizations.
  3. Documentation + deployment ease.
- **Risks/Tech Debt:** Synthetic data reliance, limited real integrations (QuickBooks/ServiceTitan), basic error surfaces in UI.

## Roadmap Phases
**Phase 1: Demo Excellence (Current – High Priority)**  
- Premium Streamlit dashboard: Modern visuals, interactivity, one-click demo, exports, mobile-friendly.  
- Rich README with screenshots/GIFs + live demo link.  
- Clean, consistent branding across UI/readme.

**Phase 2: Core Reliability**  
- Comprehensive tests, error handling, logging.  
- Enhanced ML forecasting + optimization (PuLP/OR-Tools).  
- Real data connectors.

**Phase 3: Production & Extensions**  
- Additional agents (PartsOrderer, CustomerCommunicator, etc.).  
- Notifications (SMS/email), mobile tech view.  
- Integrations (QuickBooks, ServiceTitan, Housecall Pro).  
- Monitoring, security, scalability.

**Phase 4: SaaS / Monetization**  
- Multi-tenant, deployment templates, marketplace.

## Stack (Enforce These)
- **Backend:** Python 3.11+, FastAPI (async API endpoints)
- **Agents:** Multi-agent orchestration (Lead Architect + specialists: InventoryForecaster, SchedulerOptimizer, ARCollector, RiskAssessor). Follow existing patterns from `core/agents/`.
- **AI/ML:** PyTorch/NumPy for forecasting; PuLP/OR-Tools for scheduling/optimization.
- **Data:** MongoDB Atlas + Motor (async); Pandas for analysis.
- **Frontend:** Streamlit (primary dashboard – prioritize polish); optional static web/ (HTML/JS) for landing.
- **DevOps:** Docker + docker-compose, Nginx reverse proxy, Pytest.
- **Other:** Pydantic for validation, Matplotlib/Plotly for visuals.

## Conventions (Strictly Enforce)
- **Code Style:** Type hints everywhere. Black/ruff formatting. Comprehensive docstrings.
- **Error Handling & Logging:** Try/except with context; structured logging (no bare prints in prod paths).
- **Testing:** Tests *before* any core change. Use pytest; aim for good coverage on agents/orchestrator.
- **Domain Language:** HVAC/Construction/Operations PM focus – scope, risks, schedules, stakeholders, inventory, AR, technicians.
- **Agent Patterns:** All new agents follow `core/agents/` base + existing specialists (Lead Architect decomposes goals).
- **UI/UX:** Professional, clean, intuitive. Wide layout, responsive, accessible. Strong demo flow (synthetic data instant-on). Use custom CSS/themes for branding (AF icon, blues/greens for HVAC/trust/tech).
- **Git Workflow:** Feature branches → PRs. Small, focused commits. Codex PR reviews encouraged.
- **Branding Consistency:** Use full name "HVAC OpsForge", tagline, and professional tone in UI copy, README, comments.

## Tools & Commands
- **Testing:** `pytest tests/ -v` or with coverage.
- **Local Run:** `docker compose up -d` (preferred) or `streamlit run streamlit_app.py`.
- **Mongo Test:** `python test_mongo.py`.
- **Lint/Format:** ruff/black (configure if missing).
- **Codex-Specific:** Use plan mode for complex tasks; output git-ready diffs.

## Codex / AI Agent Instructions (For Codex, Claude, etc.)
- **Role:** Act as a senior HVAC-tech + full-stack engineer who ships production polish.
- **Workflow:** 
  1. Audit & plan (phased TODO).
  2. Read relevant files first.
  3. Propose small, reviewable changes.
  4. Include tests/verification steps.
  5. Respect human-in-the-loop.
- **Review Guidelines:** 
  - Check functionality, edge cases, HVAC domain accuracy.
  - Ensure UI is premium/demo-ready (visuals, flow, branding).
  - No breaking changes without discussion.
  - Security: Sanitize inputs, no PII leaks.
- **Output Format:** Structured Markdown – Summary → Plan → File diffs/edits → Verification steps → Risks/Next.
- **Priorities:** Demo UX > Core stability > New features. Minimize token waste with focused scopes.

## Additional Notes
- Inspired by real HVAC ops challenges + Google Cloud Rapid Agent Hackathon 2026.
- Always maintain human approval for agent actions.
- Contributions: Open issues first for major changes.

**Status:** Active – Focus on Phase 1 Demo Excellence.
**Last Updated:** July 2026
