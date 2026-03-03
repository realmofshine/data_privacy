"""Mock responses for all 18 agents — used when USE_MOCK_DATA=True.

Each function returns the same dict shape as the real agent's stream() method.
"""


def mock_news_verification(message: str) -> dict:
    return {
        "agent_name": "NewsVerificationAgent",
        "agent_message": (
            "VERDICT: REAL\n\n"
            "The article describes a legitimate data breach incident. "
            "Cross-referenced with 3 independent sources:\n"
            "- Reuters: Confirmed the breach report\n"
            "- SecurityWeek: Published corroborating details\n"
            "- Company press release: Official statement found\n\n"
            "Confidence: 92%\n"
            "Assessment: The article is factually accurate and can be processed."
        ),
    }


def mock_tavily_verification(message: str) -> dict:
    return {
        "agent_name": "TavilyNewsVerificationAgent",
        "agent_message": (
            "VERDICT: REAL\n\n"
            "Web search confirms the breach incident.\n"
            "Sources found: 7 independent reports\n\n"
            "Key sources:\n"
            "- https://www.reuters.com/technology/breach-report-2025\n"
            "- https://www.securityweek.com/data-breach-analysis\n"
            "- https://techcrunch.com/2025/breach-confirmed\n\n"
            "All sources corroborate the core claims. No contradictory evidence found."
        ),
    }


def mock_nlp_agent(message: str) -> dict:
    return {
        "agent_name": "NLPAgent",
        "agent_message": (
            "INCIDENT PROFILE:\n\n"
            "Organization: TechCorp International\n"
            "Industry: Technology / Cloud Services\n"
            "Date Reported: March 2025\n"
            "Attack Vector: Ransomware (LockBit 3.0)\n"
            "Impact: 500,000 customer records compromised\n\n"
            "DATA EXPOSED:\n"
            "- Full names\n"
            "- Email addresses\n"
            "- Phone numbers\n"
            "- Hashed passwords (SHA-256)\n"
            "- Last 4 digits of credit cards\n\n"
            "THIRD PARTIES IDENTIFIED:\n"
            "1. AWS (Cloud Infrastructure)\n"
            "2. Stripe (Payment Processing)\n"
            "3. Twilio (Communications)\n"
            "4. Datadog (Monitoring)\n\n"
            "SEVERITY: HIGH\n"
            "REGULATORY IMPACT: GDPR, CCPA applicable"
        ),
        "agent_metadata": {
            "Incident": {
                "id": "INC-2025-0342",
                "description": "TechCorp ransomware breach affecting 500K records",
                "organization": "TechCorp International",
                "severity": "HIGH",
                "attack_vector": "Ransomware",
            },
            "ThirdParties": ["AWS", "Stripe", "Twilio", "Datadog"],
        },
    }


def mock_risk_agent(message: str, metadata: dict = None) -> dict:
    return {
        "agent_name": "RiskAgent",
        "agent_message": (
            "RISK ASSESSMENT:\n\n"
            "Overall Risk Score: 7.8 / 10 (HIGH)\n\n"
            "THIRD-PARTY RISK SCORES:\n"
            "| Vendor | Risk Score | PII Shared | Criticality |\n"
            "| AWS | 0.35 | Yes | CRITICAL |\n"
            "| Stripe | 0.62 | Yes (payment) | HIGH |\n"
            "| Twilio | 0.28 | Yes (phone) | MEDIUM |\n"
            "| Datadog | 0.15 | No | LOW |\n\n"
            "HIGH-RISK FINDINGS:\n"
            "- Stripe: Elevated risk due to payment data exposure and direct PII sharing\n"
            "- AWS: Critical dependency but lower direct risk score\n\n"
            "RECOMMENDATION: Immediate vendor risk review for Stripe"
        ),
        "predictions": [
            {"thirdPartyId": "tp-001", "companyName": "Stripe", "riskScore": 0.62},
            {"thirdPartyId": "tp-002", "companyName": "AWS", "riskScore": 0.35},
            {"thirdPartyId": "tp-003", "companyName": "Twilio", "riskScore": 0.28},
            {"thirdPartyId": "tp-004", "companyName": "Datadog", "riskScore": 0.15},
        ],
    }


def mock_similar_company(message: str, metadata: dict = None) -> dict:
    return {
        "agent_name": "SimilarCompanyAgent",
        "agent_message": (
            "SIMILAR COMPANIES (potential risk exposure):\n\n"
            "Based on the identified third parties, similar companies that may face analogous risks:\n"
            "1. Shopify (similar payment stack)\n"
            "2. Square (payment processing)\n"
            "3. Zendesk (customer data platform)\n"
            "4. HubSpot (CRM with similar data footprint)\n"
            "5. Intercom (communications platform)\n\n"
            "These companies share overlapping vendor dependencies and data handling patterns."
        ),
        "similar_companies": ["Shopify", "Square", "Zendesk", "HubSpot", "Intercom"],
    }


def mock_alert_agent(metadata: dict = None) -> dict:
    return {
        "agent_name": "AlertAgent",
        "agent_message": (
            "EXECUTIVE SUMMARY:\n"
            "A significant ransomware incident at TechCorp has exposed 500,000 customer records. "
            "Our analysis identified 1 RED alert (Stripe — direct PII exposure through payment processing), "
            "1 ORANGE alert (AWS — critical infrastructure dependency), and 5 YELLOW alerts for similar companies.\n\n"
            "RED ALERTS:\n"
            "- Company: Stripe\n"
            "- Risk Score: 0.62 (HIGH)\n"
            "- Reason: Direct operational dependency with confirmed PII data sharing. "
            "Payment data flows through Stripe, creating secondary exposure risk.\n\n"
            "YELLOW ALERTS:\n"
            "Advisory alerts for: Shopify, Square, Zendesk, HubSpot, Intercom — "
            "similar vendor profiles warrant proactive monitoring.\n\n"
            "INCIDENT PROFILE:\n"
            "- Organization: TechCorp International\n"
            "- Industry: Technology / Cloud Services\n"
            "- Date Reported: March 2025\n"
            "- Impact: 500,000 records\n"
            "- Data Exposed: PII (names, emails, phones, hashed passwords)\n"
            "- Attack Vector: Ransomware (LockBit 3.0)\n"
            "- Location: United States\n"
            "- Consequences: Regulatory notification required under GDPR and CCPA\n\n"
            "SUGGESTIONS:\n"
            "1. Immediately contact Stripe to assess shared data exposure\n"
            "2. Rotate all API keys and credentials shared with affected vendors\n"
            "3. Issue GDPR Article 33 notification within 72 hours\n"
            "4. Engage forensic investigation team\n"
            "5. Review cyber insurance coverage for this incident type"
        ),
        "alerts": {
            "red_alerts": [{"company_name": "Stripe", "risk_score": 0.62, "alert_type": "RED"}],
            "orange_alerts": [{"company_name": "AWS", "risk_score": 0.35, "alert_type": "ORANGE"}],
            "yellow_alerts": [
                {"company_name": "Shopify"}, {"company_name": "Square"},
                {"company_name": "Zendesk"}, {"company_name": "HubSpot"},
            ],
        },
    }


def mock_suggestion_agent(incident_id: str) -> dict:
    return {
        "agent_name": "SuggestionAgent",
        "agent_message": (
            "SUGGESTIONS:\n\n"
            "1. IMMEDIATE (0-24 hours):\n"
            "   - Isolate affected systems and preserve forensic evidence\n"
            "   - Activate incident response team and war room\n"
            "   - Contact cyber insurance carrier\n\n"
            "2. SHORT-TERM (24-72 hours):\n"
            "   - Issue GDPR Article 33 notification to supervisory authority\n"
            "   - Begin individual notification process for affected users\n"
            "   - Rotate all shared API keys and credentials\n\n"
            "3. MEDIUM-TERM (1-4 weeks):\n"
            "   - Complete forensic investigation\n"
            "   - Implement additional monitoring\n"
            "   - Vendor risk reassessment\n\n"
            "4. LONG-TERM:\n"
            "   - Revise security architecture\n"
            "   - Update incident response plan\n"
            "   - Conduct tabletop exercises"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════
# NEW MODE AGENTS
# ═══════════════════════════════════════════════════════════════════════

def mock_compliance(message: str) -> dict:
    return {
        "agent_name": "ComplianceAgent",
        "agent_message": (
            "COMPLIANCE ASSESSMENT:\n\n"
            "1. APPLICABLE REGULATIONS:\n\n"
            "GDPR (General Data Protection Regulation):\n"
            "- Article 33: Notification to supervisory authority within 72 hours\n"
            "- Article 34: Communication to data subjects without undue delay\n"
            "- Article 82: Right to compensation for data subjects\n"
            "- Maximum penalty: €20M or 4% of global annual turnover\n\n"
            "CCPA (California Consumer Privacy Act):\n"
            "- §1798.150: Private right of action for data breaches\n"
            "- Statutory damages: $100-$750 per consumer per incident\n"
            "- Notification deadline: 'Most expedient time possible'\n\n"
            "PCI-DSS (Payment Card Industry):\n"
            "- Requirement 12.10: Incident response plan must be activated\n"
            "- Card brands must be notified within 24 hours\n"
            "- Forensic investigation by PFI required\n\n"
            "2. NOTIFICATION REQUIREMENTS:\n"
            "| Recipient | Deadline | Method |\n"
            "| Supervisory Authority (GDPR) | 72 hours | Written notification |\n"
            "| Affected Individuals | Without undue delay | Email + postal |\n"
            "| Card Brands (PCI) | 24 hours | Incident report form |\n"
            "| State AG (CCPA) | 'Most expedient' | Written notice |\n"
            "| Board of Directors | 24 hours | Emergency board session |\n"
            "| Cyber Insurance | Immediately | Claims notification |\n\n"
            "3. RISK OF NON-COMPLIANCE:\n"
            "- Estimated GDPR fine: €2.5M — €8M\n"
            "- CCPA statutory damages: $50M — $375M (500K × $100-$750)\n"
            "- PCI-DSS: Loss of payment processing ability\n"
            "- Reputational impact: HIGH\n\n"
            "4. RECOMMENDED ACTIONS:\n"
            "- Immediate: Engage DPO, activate IR plan, preserve evidence\n"
            "- 72 hours: File GDPR Article 33 notification\n"
            "- 30 days: Complete DPIA, update processing records"
        ),
    }


def mock_incident_response(message: str) -> dict:
    return {
        "agent_name": "IncidentResponseAgent",
        "agent_message": (
            "INCIDENT RESPONSE PLAYBOOK:\n\n"
            "INCIDENT CLASSIFICATION:\n"
            "- Type: Ransomware\n"
            "- Severity: CRITICAL\n"
            "- Estimated Impact: 500,000 affected individuals\n\n"
            "PHASE 1 — CONTAIN (Hour 0-1):\n"
            "☐ Isolate affected servers from the network\n"
            "☐ Disable compromised user accounts\n"
            "☐ Block known C2 IP addresses at firewall\n"
            "☐ Preserve volatile memory (RAM dumps)\n"
            "Owner: SOC Team Lead\n\n"
            "PHASE 2 — ASSESS (Hour 1-4):\n"
            "☐ Determine scope of encrypted/exfiltrated data\n"
            "☐ Identify patient zero and initial access vector\n"
            "☐ Map lateral movement using EDR logs\n"
            "☐ Assess backup integrity\n"
            "Owner: Incident Commander\n\n"
            "PHASE 3 — NOTIFY (Hour 4-24):\n"
            "☐ Notify CISO and executive team\n"
            "☐ Activate cyber insurance carrier\n"
            "☐ Engage external forensics firm (CrowdStrike/Mandiant)\n"
            "☐ Legal hold on all relevant data\n"
            "Owner: CISO\n\n"
            "PHASE 4 — REMEDIATE (Hour 24-72):\n"
            "☐ Rebuild affected systems from clean images\n"
            "☐ Apply patches for exploited vulnerabilities\n"
            "☐ Reset all credentials in affected domain\n"
            "☐ Deploy enhanced EDR monitoring\n"
            "Owner: IT Security Team\n\n"
            "PHASE 5 — RECOVER (Day 3-7):\n"
            "☐ Restore from verified clean backups\n"
            "☐ Validate system integrity\n"
            "☐ Resume operations in phased approach\n"
            "Owner: IT Operations\n\n"
            "MITRE ATT&CK MAPPING:\n"
            "- Initial Access: T1566 (Phishing) → T1078 (Valid Accounts)\n"
            "- Execution: T1059 (Command Line) → T1486 (Data Encrypted for Impact)\n"
            "- Exfiltration: T1041 (Exfiltration Over C2 Channel)"
        ),
    }


def mock_data_mapping(message: str) -> dict:
    return {
        "agent_name": "DataMappingAgent",
        "agent_message": (
            "DATA FLOW MAP:\n\n"
            "1. PROCESSING ACTIVITIES:\n"
            "| Activity | Purpose | Legal Basis | Data Categories | Recipients | Retention |\n"
            "| Customer Onboarding | Service delivery | Contract | Name, Email, Phone | CRM, Email | 7 years |\n"
            "| Payment Processing | Billing | Contract | Card details, Address | Stripe | 5 years |\n"
            "| Support Tickets | Customer service | Legitimate interest | Name, Email, Issue | Zendesk | 3 years |\n"
            "| Analytics | Product improvement | Consent | Usage data, IP | Mixpanel | 2 years |\n"
            "| Marketing | Campaigns | Consent | Email, Preferences | Mailchimp | Until withdrawal |\n\n"
            "2. DATA CLASSIFICATION:\n"
            "| Data Element | Classification | Sensitivity |\n"
            "| Customer Name | PII | Confidential |\n"
            "| Email Address | PII | Confidential |\n"
            "| Credit Card | PCI | Restricted |\n"
            "| IP Address | PII | Internal |\n"
            "| Health Records | PHI | Restricted |\n"
            "| Usage Analytics | Non-PII | Internal |\n\n"
            "3. DATA FLOW DIAGRAM:\n"
            "Web App → Customer PII → AWS RDS (storage)\n"
            "AWS RDS → Payment Data → Stripe API (processing)\n"
            "AWS RDS → Contact Data → Twilio (notifications)\n"
            "AWS RDS → Support Data → Zendesk (tickets)\n"
            "AWS RDS → Analytics → Mixpanel (anonymized)\n\n"
            "4. GAPS IDENTIFIED:\n"
            "- Missing DPIA for Mixpanel analytics processing\n"
            "- No documented data sharing agreement with Zendesk\n"
            "- Retention policy not enforced for support tickets\n\n"
            "5. RECOMMENDATIONS:\n"
            "- Complete DPIA for all processing activities\n"
            "- Implement automated data retention enforcement\n"
            "- Sign updated DPAs with all processors"
        ),
    }


def mock_dsr(message: str) -> dict:
    return {
        "agent_name": "DSRAgent",
        "agent_message": (
            "DSR PROCESSING REPORT:\n\n"
            "REQUEST CLASSIFICATION:\n"
            "- Type: Right to Erasure (GDPR Article 17)\n"
            "- Data Subject: Customer ID C-4521\n"
            "- Received: March 3, 2025\n"
            "- Deadline: April 2, 2025 (30 days)\n"
            "- Priority: STANDARD\n\n"
            "IDENTITY VERIFICATION:\n"
            "- Method: Email verification + ID document\n"
            "- Status: VERIFIED ✓\n\n"
            "SYSTEMS INVENTORY:\n"
            "| System | Data Found | Records | Can Delete? | Retention? |\n"
            "| CRM (Salesforce) | Yes | 12 records | Yes | None |\n"
            "| Email (SendGrid) | Yes | 847 emails | Yes | None |\n"
            "| Payment (Stripe) | Yes | 23 transactions | No | Tax (7yr) |\n"
            "| Support (Zendesk) | Yes | 5 tickets | Yes | None |\n"
            "| Analytics (Mixpanel) | Yes | ~2,400 events | Yes | None |\n"
            "| Backups (AWS S3) | Yes | In backup sets | Scheduled | 90 days |\n\n"
            "LEGAL EXCEPTIONS:\n"
            "- Stripe payment records retained for tax compliance (7 years)\n"
            "- Active contract data excluded until contract termination\n\n"
            "EXECUTION PLAN:\n"
            "☐ Delete CRM records in Salesforce\n"
            "☐ Purge email history in SendGrid\n"
            "☐ Delete support tickets in Zendesk\n"
            "☐ Anonymize analytics in Mixpanel\n"
            "☐ Flag for backup rotation (AWS S3)\n"
            "☐ Retain Stripe records (legal exception)\n\n"
            "AUDIT LOG:\n"
            "- Request received: 2025-03-03 09:15 UTC\n"
            "- Identity verified: 2025-03-03 14:22 UTC\n"
            "- Systems scanned: 2025-03-03 14:30 UTC\n"
            "- Awaiting approval for execution"
        ),
    }


def mock_dark_web(message: str) -> dict:
    return {
        "agent_name": "DarkWebMonitorAgent",
        "agent_message": (
            "DARK WEB SCAN REPORT:\n\n"
            "SCAN SUMMARY:\n"
            "- Target: techcorp.com\n"
            "- Scan Date: March 2025\n"
            "- Sources Checked: 15 dark web forums, 8 paste sites, 5 database dumps\n"
            "- Total Findings: 23\n\n"
            "[SIMULATED DATA]\n\n"
            "CRITICAL FINDINGS:\n\n"
            "Finding 1:\n"
            "- Data: 12 employee email:password pairs\n"
            "- Source: RaidForums successor (BreachForums)\n"
            "- Date: February 2025\n"
            "- Exposure: CRITICAL\n"
            "- Action: Immediate password reset required\n\n"
            "Finding 2:\n"
            "- Data: AWS API keys (AKIA...redacted)\n"
            "- Source: GitHub paste (public gist)\n"
            "- Date: January 2025\n"
            "- Exposure: CRITICAL\n"
            "- Action: Rotate keys immediately\n\n"
            "Finding 3:\n"
            "- Data: Internal Slack webhook URLs\n"
            "- Source: Pastebin\n"
            "- Date: March 2025\n"
            "- Exposure: HIGH\n"
            "- Action: Regenerate webhook URLs\n\n"
            "CREDENTIAL ANALYSIS:\n"
            "- Total compromised credentials: 12\n"
            "- Unique passwords: 8\n"
            "- Password reuse detected: Yes (4 accounts)\n"
            "- Most common pattern: Company name + year\n\n"
            "RECOMMENDATIONS:\n"
            "1. Force password reset for all 12 compromised accounts\n"
            "2. Rotate all AWS API keys found in public repos\n"
            "3. Enable MFA for all employee accounts\n"
            "4. Implement credential monitoring service"
        ),
    }


def mock_threat_model(message: str) -> dict:
    return {
        "agent_name": "ThreatModelAgent",
        "agent_message": (
            "THREAT MODEL REPORT:\n\n"
            "SYSTEM OVERVIEW:\n"
            "- Target: Payment Processing API\n"
            "- Components: API Gateway, Auth Service, Payment Engine, Database\n"
            "- Trust Boundaries: External → DMZ → Internal → Database\n\n"
            "STRIDE ANALYSIS:\n"
            "| Category | Threat | Risk |\n"
            "| Spoofing | Stolen API keys used to impersonate merchants | HIGH |\n"
            "| Tampering | Man-in-the-middle on payment amount | HIGH |\n"
            "| Repudiation | Missing audit logs for refund operations | MEDIUM |\n"
            "| Info Disclosure | PCI data in application logs | CRITICAL |\n"
            "| Denial of Service | Rate limiting bypass via distributed requests | HIGH |\n"
            "| Elevation | Merchant role escalation to admin | MEDIUM |\n\n"
            "DREAD SCORING (Top Threat — PCI data in logs):\n"
            "- Damage: 9/10\n"
            "- Reproducibility: 8/10\n"
            "- Exploitability: 7/10\n"
            "- Affected Users: 9/10\n"
            "- Discoverability: 6/10\n"
            "- Total Score: 39/50 (CRITICAL)\n\n"
            "MITRE ATT&CK MAPPING:\n"
            "| Tactic | Technique | ID |\n"
            "| Initial Access | Valid Accounts | T1078 |\n"
            "| Collection | Data from Info Repositories | T1213 |\n"
            "| Exfiltration | Exfiltration Over Web Service | T1567 |\n\n"
            "TOP RECOMMENDATIONS:\n"
            "1. Implement PCI-compliant log scrubbing (remove card data from logs)\n"
            "2. Deploy mutual TLS for all internal service communication\n"
            "3. Implement request signing for payment amount integrity"
        ),
    }


def mock_vuln_scan(message: str) -> dict:
    return {
        "agent_name": "VulnScanAgent",
        "agent_message": (
            "VULNERABILITY ASSESSMENT REPORT:\n\n"
            "TARGET INFO:\n"
            "- Software: Node.js Application Stack\n"
            "- Last Scanned: March 2025\n\n"
            "CRITICAL VULNERABILITIES:\n\n"
            "CVE-2024-21626 (CRITICAL — CVSS 8.6):\n"
            "- Component: runc container runtime\n"
            "- Impact: Container escape via /sys/fs/cgroup manipulation\n"
            "- Exploit: Public PoC available\n"
            "- Fix: Upgrade runc to 1.1.12+\n\n"
            "CVE-2024-24549 (HIGH — CVSS 7.5):\n"
            "- Component: Apache Tomcat\n"
            "- Impact: DoS via HTTP/2 header handling\n"
            "- Exploit: Not yet public\n"
            "- Fix: Upgrade Tomcat to 10.1.19+\n\n"
            "CVE-2023-44487 (HIGH — CVSS 7.5):\n"
            "- Component: HTTP/2 implementations\n"
            "- Impact: Rapid Reset DDoS attack\n"
            "- Exploit: Actively exploited (CISA KEV)\n"
            "- Fix: Apply HTTP/2 rate limiting patches\n\n"
            "PATCH PRIORITY MATRIX:\n"
            "| Priority | CVE | Impact | Effort | Action |\n"
            "| 1 | CVE-2024-21626 | CRITICAL | Low | Patch immediately |\n"
            "| 2 | CVE-2023-44487 | HIGH | Medium | Patch within 48hrs |\n"
            "| 3 | CVE-2024-24549 | HIGH | Low | Patch within 1 week |\n\n"
            "SUMMARY:\n"
            "- Total CVEs: 12\n"
            "- Critical: 1\n"
            "- High: 4\n"
            "- Medium: 5\n"
            "- Low: 2"
        ),
    }


def mock_access_control(message: str) -> dict:
    return {
        "agent_name": "AccessControlAgent",
        "agent_message": (
            "ACCESS CONTROL REVIEW:\n\n"
            "[SIMULATED DATA]\n\n"
            "OVER-PRIVILEGED ACCOUNTS:\n\n"
            "1. john.smith@techcorp.com\n"
            "   - Department: Marketing\n"
            "   - Current: Admin access to production database\n"
            "   - Required: Read-only access to reporting views\n"
            "   - Excess: Database write, schema modify, user management\n"
            "   - Risk: CRITICAL\n"
            "   - Last activity: 2025-02-28\n\n"
            "2. legacy-deploy-bot\n"
            "   - Type: Service Account\n"
            "   - Current: Full root access to all environments\n"
            "   - Required: Deploy access to staging only\n"
            "   - Excess: Production access, database access\n"
            "   - Risk: HIGH\n\n"
            "ZOMBIE ACCOUNTS:\n"
            "| Account | Last Login | Status | Action |\n"
            "| mike.jones@techcorp.com | 2024-08-15 | Terminated | Disable immediately |\n"
            "| contractor-2024-q3 | 2024-11-30 | Contract ended | Remove access |\n"
            "| temp-admin-migration | 2024-06-01 | Unknown | Investigate |\n\n"
            "LEAST PRIVILEGE RECOMMENDATIONS:\n"
            "1. john.smith: Revoke admin → assign 'marketing-readonly' role\n"
            "2. legacy-deploy-bot: Restrict to staging, rotate credentials\n"
            "3. Disable all 3 zombie accounts within 24 hours\n\n"
            "COMPLIANCE STATUS:\n"
            "- SOX: PARTIAL (3 over-privileged accounts)\n"
            "- PCI-DSS Req 7: NON-COMPLIANT (excessive access)\n"
            "- ISO 27001 A.9: NEEDS IMPROVEMENT"
        ),
    }


def mock_forensics(message: str) -> dict:
    return {
        "agent_name": "ForensicsAgent",
        "agent_message": (
            "FORENSIC ANALYSIS REPORT:\n\n"
            "ATTACK CLASSIFICATION:\n"
            "- Type: Ransomware (LockBit 3.0 variant)\n"
            "- Confidence: 94%\n"
            "- Sophistication: High\n\n"
            "RECONSTRUCTED TIMELINE:\n"
            "| Time | Event | Severity | MITRE |\n"
            "| 02:14 UTC | Phishing email delivered to finance team | HIGH | T1566.001 |\n"
            "| 02:31 UTC | Malicious macro executed by user-47 | CRITICAL | T1059.005 |\n"
            "| 02:32 UTC | Cobalt Strike beacon established | CRITICAL | T1071.001 |\n"
            "| 02:45 UTC | Credential dumping via Mimikatz | CRITICAL | T1003.001 |\n"
            "| 03:12 UTC | Lateral movement to DC-01 via PsExec | HIGH | T1021.002 |\n"
            "| 03:28 UTC | Domain admin account compromised | CRITICAL | T1078.002 |\n"
            "| 04:15 UTC | Data exfiltration to external C2 (185.x.x.x) | CRITICAL | T1041 |\n"
            "| 05:00 UTC | Ransomware deployed across 47 servers | CRITICAL | T1486 |\n\n"
            "INDICATORS OF COMPROMISE:\n"
            "- C2 IPs: 185.220.101.42, 91.238.50.78\n"
            "- Domains: update-service[.]xyz, cdn-assets[.]cc\n"
            "- File Hash: SHA256:a1b2c3d4...e5f6 (Cobalt Strike loader)\n"
            "- Tools: Mimikatz, PsExec, Cobalt Strike 4.8\n\n"
            "ROOT CAUSE:\n"
            "Phishing email bypassed email gateway (zero-day office macro). "
            "User executed attachment without MFA enforcement on email. "
            "Lateral movement possible due to flat network architecture.\n\n"
            "RECOMMENDATIONS:\n"
            "1. Block all identified IOCs at perimeter\n"
            "2. Re-image all 47 affected servers\n"
            "3. Implement network segmentation\n"
            "4. Deploy advanced email filtering (sandbox-based)"
        ),
    }


def mock_security_arch(message: str) -> dict:
    return {
        "agent_name": "SecurityArchAgent",
        "agent_message": (
            "SECURITY ARCHITECTURE ASSESSMENT:\n\n"
            "[SIMULATED DATA]\n\n"
            "ZERO TRUST MATURITY:\n"
            "| Pillar | Current | Target | Gap | Priority |\n"
            "| Identity | Level 2/5 | Level 4/5 | 2 | HIGH |\n"
            "| Devices | Level 1/5 | Level 3/5 | 2 | HIGH |\n"
            "| Networks | Level 2/5 | Level 4/5 | 2 | CRITICAL |\n"
            "| Applications | Level 3/5 | Level 4/5 | 1 | MEDIUM |\n"
            "| Data | Level 2/5 | Level 4/5 | 2 | HIGH |\n\n"
            "Overall Score: 2.0 / 5.0\n"
            "Industry Benchmark: 3.2 / 5.0\n\n"
            "SECURITY POSTURE SCORE:\n"
            "| Category | Score | Weight | Weighted |\n"
            "| Prevention | 62/100 | 25% | 15.5 |\n"
            "| Detection | 45/100 | 25% | 11.25 |\n"
            "| Response | 58/100 | 25% | 14.5 |\n"
            "| Recovery | 40/100 | 25% | 10.0 |\n"
            "Overall: 51/100 (NEEDS IMPROVEMENT)\n\n"
            "NIST CSF ALIGNMENT:\n"
            "| Function | Maturity | Key Gaps |\n"
            "| Identify | Tier 2 | Incomplete asset inventory |\n"
            "| Protect | Tier 2 | Missing MFA, weak segmentation |\n"
            "| Detect | Tier 1 | No SIEM, limited logging |\n"
            "| Respond | Tier 2 | IR plan not tested |\n"
            "| Recover | Tier 1 | No BCP/DR testing |\n\n"
            "IMPROVEMENT ROADMAP:\n"
            "Phase 1 (0-3 months): Deploy MFA, SIEM, network segmentation\n"
            "Phase 2 (3-6 months): Zero Trust identity pilot, EDR rollout\n"
            "Phase 3 (6-12 months): Full Zero Trust architecture, automated response"
        ),
    }


def mock_executive_report(message: str) -> dict:
    return {
        "agent_name": "ExecutiveReportAgent",
        "agent_message": (
            "EXECUTIVE REPORT:\n"
            "Classification: CONFIDENTIAL\n\n"
            "EXECUTIVE SUMMARY:\n"
            "Q1 2025 saw a 15% increase in cybersecurity incidents with one Critical-severity "
            "ransomware event. Overall security posture improved by 8% due to MFA deployment. "
            "Vendor risk program now covers 94% of third parties. GDPR compliance is at 87%.\n\n"
            "KEY METRICS:\n"
            "| Metric | Current | Previous | Trend |\n"
            "| Total Incidents | 23 | 20 | ↑ 15% |\n"
            "| Critical Incidents | 1 | 0 | ↑ |\n"
            "| Avg Response Time | 4.2 hrs | 6.8 hrs | ↓ 38% |\n"
            "| GDPR Compliance | 87% | 82% | ↑ 5% |\n"
            "| Vendors Assessed | 156 | 142 | ↑ 10% |\n"
            "| DSR Completed | 47 | 38 | ↑ 24% |\n"
            "| Open Vulnerabilities | 34 | 52 | ↓ 35% |\n"
            "| Patch Compliance | 91% | 84% | ↑ 7% |\n\n"
            "NOTABLE INCIDENTS:\n"
            "1. TechCorp Ransomware (March 2025) — CRITICAL\n"
            "   Impact: 500K records, estimated cost: $2.1M\n"
            "   Status: Remediation in progress\n\n"
            "RISK SUMMARY:\n"
            "- Top Risk 1: Third-party supply chain exposure (MITIGATING)\n"
            "- Top Risk 2: Insider threat from over-privileged accounts (ACTIVE)\n"
            "- Top Risk 3: Unpatched legacy systems (IMPROVING)\n\n"
            "RECOMMENDATIONS FOR BOARD:\n"
            "1. Approve $350K budget for Zero Trust network architecture\n"
            "2. Mandate MFA for all remaining systems (12% gap)\n"
            "3. Approve vendor consolidation initiative to reduce attack surface"
        ),
    }
