"use client";

import React from "react";
import dynamic from "next/dynamic";

const KnowledgeGraph = dynamic(() => import("./KnowledgeGraph"), {
    ssr: false,
    loading: () => (
        <div style={{ padding: 20, color: "#94a3b8", textAlign: "center" }}>
            Loading Knowledge Graph…
        </div>
    ),
});

interface A2UIComponent {
    id: string;
    component?: Record<string, Record<string, unknown>>;
    componentProperties?: Record<string, Record<string, unknown>>;
}

interface A2UIData {
    surfaceUpdate?: {
        components?: A2UIComponent[];
    };
    beginRendering?: {
        root?: string;
    };
}

interface Props {
    data: A2UIData;
    onAction?: (actionName: string, context?: Record<string, string>) => void;
}

export default function A2UIRenderer({ data, onAction }: Props) {
    const components = data?.surfaceUpdate?.components || [];
    const rootId = data?.beginRendering?.root || "root";

    function findComponent(id: string): A2UIComponent | undefined {
        return components.find((c) => c.id === id);
    }

    function getProps(comp: A2UIComponent): Record<string, unknown> {
        const propsObj = comp.component || comp.componentProperties || {};
        const type = Object.keys(propsObj)[0];
        return { type, ...(propsObj[type] || {}) };
    }

    function renderComponent(id: string): React.ReactNode {
        const comp = findComponent(id);
        if (!comp) return null;

        const props = getProps(comp);
        const type = props.type as string;

        switch (type) {
            case "Column": {
                const children = (props.children as { explicitList?: string[] })?.explicitList || [];
                return (
                    <div key={id} className="a2ui-column">
                        {children.map((childId: string) => renderComponent(childId))}
                    </div>
                );
            }

            case "Row": {
                const children = (props.children as { explicitList?: string[] })?.explicitList || [];
                return (
                    <div key={id} className="a2ui-row">
                        {children.map((childId: string) => renderComponent(childId))}
                    </div>
                );
            }

            case "Card": {
                const childId = props.child as string;
                // Determine card variant from children content
                let variant = "";
                const allText = components
                    .map((c) => {
                        const p = getProps(c);
                        if (p.type === "Text") {
                            const t = p.text as { literalString?: string } | string;
                            return typeof t === "string" ? t : t?.literalString || "";
                        }
                        return "";
                    })
                    .join(" ")
                    .toLowerCase();

                if (allText.includes("⚠️") || allText.includes("warning") || allText.includes("fake")) {
                    variant = "warning";
                } else if (allText.includes("❌") || allText.includes("error") || allText.includes("critical")) {
                    variant = "danger";
                } else if (allText.includes("✅") || allText.includes("success")) {
                    variant = "success";
                }

                return (
                    <div key={id} className={`a2ui-card ${variant}`}>
                        {renderComponent(childId)}
                    </div>
                );
            }

            case "Text": {
                const textVal = props.text as { literalString?: string } | string;
                const text = typeof textVal === "string" ? textVal : textVal?.literalString || "";
                const hint = (props.usageHint as string) || "body";

                if (hint === "h2" || hint === "h1") {
                    return <div key={id} className="a2ui-heading h2">{text}</div>;
                }
                if (hint === "h3") {
                    return <div key={id} className="a2ui-heading h3">{text}</div>;
                }
                if (hint === "caption") {
                    return <div key={id} className="a2ui-heading caption">{text}</div>;
                }
                return <div key={id} className="a2ui-text">{text}</div>;
            }

            case "Heading": {
                const text = (props.text as string) || "";
                return <div key={id} className="a2ui-heading h2">{text}</div>;
            }

            case "Button": {
                const action = props.action as { name?: string; context?: { key: string; value: { literalString?: string } }[] };
                const childId = props.child as string;
                const childComp = findComponent(childId);
                let label = "";
                if (childComp) {
                    const childProps = getProps(childComp);
                    const textVal = childProps.text as { literalString?: string } | string;
                    label = typeof textVal === "string" ? textVal : textVal?.literalString || "";
                }

                const actionName = action?.name || "";
                const contextMap: Record<string, string> = {};
                if (action?.context) {
                    for (const entry of action.context) {
                        contextMap[entry.key] = entry.value?.literalString || "";
                    }
                }

                const isPrimary = actionName.includes("proceed") || actionName.includes("accept");
                const isDanger = actionName.includes("cancel") || actionName.includes("discard") || actionName.includes("reject");

                return (
                    <button
                        key={id}
                        className={`a2ui-button ${isPrimary ? "primary" : ""} ${isDanger ? "danger" : ""}`}
                        onClick={() => onAction?.(actionName, contextMap)}
                    >
                        {label || actionName}
                    </button>
                );
            }

            case "Divider":
                return <div key={id} className="a2ui-divider" />;

            case "KnowledgeGraph": {
                const gd = props.graphData as string;
                const ly = (props.layout as string) || "cose";
                return (
                    <KnowledgeGraph key={id} graphData={gd} layout={ly} />
                );
            }

            default:
                return null;
        }
    }

    if (components.length === 0) return null;

    return <div className="a2ui-root">{renderComponent(rootId)}</div>;
}
