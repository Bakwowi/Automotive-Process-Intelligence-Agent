from typing import TypedDict, List, Optional
import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Adjust parent index if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DefectInput(TypedDict):
    vehicle_model: str
    year: int
    mileage_km: int
    error_codes: List[str]
    symptom_description: str
    reported_by: str


class ClassificationResult(TypedDict):
    defect_category: str        # e.g. "engine", "transmission", "electrical"
    severity: str               # "low", "medium", "high", "safety_critical"
    is_known_issue: bool
    search_keywords: List[str]  # Keywords for the researcher to use
    reasoning: str


class ResearchResult(TypedDict):
    relevant_documents: List[dict]
    root_cause_hypothesis: str
    recommended_procedure: str
    required_parts: List[str]
    estimated_repair_time_hours: float
    sources: List[str]


class ValidationResult(TypedDict):
    complies_with_standards: bool
    applicable_standards: List[str]
    compliance_notes: str
    warnings: List[str]
    requires_escalation: bool


class FinalReport(TypedDict):
    report_id: str
    vehicle_info: dict
    defect_category: str
    severity: str
    root_cause: str
    recommended_action: str
    required_parts: List[str]
    estimated_hours: float
    standards_compliance: str
    warnings: List[str]
    sources: List[str]
    priority: str               # "routine", "urgent", "immediate"


class AgentState(TypedDict):
    # Input
    report_id: str
    defect_input: DefectInput

    # Intermediate outputs (built up as graph progresses)
    classification: Optional[ClassificationResult]
    research: Optional[ResearchResult]
    validation: Optional[ValidationResult]

    # Final output
    report: Optional[FinalReport]

    # Human-in-the-loop
    human_approved: Optional[bool]
    human_feedback: Optional[str]

    # Iteration tracking (prevents infinite loops)
    iteration_count: int
    error_log: List[str]