import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ShoppingCart, Loader, Play } from 'lucide-react'
import { useT2 } from '../context/LangContext'
import api from '../api'
import toast from 'react-hot-toast'

export default function Apriori() {
  const datasetId = localStorage.getItem("dataset_id")
  const t = useT2()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [minSupport, setMinSupport] = useState(0.005)
  const [minConf, setMinConf] = useState(0.3)
  const [filter, setFilter] = useState(0)

  useEffect(() => { if (datasetId) loadApriori() }, [datasetId])

  async function loadApriori() {
    setLoading(true)
    try {
      const res = await api.get("/apriori/" + datasetId + "?min_support=" + minSupport + "&min_confidence=" + minConf)
      setResult(res.data.apriori || res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || "Apriori failed")
    } finally {
      setLoading(false)
    }
  }

  const rules = (result?.top_rules || []).filter(r => r.confidence >= filter)
  const summary = result?.summary || {}

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{"Association Rules"}</h1>
        <p className="page-subtitle">Market basket analysis — association rules</p>
      </motion.div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="glass rounded-xl p-4 flex items-center gap-6 flex-wrap">
        <div className="flex items-center gap-3">
          <label className="text-slate-400 text-sm">{"Min Support"}</label>
          <input type="range" min="0.005" max="0.05" step="0.005" value={minSupport} onChange={e => setMinSupport(Number(e.target.value))} className="w-24 accent-indigo-500" />
          <span className="text-indigo-400 font-mono text-sm w-12">{minSupport}</span>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-slate-400 text-sm">{"Min Confidence"}</label>
          <input type="range" min="0.1" max="0.9" step="0.1" value={minConf} onChange={e => setMinConf(Number(e.target.value))} className="w-24 accent-indigo-500" />
          <span className="text-indigo-400 font-mono text-sm w-8">{minConf}</span>
        </div>
        <button onClick={loadApriori} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
          {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
          {"Run Apriori"}
        </button>
      </motion.div>
      {loading && <div className="flex items-center justify-center h-48"><div className="text-center"><Loader size={32} className="text-indigo-400 animate-spin mx-auto mb-3" /><p className="text-slate-400 text-sm">{"Loading..."}</p></div></div>}
      {result && !loading && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Total Rules", value: result.total_rules_found || 0, color: "text-indigo-400" },
              { label: "Max Confidence", value: result.top_rules?.[0]?.confidence ? (result.top_rules[0].confidence*100).toFixed(1)+"%" : summary.max_confidence ? (summary.max_confidence*100).toFixed(1)+"%" : "N/A", color: "text-emerald-400" },
              { label: "Max Lift", value: summary.max_lift?.toFixed(2) || "N/A", color: "text-cyan-400" },
              { label: "Max Support", value: result.top_rules?.[0]?.support ? (result.top_rules[0].support*100).toFixed(2)+"%" : summary.max_support ? (summary.max_support*100).toFixed(2)+"%" : "N/A", color: "text-amber-400" },
            ].map(({ label, value, color }, i) => (
              <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="metric-card">
                <p className={"text-2xl font-bold font-mono " + color}>{value}</p>
                <p className="text-slate-400 text-xs mt-1">{label}</p>
              </motion.div>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <label className="text-slate-400 text-sm">{"Confidence"} ≥</label>
            <input type="range" min="0" max="0.9" step="0.1" value={filter} onChange={e => setFilter(Number(e.target.value))} className="w-32 accent-cyan-500" />
            <span className="text-cyan-400 font-mono text-sm">{(filter*100).toFixed(0)}%</span>
          </div>
          {rules.length > 0 ? (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">{"Top Rules in Plain English"} ({rules.length})</h2>
              {rules.slice(0,8).map((rule, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="glass rounded-xl p-4 border border-white/5 hover:border-indigo-500/30 transition-all">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="w-6 h-6 rounded-full bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-indigo-400 text-xs font-bold">{i+1}</span>
                      </div>
                      <p className="text-slate-200 text-sm leading-relaxed">{rule.english || "If bought " + rule.antecedents + " then bought " + rule.consequents}</p>
                    </div>
                    <div className="flex gap-2 flex-shrink-0">
                      <span className="badge-indigo">{(rule.confidence*100).toFixed(0)}% conf</span>
                      <span className="badge-cyan">{rule.lift?.toFixed(2)}x lift</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="glass rounded-xl p-8 text-center border border-white/5">
              <p className="text-slate-400">No rules found. Try lowering the confidence filter.</p>
            </div>
          )}
          {rules.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">{"Rules Table"}</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead><tr className="border-b border-white/5">{["If Bought", "Then Bought", "Support", "Confidence", "Lift"].map(h => <th key={h} className="text-left py-2 px-3 text-xs text-slate-500 uppercase tracking-wider">{h}</th>)}</tr></thead>
                  <tbody>{rules.slice(0,10).map((rule, i) => <tr key={i} className={"border-b border-white/5 " + (i%2===0?"":"bg-white/2")}><td className="py-2 px-3 text-indigo-300 text-xs">{rule.antecedents}</td><td className="py-2 px-3 text-cyan-300 text-xs">{rule.consequents}</td><td className="py-2 px-3 text-slate-300 font-mono text-xs">{(rule.support*100).toFixed(2)}%</td><td className="py-2 px-3 text-emerald-300 font-mono text-xs">{(rule.confidence*100).toFixed(1)}%</td><td className="py-2 px-3 text-amber-300 font-mono text-xs">{rule.lift?.toFixed(2)}</td></tr>)}</tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
      {!result && !loading && <div className="flex items-center justify-center h-48"><div className="text-center glass rounded-2xl p-12"><ShoppingCart size={48} className="text-slate-600 mx-auto mb-4" /><p className="text-slate-400">{"Run Apriori"}</p></div></div>}
    </div>
  )
}