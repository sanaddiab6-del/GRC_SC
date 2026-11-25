import hashlib
import json
from pathlib import Path
import runpy


# Synthetic source rows for planner accounting; these are not NIST CSF text.
REQUIREMENT_TOPICS = (
    "governance accountability",
    "identity authentication user access",
    "asset inventory ownership",
    "data protection confidentiality",
    "network firewall segmentation",
    "incident response forensic review",
    "backup restore recovery",
    "patch configuration hardening",
    "monitoring detection audit trail",
    "third-party supplier review",
    "cloud hosting oversight",
    "application secure coding",
    "employee awareness training",
    "physical facility access",
    "encrypt certificate key management",
)
REQUIREMENTS = [
    {
        "requirement_id": f"fixture-{index:03d}",
        "reference": f"FIXTURE-{index:03d}",
        "requirement_name": topic,
        "description": f"Document the owner and review evidence for {topic} ({index}).",
    }
    for index, topic in enumerate(
        (REQUIREMENT_TOPICS[i % len(REQUIREMENT_TOPICS)] for i in range(106)),
        start=1,
    )
]
SYSTEMS = (
    "warehouse management",
    "transport management",
    "fleet GPS",
    "shipment portal",
    "tracking APIs",
    "ERP/finance",
    "Microsoft 365/identity",
    "carrier integrations",
    "cloud databases",
    "backups",
    "corporate network",
)
OBJECTIVE = (
    "Assess Meridian Logistics Group against NIST CSF 2.0. Systems: "
    + "; ".join(SYSTEMS)
)
# Load the real planner directly. Its package initializer imports LLM adapters.
PLANNER = Path(__file__).resolve().parents[1] / "backend/ai_onboarding/sico_case_coverage.py"
plan_generation_queue = runpy.run_path(str(PLANNER))["plan_generation_queue"]

# Recorded with pytest against the original planner on this exact fixture.
BASELINE_RECORDS = 258
BASELINE_TASK_LIST_SHA256 = "7607dce06cc473082e0f0006e50f61387112413a6e5109d5698415ab28fc8eda"


def test_sico_call_accounting():
    plan = plan_generation_queue(authorized_requirements=REQUIREMENTS, objective=OBJECTIVE)
    queue = plan["generation_queue"]
    summary = plan["generation_summary"]
    assert summary["explicit_scope_subjects"] == list(SYSTEMS)
    assert sum(task["activity_number"] == 10 for task in queue) == len(REQUIREMENTS) == 106
    assert {task["activity_number"] for task in queue} == set(range(1, 17))

    for task in queue:
        activity = task["activity_number"]
        if activity in {1, 3, 14, 16}:
            expected_mode = "deterministic"
        elif activity == 2:
            expected_mode = "ai_single"
        else:
            expected_mode = "ai_batchable"
        assert task["execution_mode"] == expected_mode

    original_fields = [
        {field: value for field, value in task.items() if field != "execution_mode"}
        for task in queue
    ]
    queue_json = json.dumps(original_fields, sort_keys=True, separators=(",", ":"))
    assert len(queue) == summary["planned_qwen_detail_drafts"] == BASELINE_RECORDS
    assert hashlib.sha256(queue_json.encode("utf-8")).hexdigest() == BASELINE_TASK_LIST_SHA256

    records = summary["records_planned"]
    assert records == {"deterministic": 4, "ai_batchable": 253, "ai_single": 1}
    assert sum(records.values()) == len(queue)
    # 46 batches across 11 activities, plus one case-wide scope request.
    assert summary["model_calls_planned"] == 47

    print("| Plan | Records | Deterministic | AI batchable | AI single | Model calls |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    print(f"| BEFORE, one successful attempt per task | {BASELINE_RECORDS} | - | - | - | {BASELINE_RECORDS} |")
    print(
        f"| AFTER, estimate | {sum(records.values())} | {records['deterministic']} | "
        f"{records['ai_batchable']} | {records['ai_single']} | {summary['model_calls_planned']} |"
    )
