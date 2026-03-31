$users = @(
    @("admin.role@sico.sa", "Tier1-Admin"),
    @("domain.manager@sico.sa", "Tier2-DomainMgr"),
    @("analyst@sico.sa", "Tier3-Analyst"),
    @("approver@sico.sa", "Tier4-Approver"),
    @("auditor@sico.sa", "Tier5-Auditor"),
    @("auditee@sico.sa", "Tier6-Auditee"),
    @("thirdparty@sico.sa", "Tier7-ThirdParty")
)

foreach ($u in $users) {
    $email = $u[0]
    $label = $u[1]
    
    $login = Invoke-WebRequest -Uri "https://localhost:8443/api/iam/login/" -Method POST -Body "{`"username`":`"$email`",`"password`":`"Sico@2026!`"}" -ContentType "application/json" -UseBasicParsing
    $token = ($login.Content | ConvertFrom-Json).token
    
    $cu = Invoke-WebRequest -Uri "https://localhost:8443/api/iam/current-user/" -Headers @{Authorization="Token $token"} -UseBasicParsing
    $data = $cu.Content | ConvertFrom-Json
    
    $perms = $data.permissions.PSObject.Properties.Name
    $viewPerms = $perms | Where-Object { $_ -like "view_*" }
    $addPerms = $perms | Where-Object { $_ -like "add_*" }
    $changePerms = $perms | Where-Object { $_ -like "change_*" }
    $deletePerms = $perms | Where-Object { $_ -like "delete_*" }
    $domains = $data.accessible_domains.Count
    
    Write-Host ""
    Write-Host "========================================"
    Write-Host "$label ($email)"
    Write-Host "========================================"
    Write-Host "  is_admin:       $($data.is_admin)"
    Write-Host "  is_superuser:   $($data.is_superuser)"
    Write-Host "  is_third_party: $($data.is_third_party)"
    Write-Host "  total_perms:    $($perms.Count)"
    Write-Host "  can_view:       $($viewPerms.Count)"
    Write-Host "  can_create:     $($addPerms.Count)"
    Write-Host "  can_edit:       $($changePerms.Count)"
    Write-Host "  can_delete:     $($deletePerms.Count)"
    Write-Host "  domains:        $domains"
    
    # Key sidebar-visible features
    $sidebarItems = @("view_riskassessment","view_complianceassessment","view_asset","view_appliedcontrol","view_threat","view_framework","view_user","view_folder","view_riskscenario","view_evidence","view_policy","view_incident","add_riskassessment","add_complianceassessment","add_appliedcontrol","add_user","change_user","delete_user","backup","restore","approve_riskacceptance")
    
    $visible = @()
    foreach ($s in $sidebarItems) {
        if ($perms -contains $s) { $visible += $s }
    }
    Write-Host "  key_features:   $($visible -join ', ')"
}
