import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { TrendingUp, TrendingDown, Minus, Loader, Play } from 'lucide-react'
import { useT2 } from '../context/LangContext'
import api from '../api'
import toast from 'react-hot-toast'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs border border-white/10">
      <p className="text-slate-300 font-medium mb-1">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === "number" ? p.value.toFixed(2) : p.value}</p>)}
    </div>
  )
}

export default function Forecasting() {
  const datasetId = localStorage.getItem("dataset_id")
  const t = useT2()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [forecastDays, setForecastDays] = useState(30)

  useEffect(() => { if (datasetId) loadForecast() }, [datasetId])

  async function loadForecast(days = forecastDays) {
    setLoading(true)
    try {
      const res = await api.get("/arima/" + datasetId + "?forecast_days=" + days)
      setResult(res.data.arima || res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || "Forecast failed")
    } finally {
      setLoading(false)
    }
  }

  const trend = result?.summary?.trend || "stable"
  const TrendIcon = trend === "increasing" ? TrendingUp : trend === "decreasing" ? TrendingDown : Minus
  const trendColor = trend === "increasing" ? "text-emerald-400" : trend === "decreasing" ? "text-red-400" : "text-amber-400"
  const trendBg = trend === "increasing" ? "border-emerald-500/30 bg-emerald-500/5" : trend === "decreasing" ? "border-red-500/30 bg-red-500/5" : "border-amber-500/30 bg-amber-500/5"
  const historical = (result?.historical || []).slice(-60).map(h => ({ date: h.date?.slice(0,10), actual: h.revenue }))
  const forecast = (result?.forecast || []).map(f => ({ date: f.date?.slice(0,10), forecast: f.forecast, lower: f.lower_bound, upper: f.upper_bound }))
  const chartData = [...historical, ...forecast]
  const splitDate = historical[historical.length - 1]?.date

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{"Forecasting"}</h1>
        <p className="page-subtitle">ARIMA time series model with 95% confidence intervals</p>
      </motion.div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="glass rounded-xl p-4 flex items-center gap-6 flex-wrap">
        <div className="flex items-center gap-3">
          <label className="text-slate-400 text-sm">{"Forecast Days"}</label>
          <input type="range" min="7" max="90" step="7" value={forecastDays} onChange={e => setForecastDays(Number(e.target.value))} className="w-32 accent-indigo-500" />
          <span className="text-indigo-400 font-mono text-sm w-8">{forecastDays}</span>
        </div>
        <button onClick={() => loadForecast(forecastDays)} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
          {loading ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
          {"Run Forecast"}
        </button>
      </motion.div>
      {loading && <div className="flex items-center justify-center h-48"><div className="text-center"><Loader size={32} className="text-indigo-400 animate-spin mx-auto mb-3" /><p className="text-slate-400 text-sm">{"Loading..."}</p></div></div>}
      {result && !loading && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: "Model", value: result.model || "ARIMA", color: "text-indigo-400" },
              { label: "RMSE", value: result.metrics?.rmse?.toFixed(2) || "N/A", color: "text-cyan-400" },
              { label: "MAPE", value: result.metrics?.mape ? result.metrics.mape.toFixed(2)+"%" : "N/A", color: "text-violet-400" },
              { label: "Total Forecast", value: result.summary?.total_forecast_revenue?.toFixed(0) || "N/A", color: "text-emerald-400" },
              { label: "Avg Daily", value: result.summary?.avg_daily_forecast?.toFixed(2) || "N/A", color: "text-amber-400" },
            ].map(({ label, value, color }, i) => (
              <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="metric-card">
                <p className={"text-xl font-bold font-mono " + color}>{value}</p>
                <p className="text-slate-400 text-xs mt-1">{label}</p>
              </motion.div>
            ))}
          </div>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className={"glass rounded-xl p-4 border flex items-center gap-4 " + trendBg}>
            <TrendIcon size={32} className={trendColor} />
            <div>
              <p className={"text-lg font-bold " + trendColor}>{trend.toUpperCase()}</p>
              <p className="text-slate-400 text-sm">{trend === "increasing" ? "Revenue is projected to grow" : trend === "decreasing" ? "Revenue is projected to decline" : "Revenue is projected to remain stable"}</p>
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="card">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-6">{"Historical + Forecast"} ({forecastDays} days)</h2>
            <ResponsiveContainer width="100%" height={340}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} /><stop offset="95%" stopColor="#6366f1" stopOpacity={0} /></linearGradient>
                  <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} /><stop offset="95%" stopColor="#22d3ee" stopOpacity={0} /></linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} interval={Math.floor(chartData.length/8)} />
                <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                {splitDate && <ReferenceLine x={splitDate} stroke="rgba(255,255,255,0.2)" strokeDasharray="4 4" />}
                <Area type="monotone" dataKey="actual" stroke="#6366f1" fill="url(#actualGrad)" strokeWidth={2} dot={false} name="Actual" />
                <Area type="monotone" dataKey="forecast" stroke="#22d3ee" fill="url(#forecastGrad)" strokeWidth={2} dot={false} name="Forecast" strokeDasharray="5 5" />
                <Area type="monotone" dataKey="upper" stroke="rgba(34,211,238,0.3)" fill="rgba(34,211,238,0.05)" strokeWidth={1} dot={false} name="Upper" />
                <Area type="monotone" dataKey="lower" stroke="rgba(34,211,238,0.3)" fill="rgba(34,211,238,0.05)" strokeWidth={1} dot={false} name="Lower" />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>
          {forecast.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card">
              <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">{"Forecast Details"}</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead><tr className="border-b border-white/5">{["Date", "Forecast", "Lower (95%)", "Upper (95%)"].map(h => <th key={h} className="text-left py-2 px-3 text-xs text-slate-500 uppercase tracking-wider">{h}</th>)}</tr></thead>
                  <tbody>{forecast.slice(0,10).map((f,i) => <tr key={i} className={"border-b border-white/5 " + (i%2===0?"":"bg-white/2")}><td className="py-2 px-3 text-slate-300 font-mono text-xs">{f.date}</td><td className="py-2 px-3 text-cyan-400 font-mono text-xs font-bold">{f.forecast?.toFixed(2)}</td><td className="py-2 px-3 text-slate-400 font-mono text-xs">{f.lower?.toFixed(2)}</td><td className="py-2 px-3 text-slate-400 font-mono text-xs">{f.upper?.toFixed(2)}</td></tr>)}</tbody>
                </table>
              </div>
            </motion.div>
          )}
        </>
      )}
      {!result && !loading && <div className="flex items-center justify-center h-48"><div className="text-center glass rounded-2xl p-12"><TrendingUp size={48} className="text-slate-600 mx-auto mb-4" /><p className="text-slate-400">{"Run Forecast"}</p></div></div>}
    </div>
  )
}