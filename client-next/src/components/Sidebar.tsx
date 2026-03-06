"use client";

import { getModeSections } from "@/lib/modes";
import type { ModeConfig } from "@/lib/modes";

interface Props {
    activeMode: string;
    onSelectMode: (modeId: string) => void;
}

export default function Sidebar({ activeMode, onSelectMode }: Props) {
    const sections = getModeSections();

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <span className="shield">🛡️</span>
                <span className="title">Data Privacy<br />Intelligence</span>
            </div>

            {sections.map(({ section, modes }) => (
                <div key={section}>
                    <div className="sidebar-section">{section}</div>
                    {modes.map((mode: ModeConfig) => (
                        <div
                            key={mode.id}
                            className={`sidebar-item ${activeMode === mode.id ? "active" : ""}`}
                            onClick={() => onSelectMode(mode.id)}
                        >
                            <span className="icon">{mode.icon}</span>
                            <span>{mode.label}</span>
                        </div>
                    ))}
                </div>
            ))}
        </aside>
    );
}
