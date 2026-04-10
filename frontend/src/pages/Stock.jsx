import { useState } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Loader, Search } from 'lucide-react'
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

export default function Stock() {
  const t = useT2()
  const [ticker, setTicker] = useState("AAPL")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function loadStock() {
    if (!ticker) return
    setLoading(true)
    try {
      const res = await api.get("/stock/" + ticker.toUpperCase())
      setResult(res.data.stock || res.data.result || res.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || "Stock fetch failed")
    } finally {
      setLoading(false)
    }
  }

  const history = Array.isArray(result?.historical) ? result.historical : []
  const forecastRaw = result?.forecast
  const forecast = Array.isArray(forecastRaw) ? forecastRaw : Array.isArray(forecastRaw?.forecast) ? forecastRaw.forecast : []
  const info = result?.info || {}
  const metrics = result?.stats || result?.metrics || {}
  const forecastMetrics = result?.forecast?.metrics || {}
  const chartData = [
    ...history.slice(-60).map(h => ({ date: h.date?.slice(0,10), close: h.close })),
    ...forecast.slice(0,30).map(f => ({ date: f.date?.slice(0,10), forecast: f.forecast, lower: f.lower_bound, upper: f.upper_bound }))
  ]
  const lastClose = history[history.length - 1]?.close
  const prevClose = history[history.length - 2]?.close
  const change = lastClose && prevClose ? lastClose - prevClose : 0
  const changePct = prevClose ? (change / prevClose * 100) : 0
  const isPositive = change >= 0

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{"Stock Market"}</h1>
        <p className="page-subtitle">Live stock data with ARIMA forecast overlay</p>
      </motion.div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="glass rounded-xl p-4 flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input type="text" value={ticker} onChange={e => setTicker(e.target.value.toUpperCase())} onKeyDown={e => e.key === "Enter" && loadStock()} className="input pl-10 font-mono uppercase" placeholder="AAPL" />
        </div>
        <button onClick={loadStock} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
          {loading ? <Loader size={14} className="animate-spin" /> : <TrendingUp size={14} />}
          {"Fetch Stock"}
        </button>
        <div className="flex gap-2">
          {["AAPL","TSLA","GOOGL","MSFT","AMZN"].map(tick => (
            <button key={tick} onClick={() => setTicker(tick)} className={"px-3 py-1.5 rounded-lg text-xs font-mono transition-all " + (ticker === tick ? "bg-green-600 text-white" : "glass text-slate-400 hover:text-white")}>{tick}</button>
          ))}
        </div>
      </motion.div>
      {loading && <div className="flex items-center justify-center h-48"><div className="text-center"><Loader size={32} className="text-green-400 animate-spin mx-auto mb-3" /><p className="text-slate-400 text-sm">{"Loading..."}</p></div></div>}
      {result && !loading && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="metric-card col-span-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-xs uppercase tracking-wider">{ticker} — {info.name || ticker}</p>
                  <p className="text-4xl font-bold font-mono text-white mt-1">${lastClose?.toFixed(2)}</p>
                </div>
                <div className={"flex items-center gap-1 " + (isPositive ? "text-emerald-400" : "text-red-400")}>
                  {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                  <span className="text-lg font-bold font-mono">{isPositive ? "+" : ""}{changePct.toFixed(2)}%</span>
                </div>
              </div>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="metric-card">
              <p className="text-2xl font-bold font-mono text-emerald-400">${metrics.period_high?.toFixed(2) || "N/A"}</p>
              <p className="text-slate-400 text-xs mt-1">{"Period High"}</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="metric-card">
              <p className="text-2xl font-bold font-mono text-red-400">${metrics.period_low?.toFixed(2) || "N/A"}</p>
              <p className="text-slate-400 text-xs mt-1">{"Period Low"}</p>
            </motion.div>
          </div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-6">{"Price History + 30-Day Forecast"}</h2>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="stockGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.3} /><stop offset="95%" stopColor="#10b981" stopOpacity={0} /></linearGradient>
                  <linearGradient id="forecastGrad2" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} /><stop offset="95%" stopColor="#22d3ee" stopOpacity={0} /></linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} interval={Math.floor(chartData.length/8)} />
                <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} domain={["auto","auto"]} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="close" stroke="#10b981" fill="url(#stockGrad)" strokeWidth={2} dot={false} name="Close" />
                <Area type="monotone" dataKey="forecast" stroke="#22d3ee" fill="url(#forecastGrad2)" strokeWidth={2} dot={false} name="Forecast" strokeDasharray="5 5" />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>
        </>
      )}
      {!result && !loading && <div className="flex items-center justify-center h-48"><div className="text-center glass rounded-2xl p-12"><TrendingUp size={48} className="text-slate-600 mx-auto mb-4" /><p className="text-slate-400">{"Fetch Stock"}</p><p className="text-slate-600 text-sm mt-1">Try AAPL, TSLA, GOOGL, MSFT</p></div></div>}
    </div>
  )
}