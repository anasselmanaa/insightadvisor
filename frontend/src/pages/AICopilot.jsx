import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Bot, Send, Loader, Zap, Target, Calendar, TrendingUp, ChevronDown, ChevronUp } from "lucide-react"
import api from "../api"
import toast from "react-hot-toast"

export default function AICopilot() {
  const datasetId = localStorage.getItem("dataset_id")
  const [recs, setRecs] = useState(null)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState("")
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem("ai_messages_" + datasetId)
    return saved ? JSON.parse(saved) : [
      { role: "assistant", text: "Hello! I am your AI business advisor. Ask me anything about your data — top products, customer segments, sales trends, anomalies, or any business question." }
    ]
  })
  const [queryLoading, setQueryLoading] = useState(false)
  const [showRecs, setShowRecs] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => { if (datasetId) loadAI() }, [datasetId])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])
  useEffect(() => {
    if (datasetId) localStorage.setItem("ai_messages_" + datasetId, JSON.stringify(messages))
  }, [messages])

  async function loadAI() {
    setLoading(true)
    try {
      const [recsRes, planRes] = await Promise.all([
        api.get("/ai/recommendations/" + datasetId),
        api.get("/ai/action-plan/" + datasetId)
      ])
      setRecs(recsRes.data.ai?.recommendations || recsRes.data.recommendations)
      setPlan(planRes.data.action_plan?.action_plan || planRes.data.action_plan)
    } catch (e) {
      toast.error("AI analysis failed")
    } finally {
      setLoading(false)
    }
  }

  async function runQuery() {
    if (!query.trim()) return
    const userMsg = query
    setMessages(prev => [...prev, { role: "user", text: userMsg }])
    setQuery("")
    setQueryLoading(true)
    try {
      const res = await api.post("/ai/query/" + datasetId, { query: userMsg })
      const answer = res.data.result?.summary || res.data.result || "I could not process that query."
      setMessages(prev => [...prev, { role: "assistant", text: answer }])
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", text: "Sorry, I could not process that right now. Try asking about top products, sales by country, or customer segments." }])
    } finally {
      setQueryLoading(false)
    }
  }

  const suggestions = [
    "What are my top selling products?",
    "Show me sales by country",
    "Who are my best customers?",
    "What is my revenue trend?",
    "What anomalies were detected?",
    "Give me a business summary",
  ]

  return (
    <div className="p-6 space-y-4 h-full flex flex-col">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">AI Copilot</h1>
        <p className="page-subtitle">Powered by LLM — ask anything about your business data</p>
      </motion.div>

      {/* Main Chat Interface */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="flex-1 flex flex-col glass rounded-2xl border border-white/5 overflow-hidden"
        style={{ minHeight: 420 }}>

        {/* Chat header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/5">
          <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center">
            <Bot size={16} className="text-indigo-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">InsightAdvisor AI</p>
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
              Online — powered by Llama 3.3 70B
            </p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4" style={{ maxHeight: 320 }}>
          {messages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className={"flex " + (msg.role === "user" ? "justify-end" : "justify-start")}>
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/20 flex items-center justify-center mr-2 flex-shrink-0 mt-0.5">
                  <Bot size={13} className="text-indigo-400" />
                </div>
              )}
              <div className={"max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed " + (
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-sm"
                  : "bg-white/5 border border-white/8 text-slate-200 rounded-tl-sm"
              )}>
                {msg.text}
              </div>
            </motion.div>
          ))}
          {queryLoading && (
            <div className="flex justify-start">
              <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/20 flex items-center justify-center mr-2 flex-shrink-0">
                <Bot size={13} className="text-indigo-400" />
              </div>
              <div className="bg-white/5 border border-white/8 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        <div className="px-5 pb-3 flex gap-2 flex-wrap">
          {suggestions.map(s => (
            <button key={s} onClick={() => setQuery(s)}
              className="px-3 py-1.5 glass text-slate-400 hover:text-white text-xs rounded-lg transition-all border border-white/5 hover:border-indigo-500/30">
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="px-4 pb-4">
          <div className="flex gap-2 items-center bg-white/3 border border-white/8 rounded-xl px-4 py-2 focus-within:border-indigo-500/40 transition-all">
            <input
              type="text" value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !queryLoading && runQuery()}
              placeholder="Ask anything about your business data..."
              className="flex-1 bg-transparent text-slate-200 text-sm outline-none placeholder-slate-600"
            />
            <button onClick={runQuery} disabled={queryLoading || !query.trim()}
              className="w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 flex items-center justify-center transition-all flex-shrink-0">
              {queryLoading ? <Loader size={14} className="text-white animate-spin" /> : <Send size={14} className="text-white" />}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Collapsible Recommendations */}
      {recs && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <button onClick={() => setShowRecs(!showRecs)}
            className="w-full flex items-center justify-between px-5 py-3 glass rounded-xl border border-white/5 hover:border-indigo-500/30 transition-all">
            <div className="flex items-center gap-3">
              <Zap size={16} className="text-indigo-400" />
              <span className="text-sm font-semibold text-slate-300">AI Recommendations & Action Plan</span>
              {loading && <Loader size={12} className="text-indigo-400 animate-spin" />}
            </div>
            {showRecs ? <ChevronUp size={16} className="text-slate-500" /> : <ChevronDown size={16} className="text-slate-500" />}
          </button>

          {showRecs && !loading && recs && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mt-3 space-y-3">
              {recs.overall_health && (
                <div className="glass rounded-xl p-4 border border-indigo-500/20 flex items-center gap-3">
                  <Bot size={18} className="text-indigo-400 flex-shrink-0" />
                  <p className="text-slate-200 text-sm">{recs.overall_health}</p>
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {[
                  { key: "priority_1", label: "TODAY",      color: "text-red-400",     bg: "border-red-500/20 bg-red-500/5"         },
                  { key: "priority_2", label: "THIS WEEK",  color: "text-amber-400",   bg: "border-amber-500/20 bg-amber-500/5"     },
                  { key: "priority_3", label: "THIS MONTH", color: "text-emerald-400", bg: "border-emerald-500/20 bg-emerald-500/5" },
                ].map(({ key, label, color, bg }) => {
                  const p = recs[key]
                  if (!p) return null
                  return (
                    <div key={key} className={"glass rounded-xl p-4 border " + bg}>
                      <span className={"text-xs font-bold uppercase tracking-wider " + color}>{label}</span>
                      <p className="text-slate-200 text-sm font-medium mt-2 mb-1">{p.action}</p>
                      <p className={"text-xs font-medium " + color}>{p.expected_impact}</p>
                    </div>
                  )
                })}
              </div>
              {plan && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { key: "today",      label: "Today",      icon: Target,     color: "text-red-400"     },
                    { key: "this_week",  label: "This Week",  icon: Calendar,   color: "text-amber-400"   },
                    { key: "this_month", label: "This Month", icon: TrendingUp, color: "text-emerald-400" },
                  ].map(({ key, label, icon: Icon, color }) => {
                    const actions = plan[key] || []
                    return (
                      <div key={key} className="glass rounded-xl p-4 border border-white/5">
                        <div className="flex items-center gap-2 mb-3">
                          <Icon size={14} className={color} />
                          <span className={"text-xs font-bold " + color}>{label}</span>
                        </div>
                        {actions.slice(0,2).map((a, i) => (
                          <div key={i} className="mb-2 last:mb-0">
                            <p className="text-slate-300 text-xs">{a.action}</p>
                            <p className={"text-xs font-medium mt-0.5 " + color}>{a.expected_revenue_impact}</p>
                          </div>
                        ))}
                      </div>
                    )
                  })}
                </div>
              )}
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  )
}