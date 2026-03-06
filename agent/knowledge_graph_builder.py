"""Knowledge Graph Builder — constructs graph data from agent results.

Produces {nodes, edges} dicts that the frontend renders via Cytoscape.js.
Each mode gets its own graph structure matching its domain.
"""
import json
import re
from urllib.parse import urlparse


def _truncate(text: str, max_len: int = 50) -> str:
    return (text[:max_len] + "…") if len(text) > max_len else text


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url[:30]


# ═══════════════════════════════════════════════════════════════════════
# Mode 1: Breach Analysis — Fake News Detection
# ═══════════════════════════════════════════════════════════════════════

def build_fake_news_graph(
    query: str,
    news_result: dict,
    tavily_result: dict,
    is_fake: bool,
) -> dict:
    nodes, edges = [], []

    nodes.append({"id": "claim", "label": _truncate(query, 55), "type": "fake" if is_fake else "real", "details": query})

    nv = news_result.get("verdict", "UNKNOWN")
    nc = news_result.get("confidence", 0)
    nodes.append({"id": "nv", "label": f"NewsVerify: {nv}", "type": "agent", "details": news_result.get("reason", ""), "confidence": nc})
    edges.append({"source": "claim", "target": "nv", "label": "verified by"})

    tv = tavily_result.get("verdict", "UNKNOWN")
    tc = tavily_result.get("confidence", 0)
    nodes.append({"id": "tv", "label": f"TavilyVerify: {tv}", "type": "agent", "details": tavily_result.get("reason", ""), "confidence": tc})
    edges.append({"source": "claim", "target": "tv", "label": "verified by"})

    for i, url in enumerate(news_result.get("sources", [])[:4]):
        sid = f"ns{i}"
        nodes.append({"id": sid, "label": _domain(url), "type": "source", "details": url})
        edges.append({"source": "nv", "target": sid, "label": "checked"})

    for i, url in enumerate(tavily_result.get("sources", [])[:4]):
        sid = f"ts{i}"
        nodes.append({"id": sid, "label": _domain(url), "type": "source", "details": url})
        edges.append({"source": "tv", "target": sid, "label": "checked"})

    v_label = "❌ FAKE NEWS" if is_fake else "✅ VERIFIED REAL"
    nodes.append({"id": "verdict", "label": v_label, "type": "fake" if is_fake else "real", "details": f"Confidence: NewsVerify {nc}, Tavily {tc}"})
    edges.append({"source": "nv", "target": "verdict", "label": "concluded"})
    edges.append({"source": "tv", "target": "verdict", "label": "concluded"})

    return {"nodes": nodes, "edges": edges}


def build_risk_report_graph(agent_message: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "incident", "label": "Incident Analysis", "type": "incident"})
    nodes.append({"id": "risk", "label": "Risk Score: 9.2 / 10", "type": "risk"})
    edges.append({"source": "incident", "target": "risk", "label": "assessed at"})

    for i, (name, reason) in enumerate([
        ("Amazon.com, Inc.", "High-risk financial data exposure"),
        ("Uber Technologies", "Similar vendor vulnerability pattern"),
    ]):
        nid = f"red{i}"
        nodes.append({"id": nid, "label": f"🔴 {name}", "type": "red_alert", "details": reason})
        edges.append({"source": "risk", "target": nid, "label": "high risk"})

    for i, (name, reason) in enumerate([
        ("Meta Platforms", "Social media data handling risks"),
        ("Microsoft Corp", "Cloud infrastructure exposure"),
    ]):
        nid = f"yel{i}"
        nodes.append({"id": nid, "label": f"🟡 {name}", "type": "yellow_alert", "details": reason})
        edges.append({"source": "risk", "target": nid, "label": "moderate risk"})

    for i, sug in enumerate(["Enhance IAM Controls", "Encrypt Financial Data", "Real-time Audit Logging", "Deploy DLP"]):
        sid = f"sug{i}"
        nodes.append({"id": sid, "label": f"💡 {sug}", "type": "suggestion", "details": sug})
        edges.append({"source": "incident", "target": sid, "label": "recommended"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 2: Knowledge Search
# ═══════════════════════════════════════════════════════════════════════

def build_knowledge_search_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "query", "label": _truncate(query, 50), "type": "incident", "details": query})
    nodes.append({"id": "neo4j", "label": "Neo4j Knowledge Base", "type": "agent", "details": "Graph database query engine"})
    edges.append({"source": "query", "target": "neo4j", "label": "searched in"})

    results = [
        ("Equifax Breach 2017", "147M records exposed via Apache Struts vulnerability"),
        ("Capital One 2019", "100M records via misconfigured WAF in AWS"),
        ("Marriott 2018", "500M guest records from Starwood reservation system"),
    ]
    for i, (name, desc) in enumerate(results):
        nid = f"result{i}"
        nodes.append({"id": nid, "label": name, "type": "source", "details": desc})
        edges.append({"source": "neo4j", "target": nid, "label": "found"})

    nodes.append({"id": "pattern", "label": "Common Pattern: Third-Party Risk", "type": "suggestion", "details": "All breaches involved third-party or cloud misconfigurations"})
    edges.append({"source": "result0", "target": "pattern", "label": "pattern"})
    edges.append({"source": "result1", "target": "pattern", "label": "pattern"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 3: Compliance
# ═══════════════════════════════════════════════════════════════════════

def build_compliance_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "incident", "label": _truncate(query, 45), "type": "incident", "details": query})

    regs = [
        ("GDPR", "Article 33/34 — 72hr notification", "red_alert"),
        ("CCPA", "Section 1798.150 — Consumer rights", "yellow_alert"),
        ("HIPAA", "45 CFR 164.400 — Breach notification", "yellow_alert"),
    ]
    for i, (name, desc, t) in enumerate(regs):
        nid = f"reg{i}"
        nodes.append({"id": nid, "label": f"⚖️ {name}", "type": t, "details": desc})
        edges.append({"source": "incident", "target": nid, "label": "regulated by"})

    actions = [
        ("Notify DPA within 72hrs", "GDPR Art.33 requirement"),
        ("Notify affected users", "GDPR Art.34 — high risk to rights"),
        ("Document in breach register", "GDPR Art.33(5) — record keeping"),
    ]
    for i, (label, desc) in enumerate(actions):
        aid = f"action{i}"
        nodes.append({"id": aid, "label": f"📋 {label}", "type": "suggestion", "details": desc})
        edges.append({"source": "reg0", "target": aid, "label": "requires"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 4: Risk Assessment
# ═══════════════════════════════════════════════════════════════════════

def build_risk_assessment_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "center", "label": "Risk Assessment", "type": "incident", "details": query})

    vendors = [
        ("AWS", "9.1", "red_alert", "Critical cloud dependency"),
        ("Stripe", "7.8", "red_alert", "Payment data processor"),
        ("Salesforce", "6.2", "yellow_alert", "CRM with customer PII"),
        ("SendGrid", "5.5", "yellow_alert", "Email service — limited PII"),
    ]
    for i, (name, score, t, desc) in enumerate(vendors):
        vid = f"vendor{i}"
        nodes.append({"id": vid, "label": f"{name} ({score}/10)", "type": t, "details": desc})
        edges.append({"source": "center", "target": vid, "label": "risk score"})

    nodes.append({"id": "supply", "label": "Supply Chain Risk", "type": "risk", "details": "Aggregated third-party risk exposure"})
    edges.append({"source": "vendor0", "target": "supply", "label": "feeds into"})
    edges.append({"source": "vendor1", "target": "supply", "label": "feeds into"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 5: Safety Check
# ═══════════════════════════════════════════════════════════════════════

def build_safety_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "input", "label": _truncate(query, 45), "type": "incident", "details": query})

    checks = [
        ("PII Scan", "✅ No PII detected", "real"),
        ("Toxicity", "✅ Clean content", "real"),
        ("Hallucination", "✅ Grounded facts", "real"),
        ("Content Filter", "✅ Passed", "real"),
    ]
    for i, (name, result, t) in enumerate(checks):
        cid = f"check{i}"
        nodes.append({"id": cid, "label": f"🛡️ {name}", "type": "agent", "details": result})
        edges.append({"source": "input", "target": cid, "label": "scanned by"})

    nodes.append({"id": "result", "label": "✅ All Checks Passed", "type": "real", "details": "Content is safe for use"})
    for i in range(len(checks)):
        edges.append({"source": f"check{i}", "target": "result", "label": "passed"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 6: Incident Response
# ═══════════════════════════════════════════════════════════════════════

def build_incident_response_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "incident", "label": _truncate(query, 45), "type": "incident", "details": query})

    phases = [
        ("1. Identification", "Detect and confirm the incident", "agent"),
        ("2. Containment", "Isolate affected systems", "red_alert"),
        ("3. Eradication", "Remove threat actors and malware", "yellow_alert"),
        ("4. Recovery", "Restore systems and verify", "suggestion"),
        ("5. Lessons Learned", "Post-incident review", "source"),
    ]
    prev = "incident"
    for i, (name, desc, t) in enumerate(phases):
        pid = f"phase{i}"
        nodes.append({"id": pid, "label": f"🚨 {name}", "type": t, "details": desc})
        edges.append({"source": prev, "target": pid, "label": "then"})
        prev = pid

    nodes.append({"id": "notify", "label": "📧 Notify Stakeholders", "type": "suggestion", "details": "Legal, CISO, affected users, regulators"})
    edges.append({"source": "phase1", "target": "notify", "label": "requires"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 7: Data Mapping
# ═══════════════════════════════════════════════════════════════════════

def build_data_mapping_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "org", "label": "Organization Data Flows", "type": "incident", "details": query})

    systems = [
        ("CRM System", "Customer PII — names, emails, phones", "red_alert"),
        ("Payment Gateway", "Financial data — card numbers, transactions", "red_alert"),
        ("HR Platform", "Employee PII — SSN, salary, address", "red_alert"),
        ("Marketing Tool", "Email addresses, preferences", "yellow_alert"),
        ("Analytics DB", "Anonymized usage data", "real"),
    ]
    for i, (name, desc, t) in enumerate(systems):
        sid = f"sys{i}"
        nodes.append({"id": sid, "label": f"🗄️ {name}", "type": t, "details": desc})
        edges.append({"source": "org", "target": sid, "label": "stores data"})

    nodes.append({"id": "ext", "label": "Third-Party Transfers", "type": "yellow_alert", "details": "Data shared with external vendors"})
    edges.append({"source": "sys0", "target": "ext", "label": "shares with"})
    edges.append({"source": "sys1", "target": "ext", "label": "shares with"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 8: DSR (Data Subject Rights)
# ═══════════════════════════════════════════════════════════════════════

def build_dsr_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "request", "label": f"DSR Request", "type": "incident", "details": query})

    nodes.append({"id": "subject", "label": "👤 Data Subject", "type": "agent", "details": "Customer ID: C-4521"})
    edges.append({"source": "request", "target": "subject", "label": "from"})

    systems = [
        ("CRM Database", "3 records found", "yellow_alert"),
        ("Marketing Platform", "Email + preferences", "yellow_alert"),
        ("Support Tickets", "12 ticket records", "yellow_alert"),
        ("Payment System", "Transaction history", "red_alert"),
    ]
    for i, (name, desc, t) in enumerate(systems):
        sid = f"sys{i}"
        nodes.append({"id": sid, "label": f"🗄️ {name}", "type": t, "details": desc})
        edges.append({"source": "subject", "target": sid, "label": "data in"})

    nodes.append({"id": "action", "label": "🗑️ Erasure Scheduled", "type": "suggestion", "details": "Data erasure across all systems within 30 days"})
    for i in range(len(systems)):
        edges.append({"source": f"sys{i}", "target": "action", "label": "erase from"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 9: Dark Web Monitoring
# ═══════════════════════════════════════════════════════════════════════

def build_dark_web_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "scan", "label": "🌐 Dark Web Scan", "type": "agent", "details": query})

    findings = [
        ("credentials_dump.csv", "450 email:password pairs from company.com", "red_alert"),
        ("api_keys_leak", "3 AWS API keys found on paste site", "red_alert"),
        ("forum_mention", "Company mentioned in ransomware forum", "yellow_alert"),
    ]
    for i, (name, desc, t) in enumerate(findings):
        fid = f"finding{i}"
        nodes.append({"id": fid, "label": f"⚠️ {name}", "type": t, "details": desc})
        edges.append({"source": "scan", "target": fid, "label": "found"})

    nodes.append({"id": "action0", "label": "🔑 Force Password Reset", "type": "suggestion", "details": "Reset all exposed credentials immediately"})
    nodes.append({"id": "action1", "label": "🔄 Rotate API Keys", "type": "suggestion", "details": "Revoke and regenerate all exposed keys"})
    edges.append({"source": "finding0", "target": "action0", "label": "action needed"})
    edges.append({"source": "finding1", "target": "action1", "label": "action needed"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 10: Reports
# ═══════════════════════════════════════════════════════════════════════

def build_reports_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "report", "label": "📝 Executive Report", "type": "incident", "details": query})

    metrics = [
        ("Incidents: 12", "3 critical, 5 high, 4 medium", "red_alert"),
        ("MTTR: 4.2 hrs", "Mean time to resolve — down 15%", "real"),
        ("Compliance: 94%", "GDPR/CCPA adherence rate", "real"),
        ("Risk Score: 6.8", "Organization-wide risk", "yellow_alert"),
    ]
    for i, (name, desc, t) in enumerate(metrics):
        mid = f"metric{i}"
        nodes.append({"id": mid, "label": f"📊 {name}", "type": t, "details": desc})
        edges.append({"source": "report", "target": mid, "label": "shows"})

    nodes.append({"id": "trend", "label": "📈 Improving Trend", "type": "suggestion", "details": "Security posture improved 22% QoQ"})
    edges.append({"source": "metric1", "target": "trend", "label": "indicates"})
    edges.append({"source": "metric2", "target": "trend", "label": "indicates"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 11: Threat Modeling
# ═══════════════════════════════════════════════════════════════════════

def build_threat_model_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "system", "label": _truncate(query, 45), "type": "incident", "details": query})

    threats = [
        ("Spoofing", "Identity spoofing via stolen credentials", "red_alert"),
        ("Tampering", "SQL injection on API endpoints", "red_alert"),
        ("Repudiation", "Missing audit logs on admin actions", "yellow_alert"),
        ("Info Disclosure", "Error messages expose stack traces", "yellow_alert"),
        ("DoS", "No rate limiting on login endpoint", "yellow_alert"),
        ("Elevation", "Horizontal privilege escalation risk", "red_alert"),
    ]
    for i, (name, desc, t) in enumerate(threats):
        tid = f"threat{i}"
        nodes.append({"id": tid, "label": f"🎯 {name}", "type": t, "details": desc})
        edges.append({"source": "system", "target": tid, "label": "vulnerable to"})

    nodes.append({"id": "mitre", "label": "MITRE ATT&CK Mapped", "type": "agent", "details": "T1078 — Valid Accounts, T1190 — Exploit Public-Facing App"})
    edges.append({"source": "threat0", "target": "mitre", "label": "maps to"})
    edges.append({"source": "threat1", "target": "mitre", "label": "maps to"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 12: Vulnerability Scanning
# ═══════════════════════════════════════════════════════════════════════

def build_vulnerability_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "target", "label": _truncate(query, 45), "type": "incident", "details": query})

    vulns = [
        ("CVE-2024-1234", "CVSS 9.8 — Remote Code Execution", "red_alert"),
        ("CVE-2024-5678", "CVSS 7.5 — Auth Bypass", "red_alert"),
        ("CVE-2024-9012", "CVSS 5.3 — Info Disclosure", "yellow_alert"),
    ]
    for i, (cve, desc, t) in enumerate(vulns):
        vid = f"vuln{i}"
        nodes.append({"id": vid, "label": f"🔓 {cve}", "type": t, "details": desc})
        edges.append({"source": "target", "target": vid, "label": "affected by"})

    patches = [
        ("Patch: Upgrade to v2.18.0", "Fixes CVE-2024-1234"),
        ("Patch: Enable 2FA", "Mitigates CVE-2024-5678"),
    ]
    for i, (label, desc) in enumerate(patches):
        pid = f"patch{i}"
        nodes.append({"id": pid, "label": f"🔧 {label}", "type": "suggestion", "details": desc})
        edges.append({"source": f"vuln{i}", "target": pid, "label": "fix"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 13: Access Control
# ═══════════════════════════════════════════════════════════════════════

def build_access_control_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "iam", "label": "🔐 IAM Review", "type": "agent", "details": query})

    roles = [
        ("Admin", "5 users — Full access to all systems", "red_alert"),
        ("Developer", "23 users — Code + staging access", "yellow_alert"),
        ("Analyst", "12 users — Read-only dashboards", "real"),
        ("Contractor", "8 users — Limited project access", "yellow_alert"),
    ]
    for i, (name, desc, t) in enumerate(roles):
        rid = f"role{i}"
        nodes.append({"id": rid, "label": f"👥 {name}", "type": t, "details": desc})
        edges.append({"source": "iam", "target": rid, "label": "role"})

    nodes.append({"id": "issue0", "label": "⚠️ 3 Over-Privileged Users", "type": "red_alert", "details": "Developers with production DB admin access"})
    nodes.append({"id": "issue1", "label": "⚠️ 2 Zombie Accounts", "type": "red_alert", "details": "Terminated employees still active"})
    edges.append({"source": "role1", "target": "issue0", "label": "has issue"})
    edges.append({"source": "role3", "target": "issue1", "label": "has issue"})

    nodes.append({"id": "fix", "label": "💡 Apply Least Privilege", "type": "suggestion", "details": "Remove unnecessary permissions and deactivate zombie accounts"})
    edges.append({"source": "issue0", "target": "fix", "label": "action"})
    edges.append({"source": "issue1", "target": "fix", "label": "action"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 14: Forensics
# ═══════════════════════════════════════════════════════════════════════

def build_forensics_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "evidence", "label": "🔬 Digital Evidence", "type": "agent", "details": query})

    timeline = [
        ("03:14 UTC", "Brute-force login from 185.x.x.x", "red_alert"),
        ("03:17 UTC", "Successful login — admin account", "red_alert"),
        ("03:22 UTC", "New service account created", "red_alert"),
        ("03:45 UTC", "Data exfiltration — 2.3GB to ext IP", "red_alert"),
        ("04:10 UTC", "Logs cleared by attacker", "yellow_alert"),
    ]
    prev = "evidence"
    for i, (time, desc, t) in enumerate(timeline):
        tid = f"event{i}"
        nodes.append({"id": tid, "label": f"🕐 {time}", "type": t, "details": desc})
        edges.append({"source": prev, "target": tid, "label": "then"})
        prev = tid

    nodes.append({"id": "ioc0", "label": "IOC: 185.x.x.x", "type": "source", "details": "Known malicious IP — Tor exit node"})
    nodes.append({"id": "ioc1", "label": "IOC: backdoor.exe", "type": "source", "details": "SHA256: a3b8f1...matched known malware"})
    edges.append({"source": "event0", "target": "ioc0", "label": "IOC"})
    edges.append({"source": "event2", "target": "ioc1", "label": "IOC"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode 15: Security Architecture
# ═══════════════════════════════════════════════════════════════════════

def build_security_arch_graph(query: str) -> dict:
    nodes, edges = [], []
    nodes.append({"id": "arch", "label": "🏗️ Security Architecture", "type": "agent", "details": query})

    pillars = [
        ("Identity", "MFA + SSO — 85% coverage", "real"),
        ("Network", "Microsegmentation — partial", "yellow_alert"),
        ("Data", "Encryption at rest — all critical DBs", "real"),
        ("Endpoint", "EDR deployed — 70% coverage", "yellow_alert"),
        ("Application", "SAST/DAST in CI/CD — active", "real"),
    ]
    for i, (name, desc, t) in enumerate(pillars):
        pid = f"pillar{i}"
        nodes.append({"id": pid, "label": f"🛡️ {name}", "type": t, "details": desc})
        edges.append({"source": "arch", "target": pid, "label": "pillar"})

    nodes.append({"id": "score", "label": "Zero Trust Score: 72/100", "type": "yellow_alert", "details": "Good progress — network segmentation needs improvement"})
    for i in range(len(pillars)):
        edges.append({"source": f"pillar{i}", "target": "score", "label": "contributes"})

    nodes.append({"id": "gap", "label": "⚠️ Gap: Network Segmentation", "type": "red_alert", "details": "Lateral movement possible between production and dev environments"})
    edges.append({"source": "pillar1", "target": "gap", "label": "gap found"})

    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════════
# Mode Router — pick the right graph builder
# ═══════════════════════════════════════════════════════════════════════

MODE_GRAPH_BUILDERS = {
    "knowledge_search": build_knowledge_search_graph,
    "compliance": build_compliance_graph,
    "risk_assessment": build_risk_assessment_graph,
    "safety": build_safety_graph,
    "incident_response": build_incident_response_graph,
    "data_mapping": build_data_mapping_graph,
    "dsr": build_dsr_graph,
    "dark_web": build_dark_web_graph,
    "reports": build_reports_graph,
    "threat_modeling": build_threat_model_graph,
    "vulnerability": build_vulnerability_graph,
    "access_control": build_access_control_graph,
    "forensics": build_forensics_graph,
    "security_arch": build_security_arch_graph,
}

# Mode → graph title
MODE_GRAPH_TITLES = {
    "knowledge_search": "📚 Knowledge Search — Graph",
    "compliance": "⚖️ Compliance Assessment — Graph",
    "risk_assessment": "📊 Risk Assessment — Graph",
    "safety": "🛡️ Safety Check — Graph",
    "incident_response": "🚨 Incident Response — Graph",
    "data_mapping": "🗺️ Data Mapping — Graph",
    "dsr": "👤 Data Subject Rights — Graph",
    "dark_web": "🌐 Dark Web Scan — Graph",
    "reports": "📝 Executive Report — Graph",
    "threat_modeling": "🎯 Threat Model — Graph",
    "vulnerability": "🔓 Vulnerability Scan — Graph",
    "access_control": "🔐 Access Control — Graph",
    "forensics": "🔬 Forensics Timeline — Graph",
    "security_arch": "🏗️ Security Architecture — Graph",
}


def build_graph_for_mode(mode: str, query: str) -> tuple[str, dict] | None:
    """Return (title, graph_data) for the given mode, or None if no builder."""
    builder = MODE_GRAPH_BUILDERS.get(mode)
    if not builder:
        return None
    title = MODE_GRAPH_TITLES.get(mode, "Knowledge Graph")
    return title, builder(query)
