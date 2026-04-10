import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis } from 'recharts'
import { Users, Loader, Play } from 'lucide-react'
import { useT2 } from '../context/LangContext'
import api from '../api'
import toast from 'react-hot-toast'

const COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#10b981', '#f43f5e', '#a78bfa']

function ClusterCard({ profile, color, index, mode }) {
  const isRFM = mode === 'rfm'

  // RFM mode: show Recency/Frequency/Monetary
  const recency   = profile.Recency   ?? 0
  const frequency = profile.Frequency ?? 0
  const monetary  = profile.Monetary  ?? 0

  // Generic mode: show top 3 numeric fields from profile
  const genericFields = Object.entries(profile).filter(([k]) =>
    !['cluster','size','pct','name','revenue_pct','_scaled_importance'].includes(k) &&
    typeof profile[k] === 'number'
  ).slice(0, 3)

  const radarData = isRFM ? [
    { metric: 'Recency',   value: recency   },
    { metric: 'Frequency', value: frequency },
    { metric: 'Monetary',  value: monetary  },
  ] : genericFields.map(([k, v]) => ({ metric: k.replace(/_/g,' '), value: Math.abs(v) }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="glass rounded-xl p-5 border border-white/5 hover:border-indigo-500/30 transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-white font-bold text-sm">{profile.name || "Cluster " + profile.cluster}</h3>
          <p className="text-slate-400 text-xs mt-0.5">{(profile.size || 0).toLocaleString()} {isRFM ? 'customers' : 'records'}</p>
          <p className="text-slate-500 text-xs">{profile.pct}% of total</p>
        </div>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: color + "20", border: "1px solid " + color + "40" }}>
          <Users size={18} style={{ color: color }} />
        </div>
      </div>

      {isRFM ? (
        <div className="grid grid-cols-3 gap-2 mb-4">
          {[
            { label: 'Recency',   value: recency.toFixed(1),   unit: 'd' },
            { label: 'Frequency', value: frequency.toFixed(1), unit: 'x' },
            { label: 'Monetary',  value: monetary.toFixed(2),  unit: ''  },
          ].map(({ label, value, unit }) => (
            <div key={label} className="text-center">
              <p className="text-lg font-bold font-mono" style={{ color: color }}>{value}{unit}</p>
              <p className="text-slate-500 text-[10px]">{label}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-2 mb-4">
          {genericFields.map(([key, val]) => (
            <div key={key} className="text-center">
              <p className="text-sm font-bold font-mono" style={{ color: color }}>{typeof val === 'number' ? val.toFixed(1) : val}</p>
              <p className="text-slate-500 text-[10px]">{key.replace(/_/g,' ')}</p>
            </div>
          ))}
        </div>
      )}

      {radarData.length > 0 && (
        <RadarChart cx="50%" cy="50%" outerRadius={70} width={260} height={200} data={radarData}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="metric" tick={{ fill: "#64748b", fontSize: 9 }} />
          <Radar dataKey="value" stroke={color} fill={color} fillOpacity={0.15} strokeWidth={1.5} />
        </RadarChart>
      )}
    </motion.div>
  )
}

export default function Clustering() {
  const datasetId = localStorage.getItem("dataset_id")
  const t = useT2()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [k, setK] = useState(4)

  useEffect(() => { if (datasetId) loadClustering() }, [datasetId])

  async function loadClustering(kVal = k) {
    setLoading(true)
    try {
      const res = await api.get("/kmeans/" + datasetId + "?k=" + kVal)
      setResult(res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || "Clustering failed")
    } finally {
      setLoading(false)
    }
  }

  const profiles = result?.cluster_profiles || []
  const sizeData = profiles.map(p => ({ name: p.name || "C"+p.cluster, size: p.size || 0 }))

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{t("clustering")}</h1>
        <p className="page-subtitle">{result?.mode === "generic" ? "KMeans clustering analysis" : "KMeans + RFM clustering analysis"}</p>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="glass rounded-xl p-4 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <label className="text-slate-400 text-sm">Number of Clusters (k)</label>
          <input type="range" min="2" max="10" step="1" value={k}
            onChange={e => setK(Number(e.target.value))}
            className="w-32 accent-indigo-500" />
          <span className="text-indigo-400 font-mono text-sm w-4">{k}</span>
          <button onClick={() => loadClustering(k)} disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
            {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
            Run Clustering
          </button>
        </div>
        {result && (
          <div className="flex items-center gap-6">
            {[
              { label: t("silhouette"), value: result.silhouette_score?.toFixed(4), color: "text-indigo-400" },
              { label: t("davies"),     value: (result.davies_bouldin || result.davies_bouldin_index)?.toFixed(4),   color: "text-cyan-400"   },
              { label: t("customers"),  value: result.cluster_profiles ? result.cluster_profiles.reduce((a,p) => a + (p.size||0), 0).toLocaleString() : "N/A", color: "text-emerald-400"},
            ].map(({ label, value, color }) => (
              <div key={label} className="text-center">
                <p className={"text-xl font-bold font-mono " + color}>{value}</p>
                <p className="text-slate-500 text-xs">{label}</p>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {loading && (
        <div className="flex items-center justify-center h-48">
          <div className="text-center">
            <Loader size={32} className="text-indigo-400 animate-spin mx-auto mb-3" />
            <p className="text-slate-400 text-sm">{t("loading")}</p>
          </div>
        </div>
      )}

      {result && !loading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {profiles.map((profile, i) => (
              <ClusterCard key={i} profile={profile} color={COLORS[i % COLORS.length]} index={i} mode={result?.mode} />
            ))}
          </div>

          {sizeData.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }} className="card">
              <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
                Cluster Size Distribution
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={sizeData}>
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: "rgba(15,15,25,0.9)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", color: "#e2e8f0" }} />
                  <Bar dataKey="size" radius={[4,4,0,0]}>
                    {sizeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          )}
        </>
      )}

      {!result && !loading && (
        <div className="flex items-center justify-center h-48">
          <div className="text-center glass rounded-2xl p-12">
            <Users size={48} className="text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Run Clustering</p>
          </div>
        </div>
      )}
    </div>
  )
}