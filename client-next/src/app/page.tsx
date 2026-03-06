"use client";

import { useState, useRef, useEffect, useCallback, FormEvent } from "react";
import Sidebar from "@/components/Sidebar";
import A2UIRenderer from "@/components/A2UIRenderer";
import { useAGUI } from "@/hooks/useAGUI";
import { getModeById } from "@/lib/modes";

export default function Home() {
  const [activeMode, setActiveMode] = useState("breach_analysis");
  const [threadId] = useState(() => `thread-${Date.now()}`);
  const [inputValue, setInputValue] = useState("");
  const chatRef = useRef<HTMLDivElement>(null);

  const { messages, isRunning, agentStatuses, sendMessage, clearMessages } =
    useAGUI({ endpoint: "/api/ag-ui" });

  const mode = getModeById(activeMode);

  // Auto-scroll
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      const text = inputValue.trim();
      if (!text || isRunning) return;
      setInputValue("");
      sendMessage(text, activeMode, threadId);
    },
    [inputValue, isRunning, activeMode, threadId, sendMessage]
  );

  const handleSample = useCallback(
    (query: string) => {
      if (isRunning) return;
      setInputValue("");
      sendMessage(query, activeMode, threadId);
    },
    [isRunning, activeMode, threadId, sendMessage]
  );

  const handleAction = useCallback(
    (actionName: string) => {
      const lastA2UI = [...messages].reverse().find((m) => m.a2ui);
      const prevQuery = lastA2UI?.previousQuery || "";
      sendMessage(prevQuery, activeMode, threadId, {
        name: actionName,
        previousQuery: prevQuery,
      });
    },
    [messages, activeMode, threadId, sendMessage]
  );

  const handleModeChange = useCallback(
    (modeId: string) => {
      setActiveMode(modeId);
      clearMessages();
    },
    [clearMessages]
  );

  return (
    <div className="app-layout">
      <Sidebar activeMode={activeMode} onSelectMode={handleModeChange} />

      <main className="main-area">
        {/* Header */}
        <div className="mode-header">
          <h2>
            {mode?.icon} {mode?.label}
          </h2>
          <div className="mode-desc">{mode?.description}</div>

          {/* Agent badges */}
          {mode && (
            <div className="agent-badges">
              {mode.agents.map((agent) => {
                const status = agentStatuses.find(
                  (a) => a.name === agent
                );
                return (
                  <span
                    key={agent}
                    className={`agent-badge ${status?.status || "pending"}`}
                  >
                    {status?.status === "done"
                      ? "✅"
                      : status?.status === "running"
                        ? "⏳"
                        : status?.status === "error"
                          ? "❌"
                          : "○"}{" "}
                    {agent}
                  </span>
                );
              })}
            </div>
          )}
        </div>

        {/* Chat Area */}
        <div className="chat-area" ref={chatRef}>
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="icon">{mode?.icon}</div>
              <h3>{mode?.label}</h3>
              <p>{mode?.description}</p>
              <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Try one of the sample queries below, or type your own.
              </p>
            </div>
          ) : (
            messages.map((msg) => {
              if (msg.role === "step") {
                return (
                  <div key={msg.id} className="step-indicator">
                    <div className="spinner" />
                    {msg.content}
                  </div>
                );
              }

              if (msg.a2ui) {
                return (
                  <A2UIRenderer
                    key={msg.id}
                    data={msg.a2ui as Record<string, unknown> & { surfaceUpdate?: { components?: Array<{ id: string }> }; beginRendering?: { root?: string } }}
                    onAction={handleAction}
                  />
                );
              }

              return (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div
                    className="message-content"
                    dangerouslySetInnerHTML={{
                      __html: msg.content
                        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                        .replace(/\n/g, "<br />"),
                    }}
                  />
                </div>
              );
            })
          )}

          {isRunning && messages.length > 0 && (
            <div className="loading-dots">
              <span />
              <span />
              <span />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-area">
          <form className="input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="input-field"
              placeholder={mode?.placeholder || "Type a message..."}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isRunning}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isRunning || !inputValue.trim()}
            >
              {isRunning ? "⏳" : "🚀"} {isRunning ? "Running..." : "Analyze"}
            </button>
          </form>

          {/* Sample queries */}
          {mode && messages.length === 0 && (
            <div className="sample-queries">
              {mode.samples.map((sample, i) => (
                <button
                  key={i}
                  className="sample-chip"
                  onClick={() => handleSample(sample)}
                >
                  {sample.length > 60 ? sample.slice(0, 60) + "..." : sample}
                </button>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
