// Mode configuration for the Data Privacy Platform
export interface ModeConfig {
    id: string;
    label: string;
    icon: string;
    description: string;
    agents: string[];
    section: string;
    samples: string[];
    placeholder: string;
}

export const MODES: ModeConfig[] = [
    // ─── Core Data Privacy ───
    {
        id: "breach_analysis",
        label: "Breach Analysis",
        icon: "🔍",
        description: "Detect, verify, and analyze data breaches end-to-end",
        agents: ["NewsVerify", "Tavily", "NLP", "Risk", "Similar", "Alert", "Suggest"],
        section: "Core Data Privacy",
        samples: [
            "TechCorp suffered a ransomware attack in March 2025, compromising 500,000 customer records including PII data",
            "A major healthcare provider reported unauthorized access to patient records affecting 1.2 million individuals",
            "Financial services company FinServ disclosed a supply chain breach through their payment processor",
        ],
        placeholder: "Paste a breach article or describe an incident...",
    },
    {
        id: "knowledge_search",
        label: "Knowledge Search",
        icon: "📚",
        description: "Query the breach knowledge graph in natural language",
        agents: ["FullText", "Hybrid", "Vector", "NLPCypher"],
        section: "Core Data Privacy",
        samples: [
            "Which third parties were impacted by ransomware in 2024?",
            "Show me all services connected to AWS",
            "Find companies similar to Stripe in the payment sector",
        ],
        placeholder: "Ask a question about the breach database...",
    },
    {
        id: "compliance",
        label: "Compliance",
        icon: "⚖️",
        description: "GDPR / CCPA / HIPAA regulatory assessment",
        agents: ["Compliance", "PrivacyImpact", "AuditTrail", "Consent"],
        section: "Core Data Privacy",
        samples: [
            "What GDPR obligations apply to the TechCorp breach?",
            "Generate a DPIA for the latest ransomware incident",
            "Show audit trail for all incidents in Q1 2025",
        ],
        placeholder: "Ask about regulatory compliance...",
    },
    {
        id: "risk_assessment",
        label: "Risk Assessment",
        icon: "📊",
        description: "Vendor & supply chain risk scoring",
        agents: ["Risk", "SimilarCompany", "VendorRisk", "SupplyChain"],
        section: "Core Data Privacy",
        samples: [
            "Evaluate risk for all our payment vendors",
            "What is the risk score for third parties connected to AWS?",
            "Which vendors have the highest PII exposure?",
        ],
        placeholder: "Ask about vendor or third-party risk...",
    },
    {
        id: "safety",
        label: "Safety Check",
        icon: "🛡️",
        description: "PII / toxicity / hallucination guardrails",
        agents: ["Guardrails", "Hallucination", "PIIRedaction", "ContentFilter"],
        section: "Core Data Privacy",
        samples: [
            "Validate: John Smith at john@techcorp.com reported the breach on March 15",
            "Check if this response is grounded: The breach affected 1 million users",
            "Scan this text for PII: Call Sarah Jones at 555-0123 about the incident",
        ],
        placeholder: "Paste text to validate for PII, toxicity, or hallucination...",
    },
    {
        id: "incident_response",
        label: "Incident Response",
        icon: "🚨",
        description: "IR playbooks, notifications & remediation",
        agents: ["IR", "Notification", "Remediation", "ThreatIntel", "PolicyGen"],
        section: "Core Data Privacy",
        samples: [
            "Generate IR playbook for ransomware affecting PII data",
            "Who do we need to notify for a GDPR breach?",
            "What patches and remediations are needed for the latest incident?",
        ],
        placeholder: "Ask about incident response plans...",
    },

    // ─── Advanced ───
    {
        id: "data_mapping",
        label: "Data Mapping",
        icon: "🗺️",
        description: "Data flow tracking & classification (GDPR Art.30)",
        agents: ["DataMapping", "DataClassification", "DataLineage"],
        section: "Advanced",
        samples: [
            "Map all PII data flows to third-party vendors",
            "Classify the data exposed in the latest breach",
            "Show data lineage for customer email addresses",
        ],
        placeholder: "Ask about data flows and classification...",
    },
    {
        id: "dsr",
        label: "DSR Rights",
        icon: "👤",
        description: "Data subject access, erasure & portability requests",
        agents: ["DSR", "Consent", "DataInventory"],
        section: "Advanced",
        samples: [
            "Process right-to-erasure request for customer ID C-4521",
            "Show consent status for user john@example.com",
            "List all systems containing data for customer C-8901",
        ],
        placeholder: "Enter a data subject request...",
    },
    {
        id: "dark_web",
        label: "Dark Web",
        icon: "🌐",
        description: "Credential leak & brand monitoring",
        agents: ["DarkWeb", "CredentialLeak", "BrandMonitor"],
        section: "Advanced",
        samples: [
            "Check if company.com credentials are on the dark web",
            "Scan for leaked API keys from our organization",
            "Monitor brand mentions in underground forums",
        ],
        placeholder: "Enter domains or emails to scan...",
    },
    {
        id: "reports",
        label: "Reports",
        icon: "📝",
        description: "Executive & regulatory report generation",
        agents: ["ExecutiveReport", "RegulatoryReport", "Metrics"],
        section: "Advanced",
        samples: [
            "Generate Q1 2025 board report",
            "Create GDPR Article 33 breach notification report",
            "Show security metrics dashboard for last 90 days",
        ],
        placeholder: "Request a report...",
    },

    // ─── Security Engineering ───
    {
        id: "threat_modeling",
        label: "Threat Modeling",
        icon: "🎯",
        description: "STRIDE / DREAD / MITRE ATT&CK analysis",
        agents: ["ThreatModel", "AttackTree", "MITRE"],
        section: "Security Engineering",
        samples: [
            "Analyze threats for our payment processing API",
            "Generate STRIDE analysis for the user authentication system",
            "Map the latest attack to MITRE ATT&CK framework",
        ],
        placeholder: "Describe a system to analyze for threats...",
    },
    {
        id: "vulnerability",
        label: "Vulnerability",
        icon: "🔓",
        description: "CVE scanning, CVSS scoring & patch priority",
        agents: ["VulnScan", "CVSS", "PatchPriority"],
        section: "Security Engineering",
        samples: [
            "Check vulnerabilities for Apache Log4j 2.14.1",
            "Show critical CVEs for Node.js 18",
            "Prioritize patches for our production servers",
        ],
        placeholder: "Enter software name and version to scan...",
    },
    {
        id: "access_control",
        label: "Access Control",
        icon: "🔐",
        description: "IAM review & least privilege analysis",
        agents: ["AccessControl", "Privilege", "Identity"],
        section: "Security Engineering",
        samples: [
            "Find over-privileged users in our systems",
            "Review access permissions for the admin role",
            "Check for zombie accounts (terminated employees)",
        ],
        placeholder: "Ask about access control and permissions...",
    },
    {
        id: "forensics",
        label: "Forensics",
        icon: "🔬",
        description: "Log analysis & timeline reconstruction",
        agents: ["Forensics", "LogAnalysis", "Timeline"],
        section: "Security Engineering",
        samples: [
            "Analyze: Failed login from 185.x.x.x followed by new user creation",
            "Reconstruct attack timeline from these log entries",
            "Extract IOCs from the latest incident",
        ],
        placeholder: "Paste logs or describe evidence to analyze...",
    },
    {
        id: "security_arch",
        label: "Security Arch",
        icon: "🏗️",
        description: "Zero Trust, security posture & BCP",
        agents: ["ZeroTrust", "Posture", "BCP"],
        section: "Security Engineering",
        samples: [
            "Assess our Zero Trust maturity",
            "Generate security posture score",
            "Review our business continuity plan for ransomware scenario",
        ],
        placeholder: "Ask about security architecture...",
    },
];

export function getModeById(id: string): ModeConfig | undefined {
    return MODES.find((m) => m.id === id);
}

export function getModeSections(): { section: string; modes: ModeConfig[] }[] {
    const sections: { section: string; modes: ModeConfig[] }[] = [];
    const seen = new Set<string>();
    for (const mode of MODES) {
        if (!seen.has(mode.section)) {
            seen.add(mode.section);
            sections.push({ section: mode.section, modes: MODES.filter((m) => m.section === mode.section) });
        }
    }
    return sections;
}
