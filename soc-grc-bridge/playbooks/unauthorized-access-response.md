# Unauthorized Access Response Playbook

**Playbook Version**: 1.0  
**Last Updated**: February 2026  
**Owner**: SOC Team / GRC Team

---

## Overview

This playbook provides step-by-step procedures for responding to unauthorized access attempts and integrating the response with GRC compliance requirements.

## Trigger Conditions

This playbook is triggered when:
- Failed login attempts exceed threshold (e.g., 5 failed attempts in 10 minutes)
- Access to unauthorized resources detected
- Privilege escalation attempt detected
- Access from suspicious location or device
- Off-hours access by non-authorized users

## Severity Classification

**Critical**: Active breach with confirmed unauthorized access  
**High**: Multiple failed attempts or suspicious patterns  
**Medium**: Isolated failed attempts with no breach  
**Low**: Routine monitoring alerts

---

## Response Procedures

### Phase 1: Initial Detection (0-15 minutes)

#### Automated Actions
1. **Alert Generation**
   - SIEM generates alert with incident details
   - Alert sent to SOC team via configured channels
   - Incident ticket created automatically

2. **Initial Containment** (if configured)
   - Account temporarily locked after threshold exceeded
   - IP address blocked at firewall (if from external source)
   - Session terminated (if active)

#### Manual Actions
1. **Alert Triage**
   - SOC analyst reviews alert details
   - Verify if legitimate user or attack
   - Classify severity level

2. **Initial Investigation**
   - Review access logs
   - Check user's recent activity
   - Verify user location and device
   - Contact user if necessary

---

### Phase 2: Investigation & Analysis (15-60 minutes)

#### Data Collection
Collect the following information:
- [ ] Full access logs (30 days prior)
- [ ] User account details and permissions
- [ ] Failed login attempt records with timestamps
- [ ] Source IP addresses and geolocation
- [ ] Device fingerprints
- [ ] Recent password changes
- [ ] Recent permission changes

#### Analysis Activities
- [ ] Determine if credentials were compromised
- [ ] Identify attack vector (brute force, credential stuffing, etc.)
- [ ] Assess scope of potential breach
- [ ] Check for lateral movement attempts
- [ ] Review other accounts from same source IP

#### GRC Integration
**Automated Evidence Collection**:
- Access logs automatically saved to evidence repository
- Incident details mapped to affected controls:
  - ECC-2-2-1: Access Control Policy
  - ECC-2-2-3: User Access Review
  - ECC-2-2-4: Privileged Access Management

**Control Status Update**:
- Flag affected controls for review
- Update control effectiveness scores
- Trigger gap analysis if pattern detected

---

### Phase 3: Containment & Remediation (1-4 hours)

#### Containment Actions
- [ ] Reset user credentials if compromised
- [ ] Revoke active sessions
- [ ] Block source IP/network if malicious
- [ ] Isolate affected systems if necessary
- [ ] Enable MFA if not already active

#### Remediation Steps
- [ ] Remove unauthorized access
- [ ] Restore proper permissions
- [ ] Patch identified vulnerabilities
- [ ] Update access control rules
- [ ] Strengthen authentication mechanisms

#### Communication
- [ ] Notify user (if legitimate account holder)
- [ ] Notify management (if critical severity)
- [ ] Update incident ticket with status
- [ ] Inform compliance team

---

### Phase 4: Documentation & Compliance (4-24 hours)

#### Evidence Documentation
Ensure the following evidence is collected and stored:

1. **Technical Evidence**
   - [ ] Access logs (raw and analyzed)
   - [ ] SIEM alert details
   - [ ] Network traffic logs
   - [ ] Authentication logs
   - [ ] System event logs

2. **Response Evidence**
   - [ ] Incident response timeline
   - [ ] Actions taken (with timestamps)
   - [ ] Personnel involved
   - [ ] Communication records
   - [ ] Remediation steps

3. **Compliance Evidence**
   - [ ] Control effectiveness assessment
   - [ ] Gap identification (if any)
   - [ ] Remediation plan
   - [ ] Lessons learned

#### GRC Platform Updates
**Automated Updates**:
- Evidence automatically uploaded to GRC platform
- Control mappings updated
- Compliance status refreshed

**Manual Updates**:
- [ ] Document lessons learned
- [ ] Update access control policy (if needed)
- [ ] Schedule user access review
- [ ] Update risk assessment

---

### Phase 5: Post-Incident Activities (24-72 hours)

#### Root Cause Analysis
- [ ] Identify how unauthorized access was attempted
- [ ] Determine if security controls failed
- [ ] Assess if policies were violated
- [ ] Identify systemic issues

#### Improvement Actions
- [ ] Update access control policies
- [ ] Enhance monitoring rules
- [ ] Improve detection capabilities
- [ ] Conduct user training (if needed)
- [ ] Strengthen authentication requirements

#### Compliance Review
- [ ] Review affected controls
- [ ] Update control implementation status
- [ ] Schedule control effectiveness testing
- [ ] Update audit evidence
- [ ] Brief compliance team on findings

#### Reporting
- [ ] Complete incident report
- [ ] Update GRC dashboard
- [ ] Notify stakeholders
- [ ] Archive all documentation

---

## Escalation Procedures

### Level 1: SOC Team
- Handle routine unauthorized access attempts
- Document and contain incidents
- Follow standard procedures

### Level 2: Security Manager + GRC Team
**Escalate when**:
- Multiple accounts affected
- Privileged account compromised
- Evidence of breach or data access
- Repeated attempts over time

### Level 3: CISO + Executive Team
**Escalate when**:
- Active data breach confirmed
- Regulatory notification required
- Significant business impact
- External threat actor identified

---

## GRC Integration Points

### Automated Integrations
1. **Evidence Collection**
   - Access logs → Evidence repository
   - Incident details → Control mappings
   - Response actions → Audit trail

2. **Control Updates**
   - Incident count → Control effectiveness
   - Gap identified → Remediation tracker
   - Pattern detected → Risk score update

3. **Notifications**
   - Compliance team alerted automatically
   - Control owners notified of impacts
   - Dashboard updated in real-time

### Manual Integrations
1. **Policy Updates**
   - Review and update access control policy
   - Enhance authentication requirements
   - Strengthen monitoring procedures

2. **Training**
   - Update security awareness training
   - Conduct targeted training for affected users
   - Reinforce access control procedures

---

## Metrics & KPIs

Track the following metrics:
- Mean time to detect (MTTD)
- Mean time to respond (MTTR)
- Mean time to contain (MTTC)
- Number of incidents by type
- False positive rate
- Control effectiveness score
- Evidence collection completeness

---

## Related Documents

- Access Control Policy (ECC-2-2-1)
- User Access Review Procedure (ECC-2-2-3)
- Privileged Access Management Procedure (ECC-2-2-4)
- Incident Response Plan
- GRC Platform User Guide

---

## Appendix A: Evidence Checklist

Use this checklist to ensure complete evidence collection:

**Access Logs**:
- [ ] Authentication logs (30 days)
- [ ] Authorization logs
- [ ] Failed login attempts
- [ ] Successful logins (for comparison)

**User Information**:
- [ ] User account details
- [ ] Current permissions
- [ ] Recent permission changes
- [ ] Account creation date
- [ ] Last successful login

**Source Information**:
- [ ] Source IP addresses
- [ ] Geolocation data
- [ ] Device information
- [ ] User agent strings

**Response Documentation**:
- [ ] Incident timeline
- [ ] Actions taken
- [ ] Personnel involved
- [ ] Notifications sent
- [ ] Outcomes achieved

---

**Playbook Version**: 1.0  
**Last Updated**: February 2026  
**Review Date**: August 2026
