"""A2UI card builders for the Data Privacy application.

All functions return a valid A2UI JSON dict that the frontend can render.
Covers all 15 modes with mode-specific card layouts.
"""
from __future__ import annotations
import re


# ─── Primitive builders ─────────────────────────────────────────────

def _text(id: str, text: str, hint: str = "body") -> dict:
    return {
        "id": id,
        "component": {
            "Text": {
                "text": {"literalString": text},
                "usageHint": hint,
            }
        },
    }


def _column(id: str, children: list[str]) -> dict:
    return {
        "id": id,
        "component": {
            "Column": {"children": {"explicitList": children}}
        },
    }


def _row(id: str, children: list[str]) -> dict:
    return {
        "id": id,
        "component": {
            "Row": {"children": {"explicitList": children}}
        },
    }


def _card(id: str, child: str) -> dict:
    return {
        "id": id,
        "component": {"Card": {"child": child}},
    }


def _divider(id: str) -> dict:
    return {
        "id": id,
        "component": {"Divider": {"axis": "horizontal"}},
    }


def _button(id: str, label: str, action_name: str, context: dict | None = None) -> dict:
    context_list = []
    if context:
        for k, v in context.items():
            context_list.append({"key": k, "value": {"literalString": str(v)}})
    return {
        "id": id,
        "component": {
            "Button": {
                "child": f"{id}-label",
                "action": {
                    "name": action_name,
                    "context": context_list,
                },
            }
        },
    }


def _wrap(components: list[dict]) -> dict:
    return {
        "beginRendering": {"surfaceId": "main", "root": "root"},
        "surfaceUpdate": {
            "surfaceId": "main",
            "components": components,
        },
    }


# ─── Generic Section Parser ─────────────────────────────────────────

def _parse_sections(text: str, known_headers: list[str] | None = None) -> list[tuple[str, str]]:
    """Parse agent response into (section_name, section_body) pairs.

    Detects headers like "SECTION NAME:" or "## SECTION NAME" or numbered "1. SECTION".
    If known_headers is provided, only those headers are used.
    """
    lines = text.strip().splitlines()
    sections: list[tuple[str, str]] = []
    current_header = ""
    current_buf: list[str] = []

    # Build regex for known headers if provided
    known_upper = set()
    if known_headers:
        known_upper = {h.upper().rstrip(":") for h in known_headers}

    for line in lines:
        stripped = line.strip()
        upper = stripped.upper().rstrip(":")

        # Check for markdown-style headers
        is_md_header = stripped.startswith("#")
        # Check for UPPER CASE headers ending with ":"
        is_upper_header = (
            stripped.endswith(":") and
            len(stripped) > 3 and
            stripped[:-1].replace(" ", "").replace("-", "").replace("_", "").replace("(", "").replace(")", "").isalpha() and
            stripped[:-1] == stripped[:-1].upper()
        )
        # Check for numbered headers like "1. SECTION NAME:"
        is_numbered = bool(re.match(r'^\d+\.\s+[A-Z]', stripped))

        # Remove markdown # prefix
        clean_header = stripped.lstrip("#").strip().rstrip(":")
        clean_upper = clean_header.upper()

        if known_headers:
            is_known = clean_upper in known_upper or upper in known_upper
            if is_known:
                if current_header:
                    sections.append((current_header, "\n".join(current_buf)))
                current_header = clean_header
                current_buf = []
                continue
        elif is_md_header or is_upper_header or is_numbered:
            if current_header:
                sections.append((current_header, "\n".join(current_buf)))
            current_header = clean_header
            current_buf = []
            continue

        current_buf.append(line)

    if current_header:
        sections.append((current_header, "\n".join(current_buf)))

    return sections


def _build_sectioned_card(title: str, icon: str, sections: list[tuple[str, str]],
                          buttons: list[tuple[str, str, str]] | None = None) -> dict:
    """Build a Card with a title and multiple text sections.

    buttons: list of (id_suffix, label, action_name) tuples.
    """
    child_ids = [f"title-{icon}"]
    components = [_text(f"title-{icon}", f"{icon}  {title}", "h2")]

    for i, (header, body) in enumerate(sections):
        if not body.strip():
            continue
        div_id = f"div-s{i}"
        hdr_id = f"hdr-s{i}"
        body_id = f"body-s{i}"
        sec_id = f"sec-s{i}"

        components.append(_divider(div_id))
        components.append(_text(hdr_id, header, "h3"))
        # Truncate very long bodies
        body_text = body.strip()[:1500]
        components.append(_text(body_id, body_text, "body"))
        components.append(_column(sec_id, [hdr_id, body_id]))
        child_ids.extend([div_id, sec_id])

    # Buttons
    if buttons:
        btn_ids = []
        for suffix, label, action in buttons:
            btn_id = f"btn-{suffix}"
            components.append(_button(btn_id, label, action))
            components.append(_text(f"{btn_id}-label", label))
            btn_ids.append(btn_id)
        components.append(_row("btn-row", btn_ids))
        components.append(_divider("div-btns"))
        child_ids.extend(["div-btns", "btn-row"])

    components.insert(0, _card("card", "col"))
    components.insert(0, _column("root", ["card"]))
    components.insert(2, _column("col", child_ids))

    return _wrap(components)


# ═══════════════════════════════════════════════════════════════════════
# MODE-SPECIFIC CARD RENDERERS
# ═══════════════════════════════════════════════════════════════════════

# ─── Mode 1: Breach Analysis ────────────────────────────────────────

def render_fake_news_warning(reason: str, sources: list[str] | None = None) -> dict:
    """Render a warning card with Proceed Anyway / Discard buttons."""
    components = [
        _column("root", ["card"]),
        _card("card", "col"),
        _column("col", ["title", "divider1", "reason-text"] +
                (["sources-label", "source-list"] if sources else []) +
                ["divider2", "actions"]),
        _text("title", "⚠️  Potential Fake News Detected", "h2"),
        _divider("divider1"),
        _text("reason-text", reason[:500], "body"),
    ]

    if sources:
        components.append(_text("sources-label", "🔗  Sources Checked:", "caption"))
        source_ids = []
        for i, url in enumerate(sources[:5]):
            sid = f"src-{i}"
            components.append(_text(sid, url, "body"))
            source_ids.append(sid)
        components.append(_column("source-list", source_ids))

    components += [
        _divider("divider2"),
        _row("actions", ["btn-proceed", "btn-discard"]),
        _button("btn-proceed", "Proceed Anyway", "force_proceed"),
        _text("btn-proceed-label", "Proceed Anyway"),
        _button("btn-discard", "Discard Article", "cancel_workflow"),
        _text("btn-discard-label", "Discard Article"),
    ]

    return _wrap(components)


def render_full_report(agent_response: str) -> dict:
    """Render breach analysis full report as sectioned card."""
    sections = _parse_sections(agent_response, [
        "EXECUTIVE SUMMARY", "INCIDENT PROFILE", "RED ALERTS",
        "YELLOW ALERTS", "SUGGESTIONS",
    ])
    if not sections:
        return render_generic_report("📊 Breach Analysis Report", agent_response)
    return _build_sectioned_card("Breach Analysis Report", "🔍", sections)


# ─── Mode 3: Compliance ─────────────────────────────────────────────

def render_compliance_card(agent_response: str) -> dict:
    """Render compliance assessment as structured card."""
    sections = _parse_sections(agent_response, [
        "COMPLIANCE ASSESSMENT", "APPLICABLE REGULATIONS",
        "NOTIFICATION REQUIREMENTS", "DOCUMENTATION REQUIREMENTS",
        "RISK OF NON-COMPLIANCE", "RECOMMENDED ACTIONS",
    ])
    if not sections:
        return render_generic_report("⚖️ Compliance Assessment", agent_response)
    return _build_sectioned_card(
        "Compliance Assessment", "⚖️", sections,
        buttons=[
            ("export", "Export Report", "export_compliance"),
            ("notify", "Send Notifications", "trigger_notifications"),
        ],
    )


# ─── Mode 4: Risk Assessment ────────────────────────────────────────

def render_risk_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("📊 Risk Assessment", agent_response)
    return _build_sectioned_card(
        "Risk Assessment", "📊", sections,
        buttons=[("detail", "View Details", "view_risk_detail")],
    )


# ─── Mode 5: Safety Check ───────────────────────────────────────────

def render_safety_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🛡️ Safety Validation", agent_response)
    return _build_sectioned_card("Safety Validation", "🛡️", sections)


# ─── Mode 6: Incident Response ──────────────────────────────────────

def render_ir_card(agent_response: str) -> dict:
    """Render IR playbook as actionable card."""
    sections = _parse_sections(agent_response, [
        "INCIDENT RESPONSE PLAYBOOK", "INCIDENT CLASSIFICATION",
        "PHASE 1", "PHASE 2", "PHASE 3", "PHASE 4", "PHASE 5", "PHASE 6",
        "MITRE ATT&CK MAPPING",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🚨 Incident Response Playbook", agent_response)
    return _build_sectioned_card(
        "Incident Response Playbook", "🚨", sections,
        buttons=[
            ("execute", "Execute Playbook", "execute_ir"),
            ("escalate", "Escalate", "escalate_ir"),
        ],
    )


# ─── Mode 7: Data Mapping ───────────────────────────────────────────

def render_data_mapping_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "DATA FLOW MAP", "PROCESSING ACTIVITIES", "DATA CLASSIFICATION",
        "DATA FLOW DIAGRAM", "CROSS-BORDER TRANSFERS", "DATA LINEAGE",
        "GAPS IDENTIFIED", "RECOMMENDATIONS",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🗺️ Data Flow Map", agent_response)
    return _build_sectioned_card(
        "Data Flow Map", "🗺️", sections,
        buttons=[("export", "Export ROPA", "export_ropa")],
    )


# ─── Mode 8: DSR ────────────────────────────────────────────────────

def render_dsr_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "DSR PROCESSING REPORT", "REQUEST CLASSIFICATION",
        "IDENTITY VERIFICATION", "SYSTEMS INVENTORY", "LEGAL EXCEPTIONS",
        "EXECUTION PLAN", "RESPONSE LETTER", "AUDIT LOG",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("👤 DSR Processing", agent_response)
    return _build_sectioned_card(
        "Data Subject Request", "👤", sections,
        buttons=[
            ("approve", "Approve & Execute", "approve_dsr"),
            ("reject", "Reject Request", "reject_dsr"),
        ],
    )


# ─── Mode 9: Dark Web ───────────────────────────────────────────────

def render_dark_web_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "DARK WEB SCAN REPORT", "SCAN SUMMARY", "CRITICAL FINDINGS",
        "BRAND MENTIONS", "CREDENTIAL ANALYSIS", "RECOMMENDATIONS",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🌐 Dark Web Scan", agent_response)
    return _build_sectioned_card(
        "Dark Web Scan Report", "🌐", sections,
        buttons=[
            ("reset", "Force Password Reset", "force_password_reset"),
            ("scan", "Re-scan", "rescan_darkweb"),
        ],
    )


# ─── Mode 10: Reports ───────────────────────────────────────────────

def render_executive_report_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "EXECUTIVE REPORT", "EXECUTIVE SUMMARY", "KEY METRICS",
        "NOTABLE INCIDENTS", "RISK SUMMARY", "COMPLIANCE STATUS",
        "VENDOR RISK OVERVIEW", "RECOMMENDATIONS FOR BOARD",
        "NEXT QUARTER PRIORITIES",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("📝 Executive Report", agent_response)
    return _build_sectioned_card(
        "Executive Report", "📝", sections,
        buttons=[("pdf", "Export PDF", "export_pdf")],
    )


# ─── Mode 11: Threat Modeling ────────────────────────────────────────

def render_threat_model_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "THREAT MODEL REPORT", "SYSTEM OVERVIEW", "STRIDE ANALYSIS",
        "DREAD SCORING", "MITRE ATT&CK MAPPING", "ATTACK TREE",
        "TOP RECOMMENDATIONS",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🎯 Threat Model", agent_response)
    return _build_sectioned_card("Threat Model Report", "🎯", sections)


# ─── Mode 12: Vulnerability ─────────────────────────────────────────

def render_vuln_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "VULNERABILITY ASSESSMENT REPORT", "TARGET INFO",
        "CRITICAL VULNERABILITIES", "CVSS BREAKDOWN",
        "PATCH PRIORITY MATRIX", "SUMMARY",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🔓 Vulnerability Assessment", agent_response)
    return _build_sectioned_card(
        "Vulnerability Assessment", "🔓", sections,
        buttons=[("patch", "Generate Patch Plan", "generate_patch_plan")],
    )


# ─── Mode 13: Access Control ────────────────────────────────────────

def render_access_control_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "ACCESS CONTROL REVIEW", "OVER-PRIVILEGED ACCOUNTS",
        "ZOMBIE ACCOUNTS", "SERVICE ACCOUNTS", "ROLE-BASED ACCESS MATRIX",
        "ANOMALOUS BEHAVIOR", "LEAST PRIVILEGE RECOMMENDATIONS",
        "COMPLIANCE STATUS",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🔐 Access Control Review", agent_response)
    return _build_sectioned_card(
        "Access Control Review", "🔐", sections,
        buttons=[
            ("revoke", "Revoke Excess", "revoke_excess_permissions"),
            ("disable", "Disable Zombies", "disable_zombie_accounts"),
        ],
    )


# ─── Mode 14: Forensics ─────────────────────────────────────────────

def render_forensics_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "FORENSIC ANALYSIS REPORT", "ATTACK CLASSIFICATION",
        "RECONSTRUCTED TIMELINE", "INDICATORS OF COMPROMISE",
        "ATTACK CHAIN ANALYSIS", "EVIDENCE PRESERVATION",
        "ROOT CAUSE", "RECOMMENDATIONS",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🔬 Forensic Analysis", agent_response)
    return _build_sectioned_card(
        "Forensic Analysis Report", "🔬", sections,
        buttons=[("export", "Export IOCs", "export_iocs")],
    )


# ─── Mode 15: Security Architecture ─────────────────────────────────

def render_security_arch_card(agent_response: str) -> dict:
    sections = _parse_sections(agent_response, [
        "SECURITY ARCHITECTURE ASSESSMENT", "ZERO TRUST MATURITY",
        "SECURITY POSTURE SCORE", "NIST CSF ALIGNMENT",
        "BUSINESS CONTINUITY", "GAP ANALYSIS", "IMPROVEMENT ROADMAP",
    ])
    if not sections:
        sections = _parse_sections(agent_response)
    if not sections:
        return render_generic_report("🏗️ Security Architecture", agent_response)
    return _build_sectioned_card("Security Architecture Assessment", "🏗️", sections)


# ═══════════════════════════════════════════════════════════════════════
# GENERIC CARDS
# ═══════════════════════════════════════════════════════════════════════

def render_generic_report(title: str, agent_response: str) -> dict:
    """Fallback: render any response as a simple card with the text."""
    return _wrap([
        _column("root", ["card"]),
        _card("card", "col"),
        _column("col", ["title", "divider", "body"]),
        _text("title", title, "h2"),
        _divider("divider"),
        _text("body", agent_response[:2000], "body"),
    ])


def render_success(message: str) -> dict:
    return _wrap([
        _column("root", ["msg"]),
        _text("msg", f"✅  {message}", "h3"),
    ])


def render_cancel(message: str) -> dict:
    return _wrap([
        _column("root", ["msg"]),
        _text("msg", f"🗑️  {message}", "h3"),
    ])


def render_error(message: str) -> dict:
    return _wrap([
        _column("root", ["err"]),
        _text("err", f"❌  {message}", "h3"),
    ])


# ═══════════════════════════════════════════════════════════════════════
# MODE → CARD ROUTER (used by agui_endpoint.py)
# ═══════════════════════════════════════════════════════════════════════

MODE_CARD_RENDERERS = {
    "breach_analysis": None,  # Uses special logic (fake news / full report)
    "knowledge_search": None,  # Uses generic
    "compliance": render_compliance_card,
    "risk_assessment": render_risk_card,
    "safety": render_safety_card,
    "incident_response": render_ir_card,
    "data_mapping": render_data_mapping_card,
    "dsr": render_dsr_card,
    "dark_web": render_dark_web_card,
    "reports": render_executive_report_card,
    "threat_modeling": render_threat_model_card,
    "vulnerability": render_vuln_card,
    "access_control": render_access_control_card,
    "forensics": render_forensics_card,
    "security_arch": render_security_arch_card,
}


def render_for_mode(mode: str, agent_response: str, user_message: str = "") -> dict:
    """Main entry: pick the right A2UI card based on mode + response content."""
    if not agent_response:
        return render_success("Processing complete.")

    # Breach analysis has special logic
    if mode == "breach_analysis":
        return _determine_breach_a2ui(agent_response, user_message)

    renderer = MODE_CARD_RENDERERS.get(mode)
    if renderer:
        return renderer(agent_response)

    # Fallback: try to parse sections generically
    sections = _parse_sections(agent_response)
    if sections:
        return _build_sectioned_card("Analysis Complete", "📋", sections)

    return render_success(agent_response[:300])


def _determine_breach_a2ui(agent_message: str, user_message: str) -> dict:
    """Special breach analysis logic: fake news warning vs. full report."""
    lm = agent_message.lower()

    if "fake_news_detected" in lm or ("fake" in lm and "detected" in lm):
        sources = []
        if "sources:" in lm:
            sources_part = agent_message[agent_message.lower().find("sources:") + 8:]
            sources = re.findall(r'https?://[^\s,\]>]+', sources_part)[:5]
        reason = agent_message[:400]
        return render_fake_news_warning(reason, sources)

    if "cancel" in lm or "discard" in lm:
        return render_cancel("Workflow cancelled.")

    if any(section in agent_message.upper() for section in [
        "EXECUTIVE SUMMARY", "INCIDENT PROFILE", "RED ALERTS",
        "YELLOW ALERTS", "SUGGESTIONS",
    ]):
        return render_full_report(agent_message)

    return render_success(agent_message[:200])
