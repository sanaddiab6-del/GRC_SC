"""
Assessment Execution Router
Enterprise-grade assessment lifecycle API with RBAC enforcement
NCA ECC/CCC/PDPL compliance assessments
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.auth import get_current_user
from assessment.models import (
    AssessmentInstance,
    AssessmentResponse,
    AssessmentStatusHistory,
    AssessmentStatus,
    ASSESSMENT_LIFECYCLE_TRANSITIONS,
)
from assessment.schemas import (
    AssessmentInstanceCreate,
    AssessmentInstanceUpdate,
    AssessmentInstanceResponse,
    AssessmentInstanceListResponse,
    AssessmentLaunchRequest,
    AssessmentAssignRequest,
    AssessmentSubmitRequest,
    AssessmentReviewRequest,
    AssessmentApprovalRequest,
    AssessmentCloseRequest,
    AssessmentResponseCreate,
    AssessmentResponseUpdate,
    AssessmentResponseResponse,
    AssessmentResponseListResponse,
    AssessmentStatusHistoryResponse,
    AssessmentDashboardStats,
)

router = APIRouter(prefix="/assessments", tags=["Assessment Execution"])


# ============================================================================
# Helper Functions
# ============================================================================

def _validate_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if status transition is allowed"""
    current = AssessmentStatus(current_status)
    new = AssessmentStatus(new_status)
    allowed_transitions = ASSESSMENT_LIFECYCLE_TRANSITIONS.get(current, set())
    return new in allowed_transitions


async def _log_status_change(
    db: AsyncSession,
    assessment_id: int,
    from_status: str,
    to_status: str,
    changed_by_id: int,
    comment: Optional[str] = None,
    approval_decision: Optional[str] = None,
    approval_comment: Optional[str] = None,
    request: Optional[Request] = None,
):
    """Log status change to audit trail"""
    history = AssessmentStatusHistory(
        assessment_id=assessment_id,
        from_status=from_status,
        to_status=to_status,
        changed_by_id=changed_by_id,
        changed_at=datetime.utcnow(),
        comment=comment,
        approval_decision=approval_decision,
        approval_comment=approval_comment,
        ip_address=request.client.host if request and request.client else None,  # type: ignore
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(history)
    await db.flush()


async def _calculate_assessment_score(db: AsyncSession, assessment_id: int):
    """Calculate assessment compliance score and progress"""
    # Get all responses for this assessment
    query = select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment_id)
    result = await db.execute(query)
    responses = result.scalars().all()

    if not responses:
        return {
            "progress_percentage": 0.0,
            "compliance_score": None,
            "weighted_score": None,
            "compliant_count": 0,
            "non_compliant_count": 0,
            "partial_compliant_count": 0,
            "not_applicable_count": 0,
            "completed_controls": 0,
        }

    total_controls = len(responses)
    compliant = sum(1 for r in responses if str(r.compliance_status) == "compliant")
    non_compliant = sum(1 for r in responses if str(r.compliance_status) == "non_compliant")
    partial = sum(1 for r in responses if str(r.compliance_status) == "partial")
    not_applicable = sum(1 for r in responses if str(r.compliance_status) == "not_applicable")

    # Calculate scores (excluding N/A)
    applicable_controls = total_controls - not_applicable
    if applicable_controls > 0:
        # Simple percentage: (compliant + 0.5*partial) / applicable
        compliance_score = ((compliant + 0.5 * partial) / applicable_controls) * 100

        # Weighted score considering control weights and maturity
        total_weight = sum(float(r.control_weight) for r in responses if str(r.compliance_status) != "not_applicable")
        if total_weight > 0:
            weighted_sum = sum(
                float(r.control_weight) * (float(r.maturity_level or 0)) / 5.0
                for r in responses
                if str(r.compliance_status) != "not_applicable" and r.maturity_level is not None
            )
            weighted_score = (weighted_sum / total_weight) * 100
        else:
            weighted_score = compliance_score
    else:
        compliance_score = None
        weighted_score = None

    completed = sum(1 for r in responses if r.compliance_status in ["compliant", "non_compliant", "partial", "not_applicable"])
    progress_percentage = (completed / total_controls) * 100 if total_controls > 0 else 0

    return {
        "progress_percentage": round(progress_percentage, 2),
        "compliance_score": round(compliance_score, 2) if compliance_score else None,
        "weighted_score": round(weighted_score, 2) if weighted_score else None,
        "compliant_count": compliant,
        "non_compliant_count": non_compliant,
        "partial_compliant_count": partial,
        "not_applicable_count": not_applicable,
        "completed_controls": completed,
    }


# ============================================================================
# Assessment Instance Endpoints
# ============================================================================

@router.post("", response_model=AssessmentInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentInstanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create new assessment instance (Draft state)
    Permission: assessment:create (Admin, Auditor)
    """
    # Check if assessment_id already exists
    existing = await db.execute(
        select(AssessmentInstance).where(AssessmentInstance.assessment_id == assessment_data.assessment_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message_en": f"Assessment {assessment_data.assessment_id} already exists",
                "message_ar": f"التقييم {assessment_data.assessment_id} موجود بالفعل",
            },
        )

    assessment = AssessmentInstance(
        **assessment_data.model_dump(),
        created_by_id=current_user["id"],
        status=AssessmentStatus.DRAFT.value,
        total_controls=len(assessment_data.control_scope) if assessment_data.control_scope else 0,
    )

    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.get("", response_model=AssessmentInstanceListResponse)
async def list_assessments(
    status: Optional[str] = None,
    framework: Optional[str] = None,
    assigned_to_me: bool = False,
    offset: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List assessments with filters and pagination
    Permission: assessment:read
    """
    query = select(AssessmentInstance)

    # Apply filters
    if status:
        query = query.where(AssessmentInstance.status == status)
    if framework:
        query = query.where(AssessmentInstance.framework == framework)
    if assigned_to_me:
        query = query.where(
            (AssessmentInstance.assigned_assessor_id == current_user["id"]) |
            (AssessmentInstance.reviewer_id == current_user["id"])
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(AssessmentInstance.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    return AssessmentInstanceListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[AssessmentInstanceResponse.model_validate(item) for item in items],
    )


@router.get("/{assessment_id}", response_model=AssessmentInstanceResponse)
async def get_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get assessment by ID"""
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message_en": "Assessment not found", "message_ar": "لم يتم العثور على التقييم"},
        )
    return assessment


@router.patch("/{assessment_id}", response_model=AssessmentInstanceResponse)
async def update_assessment(
    assessment_id: int,
    update_data: AssessmentInstanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update assessment (only in DRAFT or LAUNCHED state)"""
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message_en": "Assessment not found", "message_ar": "لم يتم العثور على التقييم"},
        )

    # Can only update if DRAFT or LAUNCHED
    if str(assessment.status) not in [AssessmentStatus.DRAFT.value, AssessmentStatus.LAUNCHED.value]:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message_en": f"Cannot update assessment in {assessment.status} state",
                "message_ar": f"لا يمكن تحديث التقييم في حالة {assessment.status}",
            },
        )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)
    
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore
    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete assessment (only DRAFT)"""
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message_en": "Assessment not found", "message_ar": "لم يتم العثور على التقييم"},
        )

    if str(assessment.status) != AssessmentStatus.DRAFT.value:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message_en": "Can only delete assessments in DRAFT state",
                "message_ar": "يمكن حذف التقييمات في حالة المسودة فقط",
            },
        )

    await db.delete(assessment)
    await db.commit()


# ============================================================================
# Lifecycle Workflow Endpoints
# ============================================================================

@router.post("/{assessment_id}/launch", response_model=AssessmentInstanceResponse)
async def launch_assessment(
    assessment_id: int,
    launch_data: AssessmentLaunchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Launch assessment (DRAFT → LAUNCHED)
    Permission: assessment:launch (Admin, Auditor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    # Validate transition
    if not _validate_status_transition(str(assessment.status), AssessmentStatus.LAUNCHED.value):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot launch assessment from {assessment.status} state",
        )

    # Update assessment
    old_status = str(assessment.status)
    setattr(assessment, 'status', AssessmentStatus.LAUNCHED.value)  # type: ignore
    setattr(assessment, 'launched_at', datetime.utcnow())  # type: ignore
    setattr(assessment, 'assigned_assessor_id', launch_data.assigned_assessor_id)  # type: ignore
    setattr(assessment, 'due_date', launch_data.due_date)  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore

    # Log transition
    await _log_status_change(
        db, assessment_id, old_status, AssessmentStatus.LAUNCHED.value,
        current_user["id"], "Assessment launched", request=request
    )

    await db.commit()
    await db.refresh(assessment)

    # TODO: Send notification to assigned assessor if launch_notification=True

    return assessment


@router.post("/{assessment_id}/assign", response_model=AssessmentInstanceResponse)
async def assign_assessment(
    assessment_id: int,
    assign_data: AssessmentAssignRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Assign/reassign assessor
    Permission: assessment:assign (Admin, Auditor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if str(assessment.status) not in [AssessmentStatus.LAUNCHED.value, AssessmentStatus.IN_PROGRESS.value]:  # type: ignore
        raise HTTPException(status_code=400, detail="Assessment must be LAUNCHED or IN_PROGRESS to reassign")

    old_assessor = assessment.assigned_assessor_id
    setattr(assessment, 'assigned_assessor_id', assign_data.assigned_assessor_id)  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore

    # Log assignment change
    await _log_status_change(
        db, assessment_id, str(assessment.status), str(assessment.status),  # type: ignore
        current_user["id"],
        f"Reassigned from user {old_assessor} to {assign_data.assigned_assessor_id}: {assign_data.comment or 'No comment'}",
        request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.post("/{assessment_id}/start", response_model=AssessmentInstanceResponse)
async def start_assessment(
    assessment_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Start assessment execution (LAUNCHED → IN_PROGRESS)
    Permission: assessment:execute (Assessor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Only assigned assessor can start
    if assessment.assigned_assessor_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only assigned assessor can start assessment")

    if not _validate_status_transition(str(assessment.status), AssessmentStatus.IN_PROGRESS.value):  # type: ignore
        raise HTTPException(status_code=400, detail=f"Cannot start from {assessment.status} state")

    old_status = str(assessment.status)
    setattr(assessment, 'status', AssessmentStatus.IN_PROGRESS.value)  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore
    
    await _log_status_change(
        db, assessment_id, old_status, AssessmentStatus.IN_PROGRESS.value,
        current_user["id"], "Assessment execution started", request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.post("/{assessment_id}/submit", response_model=AssessmentInstanceResponse)
async def submit_assessment(
    assessment_id: int,
    submit_data: AssessmentSubmitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit assessment for review (IN_PROGRESS → SUBMITTED)
    Permission: assessment:submit (Assessor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Only assigned assessor can submit
    if assessment.assigned_assessor_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only assigned assessor can submit")

    if not _validate_status_transition(str(assessment.status), AssessmentStatus.SUBMITTED.value):  # type: ignore
        raise HTTPException(status_code=400, detail=f"Cannot submit from {assessment.status} state")

    # Calculate final scores before submission
    scores = await _calculate_assessment_score(db, assessment_id)

    # Update assessment
    old_status = str(assessment.status)
    setattr(assessment, 'status', AssessmentStatus.SUBMITTED.value)  # type: ignore
    setattr(assessment, 'submitted_at', datetime.utcnow())  # type: ignore
    setattr(assessment, 'progress_percentage', scores["progress_percentage"])  # type: ignore
    setattr(assessment, 'compliance_score', scores["compliance_score"])  # type: ignore
    setattr(assessment, 'weighted_score', scores["weighted_score"])  # type: ignore
    setattr(assessment, 'compliant_count', scores["compliant_count"])  # type: ignore
    setattr(assessment, 'non_compliant_count', scores["non_compliant_count"])  # type: ignore
    setattr(assessment, 'partial_compliant_count', scores["partial_compliant_count"])  # type: ignore
    setattr(assessment, 'not_applicable_count', scores["not_applicable_count"])  # type: ignore
    setattr(assessment, 'completed_controls', scores["completed_controls"])  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore

    await _log_status_change(
        db, assessment_id, old_status, AssessmentStatus.SUBMITTED.value,
        current_user["id"], submit_data.submission_comment, request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.post("/{assessment_id}/review", response_model=AssessmentInstanceResponse)
async def review_assessment(
    assessment_id: int,
    review_data: AssessmentReviewRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Review assessment (SUBMITTED → REVIEWED or back to IN_PROGRESS)
    Permission: assessment:review (Admin, Auditor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if str(assessment.status) != AssessmentStatus.SUBMITTED.value:
        raise HTTPException(status_code=400, detail="Assessment must be SUBMITTED for review")

    old_status = str(assessment.status)
    
    if review_data.return_for_revision:
        # Return to IN_PROGRESS for corrections
        new_status = AssessmentStatus.IN_PROGRESS.value
        comment = f"Returned for revision: {review_data.revision_notes}"
    else:
        # Mark as reviewed
        new_status = AssessmentStatus.REVIEWED.value
        setattr(assessment, 'reviewer_id', review_data.reviewer_id)  # type: ignore
        setattr(assessment, 'reviewed_at', datetime.utcnow())  # type: ignore
        comment = review_data.review_comment
    
    setattr(assessment, 'status', new_status)  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore
    
    await _log_status_change(
        db, assessment_id, old_status, new_status,
        current_user["id"], comment, request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.post("/{assessment_id}/approve", response_model=AssessmentInstanceResponse)
async def approve_assessment(
    assessment_id: int,
    approval_data: AssessmentApprovalRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Approve or reject assessment (REVIEWED → APPROVED/REJECTED)
    Permission: assessment:approve (Admin only)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if str(assessment.status) != AssessmentStatus.REVIEWED.value:
        raise HTTPException(status_code=400, detail="Assessment must be REVIEWED before approval")

    old_status = str(assessment.status)
    
    if approval_data.decision == "approved":
        new_status = AssessmentStatus.APPROVED.value
        setattr(assessment, 'approved_at', datetime.utcnow())  # type: ignore
        setattr(assessment, 'approver_id', approval_data.approver_id)  # type: ignore
        setattr(assessment, 'approval_comment', approval_data.approval_comment)  # type: ignore
    else:  # rejected
        new_status = AssessmentStatus.REJECTED.value
        setattr(assessment, 'rejection_reason', approval_data.approval_comment)  # type: ignore
    
    setattr(assessment, 'status', new_status)  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore
    
    await _log_status_change(
        db, assessment_id, old_status, new_status,
        current_user["id"],
        approval_data.approval_comment,
        approval_decision=approval_data.decision,
        approval_comment=approval_data.approval_comment,
        request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


@router.post("/{assessment_id}/close", response_model=AssessmentInstanceResponse)
async def close_assessment(
    assessment_id: int,
    close_data: AssessmentCloseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Close assessment (APPROVED → CLOSED)
    Permission: assessment:close (Admin)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if not _validate_status_transition(str(assessment.status), AssessmentStatus.CLOSED.value):
        raise HTTPException(status_code=400, detail=f"Cannot close from {assessment.status} state")

    old_status = str(assessment.status)
    setattr(assessment, 'status', AssessmentStatus.CLOSED.value)  # type: ignore
    setattr(assessment, 'closed_at', datetime.utcnow())  # type: ignore
    
    if close_data.submit_to_regulator:
        setattr(assessment, 'submitted_to_regulator', True)  # type: ignore
        setattr(assessment, 'regulator_submission_date', datetime.utcnow())  # type: ignore
        setattr(assessment, 'regulator_reference_number', close_data.regulator_reference)  # type: ignore
    
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore
    
    await _log_status_change(
        db, assessment_id, old_status, AssessmentStatus.CLOSED.value,
        current_user["id"], close_data.closure_comment, request=request
    )

    await db.commit()
    await db.refresh(assessment)

    return assessment


# ============================================================================
# Assessment Responses Endpoints
# ============================================================================

@router.post("/{assessment_id}/responses", response_model=AssessmentResponseResponse, status_code=201)
async def create_assessment_response(
    assessment_id: int,
    response_data: AssessmentResponseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create or update control assessment response
    Permission: assessment:execute (Assessor)
    """
    assessment = await db.get(AssessmentInstance, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Only assigned assessor can add responses
    if assessment.assigned_assessor_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only assigned assessor can add responses")

    if str(assessment.status) not in [AssessmentStatus.IN_PROGRESS.value, AssessmentStatus.LAUNCHED.value]:
        raise HTTPException(status_code=400, detail="Assessment must be IN_PROGRESS to add responses")

    # Check if response already exists for this control
    existing = await db.execute(
        select(AssessmentResponse).where(
            and_(
                AssessmentResponse.assessment_id == assessment_id,
                AssessmentResponse.control_id == response_data.control_id
            )
        )
    )
    existing_response = existing.scalar_one_or_none()

    if existing_response:
        # Update existing response
        for field, value in response_data.model_dump(exclude={"assessment_id", "control_id"}).items():
            setattr(existing_response, field, value)
        setattr(existing_response, 'assessed_by_id', current_user["id"])  # type: ignore
        setattr(existing_response, 'assessed_at', datetime.utcnow())  # type: ignore
        setattr(existing_response, 'updated_at', datetime.utcnow())  # type: ignore
        response = existing_response
    else:
        # Create new response
        response = AssessmentResponse(
            **response_data.model_dump(),
            assessed_by_id=current_user["id"],
            assessed_at=datetime.utcnow(),
        )
        db.add(response)

    # Recalculate assessment progress
    await db.flush()
    scores = await _calculate_assessment_score(db, assessment_id)
    setattr(assessment, 'progress_percentage', scores["progress_percentage"])  # type: ignore
    setattr(assessment, 'completed_controls', scores["completed_controls"])  # type: ignore
    setattr(assessment, 'updated_at', datetime.utcnow())  # type: ignore

    await db.commit()
    await db.refresh(response)

    return response


@router.get("/{assessment_id}/responses", response_model=AssessmentResponseListResponse)
async def list_assessment_responses(
    assessment_id: int,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all responses for an assessment"""
    query = select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(offset).limit(limit).order_by(AssessmentResponse.control_id)
    result = await db.execute(query)
    items = result.scalars().all()

    return AssessmentResponseListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[AssessmentResponseResponse.model_validate(item) for item in items],
    )


# ============================================================================
# Audit Trail & History
# ============================================================================

@router.get("/{assessment_id}/history", response_model=List[AssessmentStatusHistoryResponse])
async def get_assessment_history(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
   current_user: dict = Depends(get_current_user),
):
    """Get complete audit trail for assessment"""
    query = select(AssessmentStatusHistory).where(
        AssessmentStatusHistory.assessment_id == assessment_id
    ).order_by(AssessmentStatusHistory.changed_at.desc())

    result = await db.execute(query)
    history = result.scalars().all()

    return [AssessmentStatusHistoryResponse.model_validate(h) for h in history]


# ============================================================================
# Dashboard & Analytics
# ============================================================================

@router.get("/dashboard/stats", response_model=AssessmentDashboardStats)
async def get_assessment_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get assessment execution dashboard statistics"""

    # Count by status
    status_counts = {}
    for status_value in AssessmentStatus:
        count = await db.scalar(
            select(func.count()).select_from(AssessmentInstance).where(
                AssessmentInstance.status == status_value.value
            )
        )
        status_counts[status_value.value] = count or 0

    # Count overdue assessments
    overdue = await db.scalar(
        select(func.count()).select_from(AssessmentInstance).where(
            and_(
                AssessmentInstance.due_date < datetime.utcnow(),
                AssessmentInstance.status.in_([
                    AssessmentStatus.LAUNCHED.value,
                    AssessmentStatus.IN_PROGRESS.value,
                    AssessmentStatus.SUBMITTED.value,
                ])
            )
        )
    ) or 0

    # Average compliance score
    avg_score_result = await db.scalar(
        select(func.avg(AssessmentInstance.compliance_score)).where(
            AssessmentInstance.compliance_score.isnot(None)
        )
    )
    avg_score = float(avg_score_result) if avg_score_result else None

    total = await db.scalar(select(func.count()).select_from(AssessmentInstance)) or 0

    return AssessmentDashboardStats(
        total_assessments=total,
        draft=status_counts.get(AssessmentStatus.DRAFT.value, 0),
        launched=status_counts.get(AssessmentStatus.LAUNCHED.value, 0),
        in_progress=status_counts.get(AssessmentStatus.IN_PROGRESS.value, 0),
        submitted=status_counts.get(AssessmentStatus.SUBMITTED.value, 0),
        reviewed=status_counts.get(AssessmentStatus.REVIEWED.value, 0),
        approved=status_counts.get(AssessmentStatus.APPROVED.value, 0),
        closed=status_counts.get(AssessmentStatus.CLOSED.value, 0),
        overdue=overdue,
        avg_compliance_score=round(avg_score, 2) if avg_score else None,
    )
