"""
AI Governance API router (SDAIA AI Principles).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from core.database import get_db
from auth.security import get_current_user, require_permission, log_audit_event
from auth.models import User
from .models import AIModel, BiasTestResult, ModelAudit, AIEthicsReview, ModelType, ModelStatus
from .schemas import (
    AIModelCreate, AIModelUpdate, AIModelResponse,
    BiasTestCreate, BiasTestResponse,
    EthicsReviewCreate, EthicsReviewResponse
)

router = APIRouter()


@router.post("/models", response_model=AIModelResponse, dependencies=[Depends(require_permission("ai:create"))])
async def create_ai_model(
    model: AIModelCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register AI model (SDAIA AI Principles)"""
    try:
        # Create model
        new_model = AIModel(
            **model.model_dump(),
            created_by=current_user.user_id
        )
        
        db.add(new_model)
        await db.commit()
        await db.refresh(new_model)
        
        # Audit log
        await log_audit_event(
            db=db,
            user_id=str(current_user.user_id),
            action="ai_model.created",
            resource="ai_model",
            resource_id=str(new_model.model_id),
            status="success",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={
                "model_name": model.model_name,
                "model_type": model.model_type.value,
                "processes_personal_data": model.processes_personal_data
            }
        )
        
        # Create audit entry
        audit = ModelAudit(
            model_id=new_model.model_id,
            event_type="created",
            performed_by=current_user.user_id,
            reason_en="Initial model registration",
            reason_ar="تسجيل النموذج الأولي"
        )
        db.add(audit)
        await db.commit()
        
        return new_model
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create AI model: {str(e)}")


@router.get("/models", response_model=List[AIModelResponse], dependencies=[Depends(require_permission("ai:read"))])
async def list_ai_models(
    model_type: Optional[ModelType] = None,
    status: Optional[ModelStatus] = None,
    processes_personal_data: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List AI models"""
    query = select(AIModel)
    
    # Filters
    filters = []
    if model_type:
        filters.append(AIModel.model_type == model_type)
    if status:
        filters.append(AIModel.status == status)
    if processes_personal_data is not None:
        filters.append(AIModel.processes_personal_data == processes_personal_data)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(AIModel.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    models = result.scalars().all()
    return models


@router.get("/models/{model_id}", response_model=AIModelResponse, dependencies=[Depends(require_permission("ai:read"))])
async def get_ai_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get AI model details"""
    result = await db.execute(
        select(AIModel).where(AIModel.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    return model


@router.patch("/models/{model_id}", response_model=AIModelResponse, dependencies=[Depends(require_permission("ai:update"))])
async def update_ai_model(
    model_id: UUID,
    update: AIModelUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update AI model"""
    result = await db.execute(
        select(AIModel).where(AIModel.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Track changes for audit
    changes = {}
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_value = getattr(model, field)
        if old_value != value:
            changes[field] = {"old": str(old_value), "new": str(value)}
        setattr(model, field, value)
    
    # Update timestamp
    setattr(model, "last_updated_at", datetime.utcnow())
    
    # Mark as deployed if status changed to PRODUCTION
    if update.status == ModelStatus.PRODUCTION and getattr(model, "deployed_at") is None:
        setattr(model, "deployed_at", datetime.utcnow())
    
    await db.commit()
    await db.refresh(model)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="ai_model.updated",
        resource="ai_model",
        resource_id=str(model_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=changes
    )
    
    # Create audit entry
    audit = ModelAudit(
        model_id=model_id,
        event_type="updated",
        performed_by=current_user.user_id,
        changes=changes,
        reason_en="Model update",
        reason_ar="تحديث النموذج"
    )
    db.add(audit)
    await db.commit()
    
    return model


# Bias testing endpoints
@router.post("/bias-tests", response_model=BiasTestResponse, dependencies=[Depends(require_permission("ai:test"))])
async def create_bias_test(
    test: BiasTestCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create bias test result (SDAIA AI Principles)"""
    # Verify model exists
    result = await db.execute(select(AIModel).where(AIModel.model_id == test.model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Create test result
    new_test = BiasTestResult(
        **test.model_dump(),
        tested_by=current_user.user_id
    )
    
    db.add(new_test)
    
    # Update model
    setattr(model, "bias_assessment_completed", True)
    setattr(model, "bias_assessment_date", datetime.utcnow())
    if test.bias_detected:
        setattr(model, "known_biases_en", test.findings_en)
        setattr(model, "known_biases_ar", test.findings_ar)
        setattr(model, "mitigation_strategies_en", test.recommendations_en)
        setattr(model, "mitigation_strategies_ar", test.recommendations_ar)
    
    await db.commit()
    await db.refresh(new_test)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="bias_test.created",
        resource="bias_test",
        resource_id=str(new_test.test_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={
            "model_id": str(test.model_id),
            "bias_detected": test.bias_detected,
            "severity": test.severity
        }
    )
    
    return new_test


@router.get("/models/{model_id}/bias-tests", response_model=List[BiasTestResponse], dependencies=[Depends(require_permission("ai:read"))])
async def list_bias_tests(
    model_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get bias test history for model"""
    result = await db.execute(
        select(BiasTestResult)
        .where(BiasTestResult.model_id == model_id)
        .order_by(BiasTestResult.tested_at.desc())
    )
    tests = result.scalars().all()
    return tests


# Ethics review endpoints
@router.post("/ethics-reviews", response_model=EthicsReviewResponse, dependencies=[Depends(require_permission("ai:review"))])
async def create_ethics_review(
    review: EthicsReviewCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create AI ethics review (SDAIA AI Principles)"""
    # Verify model exists
    result = await db.execute(select(AIModel).where(AIModel.model_id == review.model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Create review
    new_review = AIEthicsReview(
        **review.model_dump(),
        reviewer=current_user.user_id
    )
    
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    
    # Audit log
    await log_audit_event(
        db=db,
        user_id=str(current_user.user_id),
        action="ethics_review.created",
        resource="ethics_review",
        resource_id=str(new_review.review_id),
        status="success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={
            "model_id": str(review.model_id),
            "approved": review.approved,
            "review_type": review.review_type
        }
    )
    
    return new_review


@router.get("/models/{model_id}/ethics-reviews", response_model=List[EthicsReviewResponse], dependencies=[Depends(require_permission("ai:read"))])
async def list_ethics_reviews(
    model_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get ethics review history for model"""
    result = await db.execute(
        select(AIEthicsReview)
        .where(AIEthicsReview.model_id == model_id)
        .order_by(AIEthicsReview.review_date.desc())
    )
    reviews = result.scalars().all()
    return reviews


@router.get("/statistics/ai-governance")
async def get_ai_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("ai:read"))
):
    """Get AI governance statistics"""
    # Total models
    total_query = select(func.count(AIModel.model_id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Models by status
    status_query = select(
        AIModel.status,
        func.count(AIModel.model_id).label('count')
    ).group_by(AIModel.status)
    
    status_result = await db.execute(status_query)
    status_stats = {row.status.value: row.count for row in status_result}
    
    # Bias assessment completion
    bias_assessed_query = select(func.count(AIModel.model_id)).where(
        AIModel.bias_assessment_completed == True
    )
    bias_assessed_result = await db.execute(bias_assessed_query)
    bias_assessed = bias_assessed_result.scalar()
    
    # Models processing personal data
    personal_data_query = select(func.count(AIModel.model_id)).where(
        AIModel.processes_personal_data == True
    )
    personal_data_result = await db.execute(personal_data_query)
    personal_data = personal_data_result.scalar()
    
    # Models with bias detected
    bias_detected_query = select(func.count(func.distinct(BiasTestResult.model_id))).where(
        BiasTestResult.bias_detected == True
    )
    bias_detected_result = await db.execute(bias_detected_query)
    bias_detected = bias_detected_result.scalar()
    
    total_value = total or 0
    bias_assessed_value = bias_assessed or 0
    
    return {
        "total_models": total_value,
        "by_status": status_stats,
        "bias_assessed": bias_assessed_value,
        "bias_detected": bias_detected or 0,
        "processing_personal_data": personal_data or 0,
        "bias_assessment_rate": f"{(bias_assessed_value/total_value*100):.1f}%" if total_value > 0 else "0%",
        "message_en": "AI governance statistics",
        "message_ar": "إحصائيات حوكمة الذكاء الاصطناعي"
    }
