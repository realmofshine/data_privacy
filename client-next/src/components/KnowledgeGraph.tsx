"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import cytoscape, { Core } from "cytoscape";

/* ─── Types ──────────────────────────────────────────────────────── */

interface GraphNode {
    id: string;
    label: string;
    type: string;
    details?: string;
    confidence?: number;
}

interface GraphEdge {
    source: string;
    target: string;
    label?: string;
}

interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

interface Props {
    graphData: string; // JSON string of GraphData
    layout?: string;
}

/* ─── Color mapping ──────────────────────────────────────────────── */

const COLORS: Record<string, { bg: string; border: string }> = {
    fake: { bg: "#ef4444", border: "#fca5a5" },
    real: { bg: "#22c55e", border: "#86efac" },
    agent: { bg: "#3b82f6", border: "#93c5fd" },
    source: { bg: "#8b5cf6", border: "#c4b5fd" },
    incident: { bg: "#f97316", border: "#fdba74" },
    risk: { bg: "#ef4444", border: "#fca5a5" },
    red_alert: { bg: "#dc2626", border: "#f87171" },
    yellow_alert: { bg: "#eab308", border: "#fde047" },
    suggestion: { bg: "#059669", border: "#6ee7b7" },
    similar: { bg: "#0891b2", border: "#67e8f9" },
    default: { bg: "#6b7280", border: "#9ca3af" },
};

/* ─── Component ──────────────────────────────────────────────────── */

export default function KnowledgeGraph({ graphData, layout = "cose" }: Props) {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<Core | null>(null);
    const [selected, setSelected] = useState<GraphNode | null>(null);

    const handleClose = useCallback(() => setSelected(null), []);

    useEffect(() => {
        if (!containerRef.current) return;

        let parsed: GraphData;
        try {
            parsed = JSON.parse(graphData);
        } catch {
            return;
        }

        if (!parsed.nodes?.length) return;

        // Build elements
        const elements: cytoscape.ElementDefinition[] = [
            ...parsed.nodes.map((n) => ({
                data: {
                    id: n.id,
                    label: n.label,
                    nodeType: n.type,
                    details: n.details || "",
                    confidence: n.confidence,
                },
            })),
            ...parsed.edges.map((e, i) => ({
                data: {
                    id: `e${i}`,
                    source: e.source,
                    target: e.target,
                    label: e.label || "",
                },
            })),
        ];

        const cy = cytoscape({
            container: containerRef.current,
            elements,
            style: [
                {
                    selector: "node",
                    style: {
                        label: "data(label)",
                        "text-wrap": "wrap",
                        "text-max-width": "110px",
                        "font-size": "11px",
                        color: "#ffffff",
                        "text-valign": "center",
                        "text-halign": "center",
                        "background-color": (ele) => {
                            const t = ele.data("nodeType") as string;
                            return (COLORS[t] || COLORS.default).bg;
                        },
                        width: 65,
                        height: 65,
                        "border-width": 3,
                        "border-color": (ele) => {
                            const t = ele.data("nodeType") as string;
                            return (COLORS[t] || COLORS.default).border;
                        },
                        "text-outline-width": 2,
                        "text-outline-color": "#0f172a",
                    } as cytoscape.Css.Node,
                },
                {
                    selector: "edge",
                    style: {
                        label: "data(label)",
                        "font-size": "9px",
                        color: "#94a3b8",
                        "text-rotation": "autorotate",
                        "text-outline-width": 1,
                        "text-outline-color": "#0f172a",
                        "curve-style": "bezier",
                        "target-arrow-shape": "triangle",
                        "line-color": "#475569",
                        "target-arrow-color": "#475569",
                        width: 2,
                    } as cytoscape.Css.Edge,
                },
                {
                    selector: "node:selected",
                    style: {
                        "border-width": 5,
                        "border-color": "#60a5fa",
                        "background-color": "#1d4ed8",
                    } as cytoscape.Css.Node,
                },
            ],
            layout: {
                name: layout,
                padding: 40,
                nodeDimensionsIncludeLabels: true,
                animate: true,
                animationDuration: 600,
            } as cytoscape.LayoutOptions,
            minZoom: 0.3,
            maxZoom: 3,
        });

        // Node click → detail panel
        cy.on("tap", "node", (evt) => {
            const d = evt.target.data();
            setSelected({
                id: d.id,
                label: d.label,
                type: d.nodeType,
                details: d.details,
                confidence: d.confidence,
            });
        });

        // Click background → close
        cy.on("tap", (evt) => {
            if (evt.target === cy) setSelected(null);
        });

        cyRef.current = cy;

        return () => {
            cy.destroy();
        };
    }, [graphData, layout]);

    return (
        <div className="kg-wrapper">
            <div ref={containerRef} className="kg-canvas" />

            {/* Legend */}
            <div className="kg-legend">
                {[
                    { color: "#ef4444", label: "Fake/Risk" },
                    { color: "#22c55e", label: "Real/Suggestion" },
                    { color: "#3b82f6", label: "Agent" },
                    { color: "#8b5cf6", label: "Source" },
                    { color: "#f97316", label: "Incident" },
                    { color: "#eab308", label: "Warning" },
                ].map((item) => (
                    <span key={item.label} className="kg-legend-item">
                        <span
                            className="kg-legend-dot"
                            style={{ background: item.color }}
                        />
                        {item.label}
                    </span>
                ))}
            </div>

            {/* Detail Panel */}
            {selected && (
                <div className="kg-detail-panel">
                    <button className="kg-detail-close" onClick={handleClose}>
                        ✕
                    </button>
                    <div
                        className="kg-detail-type"
                        style={{
                            background: (COLORS[selected.type] || COLORS.default).bg,
                        }}
                    >
                        {selected.type.replace("_", " ").toUpperCase()}
                    </div>
                    <h4 className="kg-detail-title">{selected.label}</h4>
                    {selected.confidence !== undefined && (
                        <div className="kg-detail-confidence">
                            Confidence: {(selected.confidence * 100).toFixed(0)}%
                        </div>
                    )}
                    {selected.details && (
                        <p className="kg-detail-text">{selected.details}</p>
                    )}
                    {selected.type === "source" && selected.details?.startsWith("http") && (
                        <a
                            href={selected.details}
                            target="_blank"
                            rel="noreferrer"
                            className="kg-detail-link"
                        >
                            Open Source →
                        </a>
                    )}
                </div>
            )}
        </div>
    );
}
