# Model Card: [Model Name]

**Model Card compliant with**: SDAIA AI Principles, ISO 42001, EU AI Act (adapted for Saudi)

---

## Model Details

### Basic Information
- **Model ID**: `[model-id]`
- **Version**: `[X.Y.Z]`
- **Model Type**: Encoder-only / Encoder-Decoder / Embedding
- **Architecture**: BERT / RoBERTa / T5 / etc.
- **Base Model**: `[foundation-model-name]`
- **Parameters**: [number] parameters
- **Languages**: Arabic (ar), English (en)
- **Owner**: SICO AI Team
- **Contact**: ai-team@sico.sa
- **License**: Proprietary (Enterprise)
- **Date Created**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD

### Intended Use

#### Primary Use Cases
1. **Evidence Classification**
   - Classify evidence into types: policy, procedure, screenshot, log, contract
   - Expected accuracy: ≥90%

2. **Named Entity Recognition (NER)**
   - Extract entities: system names, assets, controls, regulations
   - Expected F1 score: ≥85%

3. **Control Similarity Matching**
   - Map evidence to controls (ECC/CCC/PDPL)
   - Expected precision: ≥80%

#### Out-of-Scope Use Cases
❌ Medical diagnosis  
❌ Financial trading decisions  
❌ Legal advice  
❌ Personal data profiling  
❌ Surveillance  

### Users
- **Primary**: GRC Analysts, Compliance Officers, Auditors
- **Secondary**: System administrators (for configuration)
- **Prohibited**: General public, unauthorized third parties

---

## Training Data

### Data Sources
| Source | Description | Size | Language | PII Status |
|--------|-------------|------|----------|------------|
| ECC Control Library | Saudi NCA Essential Controls | 115 controls | AR + EN | ✅ PII-free |
| CCC Framework | Cloud Computing Framework | 78 controls | AR + EN | ✅ PII-free |
| PDPL Guidelines | Personal Data Protection Law | 32 articles | AR + EN | ✅ PII-free |
| Internal Evidence DB | Anonymized evidence samples | [N] samples | AR + EN | ✅ Anonymized |

### Data Preprocessing
- **Anonymization**: All PII removed using automated redaction
- **Validation**: Manual review by 3 annotators
- **Augmentation**: Back-translation (AR↔EN) for data balancing
- **Filtering**: Removed duplicates, low-quality samples

### Data Splitting
- **Training**: 70% ([N] samples)
- **Validation**: 15% ([N] samples)
- **Test (Golden Set)**: 15% ([N] samples) - IMMUTABLE

### Data Lineage
```
Raw Data Sources
    ↓
PII Removal (ai/security/pii_redactor.py)
    ↓
Quality Filtering
    ↓
Train/Val/Test Split (stratified)
    ↓
Model Training
```

**Audit Trail**: All data transformations logged in `data/lineage/[model-id].jsonl`

### Data Governance
- **Storage**: Azure Blob Storage (Saudi region: `saudi-central`)
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Access Control**: RBAC (AI_ADMIN, DATA_ENGINEER only)
- **Retention**: Training data retained for 3 years post-deployment
- **Right to Deletion**: If client requests data removal, adapter expires immediately

---

## Model Architecture

### Technical Specifications
```yaml
Architecture: [BERT-base / RoBERTa / etc.]
Hidden Size: [768 / 1024]
Attention Heads: [12 / 16]
Layers: [12 / 24]
Max Sequence Length: [512 / 1024]
Vocabulary Size: [30K / 50K]
Positional Embeddings: Learned / Sinusoidal
```

### Fine-Tuning Details
- **Base Model**: `[huggingface-model-id]`
- **Fine-Tuning Method**: Full fine-tune / LoRA / Adapter
- **Trainable Parameters**: [N] parameters ([X]% of total)
- **Optimizer**: AdamW (lr=5e-5, weight_decay=0.01)
- **Batch Size**: 32
- **Epochs**: 10 (early stopping at epoch [X])
- **Hardware**: 4x NVIDIA A100 (40GB)
- **Training Time**: [X] hours

### Hyperparameters
```python
{
    "learning_rate": 5e-5,
    "warmup_steps": 500,
    "max_grad_norm": 1.0,
    "dropout": 0.1,
    "weight_decay": 0.01,
    "adam_epsilon": 1e-8,
}
```

---

## Performance Metrics

### Quantitative Results

#### Classification Task (Evidence Type)
| Metric | Value | Threshold |
|--------|-------|-----------|
| Accuracy | [X.XX]% | ≥90% ✅ |
| Precision (Macro) | [X.XX]% | ≥85% ✅ |
| Recall (Macro) | [X.XX]% | ≥85% ✅ |
| F1 Score (Macro) | [X.XX]% | ≥85% ✅ |

**Per-Class Performance**:
| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Policy | [X.XX]% | [X.XX]% | [X.XX]% | [N] |
| Procedure | [X.XX]% | [X.XX]% | [X.XX]% | [N] |
| Screenshot | [X.XX]% | [X.XX]% | [X.XX]% | [N] |
| Log | [X.XX]% | [X.XX]% | [X.XX]% | [N] |
| Contract | [X.XX]% | [X.XX]% | [X.XX]% | [N] |

#### NER Task (Entity Extraction)
| Entity Type | Precision | Recall | F1 |
|-------------|-----------|--------|-----|
| System Name | [X.XX]% | [X.XX]% | [X.XX]% |
| Control ID | [X.XX]% | [X.XX]% | [X.XX]% |
| Regulation | [X.XX]% | [X.XX]% | [X.XX]% |
| Asset | [X.XX]% | [X.XX]% | [X.XX]% |

#### Similarity Task (Evidence→Control Mapping)
| Metric | Value | Threshold |
|--------|-------|-----------|
| Precision@5 | [X.XX]% | ≥80% ✅ |
| Recall@5 | [X.XX]% | ≥75% ✅ |
| MRR (Mean Reciprocal Rank) | [X.XX] | ≥0.7 ✅ |

### Latency & Throughput
- **Inference Latency (p50)**: [X] ms
- **Inference Latency (p99)**: [X] ms
- **Throughput**: [X] queries/second
- **Max Batch Size**: [X]

### Cross-Lingual Performance
| Language | Accuracy | F1 Score |
|----------|----------|----------|
| Arabic | [X.XX]% | [X.XX]% |
| English | [X.XX]% | [X.XX]% |
| **Gap** | [X.XX]% | [X.XX]% |

**Target**: Language gap < 5%

---

## Fairness & Bias Analysis

### Demographic Analysis (if applicable)
**Note**: GRC domain has limited demographic factors. Analysis focuses on language fairness.

#### Language Fairness
| Metric | Arabic | English | Parity |
|--------|--------|---------|--------|
| Accuracy | [X.XX]% | [X.XX]% | [X.XX]% |
| False Positive Rate | [X.XX]% | [X.XX]% | [X.XX]% |

**Fairness Threshold**: Parity gap < 10%

### Bias Testing Results
✅ **No demographic bias** (not applicable to GRC domain)  
✅ **Language parity within threshold**  
✅ **No framework bias** (ECC/CCC/PDPL treated equally)

### Mitigation Strategies
- Balanced training data (50% AR, 50% EN)
- Framework-agnostic embeddings
- Regular bias audits (quarterly)

---

## Limitations & Risks

### Known Limitations
1. **Domain Specificity**: Only trained on GRC domain (ECC/CCC/PDPL)
   - Will perform poorly on unrelated domains (medical, financial, etc.)

2. **Language Support**: Only Arabic and English
   - No support for other languages

3. **Temporal Drift**: Training data from 2024-2026
   - May not reflect future regulatory changes
   - **Mitigation**: Quarterly retraining

4. **Edge Cases**: 
   - Long documents (>512 tokens) are truncated
   - Mixed-language documents may have reduced accuracy

### Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Hallucination** (incorrect classification) | Medium | Low | Citation validation (95% gate) |
| **PII Leakage** | High | Very Low | PII redaction enforced |
| **Model Poisoning** | High | Low | Adapter isolation + 90-day expiry |
| **Adversarial Attacks** | Medium | Low | Prompt sanitization |
| **Temporal Drift** | Medium | Medium | Quarterly retraining |

### SDAIA AI Risk Classification
**Risk Level**: **MEDIUM**  
**Rationale**: Read-only retrieval and classification tasks. No direct impact on rights/safety.

---

## Ethical Considerations

### SDAIA AI Principles Compliance

#### Principle 1: Human-Centric AI
✅ **Human-in-the-loop**: High-confidence mappings (≥70%) auto-approved, low-confidence requires human review  
✅ **Explainability**: Model provides confidence scores and citations

#### Principle 2: Fairness & Non-Discrimination
✅ **Language fairness**: Arabic and English treated equally  
✅ **Framework neutrality**: No bias towards specific regulatory framework

#### Principle 3: Transparency & Explainability
✅ **Model card published**: This document  
✅ **Citations provided**: Every output includes source reference  
✅ **Confidence scores**: Users see model uncertainty

#### Principle 4: Privacy & Data Protection
✅ **PII-free training**: All training data anonymized  
✅ **PDPL compliant**: No personal data processing  
✅ **Data minimization**: Only necessary data collected

#### Principle 5: Safety & Security
✅ **Adversarial defense**: Prompt injection detection  
✅ **Access control**: RBAC enforced  
✅ **Audit logging**: All queries logged (7-year retention)

#### Principle 6: Accountability
✅ **Owner identified**: SICO AI Team  
✅ **Audit trail**: Model registry with version history  
✅ **Incident response**: Quarantine mechanism for security issues

---

## Model Governance

### Approval Workflow
1. **Development**: Model trained and validated
2. **Gate Checks**: All gates passed (see table below)
3. **Security Review**: Penetration testing complete
4. **Approval**: AI_ADMIN + Security Team sign-off
5. **Production Deployment**: Model registry status = PRODUCTION

### Gate Checks (Go/No-Go)
| Gate | Requirement | Status |
|------|-------------|--------|
| G1 | Accuracy ≥ 90% | [✅/❌] |
| G2 | F1 Score ≥ 85% | [✅/❌] |
| G3 | PII Leakage = 0 | [✅/❌] |
| G4 | Language Parity < 10% | [✅/❌] |
| G5 | Latency (p99) < 500ms | [✅/❌] |
| G6 | Security Tests Pass | [✅/❌] |
| G7 | Bias Tests Pass | [✅/❌] |

**Deployment Decision**: [APPROVED / REJECTED]

### Monitoring & Maintenance

#### Performance Monitoring
- **Metrics Tracked**: Accuracy, latency, error rate
- **Alerting Thresholds**:
  - Accuracy drop > 5%: ⚠️ Warning
  - Accuracy drop > 10%: 🚨 Alert (quarantine)
  - Latency p99 > 1s: ⚠️ Warning

#### Model Drift Detection
- **Frequency**: Weekly
- **Method**: KL divergence on prediction distributions
- **Threshold**: Drift score > 0.3 triggers retraining

#### Retraining Schedule
- **Regular**: Quarterly (every 3 months)
- **Triggered**: If drift score > 0.3 or accuracy < 85%
- **Emergency**: Regulatory change (e.g., new PDPL article)

### Versioning & Rollback
- **Version Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Rollback Trigger**: Production incident or gate check failure
- **Rollback Process**: Automated (registry status = DEPRECATED)

---

## Deployment Information

### Production Environment
- **Platform**: Azure Kubernetes Service (AKS)
- **Region**: Saudi Central (Riyadh)
- **Compute**: 4x Standard_NC6s_v3 (GPU)
- **Storage**: Azure Blob Storage (redundant)
- **Endpoint**: `https://api.sico.sa/ai/v1/[model-id]`

### Security Controls
- ✅ TLS 1.3 encryption
- ✅ JWT authentication
- ✅ RBAC authorization
- ✅ Rate limiting (100 req/min per user)
- ✅ DDoS protection (Azure Front Door)
- ✅ Audit logging (7-year retention)

### Disaster Recovery
- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes
- **Backup Frequency**: Daily (model artifacts + registry)
- **Backup Retention**: 1 year

---

## Change Log

### Version History

#### v1.0.0 (2026-02-04)
- Initial production release
- Gate checks: 7/7 passed
- Approval: AI_ADMIN (ahmed@sico.sa)

#### v0.9.0 (2026-01-15)
- Beta release for user acceptance testing
- Feedback: Improved Arabic NER by 3%

#### v0.5.0 (2025-12-01)
- Alpha release for internal testing
- Initial classification accuracy: 87%

---

## References

### Regulatory Documents
- **NCA ECC v2.0**: Essential Cybersecurity Controls
- **PDPL (2021)**: Personal Data Protection Law
- **SDAIA AI Principles (2023)**: AI Ethics & Governance

### Technical Papers
- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [Multilingual E5: Text Embeddings](https://arxiv.org/abs/2212.03533)
- [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685)

### Standards
- **ISO 42001**: AI Management System
- **ISO 27001**: Information Security Management
- **EU AI Act**: Risk-based AI regulation (adapted)

---

## Appendix A: Test Set Examples

### Example 1: Evidence Classification
**Input**: "يجب على المنشأة وضع سياسة للأمن السيبراني معتمدة من الإدارة العليا"  
**Expected**: `policy`  
**Predicted**: `policy`  
**Confidence**: 0.97 ✅

### Example 2: NER Extraction
**Input**: "Control ECC-GV-1 requires a cybersecurity governance framework approved by the Board"  
**Expected Entities**:
- `ECC-GV-1` (CONTROL_ID)
- `cybersecurity governance framework` (REQUIREMENT)
- `Board` (ENTITY)

**Predicted**: 3/3 correct ✅

### Example 3: Control Mapping
**Input**: "Screenshot showing firewall configuration for network segmentation"  
**Expected Control**: `ECC-IS-6` (Network Security)  
**Predicted**: `ECC-IS-6` (confidence: 0.82) ✅

---

## Appendix B: Contact Information

### Model Owner
**Team**: SICO AI Team  
**Email**: ai-team@sico.sa  
**Phone**: +966-xx-xxx-xxxx

### Security Contact
**Email**: security@sico.sa  
**Hotline**: +966-xx-xxx-xxxx (24/7)

### Data Protection Officer
**Name**: [DPO Name]  
**Email**: dpo@sico.sa

---

## Appendix C: License & Usage Terms

### Enterprise License
This model is proprietary and licensed to authorized SICO clients only.

**Permitted Uses**:
- ✅ Internal GRC compliance operations
- ✅ Audit preparation
- ✅ Risk assessment

**Prohibited Uses**:
- ❌ Resale or redistribution
- ❌ Reverse engineering
- ❌ Use outside GRC domain

**Data Rights**:
- Client data used for adapters remains client property
- SICO cannot use client data for other clients
- Client can request adapter deletion (90-day automatic expiry)

---

**Model Card Version**: 1.0.0  
**Last Updated**: 2026-02-04  
**Status**: PRODUCTION  
**Next Review Date**: 2026-05-04 (Quarterly)

---

**Signature**:
- **Approved by**: [AI Team Lead Name]
- **Security Reviewed by**: [CISO Name]
- **Date**: 2026-02-04
