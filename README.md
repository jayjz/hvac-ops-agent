# HVAC OpsForge Agent

**Gemini + MongoDB Powered Autonomous Operations Agent for HVAC & Small Trades Businesses**

**Google Cloud Rapid Agent Hackathon 2026** — MongoDB Track Submission

---

## Elevator Pitch
An intelligent multi-agent system that autonomously handles core operations for small HVAC and service businesses: **inventory forecasting, job scheduling, accounts receivable follow-ups, and parts ordering** — turning chaotic operations into streamlined, proactive workflows.

Built with **Google Cloud Agent Builder + Gemini 2.5** and powered by **MongoDB MCP** for persistent memory and real-time data actions.

---

## The Problem (Real-World HVAC Pain)
From 10+ years running HVAC operations:
- Technicians show up to jobs with wrong/missing parts
- Cash flow suffers from slow AR follow-ups
- Manual scheduling leads to inefficient routes and overtime
- Owners spend nights in spreadsheets instead of growing the business

**HVAC OpsForge Agent** solves this by acting as a proactive Operations Co-Pilot.

---

## Key Features (What the Agent Actually Does)

- **Inventory Forecasting & Reordering** — Predicts part needs based on upcoming jobs and historical usage
- **Smart Job Scheduling** — Optimizes technician assignments considering skills, location, and urgency
- **Automated AR Follow-ups** — Identifies overdue invoices and drafts professional reminders
- **Parts Ordering Assistant** — Checks stock, finds suppliers, and prepares purchase orders
- **Risk & Opportunity Detection** — Flags potential issues (low stock, delayed payments, scheduling conflicts)

The agent doesn't just chat — it **plans, executes tools, updates MongoDB, and keeps humans in the loop** for final approval.

---

## Tech Stack

- **Core Reasoning**: Google Gemini via Cloud Agent Builder
- **Memory & State**: MongoDB Atlas + Model Context Protocol (MCP)
- **Agent Architecture**: Multi-agent orchestrator (Lead Architect + Specialist Agents)
- **Frontend**: Streamlit dashboard
- **Backend**: FastAPI + Python
- **Deployment**: Docker + Google Cloud Run (recommended)

---

## Architecture

1. **Lead Architect Agent** — Receives high-level goals and creates execution plans
2. **Specialist Agents**:
   - InventoryForecaster
   - SchedulerOptimizer
   - ARCollector
   - PartsOrderer
   - RiskAssessor
3. **Tool Integration** via MongoDB MCP (read/write jobs, inventory, customers)
4. **Human-in-the-Loop** approval system for all actions

---

## Hackathon Submission Details

**Track**: MongoDB  
**Goal**: Demonstrate a functional agent that uses Gemini reasoning + MongoDB MCP to solve real operational challenges in the trades industry.

**Live Demo**: (Will be added after deployment)  
**Video Demo**: (Will be recorded)

---

## Quick Start (Local Development)

# 1. Clone
git clone https://github.com/jayjz/hvac-ops-agent.git
cd hvac-ops-agent

# 2. Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Environment variables
cp .env.example .env
# Add your Gemini API key + MongoDB Atlas connection string

# 4. Run
streamlit run streamlit_app.py

# Project Status (June 2026)

Multi-agent orchestration framework ported and pivoted
MongoDB MCP integration in progress
Sample HVAC dataset included
Working towards full end-to-end flows for hackathon deadline


# Why This Matters
This isn't another generic AI demo. It's built by someone who has actually run HVAC operations for over a decade. The goal is practical impact for thousands of small service businesses.
Future Vision: Turn this into a commercial AI Operations Co-Pilot SaaS for trades companies.

# Made for the Google Cloud Rapid Agent Hackathon 2026
License: MIT
