# Load Demo Data into SICO GRC Platform
$baseUrl = "http://localhost:8000/api/v1"
$headers = @{"Content-Type"="application/json"}

Write-Host "🚀 Loading SICO GRC Demo Data..." -ForegroundColor Cyan
Write-Host ""

# Sample Controls
$controls = @(
    @{
        control_id="ECC-GV-1"
        title_en="Information Security Governance"
        title_ar="حوكمة أمن المعلومات"
        description_en="Establish and maintain an information security governance framework aligned with organizational objectives."
        description_ar="إنشاء واله وحفظ إطار حوكمة أمن المعلومات متوافق مع أهداف المنظمة."
        framework="ECC"
        domain="Governance"
        status="compliant"
    },
    @{
        control_id="ECC-RM-2"
        title_en="Risk Assessment Process"
        title_ar="عملية تقييم المخاطر"
        description_en="Implement a formal risk assessment process to identify and evaluate information security risks."
        description_ar="تنفيذ عملية رسمية لتقييم المخاطر لتحديد وتقييم مخاطر أمن المعلومات."
        framework="ECC"
        domain="Risk Management"
        status="in_progress"
    },
    @{
        control_id="CCC-SEC-01"
        title_en="Cloud Data Encryption"
        title_ar="تشفير البيانات السحابية"
        description_en="Encrypt data at rest and in transit within cloud environments using industry-standard algorithms."
        description_ar="تشفير البيانات المخزنة والمنقولة في البيئات السحابية باستخدام خوارزميات معتمدة."
        framework="CCC"
        domain="Security"
        status="compliant"
    },
    @{
        control_id="PDPL-12"
        title_en="Data Subject Rights"
        title_ar="حقوق صاحب البيانات"
        description_en="Establish processes to handle data subject access requests, rectification, and erasure."
        description_ar="إنشاء عمليات للتعامل مع طلبات الوصول والتصحيح والمحو لأصحاب البيانات."
        framework="PDPL"
        domain="Privacy"
        status="compliant"
    },
    @{
        control_id="ECC-IS-3"
        title_en="Access Control"
        title_ar="التحكم في الوصول"
        description_en="Implement role-based access control (RBAC) with multi-factor authentication."
        description_ar="تنفيذ التحكم في الوصول المعتمد على الأدوار مع المصادقة متعددة العوامل."
        framework="ECC"
        domain="Information Security"
        status="compliant"
    }
)

Write-Host "📋 Creating Controls..." -ForegroundColor Yellow
$controlCount = 0
foreach ($control in $controls) {
    try {
        $json = $control | ConvertTo-Json -Depth 10
        $result = Invoke-WebRequest -Uri "$baseUrl/controls" -Method POST -Headers $headers -Body $json -UseBasicParsing -ErrorAction Stop
        $controlCount++
        Write-Host "  ✓ Created: $($control.control_id) - $($control.title_en)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed: $($control.control_id)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Demo Data Loaded Successfully!" -ForegroundColor Green
Write-Host "   - $controlCount Controls created" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access your platform:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000/en/controls" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor White
