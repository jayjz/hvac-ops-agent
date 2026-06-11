# HVAC OpsForge Agent

**Autonomous AI Operations Co-Pilot for HVAC & Trade Services**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> Transform reactive HVAC operations into proactive, data-driven workflows with an intelligent multi-agent system.

## Overview

HVAC OpsForge is a production-ready multi-agent framework designed to automate core operations for HVAC and trade service businesses. Built on a modular agent architecture, it orchestrates specialized AI agents to handle inventory management, job scheduling, accounts receivable, and operational risk assessment.

Originally developed for the Google Cloud Rapid Agent Hackathon 2026, the system demonstrates how autonomous agents can reduce operational overhead while keeping humans in control of critical decisions.

## ✨ Key Features

- **🤖 Multi-Agent Orchestration** - Lead architect coordinates specialist agents for complex workflows
- **📦 Intelligent Inventory Management** - Predictive forecasting based on job schedules and usage patterns
- **📅 Smart Scheduling** - Optimize technician assignments by skills, location, and urgency
- **💰 Automated AR Workflows** - Identify overdue invoices and generate collection reminders
- **⚠️ Risk Detection** - Proactive alerts for low stock, scheduling conflicts, and cash flow issues
- **👤 Human-in-the-Loop** - All actions require approval before execution
- **📊 Interactive Dashboard** - Streamlit-based UI for monitoring and control

## 🏗️ Architecture

```mermaid
graph TB
    A[User Request] --> B[Lead Architect Agent]
    B --> C{Execution Plan}
    C --> D[Inventory Forecaster]
    C --> E[Scheduler Optimizer]
    C --> F[AR Collector]
    C --> G[Risk Assessor]
    
    D --> H[(MongoDB)]
    E --> H
    F --> H
    G --> H
    
    H --> I[Proposed Actions]
    I --> J{Human Approval}
    J -->|Approved| K[Execute Actions]
    J -->|Rejected| L[Revise Plan]
    
    K --> M[Update Systems]
```

**Agent Specializations:**
- **Lead Architect** - Decomposes goals into executable tasks
- **InventoryForecaster** - Analyzes stock levels and predicts reorder needs
- **SchedulerOptimizer** - Creates efficient technician routes and assignments
- **ARCollector** - Manages accounts receivable and payment follow-ups
- **RiskAssessor** - Identifies operational risks and mitigation strategies

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance async API
- [Python 3.11+](https://python.org/) - Core runtime
- [Pydantic](https://pydantic.dev/) - Data validation

**AI & Agents**
- Agent orchestration framework with async execution
- Modular agent architecture with shared context
- Tool integration pattern for external systems

**Data & Storage**
- [MongoDB Atlas](https://www.mongodb.com/atlas) - Document database
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [Pandas](https://pandas.pydata.org/) - Data analysis

**Frontend**
- [Streamlit](https://streamlit.io/) - Interactive dashboard
- [Matplotlib](https://matplotlib.org/) - Data visualization

**DevOps**
- Docker & Docker Compose
- [Nginx](https://nginx.org/) - Reverse proxy
- Pytest for testing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB Atlas account or local MongoDB
- Docker (optional, for containerized deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/jayjz/hvac-ops-agent.git
cd hvac-ops-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB connection string and API keys

# Run the Streamlit dashboard
streamlit run streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 Usage

### Running Agent Workflows

```python
from core.orchestrator import run_pm_job

# Execute a workflow
result = await run_pm_job(
    job_id="hvac-daily-001",
    goals=[
        "Check inventory for upcoming jobs",
        "Identify overdue invoices",
        "Optimize tomorrow's schedule"
    ],
    require_approval=True
)

# Review proposed actions
print(result["proposed_actions"])
```

### CLI Interface

```bash
# Run via CLI
python cli.py forge_pm --goals "Analyze inventory" --goals "Check AR status"

# With custom project data
python cli.py forge_pm --project-path ./data --goals "Generate weekly report"
```

## 📁 Project Structure

```
├── api/                    # FastAPI backend
│   └── main.py            # API endpoints and job management
├── core/                   # Core agent framework
│   ├── agents/            # Agent implementations
│   │   ├── base.py        # Base agent class
│   │   ├── lead_architect.py
│   │   └── specialists.py # Specialist agents
│   ├── tools/             # Tool integrations
│   │   └── mongodb_tools.py
│   └── orchestrator.py    # Workflow orchestration
├── streamlit_app.py       # Interactive dashboard
├── cli.py                 # Command-line interface
├── config.yaml            # Configuration
├── docker-compose.yml     # Container orchestration
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

Configuration is managed via `config.yaml` and environment variables:

```yaml
# config.yaml
mongodb:
  uri: "${MONGO_URI}"
  database: "hvac_ops"

agents:
  inventory_forecaster:
    low_stock_threshold: 10
    forecast_days: 30
  
  scheduler:
    max_travel_time: 60  # minutes
    work_hours_start: 8
    work_hours_end: 17
```

**Environment Variables:**
```bash
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## 🧪 Testing

```bash
# Run test suite
pytest tests/ -v

# Run with coverage
pytest --cov=core tests/

# Test MongoDB connection
python test_mongo.py
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional agent specializations (e.g., PartsOrderer, CustomerCommunicator)
- Enhanced ML models for inventory forecasting
- Integration with QuickBooks, ServiceTitan, or Housecall Pro
- Mobile app for technicians
- Real-time notifications via SMS/email

Please open an issue to discuss proposed changes.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built for Google Cloud Rapid Agent Hackathon 2026
- Inspired by real-world HVAC operational challenges
- Uses MongoDB Atlas for scalable data storage

---

**Status:** Active Development | **Version:** 0.3.0-alpha | **Last Updated:** June 2026