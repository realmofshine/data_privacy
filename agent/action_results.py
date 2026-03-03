"""A2UI action result builders — rendered after a button click.

These produce A2UI cards that show the result of executing an action
(e.g., Export Report, Send Notifications, Execute Playbook).
"""
from __future__ import annotations
from agent.views import _wrap, _text, _column, _card, _divider, _row, _button


# ─── Action result registry ─────────────────────────────────────────

ACTION_RESULTS: dict[str, dict] = {}


def _success_card(title: str, icon: str, details: list[str],
                  follow_ups: list[tuple[str, str, str]] | None = None) -> dict:
    """Build a styled success result card."""
    child_ids = ["title"]
    components = [_text("title", f"{icon}  {title}", "h2")]

    for i, line in enumerate(details):
        tid = f"detail-{i}"
        components.append(_text(tid, line, "body"))
        child_ids.append(tid)

    if follow_ups:
        components.append(_divider("div-actions"))
        child_ids.append("div-actions")
        btn_ids = []
        for suffix, label, action in follow_ups:
            bid = f"btn-{suffix}"
            components.append(_button(bid, label, action))
            components.append(_text(f"{bid}-label", label))
            btn_ids.append(bid)
        components.append(_row("follow-up-row", btn_ids))
        child_ids.append("follow-up-row")

    components.insert(0, _card("card", "col"))
    components.insert(0, _column("root", ["card"]))
    components.insert(2, _column("col", child_ids))
    return _wrap(components)


# ═══════════════════════════════════════════════════════════════════════
# ACTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════

def action_export_compliance() -> dict:
    return _success_card(
        "Compliance Report Exported", "📄",
        [
            "✅ PDF report generated successfully",
            "📎 File: compliance_assessment_2025-03-04.pdf (2.4 MB)",
            "📊 Contains: 4 regulations, 6 notification requirements, risk analysis",
            "📧 Sent to: legal@techcorp.com, dpo@techcorp.com",
            "🕐 Generated at: 2025-03-04 01:15:00 UTC",
        ],
        follow_ups=[("share", "Share with Board", "share_board")],
    )


def action_trigger_notifications() -> dict:
    return _success_card(
        "Notifications Triggered", "📨",
        [
            "✅ Notification queue created",
            "",
            "📋 Notification Status:",
            "  • Supervisory Authority (GDPR Art.33) — QUEUED (due in 71 hours)",
            "  • Affected Individuals (GDPR Art.34) — DRAFT PREPARED",
            "  • Card Brands (PCI-DSS) — SENT ✅",
            "  • State AG (CCPA) — DRAFT PREPARED",
            "  • Board of Directors — SENT ✅",
            "  • Cyber Insurance — SENT ✅",
            "",
            "📝 3 notifications sent, 3 pending approval",
        ],
        follow_ups=[
            ("approve-all", "Approve Pending", "approve_pending_notifications"),
            ("preview", "Preview Drafts", "preview_notification_drafts"),
        ],
    )


def action_execute_ir() -> dict:
    return _success_card(
        "IR Playbook Execution Started", "🚨",
        [
            "✅ Incident Response Playbook activated",
            "",
            "⏳ PHASE 1 — CONTAIN (In Progress):",
            "  ☑ Affected servers isolated from network",
            "  ☑ Compromised accounts disabled",
            "  ☐ C2 IP addresses blocked at firewall",
            "  ☐ Memory dumps captured",
            "",
            "👤 Assigned to: SOC Team Lead (@john.smith)",
            "🔔 War room created: #incident-2025-0342",
            "📞 Next escalation: CISO in 45 minutes",
            "",
            "🕐 Elapsed: 12 minutes | ETA Phase 1 complete: 48 minutes",
        ],
        follow_ups=[
            ("status", "View Live Status", "view_ir_status"),
            ("escalate-now", "Escalate Now", "escalate_ir"),
        ],
    )


def action_escalate_ir() -> dict:
    return _success_card(
        "Incident Escalated", "⬆️",
        [
            "✅ Escalation completed",
            "",
            "📞 Notified:",
            "  • CISO (Sarah Johnson) — ACKNOWLEDGED",
            "  • VP Engineering (Mike Chen) — NOTIFIED",
            "  • Legal Counsel (Amanda Brooks) — NOTIFIED",
            "  • CEO (via CISO) — BRIEFED",
            "",
            "📋 Emergency board meeting scheduled: Today 2:00 PM UTC",
            "📝 Executive brief document generated",
        ],
    )


def action_export_ropa() -> dict:
    return _success_card(
        "ROPA Export Complete", "📋",
        [
            "✅ Records of Processing Activities exported",
            "",
            "📎 Files generated:",
            "  • ROPA_TechCorp_2025-Q1.xlsx (148 KB)",
            "  • Data_Flow_Diagram.pdf (890 KB)",
            "  • DPIA_Required_Activities.csv (12 KB)",
            "",
            "📊 Summary:",
            "  • 5 processing activities documented",
            "  • 6 data categories classified",
            "  • 3 cross-border transfers identified",
            "  • 3 gaps requiring remediation",
            "",
            "🕐 GDPR Art.30 compliance: PARTIAL (3 gaps remaining)",
        ],
    )


def action_approve_dsr() -> dict:
    return _success_card(
        "DSR Request Approved & Executing", "✅",
        [
            "✅ Data Subject Request APPROVED",
            "",
            "⏳ Execution Progress:",
            "  ☑ CRM (Salesforce) — 12 records DELETED",
            "  ☑ Email (SendGrid) — 847 emails PURGED",
            "  ⏳ Support (Zendesk) — Deleting 5 tickets...",
            "  ⏳ Analytics (Mixpanel) — Anonymizing events...",
            "  ⏱ Backups (AWS S3) — Flagged for rotation (90 days)",
            "  🔒 Payment (Stripe) — RETAINED (tax compliance)",
            "",
            "📧 Response letter draft sent to DPO for review",
            "📋 Audit log updated with execution timestamps",
            "",
            "🕐 Estimated completion: 15 minutes",
        ],
    )


def action_reject_dsr() -> dict:
    return _success_card(
        "DSR Request Rejected", "❌",
        [
            "DSR request has been rejected.",
            "",
            "📝 Reason must be provided to the data subject.",
            "📋 Valid reasons under GDPR:",
            "  • Identity verification failed",
            "  • Manifestly unfounded or excessive request",
            "  • Legal obligation to retain data",
            "  • Freedom of expression exception",
            "",
            "📧 Rejection letter template prepared",
            "⚠️ Data subject has the right to appeal to the supervisory authority",
        ],
    )


def action_force_password_reset() -> dict:
    return _success_card(
        "Password Reset Initiated", "🔑",
        [
            "✅ Forced password reset triggered",
            "",
            "👤 Affected accounts: 12",
            "📧 Reset emails sent to all compromised accounts",
            "",
            "Status:",
            "  ☑ john.doe@techcorp.com — Reset email sent",
            "  ☑ jane.smith@techcorp.com — Reset email sent",
            "  ☑ admin@techcorp.com — Reset email sent",
            "  ☑ dev.ops@techcorp.com — Reset email sent",
            "  ... and 8 more",
            "",
            "🔐 MFA enrollment required on next login",
            "📋 Password policy: Minimum 16 chars, no reuse of last 12",
        ],
    )


def action_rescan_darkweb() -> dict:
    return _success_card(
        "Dark Web Re-scan Initiated", "🔄",
        [
            "⏳ New scan in progress...",
            "",
            "🌐 Sources being checked:",
            "  • BreachForums (successor) — Scanning...",
            "  • Exploit.in — Scanning...",
            "  • Telegram channels (47) — Scanning...",
            "  • Paste sites (12) — Scanning...",
            "  • Database dump archives — Scanning...",
            "",
            "🕐 Estimated completion: 3-5 minutes",
            "📧 Results will be emailed to security@techcorp.com",
        ],
    )


def action_export_pdf() -> dict:
    return _success_card(
        "Executive Report PDF Generated", "📝",
        [
            "✅ Board report exported successfully",
            "",
            "📎 File: Executive_Security_Report_Q1_2025.pdf (3.8 MB)",
            "",
            "📊 Report contains:",
            "  • Executive Summary (1 page)",
            "  • Key Metrics Dashboard (2 pages)",
            "  • Incident Summary (1 page)",
            "  • Risk Heatmap (1 page)",
            "  • Compliance Scorecard (1 page)",
            "  • Vendor Risk Matrix (1 page)",
            "  • Board Recommendations (1 page)",
            "",
            "📧 Ready for board distribution",
            "🔒 Classification: CONFIDENTIAL",
        ],
        follow_ups=[("email-board", "Email to Board", "email_board_report")],
    )


def action_generate_patch_plan() -> dict:
    return _success_card(
        "Patch Plan Generated", "🩹",
        [
            "✅ Patch deployment plan created",
            "",
            "📋 Priority Order:",
            "  1. CVE-2024-21626 (runc) — Deploy tonight, maintenance window 02:00-04:00 UTC",
            "     Rollback plan: Revert to runc 1.1.11",
            "",
            "  2. CVE-2023-44487 (HTTP/2) — Deploy tomorrow",
            "     Config change: Enable SETTINGS_MAX_CONCURRENT_STREAMS=100",
            "",
            "  3. CVE-2024-24549 (Tomcat) — Schedule for Friday",
            "     Upgrade path: 10.1.18 → 10.1.19",
            "",
            "📧 Change request tickets created in Jira:",
            "  • PATCH-2025-001 (CRITICAL)",
            "  • PATCH-2025-002 (HIGH)",
            "  • PATCH-2025-003 (HIGH)",
        ],
    )


def action_revoke_excess_permissions() -> dict:
    return _success_card(
        "Excess Permissions Revoked", "🔐",
        [
            "✅ Privilege revocation complete",
            "",
            "Changes applied:",
            "  ☑ john.smith@techcorp.com",
            "    Admin → marketing-readonly",
            "    Revoked: DB write, schema modify, user management",
            "",
            "  ☑ legacy-deploy-bot",
            "    Root (all envs) → staging-deploy-only",
            "    Revoked: Production access, database access",
            "",
            "📋 Audit trail updated",
            "📧 Notification sent to account holders",
            "🔒 Next review scheduled: April 4, 2025",
        ],
    )


def action_disable_zombie_accounts() -> dict:
    return _success_card(
        "Zombie Accounts Disabled", "👻",
        [
            "✅ 3 zombie accounts disabled",
            "",
            "  ☑ mike.jones@techcorp.com — DISABLED",
            "    Last login: 2024-08-15 | Status: Terminated employee",
            "    Access removed from: 7 systems",
            "",
            "  ☑ contractor-2024-q3 — DISABLED",
            "    Last login: 2024-11-30 | Status: Contract ended",
            "    Access removed from: 3 systems",
            "",
            "  ☑ temp-admin-migration — DISABLED",
            "    Last login: 2024-06-01 | Status: Temporary (expired)",
            "    Access removed from: 12 systems (!)",
            "",
            "⚠️ temp-admin-migration had admin access to 12 systems for 9 months after expiry",
            "📋 Flagged for security review",
        ],
    )


def action_export_iocs() -> dict:
    return _success_card(
        "IOCs Exported", "🔬",
        [
            "✅ Indicators of Compromise exported",
            "",
            "📎 Files generated:",
            "  • IOCs_STIX2.1.json (45 KB) — STIX format",
            "  • IOCs_CSV.csv (12 KB) — Spreadsheet format",
            "  • IOCs_MISP.json (38 KB) — MISP event format",
            "",
            "📊 IOC Summary:",
            "  • 2 C2 IP addresses",
            "  • 2 malicious domains",
            "  • 1 file hash (SHA256)",
            "  • 4 attacker tools identified",
            "  • 3 compromised accounts",
            "",
            "🔄 Auto-shared with:",
            "  • SIEM (Splunk) — Imported as correlation rules",
            "  • Firewall (Palo Alto) — Added to block list",
            "  • EDR (CrowdStrike) — Added to IOC watchlist",
        ],
    )


def action_share_board() -> dict:
    return _success_card("Shared with Board", "✅", [
        "✅ Report shared with board members",
        "📧 Sent to 5 board members via encrypted email",
    ])


def action_approve_pending() -> dict:
    return _success_card("Notifications Approved", "✅", [
        "✅ All pending notifications approved and sent",
        "  • Supervisory Authority — SENT",
        "  • Affected Individuals — SENDING (batch of 500K)",
        "  • State AG — SENT",
    ])


def action_preview_drafts() -> dict:
    return _success_card("Draft Preview", "📝", [
        "📝 GDPR Art.33 Notification Draft:",
        "",
        "To: [Supervisory Authority]",
        "Re: Personal Data Breach Notification",
        "",
        "We are writing to notify you of a personal data breach as required under "
        "Article 33 of the General Data Protection Regulation...",
        "",
        "Nature of breach: Ransomware attack resulting in unauthorized access to "
        "personal data of approximately 500,000 data subjects...",
    ])


def action_view_ir_status() -> dict:
    return _success_card("IR Live Status", "📊", [
        "🟢 PHASE 1 — CONTAIN: 75% complete",
        "  ☑ Servers isolated",
        "  ☑ Accounts disabled",
        "  ☑ C2 IPs blocked",
        "  ☐ Memory dumps (in progress)",
        "",
        "⏱ Elapsed: 28 minutes",
        "👤 Active responders: 6",
        "📞 Next check-in: 15 minutes",
    ])


def action_email_board() -> dict:
    return _success_card("Report Emailed", "📧", [
        "✅ Executive Report emailed to board",
        "📧 Recipients: 5 board members",
        "🔒 Encrypted with AES-256",
        "📝 Read receipts enabled",
    ])


# ─── Registry ───────────────────────────────────────────────────────

ACTION_RESULTS = {
    "export_compliance": action_export_compliance,
    "trigger_notifications": action_trigger_notifications,
    "execute_ir": action_execute_ir,
    "escalate_ir": action_escalate_ir,
    "export_ropa": action_export_ropa,
    "approve_dsr": action_approve_dsr,
    "reject_dsr": action_reject_dsr,
    "force_password_reset": action_force_password_reset,
    "rescan_darkweb": action_rescan_darkweb,
    "export_pdf": action_export_pdf,
    "generate_patch_plan": action_generate_patch_plan,
    "revoke_excess_permissions": action_revoke_excess_permissions,
    "disable_zombie_accounts": action_disable_zombie_accounts,
    "export_iocs": action_export_iocs,
    "view_risk_detail": lambda: _success_card("Risk Details", "📊", [
        "📊 Detailed risk breakdown loaded",
        "See the Risk Assessment card above for full details.",
    ]),
    # Follow-up actions
    "share_board": action_share_board,
    "approve_pending_notifications": action_approve_pending,
    "preview_notification_drafts": action_preview_drafts,
    "view_ir_status": action_view_ir_status,
    "email_board_report": action_email_board,
}


def get_action_result(action_name: str) -> dict | None:
    """Return the A2UI card for a button action, or None if not found."""
    handler = ACTION_RESULTS.get(action_name)
    if handler:
        return handler()
    return None
