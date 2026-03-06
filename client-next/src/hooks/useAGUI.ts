"use client";

import { useState, useCallback, useRef } from "react";

export interface AgentStatus {
    name: string;
    status: "pending" | "running" | "done" | "error";
}

export interface ChatMessage {
    id: string;
    role: "user" | "assistant" | "step";
    content: string;
    a2ui?: Record<string, unknown>;
    agentName?: string;
    previousQuery?: string;
}

interface UseAGUIOptions {
    endpoint?: string;
}

export function useAGUI({ endpoint = "/api/ag-ui" }: UseAGUIOptions = {}) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isRunning, setIsRunning] = useState(false);
    const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
    const abortRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(
        async (
            userMessage: string,
            mode: string,
            threadId: string,
            action?: { name: string; previousQuery?: string }
        ) => {
            // Add user message
            if (!action) {
                const userMsg: ChatMessage = {
                    id: `user-${Date.now()}`,
                    role: "user",
                    content: userMessage,
                };
                setMessages((prev) => [...prev, userMsg]);
            }

            setIsRunning(true);

            const body: Record<string, unknown> = {
                threadId,
                mode,
                messages: [{ role: "user", content: userMessage }],
            };

            if (action) {
                body.action = { name: action.name };
                body.previousQuery = action.previousQuery || userMessage;
                body.previous_query = action.previousQuery || userMessage;
                body.message = action.previousQuery || userMessage;
            }

            // Abort any existing stream
            abortRef.current?.abort();
            const controller = new AbortController();
            abortRef.current = controller;

            try {
                const res = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body),
                    signal: controller.signal,
                });

                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }

                const contentType = res.headers.get("content-type") || "";

                // Handle JSON responses (cancel actions)
                if (contentType.includes("application/json")) {
                    const data = await res.json();
                    if (data.a2ui) {
                        const msg: ChatMessage = {
                            id: `a2ui-${Date.now()}`,
                            role: "assistant",
                            content: "",
                            a2ui: data.a2ui,
                        };
                        setMessages((prev) => [...prev, msg]);
                    }
                    setIsRunning(false);
                    return;
                }

                // Handle SSE stream
                const reader = res.body?.getReader();
                if (!reader) throw new Error("No readable stream");

                const decoder = new TextDecoder();
                let buffer = "";
                let currentMsgId = "";
                let accText = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop() || "";

                    for (const line of lines) {
                        if (line.startsWith("event: ")) {
                            // event type is on this line, data on the next
                        } else if (line.startsWith("data: ")) {
                            const raw = line.slice(6);
                            try {
                                const evt = JSON.parse(raw);
                                handleEvent(evt);
                            } catch {
                                // skip malformed JSON
                            }
                        }
                    }
                }

                function handleEvent(evt: Record<string, unknown>) {
                    const type = evt.type as string;

                    switch (type) {
                        case "RUN_STARTED":
                            setAgentStatuses([]);
                            break;

                        case "STEP_STARTED": {
                            const stepName = (evt.step_name as string) || (evt.stepName as string) || "agent";
                            setAgentStatuses((prev) => {
                                const existing = prev.find((a) => a.name === stepName);
                                if (existing) {
                                    return prev.map((a) =>
                                        a.name === stepName ? { ...a, status: "running" } : a
                                    );
                                }
                                return [...prev, { name: stepName, status: "running" }];
                            });
                            break;
                        }

                        case "STEP_FINISHED": {
                            const stepName = (evt.step_name as string) || (evt.stepName as string) || "agent";
                            setAgentStatuses((prev) =>
                                prev.map((a) =>
                                    a.name === stepName ? { ...a, status: "done" } : a
                                )
                            );
                            break;
                        }

                        case "TEXT_MESSAGE_START":
                            currentMsgId = (evt.message_id as string) || (evt.messageId as string) || `msg-${Date.now()}`;
                            accText = "";
                            setMessages((prev) => [
                                ...prev,
                                { id: currentMsgId, role: "assistant", content: "" },
                            ]);
                            break;

                        case "TEXT_MESSAGE_CONTENT": {
                            const delta = (evt.delta as string) || (evt.content as string) || "";
                            accText += delta;
                            const mid = currentMsgId;
                            setMessages((prev) =>
                                prev.map((m) =>
                                    m.id === mid ? { ...m, content: accText } : m
                                )
                            );
                            break;
                        }

                        case "TEXT_MESSAGE_END":
                            break;

                        case "STATE_SNAPSHOT": {
                            const snapshot = evt.snapshot as Record<string, unknown>;
                            if (snapshot) {
                                const a2ui = snapshot.a2ui as Record<string, unknown>;
                                const agentName = snapshot.agentName as string;
                                const previousQuery = snapshot.previousQuery as string;
                                if (a2ui) {
                                    setMessages((prev) => [
                                        ...prev,
                                        {
                                            id: `a2ui-${Date.now()}`,
                                            role: "assistant",
                                            content: "",
                                            a2ui,
                                            agentName,
                                            previousQuery,
                                        },
                                    ]);
                                }
                            }
                            break;
                        }

                        case "RUN_FINISHED":
                            setIsRunning(false);
                            break;

                        case "RUN_ERROR": {
                            const errMsg = (evt.message as string) || "Unknown error";
                            setMessages((prev) => [
                                ...prev,
                                {
                                    id: `err-${Date.now()}`,
                                    role: "assistant",
                                    content: `❌ Error: ${errMsg}`,
                                },
                            ]);
                            setIsRunning(false);
                            break;
                        }
                    }
                }
            } catch (err: unknown) {
                if ((err as Error).name !== "AbortError") {
                    setMessages((prev) => [
                        ...prev,
                        {
                            id: `err-${Date.now()}`,
                            role: "assistant",
                            content: `❌ Connection error: ${(err as Error).message}`,
                        },
                    ]);
                }
            } finally {
                setIsRunning(false);
            }
        },
        [endpoint]
    );

    const clearMessages = useCallback(() => {
        setMessages([]);
        setAgentStatuses([]);
    }, []);

    return { messages, isRunning, agentStatuses, sendMessage, clearMessages };
}
