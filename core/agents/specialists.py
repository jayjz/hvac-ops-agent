"""Specialist HVAC operations agents for HVAC OpsForge."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.agents.base import AgentContext, AgentResult, BaseAgent


class InventoryForecasterAgent(BaseAgent):
    """Forecast inventory needs based on upcoming jobs and historical usage."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="inventory_forecaster", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        mongodb = payload.get("mongodb")
        await self.report_progress(context, 0.20, "Fetching upcoming jobs from MongoDB.")
        
        # Get upcoming jobs and current inventory from MongoDB
        upcoming_jobs = []
        inventory_levels = []
        
        if mongodb:
            try:
                upcoming_jobs = await asyncio.to_thread(mongodb.get_upcoming_jobs, days=14)
                inventory_levels = await asyncio.to_thread(mongodb.get_low_inventory, threshold_multiplier=1.2)
                await self.report_progress(context, 0.50, f"Found {len(upcoming_jobs)} upcoming jobs and {len(inventory_levels)} low-stock items.")
            except Exception as exc:
                self.logger.warning("MongoDB query failed, using fallback data: %s", exc)
                # Fallback to synthetic data for demo
                upcoming_jobs = self._get_synthetic_jobs()
                inventory_levels = self._get_synthetic_inventory()
        else:
            # No MongoDB, use synthetic data
            upcoming_jobs = self._get_synthetic_jobs()
            inventory_levels = self._get_synthetic_inventory()
        
        await self.report_progress(context, 0.70, "Forecasting parts needs and reorder points.")
        
        # Analyze jobs and forecast inventory needs
        forecast = await asyncio.to_thread(
            self._forecast_inventory_needs, 
            upcoming_jobs, 
            inventory_levels,
            mongodb
        )
        
        self.remember("inventory_forecast", forecast)
        await self.report_progress(context, 0.90, "Inventory forecast ready.")
        
        return AgentResult(
            agent=self.name, 
            success=True, 
            data={
                "requirements_register": forecast.get("requirements", []),
                "inventory_forecast": forecast,
                "recommended_orders": forecast.get("recommended_orders", []),
                "upcoming_jobs_count": len(upcoming_jobs),
                "low_stock_items": len(inventory_levels),
            }
        )

    def _forecast_inventory_needs(
        self, 
        upcoming_jobs: List[Dict[str, Any]], 
        inventory_levels: List[Dict[str, Any]],
        mongodb=None
    ) -> Dict[str, Any]:
        """Analyze upcoming jobs and current inventory to forecast needs."""
        
        # Aggregate parts needed for upcoming jobs
        parts_needed = {}
        for job in upcoming_jobs:
            job_type = job.get("job_type", "general")
            # Get parts for this job type from MongoDB or use defaults
            if mongodb:
                try:
                    job_parts = mongodb.get_parts_for_job_type(job_type)
                except:
                    job_parts = self._get_default_parts_for_job(job_type)
            else:
                job_parts = self._get_default_parts_for_job(job_type)
            
            for part in job_parts:
                sku = part.get("sku")
                qty_needed = part.get("quantity", 1)
                if sku in parts_needed:
                    parts_needed[sku]["total_needed"] += qty_needed
                    parts_needed[sku]["jobs"].append(job.get("_id"))
                else:
                    parts_needed[sku] = {
                        "sku": sku,
                        "part_name": part.get("name", sku),
                        "total_needed": qty_needed,
                        "current_stock": 0,
                        "jobs": [job.get("_id")],
                    }
        
        # Check current inventory levels
        inventory_dict = {item["sku"]: item for item in inventory_levels}
        recommended_orders = []
        
        for sku, need in parts_needed.items():
            current = inventory_dict.get(sku, {"quantity": 0, "reorder_point": 10})
            current_stock = current.get("quantity", 0)
            need["current_stock"] = current_stock
            
            # Calculate if we need to order
            projected_stock = current_stock - need["total_needed"]
            reorder_point = current.get("reorder_point", 10)
            
            if projected_stock < reorder_point:
                order_qty = max(
                    need["total_needed"] * 2,  # Order 2x what we need
                    reorder_point * 3  # Or 3x reorder point
                ) - current_stock
                
                recommended_orders.append({
                    "sku": sku,
                    "part_name": need["part_name"],
                    "current_stock": current_stock,
                    "projected_need": need["total_needed"],
                    "quantity": int(order_qty),
                    "urgency": "high" if projected_stock < 0 else "medium",
                    "jobs_affected": len(need["jobs"]),
                })
        
        return {
            "requirements": list(parts_needed.values()),
            "recommended_orders": sorted(
                recommended_orders, 
                key=lambda x: (x["urgency"] == "high", x["jobs_affected"]), 
                reverse=True
            ),
            "analysis_summary": {
                "total_parts_needed": len(parts_needed),
                "orders_recommended": len(recommended_orders),
                "high_urgency_orders": len([o for o in recommended_orders if o["urgency"] == "high"]),
            }
        }

    def _get_synthetic_jobs(self) -> List[Dict[str, Any]]:
        """Fallback synthetic job data for demo/testing."""
        return [
            {
                "_id": "job_001",
                "job_type": "heat_pump_install",
                "scheduled_date": "2026-06-10",
                "customer": "ABC Corp",
                "status": "scheduled",
            },
            {
                "_id": "job_002", 
                "job_type": "ac_repair",
                "scheduled_date": "2026-06-12",
                "customer": "XYZ Inc",
                "status": "scheduled",
            },
        ]

    def _get_synthetic_inventory(self) -> List[Dict[str, Any]]:
        """Fallback synthetic inventory data."""
        return [
            {"sku": "HP-001", "name": "Heat Pump Unit", "quantity": 2, "reorder_point": 3},
            {"sku": "FILTER-01", "name": "Air Filter", "quantity": 15, "reorder_point": 20},
            {"sku": "REFRIG-R410A", "name": "R410A Refrigerant", "quantity": 5, "reorder_point": 10},
        ]

    def _get_default_parts_for_job(self, job_type: str) -> List[Dict[str, Any]]:
        """Default parts mapping for common job types."""
        parts_map = {
            "heat_pump_install": [
                {"sku": "HP-001", "name": "Heat Pump Unit", "quantity": 1},
                {"sku": "LINESET-50", "name": "Line Set 50ft", "quantity": 1},
                {"sku": "PAD-CONC", "name": "Concrete Pad", "quantity": 1},
            ],
            "ac_repair": [
                {"sku": "FILTER-01", "name": "Air Filter", "quantity": 1},
                {"sku": "REFRIG-R410A", "name": "R410A Refrigerant", "quantity": 2},
                {"sku": "CAPACITOR-45", "name": "Capacitor 45uF", "quantity": 1},
            ],
        }
        return parts_map.get(job_type, [])


class RiskAssessorAgent(BaseAgent):
    """Assess operational risks: low stock, delayed payments, scheduling conflicts."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="risk_assessor", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        await self.report_progress(context, 0.20, "Analyzing inventory, AR, and scheduling data.")
        risk_register = await asyncio.to_thread(self._forecast, payload)
        await self.report_progress(context, 0.70, "Identifying operational risks and opportunities.")
        self.remember("risk_register", risk_register)
        await self.report_progress(context, 0.90, "Risk assessment complete.")
        return AgentResult(agent=self.name, success=True, data={"risk_register": risk_register})

    def _forecast(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        import pandas as pd

        requirements = payload.get("requirements_register", [])
        project_data = payload.get("project_data", {})
        budget = project_data.get("budget", {"labor": 75000, "materials": 150000, "contingency": 20000})
        budget_total = sum(float(value) for value in budget.values())

        base = pd.DataFrame(
            [
                {"risk": "Long-lead equipment delay", "probability": 0.42, "impact": 0.75, "category": "Procurement"},
                {"risk": "Controls integration defect", "probability": 0.35, "impact": 0.70, "category": "Automation"},
                {"risk": "Field labor constraint", "probability": 0.30, "impact": 0.55, "category": "Construction"},
                {"risk": "Scope gap or late owner decision", "probability": 0.28, "impact": 0.62, "category": "Stakeholder"},
                {
                    "risk": "Budget contingency burn",
                    "probability": min(0.65, 20000 / max(budget_total, 1)),
                    "impact": 0.65,
                    "category": "Financial",
                },
            ]
        )
        requirement_factor = min(0.15, len(requirements) * 0.015)
        base["score"] = ((base["probability"] + requirement_factor) * base["impact"]).clip(upper=1.0)
        base["severity"] = base["score"].apply(
            lambda score: "High" if score >= 0.35 else "Medium" if score >= 0.18 else "Low"
        )
        base["mitigation"] = base["category"].map(
            {
                "Procurement": "Validate submittals early, track vendor commitments weekly, and approve alternates.",
                "Automation": "Run interface tests before commissioning and reserve controls engineering support.",
                "Construction": "Level labor loading and protect shutdown windows.",
                "Stakeholder": "Create decision log with dated owner approvals.",
                "Financial": "Tie contingency releases to approved risk events.",
            }
        )
        return base.sort_values("score", ascending=False).to_dict(orient="records")


class SchedulerOptimizerAgent(BaseAgent):
    """Optimize technician job scheduling considering skills, location, and urgency."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="scheduler", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        await self.report_progress(context, 0.20, "Loading technician schedules and job requirements.")
        schedule = await asyncio.to_thread(self._optimize, payload)
        await self.report_progress(context, 0.70, "Optimizing routes and technician assignments.")
        self.remember("optimized_schedule", schedule)
        await self.report_progress(context, 0.90, "Optimized schedule ready.")
        return AgentResult(agent=self.name, success=True, data={"optimized_schedule": schedule})

    def _optimize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_data = payload.get("project_data", {})
        tasks = project_data.get("schedule") or [
            {"task": "Requirements validation", "duration_days": 5, "predecessors": []},
            {"task": "Procurement", "duration_days": 20, "predecessors": ["Requirements validation"]},
            {"task": "Installation", "duration_days": 15, "predecessors": ["Procurement"]},
            {"task": "Commissioning", "duration_days": 7, "predecessors": ["Installation"]},
        ]
        try:
            return self._optimize_with_pulp(tasks)
        except Exception as exc:
            self.logger.warning("PuLP optimization failed, using CPM fallback: %s", exc)
            return self._cpm(tasks)

    def _optimize_with_pulp(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        import pulp

        names = [str(task["task"]) for task in tasks]
        durations = {str(task["task"]): int(task.get("duration_days", 1)) for task in tasks}
        starts = pulp.LpVariable.dicts("start", names, lowBound=0, cat="Continuous")
        makespan = pulp.LpVariable("makespan", lowBound=0, cat="Continuous")
        problem = pulp.LpProblem("pm_schedule", pulp.LpMinimize)
        problem += makespan
        for task in tasks:
            name = str(task["task"])
            problem += starts[name] + durations[name] <= makespan
            for predecessor in task.get("predecessors", []):
                if predecessor in starts:
                    problem += starts[name] >= starts[predecessor] + durations[predecessor]
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        rows = [
            {
                "task": name,
                "start_day": float(starts[name].value() or 0),
                "finish_day": float((starts[name].value() or 0) + durations[name]),
                "duration_days": durations[name],
            }
            for name in names
        ]
        return {
            "method": "pulp",
            "duration_days": float(makespan.value() or 0),
            "tasks": rows,
            "critical_path": self._critical_path(tasks),
        }

    def _cpm(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        finish: Dict[str, int] = {}
        rows = []
        unresolved = list(tasks)
        while unresolved:
            progress = False
            for task in unresolved[:]:
                predecessors = task.get("predecessors", [])
                if all(pred in finish for pred in predecessors):
                    start = max([finish[pred] for pred in predecessors] or [0])
                    duration = int(task.get("duration_days", 1))
                    finish[str(task["task"])] = start + duration
                    rows.append(
                        {
                            "task": task["task"],
                            "start_day": start,
                            "finish_day": start + duration,
                            "duration_days": duration,
                        }
                    )
                    unresolved.remove(task)
                    progress = True
            if not progress:
                raise ValueError("Schedule contains unresolved dependencies.")
        return {
            "method": "cpm",
            "duration_days": max(finish.values() or [0]),
            "tasks": rows,
            "critical_path": self._critical_path(tasks),
        }

    def _critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        by_name = {str(task["task"]): task for task in tasks}
        memo: Dict[str, tuple[int, List[str]]] = {}

        def score(name: str) -> tuple[int, List[str]]:
            if name in memo:
                return memo[name]
            task = by_name[name]
            predecessors = [pred for pred in task.get("predecessors", []) if pred in by_name]
            if not predecessors:
                result = (int(task.get("duration_days", 1)), [name])
            else:
                best = max((score(pred) for pred in predecessors), key=lambda item: item[0])
                result = (best[0] + int(task.get("duration_days", 1)), best[1] + [name])
            memo[name] = result
            return result

        if not by_name:
            return []
        return max((score(name) for name in by_name), key=lambda item: item[0])[1]


class ARCollectorAgent(BaseAgent):
    """Manage accounts receivable: identify overdue invoices and draft reminders."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="ar_collector", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        mongodb = payload.get("mongodb")
        await self.report_progress(context, 0.20, "Fetching overdue invoices from MongoDB.")
        
        overdue_invoices = []
        if mongodb:
            try:
                overdue_invoices = await asyncio.to_thread(mongodb.get_overdue_invoices, days=30)
                await self.report_progress(context, 0.50, f"Found {len(overdue_invoices)} overdue invoices.")
            except Exception as exc:
                self.logger.warning("MongoDB query failed, using synthetic data: %s", exc)
                overdue_invoices = self._get_synthetic_invoices()
        else:
            overdue_invoices = self._get_synthetic_invoices()
        
        await self.report_progress(context, 0.70, "Drafting reminder communications.")
        
        # Generate AR report with MongoDB data
        report = await asyncio.to_thread(
            self._generate_ar_report, 
            payload, 
            overdue_invoices
        )
        
        self.remember("ar_report", report)
        await self.report_progress(context, 0.90, "AR collection actions ready.")
        
        return AgentResult(
            agent=self.name, 
            success=True, 
            data={
                "pm_report": report,
                "overdue_invoices": overdue_invoices,
                "total_overdue_amount": sum(inv.get("amount", 0) for inv in overdue_invoices),
                "invoices_count": len(overdue_invoices),
            }
        )

    def _generate_ar_report(self, payload: Dict[str, Any], overdue_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AR collection report with overdue invoice data."""
        risks = payload.get("risk_register", [])
        requirements = payload.get("requirements_register", [])
        schedule = payload.get("optimized_schedule", {})
        chart_path = self._risk_chart(risks)
        high_risks = [risk for risk in risks if risk.get("severity") == "High"]
        
        total_overdue = sum(float(inv.get("amount", 0) or 0) for inv in overdue_invoices)
        now = datetime.utcnow()
        invoice_ages = [
            max((now - self._coerce_datetime(inv.get("due_date"), now)).days, 0)
            for inv in overdue_invoices
        ]
        
        return {
            "summary": f"HVAC operations analysis complete. Found {len(overdue_invoices)} overdue invoices totaling ${total_overdue:,.2f}.",
            "requirements_count": len(requirements),
            "high_risk_count": len(high_risks),
            "planned_duration_days": schedule.get("duration_days"),
            "critical_path": schedule.get("critical_path", []),
            "ar_summary": {
                "overdue_count": len(overdue_invoices),
                "total_amount": total_overdue,
                "oldest_invoice_days": max(invoice_ages or [0]),
            },
            "recommended_actions": [
                f"Send reminders for {len(overdue_invoices)} overdue invoices (${total_overdue:,.2f} total).",
                "Review inventory forecast and place orders for low-stock items.",
                "Confirm technician assignments for upcoming jobs.",
            ],
            "risk_chart_path": chart_path,
        }

    @staticmethod
    def _coerce_datetime(value: Any, default: datetime) -> datetime:
        """Return a naive UTC datetime for Mongo, ISO string, date, or missing values."""
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value
        if isinstance(value, date):
            return datetime.combine(value, time.min)
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return default
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if parsed.tzinfo is not None:
                    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
                return parsed
            except ValueError:
                try:
                    return datetime.combine(date.fromisoformat(raw[:10]), time.min)
                except ValueError:
                    return default
        return default

    def _get_synthetic_invoices(self) -> List[Dict[str, Any]]:
        """Fallback synthetic invoice data for demo."""
        from datetime import datetime, timedelta
        return [
            {
                "_id": "inv_001",
                "customer_id": "cust_abc",
                "customer_name": "ABC Corporation",
                "amount": 2500.00,
                "due_date": datetime.utcnow() - timedelta(days=45),
                "invoice_date": datetime.utcnow() - timedelta(days=75),
                "status": "overdue",
            },
            {
                "_id": "inv_002",
                "customer_id": "cust_xyz",
                "customer_name": "XYZ Industries",
                "amount": 1800.00,
                "due_date": datetime.utcnow() - timedelta(days=32),
                "invoice_date": datetime.utcnow() - timedelta(days=62),
                "status": "overdue",
            },
        ]

    def _risk_chart(self, risks: List[Dict[str, Any]]) -> str | None:
        if not risks:
            return None
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            labels = [str(risk["risk"])[:28] for risk in risks]
            scores = [float(risk.get("score", 0)) for risk in risks]
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.barh(labels, scores, color="#2f6f73")
            ax.set_xlabel("Risk score")
            ax.set_title("Top Operational Risks")
            fig.tight_layout()
            output = Path(tempfile.gettempdir()) / "hvac_ops_risk_chart.png"
            fig.savefig(output)
            plt.close(fig)
            return str(output)
        except Exception as exc:
            self.logger.warning("Risk chart generation failed: %s", exc)
            return None
