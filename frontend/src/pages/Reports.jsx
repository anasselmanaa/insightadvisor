import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileDown, FileText, Table, Presentation, Mail, Loader, CheckCircle } from 'lucide-react'
import api from '../api'
import { useT2 } from '../context/LangContext'
import toast from 'react-hot-toast'

export default function Reports() {
  const datasetId = localStorage.getItem('dataset_id')
  const t = useT2()
  const [loading, setLoading] = useState({})
  const [done, setDone]       = useState({})

  async function download(type) {
    if (!datasetId) { toast.error('Upload a dataset first'); return }
    setLoading(prev => ({ ...prev, [type]: true }))
    try {
      const res = await api.get(`/export/${type}/${datasetId}`, { responseType: 'blob' })
      const ext  = type === 'pdf' ? 'pdf' : type === 'pptx' ? 'pptx' : 'xlsx'
      const url  = URL.createObjectURL(new Blob([res.data]))
      const a    = document.createElement('a')
      a.href     = url
      a.download = `retailiq_${type}_${datasetId}.${ext}`
      a.click()
      URL.revokeObjectURL(url)
      setDone(prev => ({ ...prev, [type]: true }))
      toast.success(`${type.toUpperCase()} downloaded!`)
    } catch (e) {
      toast.error(`Failed to download ${type}`)
    } finally {
      setLoading(prev => ({ ...prev, [type]: false }))
    }
  }

  const exports = [
    {
      type:     'pdf',
      label:    'Full PDF Report',
      desc:     '8-section professional report with all analyses, metrics, and AI recommendations',
      icon:     FileText,
      color:    'text-red-400',
      bg:       'border-red-500/20 hover:border-red-500/40',
      btnColor: 'bg-red-600 hover:bg-red-500',
    },
    {
      type:     'pptx',
      label:    'PowerPoint Slides',
      desc:     '8 slides covering data quality, clustering, forecasting, regression, rules, and AI insights',
      icon:     Presentation,
      color:    'text-orange-400',
      bg:       'border-orange-500/20 hover:border-orange-500/40',
      btnColor: 'bg-orange-600 hover:bg-orange-500',
    },
    {
      type:     'cleaned',
      label:    'Cleaned Dataset (Excel)',
      desc:     'Download the cleaned and processed dataset as an Excel file',
      icon:     Table,
      color:    'text-emerald-400',
      bg:       'border-emerald-500/20 hover:border-emerald-500/40',
      btnColor: 'bg-emerald-600 hover:bg-emerald-500',
    },
    {
      type:     'kmeans',
      label:    'Clustering Results (Excel)',
      desc:     'Customer segments with RFM scores and cluster assignments',
      icon:     Table,
      color:    'text-cyan-400',
      bg:       'border-cyan-500/20 hover:border-cyan-500/40',
      btnColor: 'bg-cyan-600 hover:bg-cyan-500',
    },
  ]

  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="page-title">Reports & Exports</h1>
        <p className="page-subtitle">Download your analysis as PDF, PowerPoint, or Excel</p>
      </motion.div>

      {!datasetId && (
        <div className="glass rounded-xl p-8 text-center border border-white/5">
          <FileDown size={48} className="text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">Upload a dataset first to generate reports</p>
        </div>
      )}

      {datasetId && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exports.map(({ type, label, desc, icon: Icon, color, bg, btnColor }, i) => (
              <motion.div key={type}
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className={`glass rounded-xl p-6 border transition-all duration-200 ${bg}`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${color} bg-white/5`}>
                    <Icon size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-semibold mb-1">{label}</h3>
                    <p className="text-slate-400 text-sm mb-4">{desc}</p>
                    <button
                      onClick={() => download(type)}
                      disabled={loading[type]}
                      className={`flex items-center gap-2 px-4 py-2 ${btnColor} disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all active:scale-95`}
                    >
                      {loading[type] ? (
                        <><Loader size={14} className="animate-spin" /> Generating...</>
                      ) : done[type] ? (
                        <><CheckCircle size={14} /> Downloaded!</>
                      ) : (
                        <><FileDown size={14} /> Download</>
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="glass rounded-xl p-6 border border-indigo-500/20">
            <h3 className="text-white font-semibold mb-1 flex items-center gap-2">
              <FileDown size={18} className="text-indigo-400" />
              Dataset ID
            </h3>
            <p className="text-indigo-300 font-mono text-sm mt-2">{datasetId}</p>
            <p className="text-slate-500 text-xs mt-1">All reports are generated from this dataset</p>
          </motion.div>
        </>
      )}
    </div>
  )
}