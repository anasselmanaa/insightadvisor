import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload as UploadIcon, FileText, CheckCircle, Loader, ArrowRight, Database, Zap } from 'lucide-react'
import api from '../api'
import { useT2 } from '../context/LangContext'
import toast from 'react-hot-toast'

function MetricCard({ label, value, color = 'text-indigo-400', delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="metric-card"
    >
      <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
      <p className="text-slate-400 text-xs mt-1">{label}</p>
    </motion.div>
  )
}

export default function Upload() {
  const navigate = useNavigate()
  const t = useT2()
  const [dragging, setDragging]   = useState(false)
  const [file, setFile]           = useState(null)
  const [loading, setLoading]     = useState(false)
  const [step, setStep]           = useState('idle')
  const [report, setReport]       = useState(null)
  const [datasetId, setDatasetId] = useState(null)

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer?.files?.[0] || e.target.files?.[0]
    if (f && (f.name.endsWith('.csv') || f.name.endsWith('.xlsx'))) {
      setFile(f)
      setReport(null)
      setStep('idle')
    } else {
      toast.error('Please upload a CSV or Excel file')
    }
  }, [])

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setStep('uploading')
    try {
      const formData = new FormData()
      formData.append('file', file)
      setStep('cleaning')
      const uploadRes = await api.post('/upload', formData)
      const id = uploadRes.data.dataset_id
      setDatasetId(id)
      localStorage.setItem('dataset_id', id)
      localStorage.setItem('filename', file.name)
      localStorage.setItem('dataset_type', uploadRes.data.dataset_type || 'generic')
      localStorage.setItem('filename', file.name)
      localStorage.setItem('dataset_type', uploadRes.data.dataset_type || 'generic')
      setReport(uploadRes.data.cleaning_report || uploadRes.data)
      setStep('done')
      toast.success('Dataset uploaded and cleaned!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
      setStep('idle')
    } finally {
      setLoading(false)
    }
  }

  const qualityScore = report?.quality_score
  const qualityColor = qualityScore >= 80 ? 'text-emerald-400' :
                       qualityScore >= 60 ? 'text-amber-400' : 'text-red-400'
  const qualityBg    = qualityScore >= 80 ? 'border-emerald-500/30 bg-emerald-500/5' :
                       qualityScore >= 60 ? 'border-amber-500/30 bg-amber-500/5' :
                                            'border-red-500/30 bg-red-500/5'

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="page-title">{t('upload_title')}</h1>
        <p className="page-subtitle">{t('upload_subtitle')}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => document.getElementById('file-input').click()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
          dragging ? 'border-indigo-400 bg-indigo-500/10 shadow-glow-md' :
          file     ? 'border-indigo-500/50 bg-indigo-500/5' :
                     'border-white/10 hover:border-indigo-500/40'
        }`}
      >
        <input id="file-input" type="file" accept=".csv,.xlsx" className="hidden" onChange={onDrop} />
        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 mb-4">
                <UploadIcon size={28} className="text-indigo-400" />
              </div>
              <p className="text-slate-200 font-medium text-lg">{t('drop_file')}</p>
              <p className="text-slate-500 text-sm mt-1">{t('drop_subtitle')}</p>
              <div className="flex items-center justify-center gap-4 mt-4">
                <span className="badge-indigo">CSV</span>
                <span className="badge-indigo">XLSX</span>
                <span className="badge-indigo">Up to 50MB</span>
              </div>
            </motion.div>
          ) : (
            <motion.div key="file" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 mb-4">
                <FileText size={28} className="text-emerald-400" />
              </div>
              <p className="text-slate-200 font-medium text-lg">{file.name}</p>
              <p className="text-slate-500 text-sm mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              <p className="text-indigo-400 text-xs mt-2">Click to change file</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {file && step !== 'done' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-4">
            <button
              onClick={handleUpload}
              disabled={loading}
              className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-xl transition-all duration-200 shadow-glow-sm hover:shadow-glow-md flex items-center justify-center gap-2"
            >
              {loading ? (
                <><Loader size={18} className="animate-spin" />{step === 'uploading' ? t('uploading') : t('cleaning')}</>
              ) : (
                <><Zap size={18} />{t('upload_btn')}</>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-6 glass rounded-xl p-4">
            <div className="flex items-center gap-6">
              {[['uploading','Uploading'],['cleaning','Cleaning'],['done','Complete']].map(([key, label], i) => {
                const steps = ['uploading','cleaning','done']
                const current = steps.indexOf(step)
                const idx = steps.indexOf(key)
                const done = idx < current
                const active = idx === current
                return (
                  <div key={key} className="flex items-center gap-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${done ? 'bg-emerald-500 text-white' : active ? 'bg-indigo-500 text-white animate-pulse' : 'bg-white/10 text-slate-500'}`}>
                      {done ? '✓' : i + 1}
                    </div>
                    <span className={`text-sm ${active ? 'text-white' : done ? 'text-emerald-400' : 'text-slate-500'}`}>{label}</span>
                    {i < 2 && <div className="w-8 h-px bg-white/10 ml-2" />}
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {step === 'done' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mt-8 space-y-6">
            <div className={`glass rounded-xl p-6 border ${qualityScore ? qualityBg : 'border-indigo-500/20'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm uppercase tracking-wider">{t('upload_complete')}</p>
                  {qualityScore ? (
                    <p className={`text-5xl font-bold font-mono mt-1 ${qualityColor}`}>
                      {qualityScore}<span className="text-2xl">/100</span>
                    </p>
                  ) : (
                    <p className="text-3xl font-bold text-indigo-400 mt-1">Ready</p>
                  )}
                </div>
                <CheckCircle size={48} className={qualityScore ? qualityColor : 'text-indigo-400'} />
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard label="Rows Before"        value={report?.raw_rows ?? report?.rows_before ?? 'N/A'} delay={0.1} />
              <MetricCard label="Rows After"         value={report?.cleaned_rows ?? report?.rows_after  ?? 'N/A'} delay={0.15} color="text-emerald-400" />
              <MetricCard label="Duplicates Removed" value={report?.duplicates_removed ?? 0} delay={0.2} color="text-amber-400" />
              <MetricCard label="Outliers Removed"   value={typeof report?.outliers_removed === 'object' ? Object.values(report?.outliers_removed || {}).reduce((a,b) => a+b, 0) : report?.outliers_removed ?? 0} delay={0.25} color="text-red-400" />
            </div>

            <div className="glass rounded-xl p-4 border border-indigo-500/20">
              <div className="flex items-center gap-3">
                <Database size={18} className="text-indigo-400" />
                <div>
                  <p className="text-xs text-slate-400">{t('dataset_id')}</p>
                  <p className="text-indigo-300 font-mono text-sm">{datasetId}</p>
                </div>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/dashboard')}
              className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-all duration-200 shadow-glow-sm hover:shadow-glow-md flex items-center justify-center gap-2"
            >
              {t('go_dashboard')} <ArrowRight size={18} />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
