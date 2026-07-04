"""Lead Architect agent for PM planning."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv
from openai import AsyncOpenAI

from core.agents.base import AgentContext, AgentResult, BaseAgent


class LeadArchitect(BaseAgent):
    """Ingest project artifacts and create a specialist execution plan."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="lead_architect", **kwargs)
        load_dotenv()
        self.client = (
            AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if os.getenv("OPENAI_API_KEY")
            else None
        )

    async def execute(
        self, context: AgentContext, payload: Dict[str, Any]
    ) -> AgentResult:
        await self.report_progress(context, 0.15, "Ingesting project artifacts.")
        project_data = await asyncio.to_thread(
            self._ingest_project, context.project_path
        )

        await self.report_progress(context, 0.45, "Building PM execution plan.")
        plan = await self._create_plan(project_data, context.goals)

        self.remember("project_data", project_data)
        self.remember("execution_plan", plan)
        return AgentResult(
            agent=self.name,
            success=True,
            data={"project_data": project_data, "execution_plan": plan},
        )

    def _ingest_project(self, project_path: str | None) -> Dict[str, Any]:
        if not project_path or not Path(project_path).exists():
            return self._synthetic_project_data()

        root = Path(project_path)
        files: List[Dict[str, Any]] = []
        for path in self._iter_supported_files(root):
            try:
                files.append(self._read_file(path))
            except Exception as exc:
                self.logger.warning("Could not ingest %s: %s", path, exc)

        if not files:
            return self._synthetic_project_data()

        return {"source": str(root), "files": files, "synthetic": False}

    def _iter_supported_files(self, root: Path) -> Iterable[Path]:
        supported = {".txt", ".md", ".csv", ".xlsx", ".xlsm", ".pdf"}
        if root.is_file() and root.suffix.lower() in supported:
            yield root
            return
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in supported:
                yield path

    def _read_file(self, path: Path) -> Dict[str, Any]:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md", ".csv"}:
            return {
                "path": str(path),
                "type": suffix,
                "content": path.read_text(encoding="utf-8", errors="replace")[:12000],
            }
        if suffix in {".xlsx", ".xlsm"}:
            return self._read_excel(path)
        if suffix == ".pdf":
            return self._read_pdf(path)
        return {"path": str(path), "type": suffix, "content": ""}

    def _read_excel(self, path: Path) -> Dict[str, Any]:
        import pandas as pd

        workbook = pd.read_excel(path, sheet_name=None)
        sheets = {
            name: frame.head(50).fillna("").to_dict(orient="records")
            for name, frame in workbook.items()
        }
        return {"path": str(path), "type": "excel", "sheets": sheets}

    def _read_pdf(self, path: Path) -> Dict[str, Any]:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return {"path": str(path), "type": "pdf", "content": text[:12000]}

    def _synthetic_project_data(self) -> Dict[str, Any]:
        return {
            "source": "synthetic",
            "synthetic": True,
            "files": [
                {
                    "path": "synthetic_scope.md",
                    "type": ".md",
                    "content": (
                        "HVAC retrofit for a mixed-use facility. Replace AHUs, integrate BAS controls, "
                        "coordinate commissioning, manage procurement lead times, and maintain operations."
                    ),
                }
            ],
            "schedule": [
                {
                    "task": "Requirements validation",
                    "duration_days": 5,
                    "predecessors": [],
                },
                {
                    "task": "Equipment procurement",
                    "duration_days": 25,
                    "predecessors": ["Requirements validation"],
                },
                {
                    "task": "Installation",
                    "duration_days": 15,
                    "predecessors": ["Equipment procurement"],
                },
                {
                    "task": "Commissioning",
                    "duration_days": 7,
                    "predecessors": ["Installation"],
                },
            ],
            "budget": {"labor": 85000, "materials": 210000, "contingency": 35000},
        }

    async def _create_plan(
        self, project_data: Dict[str, Any], goals: List[str]
    ) -> List[Dict[str, Any]]:
        if self.client is None:
            return self._fallback_plan(goals)

        prompt = {
            "role": "system",
            "content": (
                "You are the Lead Architect for AgentForge PM. Create JSON only: a list of tasks "
                "for requirements, risk, schedule, and report specialists. Include id, specialist, "
                "objective, inputs, and expected_output."
            ),
        }
        user = {
            "role": "user",
            "content": json.dumps(
                {"goals": goals, "project_data": project_data}, default=str
            )[:30000],
        }
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name(),
                messages=[prompt, user],
                temperature=0.2,
            )
            content = response.choices[0].message.content or "[]"
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except Exception as exc:
            self.logger.warning("LLM planning failed, using fallback plan: %s", exc)
        return self._fallback_plan(goals)

    def _fallback_plan(self, goals: List[str]) -> List[Dict[str, Any]]:
        goal_text = "; ".join(goals) if goals else "Create a PM execution baseline."
        return [
            {
                "id": "REQ-001",
                "specialist": "requirements",
                "objective": f"Extract and validate scope: {goal_text}",
                "inputs": ["project_data"],
                "expected_output": "requirements_register",
            },
            {
                "id": "RISK-001",
                "specialist": "risk",
                "objective": "Forecast PM delivery, safety, procurement, and cost risks.",
                "inputs": ["project_data", "requirements_register"],
                "expected_output": "risk_register",
            },
            {
                "id": "SCH-001",
                "specialist": "scheduler",
                "objective": "Optimize task sequence and identify critical path.",
                "inputs": ["project_data", "risk_register"],
                "expected_output": "optimized_schedule",
            },
            {
                "id": "RPT-001",
                "specialist": "ar_collector",
                "objective": "Generate AR collection actions and operations summary.",
                "inputs": [
                    "requirements_register",
                    "risk_register",
                    "optimized_schedule",
                ],
                "expected_output": "pm_report",
            },
        ]
