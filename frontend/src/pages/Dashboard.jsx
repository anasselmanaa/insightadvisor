import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Database, AlertTriangle, BarChart2, CheckCircle, Loader } from 'lucide-react'
import { useT2 } from '../context/LangContext'
import api from '../api'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs border border-white/10">
      <p className="text-slate-300 font-medium">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const datasetId = localStorage.getItem('dataset_id')
  const t = useT2()
  const [eda, setEda]         = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    if (!datasetId) { setLoading(false); return }
    api.get(`/eda/${datasetId}`)
      .then(r => setEda(r.data.eda || r.data.report || r.data))
      .catch(e => setError(e.response?.data?.detail || 'Failed to load EDA'))
      .finally(() => setLoading(false))
  }, [datasetId])

  if (!datasetId) return (
    <div className="p-8 flex items-center justify-center h-full">
      <div className="text-center glass rounded-2xl p-12">
        <Database size={48} className="text-slate-600 mx-auto mb-4" />
        <p className="text-slate-400 text-lg font-medium">{t('no_data')}</p>
        <p className="text-slate-600 text-sm mt-1">{t('upload_first')}</p>
      </div>
    </div>
  )

  if (loading) return (
    <div className="p-8 flex items-center justify-center h-full">
      <div className="text-center">
        <Loader size={32} className="text-indigo-400 animate-spin mx-auto mb-3" />
        <p className="text-slate-400">{t('loading')}</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="p-8">
      <div className="glass rounded-xl p-6 border border-red-500/20">
        <p className="text-red-400">{error}</p>
      </div>
    </div>
  )

  const stats      = eda?.numeric_summary || eda?.summary_statistics || {}
  const topCats    = eda?.top_categories  || {}
  const colCount   = eda?.columns?.length || Object.keys(stats).length
  const missingCol = eda?.missing         || eda?.missing_values || {}

  const topProducts = (topCats?.description?.values || []).slice(0, 8).map((v, i) => ({
    name:  String(v).slice(0, 20),
    count: (topCats?.description?.counts || [])[i] || 0,
  }))

  const topCountries = (topCats?.country?.values || []).slice(0, 6).map((v, i) => ({
    name:  String(v),
    count: (topCats?.country?.counts || [])[i] || 0,
  }))

  const missingData = Object.entries(missingCol)
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: k, missing: v }))

  const statCards = [
    { icon: Database,      label: t('columns'),             value: colCount,                                              color: 'bg-indigo-500/20 text-indigo-400'  },
    { icon: BarChart2,     label: t('numeric_cols'),         value: eda?.numeric_summary ? Object.keys(eda.numeric_summary).length : 'N/A', color: 'bg-cyan-500/20 text-cyan-400' },
    { icon: AlertTriangle, label: t('missing_values_label'), value: Object.values(missingCol).reduce((a,b)=>a+b,0),       color: 'bg-amber-500/20 text-amber-400'   },
    { icon: CheckCircle,   label: t('dataset_id_label'),     value: datasetId?.slice(0,8)+'...',                          color: 'bg-emerald-500/20 text-emerald-400'},
  ]

  return (
    <div className="p-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">{t('dashboard_title')}</h1>
        <p className="page-subtitle">{t('dashboard_subtitle')} <span className="text-indigo-400 font-mono">{datasetId}</span></p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map(({ icon: Icon, label, value, color }, i) => (
          <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }} className="metric-card">
            <div className="flex items-center justify-between mb-3">
              <p className="text-slate-400 text-xs uppercase tracking-wider">{label}</p>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
                <Icon size={15} />
              </div>
            </div>
            <p className="text-2xl font-bold font-mono text-white">{value}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {topProducts.length > 0 && (
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }} className="card">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
              {t('top_products_label')}
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={topProducts} layout="vertical">
                <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} width={110} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} name={t('top_products_label')} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}

        {topCountries.length > 0 && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }} className="card">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
              {t('sales_country_label')}
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={topCountries}>
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#22d3ee" radius={[4, 4, 0, 0]} name={t('sales_country_label')} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}
      </div>

      {missingData.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }} className="card">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
            {t('missing_col_label')}
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={missingData}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="missing" fill="#f59e0b" radius={[4, 4, 0, 0]} name={t('missing_values_label')} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {Object.keys(stats).length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }} className="card">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
            {t('summary_stats_label')}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5">
                  {[t('column'), t('mean'), t('std'), t('min'), t('max')].map(h => (
                    <th key={h} className="text-left py-2 px-3 text-xs text-slate-500 uppercase tracking-wider font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats).slice(0, 8).map(([col, s], i) => (
                  <tr key={col} className={`border-b border-white/5 ${i % 2 === 0 ? '' : 'bg-white/2'}`}>
                    <td className="py-2 px-3 text-indigo-300 font-mono text-xs">{col}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono text-xs">{typeof s.mean === 'number' ? s.mean.toFixed(2) : 'N/A'}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono text-xs">{typeof s.std  === 'number' ? s.std.toFixed(2)  : 'N/A'}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono text-xs">{typeof s.min  === 'number' ? s.min.toFixed(2)  : 'N/A'}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono text-xs">{typeof s.max  === 'number' ? s.max.toFixed(2)  : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  )
}