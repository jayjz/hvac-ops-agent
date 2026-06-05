"""Base classes and shared utilities for AgentForge PM agents."""

from __future__ import annotations

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, MutableMapping, Optional

import yaml
from pydantic import BaseModel, Field

ProgressCallback = Callable[[str, float, str], Awaitable[None] | None]


class AgentContext(BaseModel):
    """Runtime context shared by PM agents."""

    job_id: Optional[str] = None
    project_path: Optional[str] = None
    goals: list[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Standard result returned by every agent."""

    agent: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base for all AgentForge PM agents."""

    def __init__(
        self,
        name: str,
        config_path: str | Path = "config.yaml",
        tools: Optional[Dict[str, Any]] = None,
        memory: Optional[MutableMapping[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        self.name = name
        self.config_path = Path(config_path)
        self.tools: Dict[str, Any] = tools or {}
        self.memory: MutableMapping[str, Any] = memory if memory is not None else {}
        self.progress_callback = progress_callback
        self.logger = logging.getLogger(f"agentforge_pm.{self.name}")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            self.logger.warning("Config file not found: %s", self.config_path)
            return {}
        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or {}
            if not isinstance(loaded, dict):
                self.logger.warning(
                    "Config root is not a mapping: %s", self.config_path
                )
                return {}
            return loaded
        except Exception as exc:
            self.logger.exception("Failed to load config from %s", self.config_path)
            return {"_config_error": str(exc)}

    async def report_progress(
        self, context: AgentContext, progress: float, detail: str
    ) -> None:
        """Send a progress update through the configured callback."""

        if not context.job_id or self.progress_callback is None:
            return
        bounded = max(0.0, min(1.0, progress))
        try:
            result = self.progress_callback(context.job_id, bounded, detail)
            if inspect.isawaitable(result):
                await result
        except Exception:
            self.logger.exception("Progress callback failed for job %s", context.job_id)

    async def run(
        self, context: AgentContext, payload: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Execute the agent with consistent logging and error handling."""

        payload = payload or {}
        await self.report_progress(context, 0.0, f"{self.name} started.")
        try:
            result = await self.execute(context, payload)
            await self.report_progress(context, 1.0, f"{self.name} completed.")
            return result
        except asyncio.CancelledError:
            self.logger.warning("%s cancelled", self.name)
            raise
        except Exception as exc:
            self.logger.exception("%s failed", self.name)
            await self.report_progress(context, 1.0, f"{self.name} failed: {exc}")
            return AgentResult(agent=self.name, success=False, errors=[str(exc)])

    @abstractmethod
    async def execute(
        self, context: AgentContext, payload: Dict[str, Any]
    ) -> AgentResult:
        """Implement domain-specific agent behavior."""

    def remember(self, key: str, value: Any) -> None:
        self.memory[f"{self.name}:{key}"] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self.memory.get(f"{self.name}:{key}", default)

    def model_name(self, default: str = "gpt-4o") -> str:
        models = self.config.get("codeforge", {}).get("models", {})
        pm_models = models.get("pm", {})
        if isinstance(pm_models, dict) and self.name in pm_models:
            return str(pm_models[self.name])
        if self.name == "lead_architect":
            return str(models.get("lead_architect", default))
        return default
