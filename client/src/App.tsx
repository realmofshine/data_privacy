import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'

// ─── Types ───────────────────────────────────────────────────────────
interface A2UIComponent {
    id: string
    component: Record<string, any>
}

interface A2UIData {
    beginRendering?: { surfaceId: string; root: string }
    surfaceUpdate?: { surfaceId: string; components: A2UIComponent[] }
}

interface ToolCall {
    name: string
    status: 'running' | 'done'
}

interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
    a2ui?: A2UIData | null
    toolCalls?: ToolCall[]
    previousQuery?: string
}

const API_URL = 'http://localhost:8002'
const THREAD_ID = crypto.randomUUID()

const SAMPLE_QUERIES = [
    "TechCorp suffered a ransomware attack in March 2025, compromising 500,000 customer records including PII data and payment information. The attacker exploited an unpatched vulnerability in their CRM system.",
    "HealthNet Inc. reported a data breach where an external supply chain partner's compromised system allowed unauthorized access to 1.2 million patient health records.",
    "There was a massive alien invasion reported yesterday by unnamed sources.",
]

export default function App() {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [currentStep, setCurrentStep] = useState('')
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const sendMessage = useCallback(async (
        messageText?: string,
        action?: { name: string },
        previousQuery?: string,
    ) => {
        const text = messageText ?? input
        if ((!text.trim() && !action) || isLoading) return

        if (!action) {
            const userMsg: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'user',
                content: text,
            }
            setMessages(prev => [...prev, userMsg])
            setInput('')
        }

        setIsLoading(true)
        setCurrentStep('Connecting to agent...')

        const assistantMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: '',
            toolCalls: [],
        }
        setMessages(prev => [...prev, assistantMsg])

        try {
            const body: Record<string, any> = {
                threadId: THREAD_ID,
                messages: [{ role: 'user', content: text }],
            }
            if (action) {
                body.action = action
                body.previous_query = previousQuery || text
                body.message = previousQuery || text
            }

            const response = await fetch(`${API_URL}/ag-ui`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })

            const reader = response.body?.getReader()
            const decoder = new TextDecoder()
            let buffer = ''

            if (!reader) throw new Error('No response body')

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6))
                            handleEvent(event, assistantMsg.id, text)
                        } catch { }
                    }
                }
            }
        } catch (err) {
            console.error('AG-UI error:', err)
            setMessages(prev =>
                prev.map(m =>
                    m.id === assistantMsg.id
                        ? { ...m, content: '❌ Error connecting to agent. Make sure the backend is running on port 8002.' }
                        : m
                )
            )
        } finally {
            setIsLoading(false)
            setCurrentStep('')
        }
    }, [input, isLoading])

    const handleEvent = (event: any, msgId: string, userQuery: string) => {
        switch (event.type) {
            case 'RUN_STARTED':
                setCurrentStep('🚀 Agent pipeline started...')
                break

            case 'STEP_STARTED':
                setCurrentStep(`⚙️ ${formatStepName(event.stepName)}...`)
                break

            case 'STEP_FINISHED':
                setCurrentStep(`✅ ${formatStepName(event.stepName)} complete`)
                break

            case 'TOOL_CALL_START':
                setCurrentStep(`🔧 Calling ${event.toolCallName}...`)
                setMessages(prev => prev.map(m =>
                    m.id === msgId
                        ? { ...m, toolCalls: [...(m.toolCalls || []), { name: event.toolCallName, status: 'running' as const }] }
                        : m
                ))
                break

            case 'TOOL_CALL_END':
                setMessages(prev => prev.map(m =>
                    m.id === msgId
                        ? { ...m, toolCalls: m.toolCalls?.map(tc => tc.status === 'running' ? { ...tc, status: 'done' as const } : tc) }
                        : m
                ))
                break

            case 'TEXT_MESSAGE_CONTENT':
                setMessages(prev => prev.map(m =>
                    m.id === msgId ? { ...m, content: m.content + event.delta } : m
                ))
                break

            case 'STATE_SNAPSHOT':
                if (event.snapshot?.a2ui) {
                    setMessages(prev => prev.map(m =>
                        m.id === msgId
                            ? { ...m, a2ui: event.snapshot.a2ui, previousQuery: event.snapshot.previousQuery || userQuery }
                            : m
                    ))
                }
                break

            case 'RUN_FINISHED':
                setCurrentStep('✅ Analysis complete')
                break

            case 'RUN_ERROR':
                setCurrentStep(`❌ ${event.message}`)
                break
        }
    }

    const handleA2UIAction = (actionName: string, _context: Record<string, string>, previousQuery: string) => {
        sendMessage('', { name: actionName }, previousQuery)
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <div className="header-icon">🛡️</div>
                    <div>
                        <h1>Data Privacy Intelligence</h1>
                        <p className="header-subtitle">AG-UI + A2UI · 7 Specialized Agents · Real-time Streaming</p>
                    </div>
                </div>
                <div className="agent-badges">
                    {['News Verify', 'Tavily', 'NLP', 'Risk', 'Similar', 'Alert', 'Suggest'].map(a => (
                        <span key={a} className="agent-badge">{a}</span>
                    ))}
                </div>
            </header>

            {/* Chat area */}
            <main className="chat-area">
                {messages.length === 0 && (
                    <div className="empty-state">
                        <div className="empty-icon">🔍</div>
                        <h2>Paste a data breach news article to analyze</h2>
                        <p>The system will verify if it's real, extract entities, calculate risk scores, and generate alerts.</p>
                        <div className="sample-queries">
                            <p className="samples-label">Try a sample:</p>
                            {SAMPLE_QUERIES.map((q, i) => (
                                <button key={i} className="sample-btn" onClick={() => setInput(q)}>
                                    {q.slice(0, 80)}...
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                        <div className="message-avatar">
                            {msg.role === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-body">
                            {/* Tool calls (AG-UI) */}
                            {msg.toolCalls && msg.toolCalls.length > 0 && (
                                <div className="tool-calls">
                                    {msg.toolCalls.map((tc, i) => (
                                        <div key={i} className={`tool-call ${tc.status}`}>
                                            <span>{tc.status === 'running' ? '⏳' : '✅'}</span>
                                            <code>{tc.name}()</code>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Text content */}
                            {msg.content && (
                                <div className="message-text">
                                    <MarkdownText text={msg.content} />
                                </div>
                            )}

                            {/* A2UI card */}
                            {msg.a2ui && (
                                <div className="a2ui-surface">
                                    <A2UIRenderer
                                        data={msg.a2ui}
                                        previousQuery={msg.previousQuery || ''}
                                        onAction={handleA2UIAction}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="loading-indicator">
                        <div className="loading-dots">
                            <span /><span /><span />
                        </div>
                        <span className="loading-text">{currentStep}</span>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </main>

            {/* Input area */}
            <footer className="chat-input-area">
                <textarea
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            sendMessage()
                        }
                    }}
                    placeholder="Paste a news article about a data breach... (Enter to send, Shift+Enter for new line)"
                    disabled={isLoading}
                    rows={3}
                />
                <button
                    className="send-btn"
                    onClick={() => sendMessage()}
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? '⏳' : '🚀 Analyze'}
                </button>
            </footer>
        </div>
    )
}


// ─── Simple Markdown Renderer ─────────────────────────────────────────
function MarkdownText({ text }: { text: string }) {
    const lines = text.split('\n')
    return (
        <div className="markdown">
            {lines.map((line, i) => {
                if (!line.trim()) return <br key={i} />
                if (line.startsWith('## ')) return <h2 key={i}>{line.slice(3)}</h2>
                if (line.startsWith('# ')) return <h1 key={i}>{line.slice(2)}</h1>
                if (line.startsWith('### ')) return <h3 key={i}>{line.slice(4)}</h3>
                if (line.startsWith('- ') || line.startsWith('* ')) return <li key={i}>{formatInline(line.slice(2))}</li>
                if (/^\d+\. /.test(line)) return <li key={i}>{formatInline(line.replace(/^\d+\. /, ''))}</li>
                return <p key={i}>{formatInline(line)}</p>
            })}
        </div>
    )
}

function formatInline(text: string): React.ReactNode {
    const parts = text.split(/(\*\*[^*]+\*\*)/g)
    return parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
            ? <strong key={i}>{part.slice(2, -2)}</strong>
            : part
    )
}


// ─── A2UI Renderer ────────────────────────────────────────────────────

interface A2UIRendererProps {
    data: A2UIData
    previousQuery: string
    onAction: (name: string, context: Record<string, string>, previousQuery: string) => void
}

function A2UIRenderer({ data, previousQuery, onAction }: A2UIRendererProps) {
    const components = data.surfaceUpdate?.components || []
    const rootId = data.beginRendering?.root || 'root'
    const compMap = new Map<string, A2UIComponent>(components.map(c => [c.id, c]))

    return (
        <div className="a2ui-root">
            {renderComp(rootId, compMap, previousQuery, onAction)}
        </div>
    )
}

function renderComp(
    id: string,
    map: Map<string, A2UIComponent>,
    previousQuery: string,
    onAction: (name: string, context: Record<string, string>, previousQuery: string) => void
): React.ReactNode {
    const comp = map.get(id)
    if (!comp) return null
    const details = comp.component

    if (details.Text) {
        const text = details.Text.text?.literalString || ''
        const hint = details.Text.usageHint || 'body'
        const cls = `a2ui-text a2ui-${hint}`
        return <span key={id} className={cls}>{text}</span>
    }

    if (details.Column) {
        const children = details.Column.children?.explicitList || []
        return (
            <div key={id} className="a2ui-col">
                {children.map((cid: string) => renderComp(cid, map, previousQuery, onAction))}
            </div>
        )
    }

    if (details.Row) {
        const children = details.Row.children?.explicitList || []
        return (
            <div key={id} className="a2ui-row">
                {children.map((cid: string) => renderComp(cid, map, previousQuery, onAction))}
            </div>
        )
    }

    if (details.Card) {
        const childId = details.Card.child
        return (
            <div key={id} className="a2ui-card">
                {renderComp(childId, map, previousQuery, onAction)}
            </div>
        )
    }

    if (details.Divider) {
        return <hr key={id} className="a2ui-divider" />
    }

    if (details.Button) {
        const action = details.Button.action || {}
        const actionName = action.name || ''
        const context: Record<string, string> = {}
        for (const ctx of action.context || []) {
            context[ctx.key] = ctx.value?.literalString || ''
        }
        const labelId = details.Button.child
        const labelComp = map.get(labelId)
        const label = labelComp?.component?.Text?.text?.literalString || actionName

        const isProceeed = actionName === 'force_proceed'
        const isDiscard = actionName === 'cancel_workflow' || actionName === 'discard_article'

        return (
            <button
                key={id}
                id={id}
                className={`a2ui-btn ${isProceeed ? 'a2ui-btn-proceed' : isDiscard ? 'a2ui-btn-discard' : 'a2ui-btn-default'}`}
                onClick={() => onAction(actionName, context, previousQuery)}
            >
                {isProceeed ? '⚡ ' : isDiscard ? '🗑️ ' : ''}{label}
            </button>
        )
    }

    return null
}


// ─── Helpers ──────────────────────────────────────────────────────────

function formatStepName(name: string): string {
    const map: Record<string, string> = {
        dp_orchestrator: '🧠 Orchestrator',
        view_renderer: '🎨 Rendering UI',
    }
    return map[name] || name.replace(/_/g, ' ')
}
