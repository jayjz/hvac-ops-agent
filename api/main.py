import logging
import uuid
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from core.logging_config import configure_logging
from core.orchestrator import run_pm_job

configure_logging()
logger = logging.getLogger("hvac_opsforge.api")

app = FastAPI(
    title="HVAC OpsForge API",
    description="API for HVAC operations automation: inventory forecasting, job scheduling, and AR management.",
    version="1.0.0",
)

# --- Pydantic Models ---

class PMJobRequest(BaseModel):
    repo_url: str = Field(..., example="https://github.com/someuser/somerepo")
    goals: List[str] = Field(..., example=["Forecast inventory for upcoming heat pump installs", "Optimize technician schedules for next week"])
    branch_name: str = Field("codeforge-modernized", example="feat/ai-upgrade")
    project_path: Optional[str] = Field(None, example="C:/projects/hvac-retrofit")

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str # PENDING, RUNNING, COMPLETED, FAILED
    progress: float = 0.0
    details: str
    result: Optional[dict] = None

# --- In-Memory Job Store (for demonstration) ---
# In production, replace this with Redis or a database.
jobs: Dict[str, JobStatus] = {}

# --- Background Tasks ---

async def run_modernization_task(job_id: str, request: PMJobRequest):
    """Run the HVAC OpsForge workflow for an accepted job."""
    await run_pm_job(
        job_id=job_id,
        goals=request.goals,
        project_path=request.project_path,
        jobs=jobs,
    )


# --- API Endpoints ---

@app.get("/api", tags=["Status"])
def read_root():
    return {"service": "HVAC OpsForge API", "status": "online"}


@app.post("/api/jobs", response_model=JobResponse, status_code=202, tags=["Jobs"])
async def start_modernization_job(
    request: PMJobRequest,
    background_tasks: BackgroundTasks
):
    """
    Starts a new HVAC OpsForge job.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = JobStatus(job_id=job_id, status="PENDING", details="Job accepted and queued.")
    
    background_tasks.add_task(run_modernization_task, job_id, request)
    
    return JobResponse(
        job_id=job_id,
        status="PENDING",
        message="HVAC OpsForge job has been successfully queued."
    )

@app.get("/api/jobs/{job_id}", response_model=JobStatus, tags=["Jobs"])
async def get_job_status(job_id: str):
    """
    Retrieves the status of a specific operations job.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@app.get("/api/jobs", response_model=List[JobStatus], tags=["Jobs"])
async def list_all_jobs():
    """
    Lists all submitted jobs.
    """
    return list(jobs.values())
