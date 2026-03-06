"use client";

import { useState } from "react";
import { getModeSections } from "@/lib/modes";
import type { ModeConfig } from "@/lib/modes";

interface Props {
    activeMode: string;
    onSelectMode: (modeId: string) => void;
}

export default function Sidebar({ activeMode, onSelectMode }: Props) {
    const sections = getModeSections();
    const [open, setOpen] = useState(false);

    const handleSelect = (modeId: string) => {
        onSelectMode(modeId);
        setOpen(false); // close sidebar on mobile after selection
    };

    return (
        <>
            {/* Mobile hamburger button */}
            <button
                className="mobile-menu-btn"
                onClick={() => setOpen(!open)}
                aria-label="Toggle menu"
            >
                {open ? "✕" : "☰"}
            </button>

            {/* Overlay for mobile */}
            {open && (
                <div className="sidebar-overlay" onClick={() => setOpen(false)} />
            )}

            <aside className={`sidebar ${open ? "open" : ""}`}>
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
                                onClick={() => handleSelect(mode.id)}
                            >
                                <span className="icon">{mode.icon}</span>
                                <span>{mode.label}</span>
                            </div>
                        ))}
                    </div>
                ))}
            </aside>
        </>
    );
}
