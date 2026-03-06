# Agentic Knowledge Graph — Complete Implementation Guide
## For Zenia Data Privacy Platform (Fake News Detection Use Case)

---

# 1. What Are We Building?

**Current behavior:** When a user submits a news claim, the app returns TEXT responses from agents (NewsVerify, Tavily, NLP, Risk, etc.) and renders them as A2UI cards.

**New behavior:** Along with the text, the app also renders an **interactive knowledge graph** — a visual diagram where nodes represent facts, claims, sources, and risks, and edges show how they connect. Users can click any node to explore deeper.

---

# 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                   │
│                                                         │
│  ┌───────────────────┐    ┌──────────────────────────┐  │
│  │  Chat Component   │    │  KnowledgeGraph Component│  │
│  │  (existing)       │    │  (NEW — Cytoscape.js)    │  │
│  └────────┬──────────┘    └──────────┬───────────────┘  │
│           │                          │                   │
│           └──────────┬───────────────┘                   │
│                      │ A2UI StateSnapshot                │
└──────────────────────┼───────────────────────────────────┘
                       │
                       │ HTTP (AG-UI Protocol)
                       │
┌──────────────────────┼───────────────────────────────────┐
│                  BACKEND (Python)                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │           DPOrchestrator (dp_orchestrator.py)     │    │
│  │                                                   │    │
│  │  Step 1: NewsVerifyAgent ──→ verdict + sources    │    │
│  │  Step 2: TavilyVerifyAgent ──→ verdict + sources  │    │
│  │  Step 3: Build knowledge_graph_data (NEW)         │    │
│  │  Step 4: Return A2UI with KnowledgeGraph component│    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │           views.py (A2UI builders)                │    │
│  │                                                   │    │
│  │  render_fake_news_warning()  ← existing           │    │
│  │  render_knowledge_graph()    ← NEW function       │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

# 3. Backend Changes

## 3.1 New File: `agent/knowledge_graph_builder.py`

This module takes agent results and builds knowledge graph data (nodes + edges).

```python
"""
knowledge_graph_builder.py — Builds knowledge graph data from agent results.
"""
import json
from typing import Optional


def build_fake_news_graph(
    query: str,
    news_result: dict,
    tavily_result: dict,
    is_fake: bool,
) -> dict:
    """
    Build a knowledge graph for the fake news detection flow.
    
    Returns:
        dict with "nodes" and "edges" lists
    """
    nodes = []
    edges = []
    
    # ── Node 1: The user's claim (always present)
    nodes.append({
        "id": "claim",
        "label": _truncate(query, 60),
        "type": "fake" if is_fake else "real",
        "details": query,
    })
    
    # ── Node 2: NewsVerificationAgent result
    nodes.append({
        "id": "newsverify",
        "label": f"NewsVerify: {news_result.get('verdict', 'UNKNOWN')}",
        "type": "agent",
        "details": news_result.get("reason", ""),
        "confidence": news_result.get("confidence", 0),
    })
    edges.append({
        "source": "claim",
        "target": "newsverify",
        "label": "verified by",
    })
    
    # ── Node 3: TavilyVerificationAgent result
    nodes.append({
        "id": "tavilyverify",
        "label": f"TavilyVerify: {tavily_result.get('verdict', 'UNKNOWN')}",
        "type": "agent",
        "details": tavily_result.get("reason", ""),
        "confidence": tavily_result.get("confidence", 0),
    })
    edges.append({
        "source": "claim",
        "target": "tavilyverify",
        "label": "verified by",
    })
    
    # ── Source nodes from NewsVerify
    for i, url in enumerate(news_result.get("sources", [])[:5]):
        source_id = f"news_src_{i}"
        nodes.append({
            "id": source_id,
            "label": _domain_from_url(url),
            "type": "source",
            "details": url,
        })
        edges.append({
            "source": "newsverify",
            "target": source_id,
            "label": "checked",
        })
    
    # ── Source nodes from Tavily
    for i, url in enumerate(tavily_result.get("sources", [])[:5]):
        source_id = f"tavily_src_{i}"
        nodes.append({
            "id": source_id,
            "label": _domain_from_url(url),
            "type": "source",
            "details": url,
        })
        edges.append({
            "source": "tavilyverify",
            "target": source_id,
            "label": "checked",
        })
    
    # ── Verdict node
    verdict = "FAKE" if is_fake else "REAL"
    nodes.append({
        "id": "verdict",
        "label": f"Verdict: {verdict}",
        "type": "fake" if is_fake else "real",
        "details": f"Both agents concluded: {verdict}",
    })
    edges.append({"source": "newsverify", "target": "verdict", "label": "concluded"})
    edges.append({"source": "tavilyverify", "target": "verdict", "label": "concluded"})
    
    return {"nodes": nodes, "edges": edges}


def build_risk_report_graph(
    query: str,
    risk_data: dict,
    alerts: dict,
    suggestions: list,
    similar_companies: list,
) -> dict:
    """
    Build a knowledge graph for the risk report flow (after Proceed Anyway).
    """
    nodes = []
    edges = []
    
    # ── Central: Incident node
    nodes.append({
        "id": "incident",
        "label": _truncate(query, 50),
        "type": "incident",
    })
    
    # ── Risk score node
    risk_score = risk_data.get("overall_risk", "N/A")
    nodes.append({
        "id": "risk_score",
        "label": f"Risk Score: {risk_score}/10",
        "type": "risk",
    })
    edges.append({"source": "incident", "target": "risk_score", "label": "assessed at"})
    
    # ── Alert nodes (RED)
    red_alerts = alerts.get("red", [])
    for i, alert in enumerate(red_alerts[:5]):
        alert_id = f"red_alert_{i}"
        company = alert.get("company", f"Company {i+1}")
        nodes.append({
            "id": alert_id,
            "label": f"🔴 {company}",
            "type": "red_alert",
            "details": alert.get("reason", ""),
        })
        edges.append({
            "source": "risk_score",
            "target": alert_id,
            "label": "high risk",
        })
    
    # ── Alert nodes (YELLOW)
    yellow_alerts = alerts.get("yellow", [])
    for i, alert in enumerate(yellow_alerts[:3]):
        alert_id = f"yellow_alert_{i}"
        company = alert.get("company", f"Company {i+1}")
        nodes.append({
            "id": alert_id,
            "label": f"🟡 {company}",
            "type": "yellow_alert",
            "details": alert.get("reason", ""),
        })
        edges.append({
            "source": "risk_score",
            "target": alert_id,
            "label": "moderate risk",
        })
    
    # ── Suggestion nodes
    for i, suggestion in enumerate(suggestions[:5]):
        sug_id = f"suggestion_{i}"
        nodes.append({
            "id": sug_id,
            "label": f"💡 {_truncate(suggestion, 40)}",
            "type": "suggestion",
            "details": suggestion,
        })
        edges.append({
            "source": "incident",
            "target": sug_id,
            "label": "recommended",
        })
    
    # ── Similar company nodes
    for i, company in enumerate(similar_companies[:3]):
        comp_id = f"similar_{i}"
        nodes.append({
            "id": comp_id,
            "label": f"📊 {company.get('name', f'Company {i+1}')}",
            "type": "similar",
            "details": company.get("reason", ""),
        })
        edges.append({
            "source": "incident",
            "target": comp_id,
            "label": "similar case",
        })
    
    return {"nodes": nodes, "edges": edges}


def _truncate(text: str, max_len: int) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


def _domain_from_url(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url[:30]
```

---

## 3.2 Update: `agent/views.py` — Add Knowledge Graph Renderer

Add this new function to `views.py`:

```python
def render_knowledge_graph(
    title: str,
    graph_data: dict,
    layout: str = "cose",
    buttons: list[tuple[str, str, str]] | None = None,
) -> dict:
    """
    Render an interactive knowledge graph as A2UI component.
    
    Args:
        title: Title text shown above the graph
        graph_data: dict with "nodes" and "edges" lists
        layout: Cytoscape.js layout (cose, circle, breadthfirst, grid)
        buttons: Optional list of (id, label, action_name) tuples
    """
    import json
    
    # Build node + edge items for the data model
    items = []
    for node in graph_data.get("nodes", []):
        items.append(node)
    for edge in graph_data.get("edges", []):
        items.append(edge)
    
    children = ["kg_title", "kg_graph"]
    if buttons:
        children.append("kg_buttons")
    
    components = [
        _column("root", ["kg_card"]),
        _card("kg_card", "kg_col"),
        _column("kg_col", children),
        _text("kg_title", title, "h2"),
        
        # The KnowledgeGraph custom component
        {
            "id": "kg_graph",
            "component": {
                "KnowledgeGraph": {
                    "title": title,
                    "layout": layout,
                    "graphData": json.dumps(items),
                }
            }
        },
    ]
    
    if buttons:
        btn_ids = []
        for btn_id, btn_label, btn_action in buttons:
            components.append(_button(btn_id, btn_label, btn_action))
            btn_ids.append(btn_id)
        components.append(_row("kg_buttons", btn_ids))
    
    return _wrap(components)
```

---

## 3.3 Update: `agent/agui_endpoint.py` — Wire Knowledge Graph Into the Pipeline

In the main endpoint, after the verification agents return their results, build the knowledge graph:

```python
# ── Inside the breach_analysis flow ──

from agent.knowledge_graph_builder import (
    build_fake_news_graph,
    build_risk_report_graph,
)
from agent.views import render_knowledge_graph, render_fake_news_warning

# After NewsVerify + Tavily return results:
news_result = json.loads(news_agent_response)
tavily_result = json.loads(tavily_agent_response)

is_fake = (
    news_result.get("verdict") == "FAKE"
    or tavily_result.get("verdict") == "FAKE"
)

# Build the knowledge graph data
graph_data = build_fake_news_graph(
    query=user_query,
    news_result=news_result,
    tavily_result=tavily_result,
    is_fake=is_fake,
)

# Build the A2UI response with BOTH text card AND knowledge graph
if is_fake:
    a2ui_response = render_knowledge_graph(
        title="⚠️ Fake News Analysis — Knowledge Graph",
        graph_data=graph_data,
        layout="cose",
        buttons=[
            ("btn-proceed", "Proceed Anyway", "force_proceed"),
            ("btn-discard", "Discard Article", "cancel_workflow"),
        ],
    )
```

---

## 3.4 Request & Response Payloads

### Request 1: User submits a news claim

```json
{
    "threadId": "ae715e25-3e46-4f6d-af23-d9dab8e0f557",
    "messages": [
        {
            "role": "user",
            "content": "In October 2025, Amazon disclosed that hackers breached its internal financial systems and exfiltrated detailed accounting and revenue records for 2024–2025, posting them publicly. The leak claimed to show previously unreported losses of over $200 billion."
        }
    ]
}
```

### Response 1: Fake news detected + Knowledge Graph

```json
{
    "type": "STATE_SNAPSHOT",
    "snapshot": {
        "a2ui": {
            "beginRendering": {
                "surfaceId": "main",
                "root": "root"
            },
            "surfaceUpdate": {
                "surfaceId": "main",
                "components": [
                    {
                        "id": "root",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": [
                                        "fake_news_title",
                                        "text_explanation",
                                        "knowledge_graph",
                                        "buttons_row"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": "fake_news_title",
                        "component": {
                            "Text": {
                                "text": {
                                    "literalString": "⚠️ Fake News Analysis"
                                },
                                "usageHint": "h1"
                            }
                        }
                    },
                    {
                        "id": "text_explanation",
                        "component": {
                            "Text": {
                                "text": {
                                    "literalString": "The claim conflates several unrelated events. See the visual analysis below."
                                }
                            }
                        }
                    },
                    {
                        "id": "knowledge_graph",
                        "component": {
                            "KnowledgeGraph": {
                                "title": "Claim Analysis",
                                "layout": "cose",
                                "data": {
                                    "path": "/graphData"
                                }
                            }
                        }
                    },
                    {
                        "id": "buttons_row",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": [
                                        "proceed_button",
                                        "discard_button"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": "proceed_button",
                        "component": {
                            "Button": {
                                "child": "proceed_text",
                                "action": { "name": "force_proceed" }
                            }
                        }
                    },
                    {
                        "id": "proceed_text",
                        "component": {
                            "Text": {
                                "text": { "literalString": "Proceed Anyway" }
                            }
                        }
                    },
                    {
                        "id": "discard_button",
                        "component": {
                            "Button": {
                                "child": "discard_text",
                                "action": { "name": "cancel_workflow" }
                            }
                        }
                    },
                    {
                        "id": "discard_text",
                        "component": {
                            "Text": {
                                "text": { "literalString": "Discard Article" }
                            }
                        }
                    }
                ]
            },
            "dataModelUpdate": {
                "surfaceId": "main",
                "contents": [
                    {
                        "key": "graphData",
                        "valueArray": [
                            {
                                "key": "0",
                                "valueMap": [
                                    { "key": "id", "valueString": "claim" },
                                    { "key": "label", "valueString": "Amazon $200B Breach (CLAIM)" },
                                    { "key": "type", "valueString": "fake" }
                                ]
                            },
                            {
                                "key": "1",
                                "valueMap": [
                                    { "key": "id", "valueString": "newsverify" },
                                    { "key": "label", "valueString": "NewsVerify: FAKE (95%)" },
                                    { "key": "type", "valueString": "agent" }
                                ]
                            },
                            {
                                "key": "2",
                                "valueMap": [
                                    { "key": "id", "valueString": "tavilyverify" },
                                    { "key": "label", "valueString": "TavilyVerify: FAKE (92%)" },
                                    { "key": "type", "valueString": "agent" }
                                ]
                            },
                            {
                                "key": "3",
                                "valueMap": [
                                    { "key": "id", "valueString": "src_0" },
                                    { "key": "label", "valueString": "thousandeyes.com" },
                                    { "key": "type", "valueString": "source" }
                                ]
                            },
                            {
                                "key": "4",
                                "valueMap": [
                                    { "key": "id", "valueString": "verdict" },
                                    { "key": "label", "valueString": "❌ VERDICT: FAKE NEWS" },
                                    { "key": "type", "valueString": "fake" }
                                ]
                            },
                            {
                                "key": "5",
                                "valueMap": [
                                    { "key": "source", "valueString": "claim" },
                                    { "key": "target", "valueString": "newsverify" },
                                    { "key": "label", "valueString": "verified by" }
                                ]
                            },
                            {
                                "key": "6",
                                "valueMap": [
                                    { "key": "source", "valueString": "claim" },
                                    { "key": "target", "valueString": "tavilyverify" },
                                    { "key": "label", "valueString": "verified by" }
                                ]
                            },
                            {
                                "key": "7",
                                "valueMap": [
                                    { "key": "source", "valueString": "newsverify" },
                                    { "key": "target", "valueString": "src_0" },
                                    { "key": "label", "valueString": "checked" }
                                ]
                            },
                            {
                                "key": "8",
                                "valueMap": [
                                    { "key": "source", "valueString": "newsverify" },
                                    { "key": "target", "valueString": "verdict" },
                                    { "key": "label", "valueString": "concluded" }
                                ]
                            },
                            {
                                "key": "9",
                                "valueMap": [
                                    { "key": "source", "valueString": "tavilyverify" },
                                    { "key": "target", "valueString": "verdict" },
                                    { "key": "label", "valueString": "concluded" }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

### Request 2: User clicks "Proceed Anyway"

```json
{
    "threadId": "ae715e25-3e46-4f6d-af23-d9dab8e0f557",
    "action": {
        "name": "force_proceed"
    },
    "previous_query": "In October 2025, Amazon disclosed that hackers..."
}
```

### Response 2: Risk Report + Expanded Knowledge Graph

The graph now includes additional nodes from Risk, Alert, Similar, and Suggestion agents:

```json
{
    "dataModelUpdate": {
        "surfaceId": "main",
        "contents": [
            {
                "key": "graphData",
                "valueArray": [
                    {
                        "key": "0",
                        "valueMap": [
                            { "key": "id", "valueString": "incident" },
                            { "key": "label", "valueString": "Amazon Breach Analysis" },
                            { "key": "type", "valueString": "incident" }
                        ]
                    },
                    {
                        "key": "1",
                        "valueMap": [
                            { "key": "id", "valueString": "risk_score" },
                            { "key": "label", "valueString": "Risk Score: 9.2/10" },
                            { "key": "type", "valueString": "risk" }
                        ]
                    },
                    {
                        "key": "2",
                        "valueMap": [
                            { "key": "id", "valueString": "red_alert_0" },
                            { "key": "label", "valueString": "🔴 Amazon.com, Inc." },
                            { "key": "type", "valueString": "red_alert" }
                        ]
                    },
                    {
                        "key": "3",
                        "valueMap": [
                            { "key": "id", "valueString": "red_alert_1" },
                            { "key": "label", "valueString": "🔴 Uber Technologies" },
                            { "key": "type", "valueString": "red_alert" }
                        ]
                    },
                    {
                        "key": "4",
                        "valueMap": [
                            { "key": "id", "valueString": "suggestion_0" },
                            { "key": "label", "valueString": "💡 Enhance IAM Controls" },
                            { "key": "type", "valueString": "suggestion" }
                        ]
                    },
                    {
                        "key": "5",
                        "valueMap": [
                            { "key": "id", "valueString": "suggestion_1" },
                            { "key": "label", "valueString": "💡 Encrypt Financial Data" },
                            { "key": "type", "valueString": "suggestion" }
                        ]
                    },
                    {
                        "key": "6",
                        "valueMap": [
                            { "key": "source", "valueString": "incident" },
                            { "key": "target", "valueString": "risk_score" },
                            { "key": "label", "valueString": "assessed at" }
                        ]
                    },
                    {
                        "key": "7",
                        "valueMap": [
                            { "key": "source", "valueString": "risk_score" },
                            { "key": "target", "valueString": "red_alert_0" },
                            { "key": "label", "valueString": "high risk" }
                        ]
                    },
                    {
                        "key": "8",
                        "valueMap": [
                            { "key": "source", "valueString": "risk_score" },
                            { "key": "target", "valueString": "red_alert_1" },
                            { "key": "label", "valueString": "high risk" }
                        ]
                    },
                    {
                        "key": "9",
                        "valueMap": [
                            { "key": "source", "valueString": "incident" },
                            { "key": "target", "valueString": "suggestion_0" },
                            { "key": "label", "valueString": "recommended" }
                        ]
                    },
                    {
                        "key": "10",
                        "valueMap": [
                            { "key": "source", "valueString": "incident" },
                            { "key": "target", "valueString": "suggestion_1" },
                            { "key": "label", "valueString": "recommended" }
                        ]
                    }
                ]
            }
        ]
    }
}
```

### Request 3: User clicks "Discard Article"

```json
{
    "threadId": "ae715e25-3e46-4f6d-af23-d9dab8e0f557",
    "action": {
        "name": "cancel_workflow"
    }
}
```

### Response 3: Workflow cancelled (same as current behavior)

```json
{
    "surfaceUpdate": {
        "components": [
            {
                "id": "root",
                "component": {
                    "Column": {
                        "children": {
                            "explicitList": ["cancelled_card"]
                        }
                    }
                }
            },
            {
                "id": "cancelled_card",
                "component": {
                    "Card": { "child": "cancelled_content" }
                }
            },
            {
                "id": "cancelled_content",
                "component": {
                    "Column": {
                        "children": {
                            "explicitList": ["cancelled_title", "cancelled_msg"]
                        }
                    }
                }
            },
            {
                "id": "cancelled_title",
                "component": {
                    "Text": {
                        "text": { "literalString": "❌ Workflow Cancelled" },
                        "usageHint": "h2"
                    }
                }
            },
            {
                "id": "cancelled_msg",
                "component": {
                    "Text": {
                        "text": { "literalString": "The article was discarded by the user." }
                    }
                }
            }
        ]
    }
}
```

---

# 4. Frontend Changes

## 4.1 Install Cytoscape.js

```bash
cd client-next
npm install cytoscape
```

## 4.2 New Component: `KnowledgeGraph.tsx`

```tsx
// components/KnowledgeGraph.tsx
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

interface GraphItem {
  id?: string;
  label?: string;
  type?: string;
  details?: string;
  source?: string;
  target?: string;
}

interface KnowledgeGraphProps {
  items: GraphItem[];
  layout?: string;
  onNodeClick?: (nodeData: any) => void;
}

// Color mapping for node types
const NODE_COLORS: Record<string, string> = {
  fake:         '#ef4444',  // Red
  real:         '#22c55e',  // Green
  agent:        '#3b82f6',  // Blue
  source:       '#8b5cf6',  // Purple
  incident:     '#f97316',  // Orange
  risk:         '#ef4444',  // Red
  red_alert:    '#ef4444',  // Red
  yellow_alert: '#eab308',  // Yellow
  suggestion:   '#22c55e',  // Green
  similar:      '#06b6d4',  // Cyan
  default:      '#6b7280',  // Gray
};

export default function KnowledgeGraph({
  items,
  layout = 'cose',
  onNodeClick,
}: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !items.length) return;

    // Separate nodes and edges
    const nodes = items
      .filter((item) => item.id && !item.source)
      .map((item) => ({
        data: {
          id: item.id,
          label: item.label || item.id,
          type: item.type || 'default',
          details: item.details || '',
        },
      }));

    const edges = items
      .filter((item) => item.source && item.target)
      .map((item, i) => ({
        data: {
          id: `edge_${i}`,
          source: item.source,
          target: item.target,
          label: item.label || '',
        },
      }));

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-wrap': 'wrap',
            'text-max-width': '120px',
            'font-size': '11px',
            'color': '#ffffff',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': (ele: any) =>
              NODE_COLORS[ele.data('type')] || NODE_COLORS.default,
            'width': 60,
            'height': 60,
            'border-width': 2,
            'border-color': '#ffffff22',
          },
        },
        {
          selector: 'edge',
          style: {
            'label': 'data(label)',
            'font-size': '9px',
            'color': '#94a3b8',
            'text-rotation': 'autorotate',
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'width': 2,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#60a5fa',
            'background-color': '#2563eb',
          },
        },
      ],
      layout: { name: layout },
      minZoom: 0.3,
      maxZoom: 3,
    });

    // Click handler
    cy.on('tap', 'node', (evt: any) => {
      const data = evt.target.data();
      if (onNodeClick) onNodeClick(data);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [items, layout]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '400px',
        background: '#0f172a',
        borderRadius: '12px',
        border: '1px solid #1e293b',
      }}
    />
  );
}
```

## 4.3 Using the Component in the Chat

```tsx
// Inside your AG-UI response renderer:

import KnowledgeGraph from './KnowledgeGraph';

// When you detect a KnowledgeGraph component in the A2UI response:
if (component.KnowledgeGraph) {
  const graphData = dataModel[component.KnowledgeGraph.data.path];
  
  // Convert A2UI valueArray format to simple array
  const items = Object.values(graphData).map((item: any) => {
    const obj: any = {};
    if (item.valueMap) {
      item.valueMap.forEach((kv: any) => {
        obj[kv.key] = kv.valueString || kv.valueNumber;
      });
    }
    return obj;
  });
  
  return (
    <KnowledgeGraph
      items={items}
      layout={component.KnowledgeGraph.layout}
      onNodeClick={(data) => {
        // Show detail panel or send userAction
        setSelectedNode(data);
      }}
    />
  );
}
```

---

# 5. Node Click → Detail Panel

When a user clicks a node, show a slide-in detail panel:

```tsx
// DetailPanel.tsx
interface DetailPanelProps {
  node: { id: string; label: string; type: string; details: string } | null;
  onClose: () => void;
}

export default function DetailPanel({ node, onClose }: DetailPanelProps) {
  if (!node) return null;

  return (
    <div style={{
      position: 'absolute',
      right: 0, top: 0,
      width: '300px', height: '100%',
      background: 'rgba(15, 23, 42, 0.95)',
      borderLeft: '1px solid #1e293b',
      padding: '20px',
      backdropFilter: 'blur(10px)',
    }}>
      <button onClick={onClose} style={{ float: 'right' }}>✕</button>
      <h3>{node.label}</h3>
      <p style={{ color: '#94a3b8' }}>Type: {node.type}</p>
      <p>{node.details}</p>
      
      {/* If the node is a source, show clickable link */}
      {node.type === 'source' && (
        <a href={node.details} target="_blank" rel="noreferrer"
           style={{ color: '#60a5fa' }}>
          Open Source →
        </a>
      )}
    </div>
  );
}
```

---

# 6. Files to Change — Summary

| # | File | Action | What Changes |
|---|---|---|---|
| 1 | `agent/knowledge_graph_builder.py` | **NEW** | Builds graph data (nodes + edges) from agent results |
| 2 | `agent/views.py` | **MODIFY** | Add `render_knowledge_graph()` function |
| 3 | `agent/agui_endpoint.py` | **MODIFY** | Call graph builder after agents return, include graph in A2UI |
| 4 | `client-next/components/KnowledgeGraph.tsx` | **NEW** | Cytoscape.js React component |
| 5 | `client-next/components/DetailPanel.tsx` | **NEW** | Slide-in panel for node details |
| 6 | `client-next/` (AG-UI renderer) | **MODIFY** | Handle `KnowledgeGraph` component type in A2UI response |
| 7 | `package.json` | **MODIFY** | Add `cytoscape` dependency |

---

# 7. Estimated Timeline

| Task | Time |
|---|---|
| Backend: `knowledge_graph_builder.py` | 1 day |
| Backend: Update `views.py` + `agui_endpoint.py` | 1 day |
| Frontend: `KnowledgeGraph.tsx` with Cytoscape.js | 2 days |
| Frontend: `DetailPanel.tsx` + integration | 1 day |
| Testing + polish | 1–2 days |
| **Total** | **5–7 days** |

---

# 8. Data Flow Summary

```
USER types query
    │
    ▼
Backend: DPOrchestrator receives query
    │
    ├── NewsVerificationAgent → { verdict, confidence, reason, sources }
    ├── TavilyVerificationAgent → { verdict, confidence, reason, sources }
    │
    ▼
Backend: knowledge_graph_builder.build_fake_news_graph()
    │
    ├── Creates nodes: [claim, newsverify, tavilyverify, sources..., verdict]
    ├── Creates edges: [claim→newsverify, claim→tavily, agents→sources, agents→verdict]
    │
    ▼
Backend: views.render_knowledge_graph()
    │
    ├── Builds A2UI surfaceUpdate with KnowledgeGraph component
    ├── Builds A2UI dataModelUpdate with graph nodes + edges
    │
    ▼
Frontend: AG-UI protocol delivers StateSnapshot
    │
    ├── Chat renders text message (existing behavior)
    ├── KnowledgeGraph.tsx renders Cytoscape.js graph (NEW)
    ├── Buttons render below graph (existing behavior)
    │
    ▼
USER clicks a node
    │
    ├── DetailPanel.tsx shows node info (client-side, instant)
    │   OR
    ├── userAction sent to backend → agent expands graph → new dataModelUpdate
    │
    ▼
USER clicks "Proceed Anyway"
    │
    ▼
Backend: Runs remaining agents (NLP, Risk, Similar, Alert, Suggest)
    │
    ▼
Backend: knowledge_graph_builder.build_risk_report_graph()
    │
    ├── Creates nodes: [incident, risk_score, red_alerts, suggestions, similar]
    │
    ▼
Frontend: Graph EXPANDS with new nodes (animated by Cytoscape.js)
```
