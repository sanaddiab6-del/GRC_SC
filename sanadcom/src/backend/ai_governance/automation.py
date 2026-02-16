"""
AI Governance Automation Services
Automated bias testing, performance monitoring, and incident detection
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import json
import numpy as np

from ai_governance.models import (
    AIModel, BiasTestResult, ModelAudit, AIEthicsReview,
    ModelType, ModelStatus
)
from auth.models import User


class BiasTestingService:
    """
    Automated bias testing for AI models (SDAIA AI Principles - Fairness).
    Tests for demographic parity, equal opportunity, and calibration across protected attributes.
    """
    
    @staticmethod
    async def auto_run_bias_tests(
        db: AsyncSession,
        model_id: str,
        test_data: Dict,
        protected_attributes: List[str] = ["gender", "nationality", "age_group"]
    ) -> List[str]:
        """
        Automatically run comprehensive bias tests on AI model.
        Returns list of test IDs created.
        """
        test_ids = []
        
        # Get model
        model_result = await db.execute(
            select(AIModel).where(AIModel.model_id == model_id)
        )
        model = model_result.scalar_one_or_none()
        
        if not model:
            return []
        
        # Run tests for each protected attribute
        for attribute in protected_attributes:
            if attribute not in test_data.get('attributes', {}):
                continue
            
            # Demographic Parity Test
            test_id = await BiasTestingService._test_demographic_parity(
                db, model_id, attribute, test_data
            )
            if test_id:
                test_ids.append(test_id)
            
            # Equal Opportunity Test
            test_id = await BiasTestingService._test_equal_opportunity(
                db, model_id, attribute, test_data
            )
            if test_id:
                test_ids.append(test_id)
            
            # Calibration Test
            test_id = await BiasTestingService._test_calibration(
                db, model_id, attribute, test_data
            )
            if test_id:
                test_ids.append(test_id)
        
        # Update model bias assessment status
        model.bias_assessment_completed = True  # type: ignore
        model.bias_assessment_date = datetime.utcnow()  # type: ignore
        await db.commit()
        
        return test_ids
    
    @staticmethod
    async def _test_demographic_parity(
        db: AsyncSession,
        model_id: str,
        attribute: str,
        test_data: Dict
    ) -> Optional[str]:
        """
        Test demographic parity: positive prediction rate should be similar across groups.
        """
        attribute_data = test_data['attributes'].get(attribute, {})
        if not attribute_data:
            return None
        
        # Calculate positive prediction rates for each group
        group_rates = {}
        for group, data in attribute_data.items():
            predictions = data.get('predictions', [])
            if predictions:
                positive_rate = sum(1 for p in predictions if p == 1) / len(predictions)
                group_rates[group] = positive_rate
        
        # Calculate disparity
        if len(group_rates) < 2:
            return None
        
        rates = list(group_rates.values())
        max_rate = max(rates)
        min_rate = min(rates)
        bias_score = (max_rate - min_rate) / max_rate if max_rate > 0 else 0
        
        # Threshold: 0.2 (20% disparity is acceptable per SDAIA guidelines)
        bias_detected = bias_score > 0.2
        severity = "high" if bias_score > 0.4 else "medium" if bias_score > 0.2 else "low"
        
        # Create test result
        test = BiasTestResult(
            model_id=model_id,
            test_name="Demographic Parity Test",
            test_type="demographic_parity",
            protected_attribute=attribute,
            attribute_values=list(group_rates.keys()),
            bias_detected=bias_detected,
            severity=severity if bias_detected else None,
            bias_score=bias_score,
            fairness_metrics=group_rates,
            test_dataset_size=sum(len(d.get('predictions', [])) for d in attribute_data.values()),
            findings_en=f"Positive prediction rate varies by {bias_score*100:.1f}% across {attribute} groups. Groups: {json.dumps(group_rates, indent=2)}",
            findings_ar=f"معدل التنبؤ الإيجابي يختلف بنسبة {bias_score*100:.1f}٪ عبر مجموعات {attribute}",
            recommendations_en="Consider rebalancing training data or applying fairness constraints during training." if bias_detected else "Model shows acceptable demographic parity.",
            recommendations_ar="يُنصح بإعادة توازن بيانات التدريب أو تطبيق قيود العدالة أثناء التدريب" if bias_detected else "النموذج يُظهر تكافؤ ديموغرافي مقبول",
            requires_action=bias_detected and bias_score > 0.3,
            tested_by=test_data.get('tested_by')
        )
        
        db.add(test)
        await db.commit()
        await db.refresh(test)
        
        return str(test.test_id)
    
    @staticmethod
    async def _test_equal_opportunity(
        db: AsyncSession,
        model_id: str,
        attribute: str,
        test_data: Dict
    ) -> Optional[str]:
        """
        Test equal opportunity: true positive rate (recall) should be similar across groups.
        """
        attribute_data = test_data['attributes'].get(attribute, {})
        if not attribute_data:
            return None
        
        # Calculate TPR for each group
        group_tpr = {}
        for group, data in attribute_data.items():
            predictions = data.get('predictions', [])
            actuals = data.get('actuals', [])
            
            if len(predictions) != len(actuals):
                continue
            
            # Calculate True Positive Rate (Recall)
            true_positives = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 1)
            actual_positives = sum(1 for a in actuals if a == 1)
            
            if actual_positives > 0:
                tpr = true_positives / actual_positives
                group_tpr[group] = tpr
        
        if len(group_tpr) < 2:
            return None
        
        # Calculate disparity
        tpr_values = list(group_tpr.values())
        max_tpr = max(tpr_values)
        min_tpr = min(tpr_values)
        bias_score = (max_tpr - min_tpr) / max_tpr if max_tpr > 0 else 0
        
        bias_detected = bias_score > 0.2
        severity = "high" if bias_score > 0.4 else "medium" if bias_score > 0.2 else "low"
        
        test = BiasTestResult(
            model_id=model_id,
            test_name="Equal Opportunity Test",
            test_type="equal_opportunity",
            protected_attribute=attribute,
            attribute_values=list(group_tpr.keys()),
            bias_detected=bias_detected,
            severity=severity if bias_detected else None,
            bias_score=bias_score,
            fairness_metrics=group_tpr,
            test_dataset_size=sum(len(d.get('predictions', [])) for d in attribute_data.values()),
            findings_en=f"True positive rate (recall) varies by {bias_score*100:.1f}% across {attribute} groups. TPR by group: {json.dumps(group_tpr, indent=2)}",
            findings_ar=f"معدل الإيجابيات الحقيقية يختلف بنسبة {bias_score*100:.1f}٪ عبر مجموعات {attribute}",
            recommendations_en="Review model performance on underrepresented groups. Consider oversampling or cost-sensitive learning." if bias_detected else "Model demonstrates good equal opportunity.",
            recommendations_ar="مراجعة أداء النموذج على المجموعات الممثلة تمثيلاً ناقصًا" if bias_detected else "النموذج يُظهر فرص متساوية جيدة",
            requires_action=bias_detected and bias_score > 0.3,
            tested_by=test_data.get('tested_by')
        )
        
        db.add(test)
        await db.commit()
        await db.refresh(test)
        
        return str(test.test_id)
    
    @staticmethod
    async def _test_calibration(
        db: AsyncSession,
        model_id: str,
        attribute: str,
        test_data: Dict
    ) -> Optional[str]:
        """
        Test calibration: predicted probabilities should match actual outcomes across groups.
        """
        attribute_data = test_data['attributes'].get(attribute, {})
        if not attribute_data:
            return None
        
        # Calculate calibration error for each group
        group_calibration = {}
        for group, data in attribute_data.items():
            probabilities = data.get('probabilities', [])
            actuals = data.get('actuals', [])
            
            if len(probabilities) != len(actuals) or len(probabilities) == 0:
                continue
            
            # Calculate Expected Calibration Error (ECE)
            n_bins = 10
            bin_edges = np.linspace(0, 1, n_bins + 1)
            bin_errors = []
            
            for i in range(n_bins):
                bin_mask = (probabilities >= bin_edges[i]) & (probabilities < bin_edges[i+1])
                if np.sum(bin_mask) > 0:
                    bin_probs = probabilities[bin_mask]
                    bin_actuals = actuals[bin_mask]
                    avg_prob = np.mean(bin_probs)
                    avg_actual = np.mean(bin_actuals)
                    bin_errors.append(abs(avg_prob - avg_actual) * np.sum(bin_mask))
            
            ece = sum(bin_errors) / len(probabilities) if probabilities.size > 0 else 0
            group_calibration[group] = float(ece)
        
        if len(group_calibration) < 2:
            return None
        
        # Calculate disparity in calibration
        cal_values = list(group_calibration.values())
        max_cal_error = max(cal_values)
        min_cal_error = min(cal_values)
        bias_score = max_cal_error - min_cal_error
        
        bias_detected = bias_score > 0.1  # 10% calibration difference
        severity = "high" if bias_score > 0.2 else "medium" if bias_score > 0.1 else "low"
        
        test = BiasTestResult(
            model_id=model_id,
            test_name="Calibration Test",
            test_type="calibration",
            protected_attribute=attribute,
            attribute_values=list(group_calibration.keys()),
            bias_detected=bias_detected,
            severity=severity if bias_detected else None,
            bias_score=bias_score,
            fairness_metrics=group_calibration,
            test_dataset_size=sum(len(d.get('predictions', [])) for d in attribute_data.values()),
            findings_en=f"Calibration error varies by {bias_score*100:.1f}% across {attribute} groups. Calibration errors: {json.dumps(group_calibration, indent=2)}",
            findings_ar=f"خطأ المعايرة يختلف بنسبة {bias_score*100:.1f}٪ عبر مجموعات {attribute}",
            recommendations_en="Apply post-processing calibration techniques like Platt scaling or isotonic regression." if bias_detected else "Model is well-calibrated across groups.",
            recommendations_ar="تطبيق تقنيات معايرة ما بعد المعالجة" if bias_detected else "النموذج معاير بشكل جيد عبر المجموعات",
            requires_action=bias_detected and bias_score > 0.15,
            tested_by=test_data.get('tested_by')
        )
        
        db.add(test)
        await db.commit()
        await db.refresh(test)
        
        return str(test.test_id)
    
    @staticmethod
    async def get_models_requiring_testing(db: AsyncSession) -> List[AIModel]:
        """
        Get models that require bias testing (never tested or due for retest).
        """
        # Models in production without bias assessment
        never_tested_result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.status == ModelStatus.PRODUCTION,
                    AIModel.bias_assessment_completed == False
                )
            )
        )
        never_tested = list(never_tested_result.scalars().all())
        
        # Models tested more than 90 days ago (require periodic retesting)
        retest_cutoff = datetime.utcnow() - timedelta(days=90)
        retest_required_result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.status == ModelStatus.PRODUCTION,
                    AIModel.bias_assessment_completed == True,
                    or_(
                        AIModel.bias_assessment_date.is_(None),
                        AIModel.bias_assessment_date < retest_cutoff
                    )
                )
            )
        )
        retest_required = list(retest_required_result.scalars().all())
        
        return never_tested + retest_required


class ModelPerformanceMonitoringService:
    """
    Continuous monitoring of AI model performance for drift detection and degradation.
    """
    
    @staticmethod
    async def monitor_model_performance(
        db: AsyncSession,
        model_id: str,
        recent_predictions: List[Dict]
    ) -> Dict:
        """
        Monitor model performance and detect drift.
        Returns monitoring report with alerts.
        """
        # Get model historical performance
        model_result = await db.execute(
            select(AIModel).where(AIModel.model_id == model_id)
        )
        model = model_result.scalar_one_or_none()
        
        if not model:
            return {"error": "Model not found"}
        
        # Calculate current performance metrics
        predictions = [p['prediction'] for p in recent_predictions if 'prediction' in p]
        actuals = [p['actual'] for p in recent_predictions if 'actual' in p]
        
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return {"error": "Insufficient data for monitoring"}
        
        # Calculate metrics
        accuracy = sum(1 for p, a in zip(predictions, actuals) if p == a) / len(predictions)
        
        # True Positives, False Positives, True Negatives, False Negatives
        tp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 1)
        fp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 0)
        tn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 0)
        fn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 1)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Compare with baseline performance
        alerts = []
        
        if model.accuracy and accuracy < float(model.accuracy) * 0.9:  # type: ignore
            alerts.append({
                "type": "performance_degradation",
                "severity": "high",
                "message_en": f"Accuracy dropped from {model.accuracy:.2%} to {accuracy:.2%}",
                "message_ar": f"انخفضت الدقة من {model.accuracy:.2%} إلى {accuracy:.2%}"
            })
        
        if model.precision and precision < float(model.precision) * 0.9:  # type: ignore
            alerts.append({
                "type": "precision_drop",
                "severity": "medium",
                "message_en": f"Precision dropped from {model.precision:.2%} to {precision:.2%}",
                "message_ar": f"انخفضت الدقة من {model.precision:.2%} إلى {precision:.2%}"
            })if model.recall and recall < float(model.recall) * 0.9:  # type: ignore
            alerts.append({
                "type": "recall_drop",
                "severity": "medium",
                "message_en": f"Recall dropped from {model.recall:.2%} to {recall:.2%}",
                "message_ar": f"انخفض الاستدعاء من {model.recall:.2%} إلى {recall:.2%}"
            })
        
        # Update model's last monitored timestamp
        model.last_monitored_at = datetime.utcnow()  # type: ignore
        await db.commit()
        
        # Create audit log if significant degradation
        if len(alerts) > 0:
            audit = ModelAudit(
                model_id=model_id,
                event_type="performance_alert",
                performed_by=None,  # Automated monitoring
                reason_en=f"Performance degradation detected: {len(alerts)} alert(s)",
                reason_ar=f"تم اكتشاف تدهور الأداء: {len(alerts)} تنبيه",
                changes={
                    "accuracy": {"old": float(model.accuracy) if model.accuracy else None, "new": accuracy},  # type: ignore
                    "precision": {"old": float(model.precision) if model.precision else None, "new": precision},  # type: ignore
                    "recall": {"old": float(model.recall) if model.recall else None, "new": recall},  # type: ignore
                    "f1_score": {"old": float(model.f1_score) if model.f1_score else None, "new": f1_score}  # type: ignore
                },
                requires_retraining=len([a for a in alerts if a['severity'] == 'high']) > 0,
                requires_retesting=True
            )
            db.add(audit)
            await db.commit()
        
        return {
            "model_id": str(model_id),
            "monitored_at": datetime.utcnow().isoformat(),
            "sample_size": len(predictions),
            "current_metrics": {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            },
            "baseline_metrics": {
                "accuracy": float(model.accuracy) if model.accuracy else None,  # type: ignore
                "precision": float(model.precision) if model.precision else None,  # type: ignore
                "recall": float(model.recall) if model.recall else None,  # type: ignore
                "f1_score": float(model.f1_score) if model.f1_score else None  # type: ignore
            },
            "alerts": alerts,
            "requires_action": len(alerts) > 0
        }
    
    @staticmethod
    async def get_models_requiring_monitoring(db: AsyncSession) -> List[AIModel]:
        """
        Get production models that haven't been monitored recently (> 24 hours).
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.status == ModelStatus.PRODUCTION,
                    AIModel.performance_monitoring_enabled == True,
                    or_(
                        AIModel.last_monitored_at.is_(None),
                        AIModel.last_monitored_at < cutoff_time
                    )
                )
            )
        )
        
        return list(result.scalars().all())


class AIIncidentResponseService:
    """
    Automated incident detection and response for AI systems.
    """
    
    @staticmethod
    async def detect_ai_incidents(db: AsyncSession) -> List[Dict]:
        """
        Detect AI-related incidents from bias tests and performance monitoring.
        Returns list of detected incidents.
        """
        incidents = []
        
        # Critical bias detected in production models
        bias_result = await db.execute(
            select(BiasTestResult).join(AIModel).where(
                and_(
                    BiasTestResult.bias_detected == True,
                    BiasTestResult.severity == "high",
                    AIModel.status == ModelStatus.PRODUCTION,
                    BiasTestResult.requires_action == True,
                    BiasTestResult.action_taken_en.is_(None)  # No action taken yet
                )
            )
        )
        bias_incidents = bias_result.scalars().all()
        
        for bias_test in bias_incidents:
            incidents.append({
                "type": "high_bias_detected",
                "severity": "critical",
                "model_id": str(bias_test.model_id),
                "test_id": str(bias_test.test_id),
                "protected_attribute": bias_test.protected_attribute,
                "bias_score": float(bias_test.bias_score) if bias_test.bias_score else None,  # type: ignore
                "findings": bias_test.findings_en,
                "required_action": "Immediate review and potential model rollback"
            })
        
        # Performance degradation requiring retraining
        audit_result = await db.execute(
            select(ModelAudit).where(
                and_(
                    ModelAudit.event_type == "performance_alert",
                    ModelAudit.requires_retraining == True,
                    ModelAudit.event_timestamp >= datetime.utcnow() - timedelta(hours=72)
                )
            )
        )
        audit_incidents = audit_result.scalars().all()
        
        for audit in audit_incidents:
            incidents.append({
                "type": "performance_degradation",
                "severity": "high",
                "model_id": str(audit.model_id),
                "audit_id": str(audit.audit_id),
                "timestamp": audit.event_timestamp.isoformat(),
                "reason": audit.reason_en,
                "required_action": "Model retraining and validation"
            })
        
        return incidents
