import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Loader, Play, Shield } from 'lucide-react'
import { useT2 } from '../context/LangContext'
import api from '../api'
import toast from 'react-hot-toast'

export default function Anomaly() {
  const datasetId = localStorage.getItem("dataset_id")
  const t = useT2()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [contamination, setContamination] = useState(0.05)

  useEffect(() => { if (datasetId) loadAnomaly() }, [datasetId])

  async function loadAnomaly() {
    setLoading(true)
    try {
      const res = await api.get("/anomaly/" + datasetId + "?contamination=" + contamination)
      setResult(res.data.anomaly || res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || "Anomaly detection failed")
    } finally {
      setLoading(false)
    }
  }

  const anomalies = result?.top_anomalies || []
  const summary = result?.summary || {}
  const severityColor = s => s === "High" ? "text-red-400" : s === "Medium" ? "text-amber-400" : "text-yellow-300"
  const severityBg = s => s === "High" ? "border-red-500/30 bg-red-500/5" : s === "Medium" ? "border-amber-500/30 bg-amber-500/5" : "border-yellow-500/30 bg-yellow-500/5"
  const severityBadge = s => s === "High" ? "badge-red" : s === "Medium" ? "badge-amber" : "badge-indigo"

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{"Anomaly Detection"}</h1>
        <p className="page-subtitle">Isolation Forest — automatic outlier detection</p>
      </motion.div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="glass rounded-xl p-4 flex items-center gap-6 flex-wrap">
        <div className="flex items-center gap-3">
          <label className="text-slate-400 text-sm">{"Contamination"}</label>
          <input type="range" min="0.01" max="0.2" step="0.01" value={contamination} onChange={e => setContamination(Number(e.target.value))} className="w-32 accent-red-500" />
          <span className="text-red-400 font-mono text-sm w-12">{(contamination*100).toFixed(0)}%</span>
        </div>
        <button onClick={loadAnomaly} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
          {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
          {"Detect Anomalies"}
        </button>
      </motion.div>
      {loading && <div className="flex items-center justify-center h-48"><div className="text-center"><Loader size={32} className="text-red-400 animate-spin mx-auto mb-3" /><p className="text-slate-400 text-sm">{"Loading..."}</p></div></div>}
      {result && !loading && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: "Total Rows", value: result.total_rows?.toLocaleString() || "N/A", color: "text-indigo-400" },
              { label: "Anomalies Found", value: result.total_anomalies?.toLocaleString() || "N/A", color: "text-red-400" },
              { label: "Anomaly %", value: result.anomaly_pct ? result.anomaly_pct+"%" : "N/A", color: "text-amber-400" },
              { label: "High Severity", value: summary.high_severity || 0, color: "text-red-400" },
              { label: "Med Severity", value: summary.medium_severity || 0, color: "text-amber-400" },
            ].map(({ label, value, color }, i) => (
              <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="metric-card">
                <p className={"text-2xl font-bold font-mono " + color}>{value}</p>
                <p className="text-slate-400 text-xs mt-1">{label}</p>
              </motion.div>
            ))}
          </div>
          {anomalies.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">{"Top Anomalies"}</h2>
              {anomalies.slice(0,8).map((a, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className={"glass rounded-xl p-4 border " + severityBg(a.severity)}>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle size={14} className={severityColor(a.severity)} />
                        <span className="text-slate-400 text-xs font-mono">Row {a.row_index}</span>
                        <span className="text-slate-500 text-xs">Score: {a.anomaly_score}</span>
                      </div>
                      <p className="text-slate-200 text-sm">{a.explanation}</p>
                      <div className="flex gap-3 mt-2 flex-wrap">
                        {Object.entries(a.values || {}).map(([k, v]) => (
                          <span key={k} className="text-xs text-slate-400"><span className="text-slate-500">{k}:</span> <span className="text-slate-200 font-mono">{v}</span></span>
                        ))}
                      </div>
                    </div>
                    <span className={severityBadge(a.severity)}>{a.severity}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
          <div className="glass rounded-xl p-4 border border-white/5">
            <div className="flex items-center gap-3">
              <Shield size={18} className="text-emerald-400" />
              <p className="text-slate-300 text-sm">
                <span className="text-emerald-400 font-medium">{result.total_rows - result.total_anomalies}</span> normal transactions.
                <span className="text-red-400 font-medium"> {result.total_anomalies}</span> anomalies ({result.anomaly_pct}%) flagged.
              </p>
            </div>
          </div>
        </>
      )}
      {!result && !loading && <div className="flex items-center justify-center h-48"><div className="text-center glass rounded-2xl p-12"><AlertTriangle size={48} className="text-slate-600 mx-auto mb-4" /><p className="text-slate-400">{"Detect Anomalies"}</p></div></div>}
    </div>
  )
}