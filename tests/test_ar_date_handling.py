from __future__ import annotations

from datetime import datetime, timedelta

import pytest

import core.orchestrator as orchestrator
from core.agents import AgentResult
from core.agents.specialists import ARCollectorAgent
from streamlit_app import build_demo_dataset


def test_ar_report_accepts_string_due_dates() -> None:
    agent = ARCollectorAgent()
    due_date = (datetime.utcnow() - timedelta(days=41)).isoformat()

    report = agent._generate_ar_report(
        payload={},
        overdue_invoices=[
            {
                "invoice_id": "INV-STRING",
                "amount": "1250.00",
                "due_date": due_date,
            }
        ],
    )

    assert report["ar_summary"]["oldest_invoice_days"] >= 40
    assert report["ar_summary"]["total_amount"] == 1250.00


def test_ar_report_uses_safe_default_for_bad_due_dates() -> None:
    agent = ARCollectorAgent()

    report = agent._generate_ar_report(
        payload={},
        overdue_invoices=[
            {
                "invoice_id": "INV-BAD-DATE",
                "amount": 500,
                "due_date": "not-a-date",
            }
        ],
    )

    assert report["ar_summary"]["oldest_invoice_days"] == 0
    assert report["ar_summary"]["total_amount"] == 500.00


def test_streamlit_demo_dataset_uses_datetime_due_dates() -> None:
    dataset = build_demo_dataset()

    assert dataset["overdue_invoices"]
    assert all(
        isinstance(invoice["due_date"], datetime)
        for invoice in dataset["overdue_invoices"]
    )


@pytest.mark.asyncio
async def test_orchestrator_continues_when_specialist_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLeadArchitect:
        def __init__(self, **_: object) -> None:
            pass

        async def run(self, context: object, payload: object | None = None) -> AgentResult:
            return AgentResult(
                agent="lead_architect",
                success=True,
                data={"project_data": {"schedule": []}, "execution_plan": []},
            )

    class FakeSpecialist:
        def __init__(self, name: str, result: AgentResult) -> None:
            self.name = name
            self._result = result

        async def run(self, context: object, payload: object | None = None) -> AgentResult:
            return self._result

    monkeypatch.setattr(orchestrator, "LeadArchitect", FakeLeadArchitect)
    monkeypatch.setattr(
        orchestrator,
        "InventoryForecasterAgent",
        lambda **_: FakeSpecialist(
            "inventory_forecaster",
            AgentResult(agent="inventory_forecaster", success=False, errors=["boom"]),
        ),
    )
    monkeypatch.setattr(
        orchestrator,
        "RiskAssessorAgent",
        lambda **_: FakeSpecialist(
            "risk_assessor",
            AgentResult(
                agent="risk_assessor",
                success=True,
                data={"risk_register": []},
            ),
        ),
    )
    monkeypatch.setattr(
        orchestrator,
        "SchedulerOptimizerAgent",
        lambda **_: FakeSpecialist(
            "scheduler",
            AgentResult(
                agent="scheduler",
                success=True,
                data={"optimized_schedule": {"tasks": [], "critical_path": []}},
            ),
        ),
    )
    monkeypatch.setattr(
        orchestrator,
        "ARCollectorAgent",
        lambda **_: FakeSpecialist(
            "ar_collector",
            AgentResult(
                agent="ar_collector",
                success=True,
                data={
                    "pm_report": {},
                    "overdue_invoices": [],
                    "total_overdue_amount": 0,
                    "invoices_count": 0,
                },
            ),
        ),
    )

    result = await orchestrator.run_pm_job(job_id="demo", goals=[], require_approval=True)

    assert result["specialist_errors"] == [
        {"agent": "inventory_forecaster", "errors": ["boom"]}
    ]
    assert result["recommended_orders"] == []
