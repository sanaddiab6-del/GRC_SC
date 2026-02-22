# Risk Assessment Modal - Implementation Summary

## ✅ Implementation Complete

Successfully implemented Risk Assessment functionality with professional modal interface, role-based access control, and real-time risk score calculation.

## Files Created/Modified

### Created:
- **`src/frontend/components/modals/RiskAssessmentModal.tsx`** (450+ lines)
  - Professional assessment modal with blue gradient theme
  - Real-time risk score calculation
  - Bilingual support (Arabic/English)
  - Form validation
  - Backend integration

### Modified:
- **`src/frontend/app/[locale]/risks/[id]/page.tsx`** (+40 lines)
  - Added "Assess Risk" button with role-based visibility
  - Integrated RiskAssessmentModal component
  - Added state management
  - Connected to mutate() for data refresh

## Key Features

### Assessment Modal:
- **3 Form Fields**:
  - Likelihood (1-5 dropdown): Very Rare → Almost Certain
  - Impact (1-5 dropdown): Insignificant → Catastrophic
  - Justification (textarea): Required, min 10 characters

- **Real-time Calculation**: Risk score updates as you change likelihood/impact
- **Color-coded Levels**: Critical (Red), High (Orange), Medium (Yellow), Low (Green)
- **Change Detection**: Warning shown if scores change significantly (≥2 points)
- **Pre-filled Data**: Loads current likelihood and impact values

### Role-Based Access Control:
✅ **Authorized Roles** (can see "Assess Risk" button):
- Admin
- Compliance Officer
- Auditor

❌ **Unauthorized Roles** (button hidden):
- Analyst
- Viewer

## Backend Integration

### Assess Risk Endpoint:
```http
POST /api/v1/risks/{risk_id}/assess
Authorization: Bearer {token}
Content-Type: application/json

{
  "likelihood": 4,
  "impact": 3,
  "justification": "New threat intelligence indicates increased likelihood..."
}
```

### Response:
```json
{
  "risk_id": "uuid",
  "likelihood": 4,
  "impact": 3,
  "inherent_risk_score": 12,
  "inherent_risk_level": "high",
  "last_assessed_at": "2026-02-22T10:30:00Z",
  "assessed_by": "user@example.com",
  "justification": "New threat intelligence..."
}
```

## User Flow

### Assessment Flow:
1. User opens risk detail page
2. If authorized, sees **"Assess Risk"** button (blue, with checkmark icon)
3. Clicks button → Modal opens with current scores pre-filled
4. User adjusts likelihood and/or impact (1-5 scales)
5. Risk score updates in real-time (likelihood × impact)
6. Risk level updates with color (Critical/High/Medium/Low)
7. User enters justification (min 10 characters required)
8. If significant change (≥2 points), warning appears
9. User clicks "Assess Risk"
10. Loading spinner appears, button disables
11. POST to `/api/v1/risks/{id}/assess`
12. Success: Green toast "Risk assessed successfully"
13. Modal closes, risk details refresh automatically
14. Updated scores visible in detail page

## Validation Rules

- **Likelihood**: Required, must be 1-5
- **Impact**: Required, must be 1-5
- **Justification**: Required, min 10 characters
- **Authorization**: Must be Admin, Compliance Officer, or Auditor

## Risk Score Calculation

| Score | Level | Color | Trigger |
|-------|-------|-------|---------|
| 20-25 | Critical | Red | Likelihood=5, Impact=5 or similar |
| 12-19 | High | Orange | Likelihood=4, Impact=3+ |
| 6-11 | Medium | Yellow | Likelihood=3, Impact=2+ |
| 1-5 | Low | Green | Low likelihood or impact |

**Formula**: Score = Likelihood × Impact

## UI/UX Features

### Professional Design:
- **Header**: Blue-to-indigo gradient with white text
- **Score Display**: Large, prominent box with live updates
- **Info Box**: Blue background with assessment guidelines
- **Warning Box**: Yellow background for significant changes
- **Buttons**: 
  - Primary: Blue gradient (Assess Risk)
  - Secondary: Gray (Cancel)

### Change Detection:
When likelihood or impact changes by 2+ points:
```
⚠️ Significant Assessment Change

You have significantly modified the assessment. Please ensure
your justification clearly documents this change.
```

### Score Display:
```
Updated Risk Score: 12
Risk Level: High
Formula: 4 (likelihood) × 3 (impact) = 12
```

## Testing Checklist

### Access Control:
- [ ] Admin can see "Assess Risk" button
- [ ] Compliance Officer can see "Assess Risk" button
- [ ] Auditor can see "Assess Risk" button
- [ ] Analyst CANNOT see button
- [ ] Viewer CANNOT see button
- [ ] Unauthenticated user CANNOT see button

### Modal Functionality:
- [ ] Click "Assess Risk" → Modal opens
- [ ] Current scores pre-filled
- [ ] Change likelihood → Score updates
- [ ] Change impact → Score updates
- [ ] Risk level color changes correctly
- [ ] Significant change warning appears when ≥2 point change
- [ ] Submit without justification → Error
- [ ] Submit with justification < 10 chars → Error
- [ ] Submit with valid data → Success

### Backend Integration:
- [ ] POST request sent with correct data
- [ ] JWT token included in headers
- [ ] Success → Toast notification
- [ ] Success → Modal closes
- [ ] Success → Risk details refresh
- [ ] Updated scores visible in UI
- [ ] Network error → Error message shown
- [ ] Permission denied → Error message shown

### Bilingual Support:
- [ ] Arabic locale shows Arabic labels
- [ ] English locale shows English labels
- [ ] Error messages in correct language
- [ ] Success toast in correct language
- [ ] Dropdown options in correct language

## Component Props

```typescript
interface RiskAssessmentModalProps {
  isOpen: boolean;              // Control modal visibility
  onClose: () => void;          // Called when modal closes
  onSuccess: () => void;        // Called after successful assessment
  locale: 'en' | 'ar';          // Current language
  riskId: string;               // Risk UUID to assess
  currentLikelihood?: number;   // Pre-fill current likelihood (1-5)
  currentImpact?: number;       // Pre-fill current impact (1-5)
}
```

## Integration Pattern

### In Risk Detail Page:
```tsx
// Import
import RiskAssessmentModal from '@/components/modals/RiskAssessmentModal';

// State
const [isAssessModalOpen, setIsAssessModalOpen] = useState(false);

// Role check
const canAssessRisk = () => {
  const user = JSON.parse(localStorage.getItem('currentUser'));
  const role = user.role?.toLowerCase() || '';
  return ['admin', 'compliance officer', 'auditor'].includes(role);
};

// Button
{canAssessRisk() && (
  <Button onClick={() => setIsAssessModalOpen(true)}>
    Assess Risk
  </Button>
)}

// Modal
<RiskAssessmentModal
  isOpen={isAssessModalOpen}
  onClose={() => setIsAssessModalOpen(false)}
  onSuccess={() => mutate()}
  locale={locale}
  riskId={riskId}
  currentLikelihood={risk?.likelihood}
  currentImpact={risk?.impact}
/>
```

## Success Feedback

### Toast Notification:
- **Appearance**: Green background, white text, rounded
- **Position**: Top-right corner
- **Duration**: 3 seconds auto-dismiss
- **Messages**:
  - English: "Risk assessed successfully"
  - Arabic: "تم تقييم المخاطرة بنجاح"

### Data Refresh:
- Uses SWR's `mutate()` function
- Automatically refetches risk details
- No page reload needed
- Updated scores/level visible immediately

## Compliance Impact

This Risk Assessment functionality addresses:
- **NCA ECC-RM-2**: Regular risk assessment and scoring
- **NCA ECC-RM-4**: Risk assessment documentation (justification field)
- **ISO 27001 A.8.2**: Periodic risk assessment
- **NIST CSF ID.RA-1**: Risk assessment process

### Audit Trail:
Backend logs each assessment with:
- Assessed by (user email)
- Assessment timestamp
- Previous vs new scores
- Justification text
- Risk level changes

## Deployment Notes

- Backend must be running on `http://localhost:8000`
- JWT token required in localStorage as `access_token`
- User data in localStorage as `currentUser` with role field
- Permission check happens on frontend (visual) and backend (enforcement)

## Error Handling

### User-Friendly Errors:
- Empty justification: "Justification is required (min 10 characters)"
- Network error: "Failed to assess risk. Please try again."
- Permission denied: Backend error message displayed
- Invalid role: Button not visible

### Technical Errors Logged:
- Console logs failed API calls
- Error response details preserved
- Stack traces for debugging

## Likelihood Scale

| Value | Label (EN) | Label (AR) | Description |
|-------|------------|------------|-------------|
| 1 | Very Rare | نادر جداً | Almost never happens |
| 2 | Rare | نادر | Unlikely to happen |
| 3 | Possible | محتمل | Could happen |
| 4 | Likely | مرجح | Probably will happen |
| 5 | Almost Certain | شبه مؤكد | Expected to happen |

## Impact Scale

| Value | Label (EN) | Label (AR) | Description |
|-------|------------|------------|-------------|
| 1 | Insignificant | ضئيل | Minimal impact |
| 2 | Minor | بسيط | Small impact |
| 3 | Moderate | متوسط | Noticeable impact |
| 4 | Major | كبير | Significant impact |
| 5 | Catastrophic | كارثي | Severe impact |

## Platform Progress Update

**Before Implementation**:
- Risk workflows: 60% (view + create + edit)
- Platform: 48%

**After Implementation**:
- Risk workflows: **75%** (view + create + edit + assess) ✅
- Platform: **51%** (+3%) ✅

## Future Enhancements

### Potential Features:
1. **Assessment History**: Show timeline of all assessments
2. **Comparison View**: Compare current vs previous assessments
3. **Automated Alerts**: Notify stakeholders when risk level increases
4. **Bulk Assessment**: Assess multiple risks at once
5. **Assessment Calendar**: Schedule periodic reassessments
6. **Justification Templates**: Common justification phrases
7. **Risk Trend Chart**: Visualize risk score changes over time
8. **Impact Analysis**: Detailed breakdown of impact categories

### Phase 3 Integration:
Once security is complete (Phase 2.1):
- Real permission system (not localStorage)
- Full audit trail with version history
- Notification system for risk owners
- Dashboard widget for recent assessments
- Reporting: Assessment frequency metrics

## Quick Start Testing

### Terminal 1 - Backend:
```bash
cd src/backend
uvicorn main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd src/frontend
npm run dev
```

### Browser:
1. Navigate to `http://localhost:3000/en/risks`
2. Click any risk to view details
3. If logged in as Admin/Auditor/Compliance Officer, see "Assess Risk" button
4. Click button → Modal opens
5. Adjust likelihood/impact
6. Enter justification
7. Submit → Success toast → Data refreshes

## Files to Reference

- Modal: [src/frontend/components/modals/RiskAssessmentModal.tsx](src/frontend/components/modals/RiskAssessmentModal.tsx)
- Detail Page: [src/frontend/app/[locale]/risks/[id]/page.tsx](src/frontend/app/[locale]/risks/[id]/page.tsx)
- Backend Schema: `src/backend/risk/schemas.py` (AssessmentRequest)
- Backend Router: `src/backend/risk/router.py` (assess_risk endpoint)

## Pattern Consistency

This implementation follows the established modal pattern:
- ✅ Evidence Upload Modal (Session 1)
- ✅ Evidence Approval Modal (Session 2)
- ✅ Risk Create/Edit Modal (Session 3)
- ✅ Risk Assessment Modal (Session 4) ← **Current**

### Proven Pattern:
1. Separate modal component in `/components/modals/`
2. Props: isOpen, onClose, onSuccess, locale
3. State management in page component
4. SWR mutate() for data refresh
5. Toast notifications for success
6. Loading states during submission
7. Role-based access control
8. Bilingual support throughout

---

**Status**: ✅ Complete and Ready for Testing  
**Lines of Code**: 490+ (450 modal + 40 integration)  
**Complexity**: Medium (simpler than Create/Edit, more than Approval)  
**Testing Priority**: High (core risk management workflow)
