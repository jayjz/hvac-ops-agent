from __future__ import annotations

from datetime import datetime, timedelta

from core.dispatch_baseline import (
    assemble_dispatch_baseline,
    prioritize_ar_queue,
    render_dispatch_baseline_markdown,
)


def test_prioritize_ar_queue_ranks_by_amount_and_age() -> None:
    now = datetime.utcnow()
    queue = prioritize_ar_queue(
        [
            {
                "invoice_id": "INV-SMALL",
                "customer_name": "Small Customer",
                "amount": 250,
                "due_date": now - timedelta(days=20),
            },
            {
                "invoice_id": "INV-LARGE",
                "customer_name": "Large Customer",
                "amount": 8500,
                "due_date": now - timedelta(days=45),
            },
        ]
    )

    assert queue[0]["invoice_id"] == "INV-LARGE"
    assert queue[0]["priority"] == "P1"
    assert queue[0]["rank"] == 1


def test_assemble_dispatch_baseline_outputs_reports() -> None:
    baseline = assemble_dispatch_baseline(
        goals=["Improve dispatch reliability", "Recover overdue AR"],
        project_data={
            "source": "synthetic",
            "schedule": [
                {"task": "Validate scope", "duration_days": 3, "predecessors": []},
                {"task": "Procure parts", "duration_days": 7, "predecessors": ["Validate scope"]},
            ],
        },
        execution_plan=[],
        inventory_data={
            "recommended_orders": [
                {"sku": "FILTER-01", "part_name": "Filter", "quantity": 12, "urgency": "high"}
            ]
        },
        risk_data={
            "risk_register": [
                {
                    "risk": "Supplier lead-time leverage",
                    "probability": 0.4,
                    "impact": 0.8,
                    "category": "Procurement",
                }
            ]
        },
        schedule_data={},
        ar_data={
            "overdue_invoices": [
                {
                    "invoice_id": "INV-001",
                    "customer_name": "ABC Manufacturing",
                    "amount": 4500,
                    "due_date": datetime.utcnow() - timedelta(days=50),
                }
            ]
        },
        data_source="synthetic",
    )

    assert baseline["report_type"] == "Dispatch Baseline"
    assert baseline["requirements_register"]
    assert baseline["risk_register"][0]["porter_force"] == "Supplier power"
    assert baseline["ar_follow_up_queue"][0]["priority"] == "P1"
    assert baseline["roi_summary"]["estimated_value"] > 0
    assert "# HVAC OpsForge Dispatch Baseline" in baseline["reports"]["markdown"]
    assert '"report_type": "Dispatch Baseline"' in baseline["reports"]["json"]


def test_render_markdown_includes_actions_and_roi() -> None:
    baseline = {
        "generated_at": "2026-07-03T00:00:00Z",
        "data_source": "synthetic",
        "summary": {
            "requirements_count": 1,
            "high_risk_count": 1,
            "planned_duration_days": 10,
            "ar_recovery_opportunity": 1000,
            "estimated_roi": 1.5,
        },
        "recommended_actions": ["Approve baseline."],
        "risk_register": [
            {
                "rank": 1,
                "risk": "Supplier delay",
                "severity": "High",
                "porter_force": "Supplier power",
                "score": 0.5,
            }
        ],
        "ar_follow_up_queue": [
            {
                "rank": 1,
                "customer": "ABC",
                "priority": "P1",
                "amount": 1000,
                "days_overdue": 40,
            }
        ],
        "roi_summary": {
            "expected_ar_recovery": 350,
            "avoided_delay_cost": 1850,
            "margin_protection": 5000,
            "assumptions": ["Assumption."],
        },
    }

    markdown = render_dispatch_baseline_markdown(baseline)

    assert "## Executive Summary" in markdown
    assert "Estimated ROI: 1.5x" in markdown
    assert "Approve baseline." in markdown
