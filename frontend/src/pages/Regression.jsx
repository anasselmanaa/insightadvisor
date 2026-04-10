import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'
import { BarChart2, Loader, Play } from 'lucide-react'
import api from '../api'
import { useT2 } from '../context/LangContext'
import toast from 'react-hot-toast'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs border border-white/10">
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(4) : p.value}</p>
      ))}
    </div>
  )
}

export default function Regression() {
  const datasetId = localStorage.getItem('dataset_id')
  const t = useT2()
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [target, setTarget]   = useState('revenue')

  useEffect(() => { if (datasetId) loadRegression() }, [datasetId])

  async function loadRegression() {
    setLoading(true)
    try {
      const res = await api.get(`/regression/${datasetId}?target_column=${target}`)
      setResult(res.data.regression || res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Regression failed')
    } finally {
      setLoading(false)
    }
  }

  const metrics = result?.metrics || {}
  const features = result?.feature_importance || []
  const predictions = result?.actual_vs_predicted || result?.predictions || []

  const scatterData = predictions.slice(0, 200).map((p, i) => ({
    actual: p.actual, predicted: p.predicted
  }))

  const maxVal = Math.max(...scatterData.map(d => Math.max(d.actual, d.predicted)), 1)

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">Regression Analysis</h1>
        <p className="page-subtitle">Linear regression with feature importance and prediction accuracy</p>
      </motion.div>

      {/* Controls */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="glass rounded-xl p-4 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <label className="text-slate-400 text-sm">Target Column</label>
          <input
            type="text"
            value={target}
            onChange={e => setTarget(e.target.value)}
            className="input w-40"
            placeholder="revenue"
          />
        </div>
        <button onClick={loadRegression} disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
          {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
          Run Regression
        </button>
      </motion.div>

      {loading && (
        <div className="flex items-center justify-center h-48">
          <div className="text-center">
            <Loader size={32} className="text-indigo-400 animate-spin mx-auto mb-3" />
            <p className="text-slate-400 text-sm">Training linear regression model...</p>
          </div>
        </div>
      )}

      {result && !loading && (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Target',    value: result.target_column || target, color: 'text-indigo-400' },
              { label: 'R²',        value: metrics.r2?.toFixed(4) || 'N/A', color: metrics.r2 > 0.7 ? 'text-emerald-400' : metrics.r2 > 0.4 ? 'text-amber-400' : 'text-red-400' },
              { label: 'MAE',       value: metrics.mae?.toFixed(2) || 'N/A',  color: 'text-cyan-400' },
              { label: 'RMSE',      value: metrics.rmse?.toFixed(2) || 'N/A', color: 'text-violet-400' },
            ].map(({ label, value, color }, i) => (
              <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }} className="metric-card">
                <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
                <p className="text-slate-400 text-xs mt-1">{label}</p>
              </motion.div>
            ))}
          </div>

          {/* Interpretation */}
          {result.interpretation && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
              className="glass rounded-xl p-4 border border-indigo-500/20">
              <p className="text-slate-300 text-sm">{result.interpretation}</p>
            </motion.div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Feature Importance */}
            {features.length > 0 && (
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }} className="card">
                <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
                  Feature Importance (Coefficients)
                </h2>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={features.slice(0, 8)} layout="vertical">
                    <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="feature" tick={{ fill: '#94a3b8', fontSize: 10 }} width={160} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="coefficient" radius={[0, 4, 4, 0]}>
                      {features.slice(0, 8).map((f, i) => (
                        <Cell key={i} fill={f.coefficient >= 0 ? '#10b981' : '#ef4444'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </motion.div>
            )}

            {/* Actual vs Predicted */}
            {scatterData.length > 0 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }} className="card">
                <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
                  Actual vs Predicted
                </h2>
                <ResponsiveContainer width="100%" height={240}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="actual"    name="Actual"    tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis dataKey="predicted" name="Predicted" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter data={scatterData} fill="#6366f1" fillOpacity={0.6} />
                  </ScatterChart>
                </ResponsiveContainer>
              </motion.div>
            )}
          </div>

          {/* Stats */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }} className="glass rounded-xl p-4 border border-white/5">
            <div className="flex gap-8 flex-wrap">
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Train Size</p>
                <p className="text-slate-200 font-mono mt-1">{result.train_size?.toLocaleString() || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Test Size</p>
                <p className="text-slate-200 font-mono mt-1">{result.test_size?.toLocaleString() || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Features Used</p>
                <p className="text-slate-200 font-mono mt-1">{result.features_used || result.feature_importance?.length || result.coefficients?.length?.join(', ') || 'N/A'}</p>
              </div>
            </div>
          </motion.div>
        </>
      )}

      {!result && !loading && (
        <div className="flex items-center justify-center h-48">
          <div className="text-center glass rounded-2xl p-12">
            <BarChart2 size={48} className="text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Click Run Regression to train the model</p>
          </div>
        </div>
      )}
    </div>
  )
}
