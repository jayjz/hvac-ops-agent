# HVAC OpsForge

**Autonomous AI Operations Co-Pilot for HVAC & Trade Services**

> Transform reactive HVAC operations into proactive, data-driven workflows with an intelligent multi-agent system.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

## Overview

HVAC OpsForge is a production-ready multi-agent framework designed to automate core operations for HVAC and trade service businesses. Built on a modular agent architecture, it orchestrates specialized AI agents to handle inventory management, job scheduling, accounts receivable, and operational risk assessment.

Originally developed for the **Google Cloud Rapid Agent Hackathon 2026**, the system demonstrates how autonomous agents can reduce operational overhead while keeping humans in control of critical decisions.

## ✨ Key Features
- **🤖 Multi-Agent Orchestration** — Lead Architect coordinates specialist agents
- **📦 Intelligent Inventory Management** — Predictive forecasting
- **📅 Smart Scheduling** — Optimized technician assignments
- **💰 Automated AR Workflows** — Overdue invoice handling
- **⚠️ Risk Detection** — Proactive alerts
- **👤 Human-in-the-Loop** — Approval required for actions
- **📊 Interactive Dashboard** — Polished Streamlit UI (Phase 1 Demo Ready)

## Phase 1 Demo (Try It Now)
The Streamlit dashboard runs immediately with **synthetic HVAC data** — no MongoDB required for demo.

1. `streamlit run streamlit_app.py`
2. Click **Load Demo Company**
3. Click **Run Multi-Agent Dispatch**
4. Explore KPI metrics, agent trace, dispatch board, inventory, and AR tabs

**Recommended screenshots/GIFs for README:**
- Branded hero + KPI ribbon
- Sidebar demo flow
- Agent Command Center after simulation

## Quick Start
```bash
git clone https://github.com/jayjz/hvac-ops-agent.git
cd hvac-ops-agent
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Docker
```bash
docker compose up -d
```

(Full architecture, tech stack, usage examples, testing, and contributing sections from the original `main` branch remain below...)

## License
MIT License
```

**4. After editing, complete the merge:**

```bash
git add README.md
git commit -m "Resolve merge conflict in README.md - combine Phase 1 demo with full project docs"
git push origin dev/ai-integration
```

**5. Then create / update the PR** on GitHub (as I explained earlier) from `dev/ai-integration` → `main`.

---