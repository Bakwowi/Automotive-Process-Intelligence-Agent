import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Adjust parent index if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import uuid
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langgraph.types import Command
import sqlite3
from dotenv import load_dotenv
import os

from orchestrator.graph import graph
from orchestrator.state import AgentState

load_dotenv()
app = FastAPI(title="Automotive Process Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Request / Response models ─────────────────────────────────────────────────

class DefectSubmission(BaseModel):
    vehicle_model: str
    year: int
    mileage_km: int
    error_codes: List[str] = []
    symptom_description: str
    reported_by: str = "engineer"


class HumanDecision(BaseModel):
    report_id: str
    approved: bool
    feedback: Optional[str] = ""


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "sqlLite_db" / "apia_db.db"
# CHROMADB_PATH = BASE_DIR / "data" / "chroma_db"
LOGS_DIR = BASE_DIR / "logs.json"

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/submit-defect")
async def submit_defect(submission: DefectSubmission):
    """
    Starts a new agent run for a defect report.
    The graph runs until it hits the human_checkpoint interrupt,
    then pauses and returns the generated report for review.
    """
    report_id = str(uuid.uuid4())[:8].upper()
    thread_id = f"report_{report_id}"

    # Save initial record to DB

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO defect_reports (report_id, input_data, status)
            VALUES (:report_id, :input_data, 'processing')
        """, {
            "report_id": report_id,
            "input_data": json.dumps(submission.dict())
        })
        conn.commit()

    # Build initial state
    initial_state: AgentState = {
        "report_id": report_id,
        "defect_input": dict(submission),
        "classification": None,
        "research": None,
        "validation": None,
        "report": None,
        "human_approved": None,
        "human_feedback": None,
        "iteration_count": 0,
        "error_log": []
    }

    config = {"configurable": {"thread_id": thread_id}}

    # Run graph — will pause at human_checkpoint
    result = graph.invoke(initial_state, config=config)

    # try:
    #     print("submit defect", result)
    #     with open(LOGS_DIR,"r+", encoding="utf-8") as file:
    #         arr = json.load(file)
    #         arr.append(result) 
    #         file.seek(0)
    #         json.dump(arr, file, indent=4, default=str)
    #         file.truncate()
    # except Exception as exc:
    #     print(exc)
       

    # At this point the graph is paused at interrupt()
    # Return the generated report for human review
    return {
        "report_id": report_id,
        "thread_id": thread_id,
        "status": "awaiting_review",
        "report": result.get("report"),
        "classification": result.get("classification"),
        "iteration": result.get("iteration_count", 1)
    }


@app.post("/human-decision")
async def human_decision(decision: HumanDecision):
    """
    Resumes the paused graph with the human's approve/reject decision.
    If rejected, the graph loops back to the researcher with feedback.
    If approved, the graph saves the report and ends.
    """
    thread_id = f"report_{decision.report_id}"
    config = {"configurable": {"thread_id": thread_id}}

    # Resume the graph from the interrupt point
    result = graph.invoke(
        Command(resume={
            "approved": decision.approved,
            "feedback": decision.feedback or ""
        }),
        config=config
    )

    if decision.approved:
        return {
            "status": "approved",
            "report_id": decision.report_id,
            "message": "Report approved and saved.",
            "report": result.get("report")
        }
    else:
        # Graph looped — return the revised report
        return {
            "status": "revised",
            "report_id": decision.report_id,
            "message": "Report revised based on feedback. Please review again.",
            "report": result.get("report"),
            "iteration": result.get("iteration_count")
        }


@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Fetches a saved report from sqlLite."""
    with sqlite3.connect() as conn:

        cursor = conn.cursor()
        row = cursor.execute("""
            SELECT report_data, status, created_at
            FROM defect_reports
            WHERE report_id = :report_id
        """, {"report_id": report_id}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "report_id": report_id,
        "status": row[1],
        "created_at": str(row[2]),
        "report": json.loads(row[0]) if row[0] else None
    }


@app.get("/health")
async def health():
    return {"status": "ok"}