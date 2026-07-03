# HVAC OpsForge

**Autonomous AI Operations Co-Pilot for HVAC & Trade Services**

HVAC OpsForge is a multi-agent operations dashboard for small HVAC and trade service businesses. It shows how a Lead Architect agent can coordinate specialist agents for parts availability, dispatch risk, inventory planning, accounts receivable follow-up, and owner-facing operational decisions.

Built for the **Google Cloud Rapid Agent Hackathon 2026** MongoDB track.

---

## Phase 1 Demo

The Streamlit dashboard is designed to run immediately with synthetic HVAC data, so reviewers can see the product flow without connecting MongoDB first.

1. Load a demo HVAC company.
2. Run the multi-agent dispatch simulation.
3. Explore the owner ROI metrics, agent trace, dispatch board, inventory watchlist, and AR queue.
4. Use the same app shell later with live MongoDB-backed workflows.

Recommended screenshot/GIF captures:

- Hero dashboard with the HVAC OpsForge brand and KPI row.
- Sidebar flow: `Load Demo Company` then `Run Multi-Agent Dispatch`.
- Agent Command Center after the run completes.
- Dispatch, Inventory, and AR tabs with synthetic data.

---

## Elevator Pitch

Small HVAC operators lose margin when technicians arrive without the right parts, routes are planned manually, invoices age without follow-up, and owners spend nights reconciling spreadsheets. HVAC OpsForge turns that chaos into a proactive operations cockpit: the Lead Architect plans the work, specialists inspect the operational risks, and the owner gets clear recommendations before the truck rolls.

---

## What The Agent Does

- **Inventory Forecasting and Reordering**: predicts part needs from upcoming jobs and historical usage.
- **Parts Availability Checking**: flags low-stock and job-critical parts before dispatch.
- **Smart Scheduling**: prioritizes jobs by urgency, location, and operational risk.
- **Automated AR Follow-up**: identifies overdue invoices and prepares next actions.
- **Risk Detection**: surfaces downtime, cashflow, and first-visit-completion risk.

The agent is not positioned as a generic chatbot. It plans, coordinates specialist agents, prepares operational actions, and keeps humans in the loop for approval.

---

## Architecture

1. **LeadArchitect** coordinates the workflow and maintains the execution plan.
2. **Specialist agents** handle inventory, parts availability, scheduling, AR, and risk.
3. **MongoDB** provides persistent operational state for jobs, inventory, customers, and memory.
4. **FastAPI** exposes backend services.
5. **Streamlit** provides the primary demo dashboard.
6. **Docker Compose** runs MongoDB, Redis, API, and static web services for local integration.

---

## Tech Stack

- Backend: FastAPI, Python
- Frontend: Streamlit
- Database: MongoDB
- Agent architecture: Lead Architect plus specialist agents
- Containers: Docker and Docker Compose
- Testing: pytest, pytest-asyncio, mypy, ruff

---

## Quick Start

```bash
git clone https://github.com/jayjz/hvac-ops-agent.git
cd hvac-ops-agent
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the local Streamlit URL, click `Load Demo Company`, and click `Run Multi-Agent Dispatch`.

---

## Environment

The Phase 1 dashboard runs without external services by default. For live integrations, create a `.env` file with the required API keys and MongoDB connection settings used by your deployment.

```bash
cp .env.example .env
```

If `.env.example` is not present in your checkout yet, create `.env` manually and provide the variables required by your MongoDB and model-provider setup.

---

## Docker

Run the integration stack locally:

```bash
docker compose up --build
```

Services defined in `docker-compose.yml` include MongoDB, Redis, the FastAPI service, and Nginx for static assets. The Streamlit dashboard remains the primary Phase 1 demo surface and can be run directly with:

```bash
streamlit run streamlit_app.py
```

---

## Testing

Run the focused dashboard tests:

```bash
python -m pytest tests/test_dashboard_toggle.py tests/test_specialists_split_and_streamlit.py -q
```

Run the full suite:

```bash
python -m pytest -q
```

---

## Project Status

Phase 1 focuses on demo excellence for the Streamlit experience: branded layout, synthetic data, a clear multi-agent run flow, and owner-facing operational outputs. Live MongoDB flows, advanced approvals, richer charts, and static web cleanup are planned as follow-up work.

---

## License

MIT
