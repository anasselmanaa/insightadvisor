import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LangContext, TContext } from '../context/LangContext'
import { useT } from '../i18n'
import {
  Upload, LayoutDashboard, Users, TrendingUp, BarChart2,
  ShoppingCart, AlertTriangle, LineChart, Bot, FileDown, LogOut,
  Zap, Sun, Moon, Globe
} from 'lucide-react'

const langs = ['EN', 'FR', 'ZH']
const langLabels = { EN: 'EN', FR: 'FR', ZH: '中文' }

export default function Layout() {
  const navigate  = useNavigate()
  const datasetId = localStorage.getItem('dataset_id')
  const [filename, setFilename] = useState(localStorage.getItem('filename') || null)
  const datasetType = localStorage.getItem('dataset_type') || 'generic'

  // Define which pages require specific dataset types
  const pageRequirements = {
    '/apriori': { types: ['retail'], reason: 'Requires transaction data (invoices + products)' },
    '/forecasting': { types: ['retail'], reason: 'Requires date + sales data' },
    '/stock': { types: ['all'], reason: '' },
    '/clustering': { types: ['all'], reason: '' },
    '/regression': { types: ['all'], reason: '' },
    '/anomaly': { types: ['all'], reason: '' },
    '/ai-copilot': { types: ['all'], reason: '' },
    '/reports': { types: ['all'], reason: '' },
  }

  function isPageAvailable(path) {
    const req = pageRequirements[path]
    if (!req) return true
    if (req.types.includes('all')) return true
    if (!localStorage.getItem('dataset_id')) return true // no dataset yet, don't lock
    return req.types.includes(datasetType)
  }

  function getDisabledReason(path) {
    const req = pageRequirements[path]
    if (!req) return ''
    return req.reason || ''
  }
  const [dark, setDark]       = useState(true)
  const [lang, setLang]       = useState('EN')
  const [showLang, setShowLang] = useState(false)
  const t = useT(lang)

  useEffect(() => {
    document.documentElement.classList.toggle('light', !dark)
  }, [dark])

  const nav = [
    { to: '/',            icon: Upload,          label: t('upload'),      color: 'text-violet-400' },
    { to: '/dashboard',   icon: LayoutDashboard, label: t('dashboard'),   color: 'text-indigo-400' },
    { to: '/clustering',  icon: Users,           label: t('clustering'),  color: 'text-cyan-400' },
    { to: '/forecasting', icon: TrendingUp,      label: t('forecasting'), color: 'text-emerald-400' },
    { to: '/regression',  icon: BarChart2,       label: t('regression'),  color: 'text-blue-400' },
    { to: '/apriori',     icon: ShoppingCart,    label: t('apriori'),     color: 'text-amber-400' },
    { to: '/anomaly',     icon: AlertTriangle,   label: t('anomaly'),     color: 'text-red-400' },
    { to: '/stock',       icon: LineChart,       label: t('stock'),       color: 'text-green-400' },
    { to: '/ai-copilot',  icon: Bot,             label: t('ai_copilot'),  color: 'text-pink-400' },
    { to: '/reports',     icon: FileDown,        label: t('reports'),     color: 'text-orange-400' },
  ]

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('dataset_id')
    localStorage.removeItem('username')
    navigate('/login')
  }

  return (
    <LangContext.Provider value={lang}><TContext.Provider value={t}>
    <div className={`flex h-screen overflow-hidden ${dark ? 'bg-dark-900' : 'bg-slate-100'}`}>
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-40 pointer-events-none" />
      {dark && <div className="fixed top-0 left-64 right-0 h-96 bg-glow-indigo pointer-events-none" />}

      <motion.aside
        initial={{ x: -280 }} animate={{ x: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-64 flex-shrink-0 flex flex-col z-10 border-r border-white/5"
        style={{ background: dark ? 'rgba(7,7,15,0.95)' : 'rgba(255,255,255,0.95)', backdropFilter: 'blur(20px)' }}
      >
        {/* Logo + controls */}
        <div className={`px-6 py-6 border-b ${dark ? 'border-white/5' : 'border-slate-200'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <svg width="38" height="38" viewBox="0 0 36 36" fill="none">
                <rect x="3" y="5" width="30" height="20" rx="3" stroke="url(#sl1)" strokeWidth="1.8" fill="rgba(99,102,241,0.08)"/>
                <line x1="3" y1="10" x2="33" y2="10" stroke="url(#sl1)" strokeWidth="1.2" opacity="0.4"/>
                <line x1="18" y1="25" x2="18" y2="30" stroke="url(#sl1)" strokeWidth="1.8" strokeLinecap="round"/>
                <line x1="11" y1="30" x2="25" y2="30" stroke="url(#sl1)" strokeWidth="1.8" strokeLinecap="round"/>
                <rect x="7" y="17" width="4" height="6" rx="1" fill="#6366f1" opacity="0.7"/>
                <rect x="13" y="14" width="4" height="9" rx="1" fill="#818cf8"/>
                <rect x="19" y="16" width="4" height="7" rx="1" fill="#22d3ee" opacity="0.8"/>
                <polyline points="9,16 15,13 21,15 25,12" stroke="#f472b6" strokeWidth="1.2" strokeLinecap="round" fill="none"/>
                <circle cx="9" cy="16" r="1.2" fill="#f472b6"/>
                <circle cx="15" cy="13" r="1.2" fill="#f472b6"/>
                <circle cx="21" cy="15" r="1.2" fill="#f472b6"/>
                <circle cx="25" cy="12" r="1.2" fill="#f472b6"/>
                <defs><linearGradient id="sl1" x1="0" y1="0" x2="36" y2="36"><stop stopColor="#6366f1"/><stop offset="1" stopColor="#22d3ee"/></linearGradient></defs>
              </svg>
              <div>
                <h1 className={`text-lg font-bold tracking-tight leading-none ${dark ? 'text-white' : 'text-slate-800'}`}>
                  Insight<span style={{background:'linear-gradient(135deg,#a5b4fc,#22d3ee)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>Advisor</span>
                </h1>
                <p className="text-slate-500 text-[10px] mt-0.5 uppercase tracking-widest">AI Analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {/* Dark/Light toggle */}
              <button onClick={() => setDark(!dark)}
                className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all ${
                  dark ? 'text-slate-400 hover:text-amber-400 hover:bg-amber-400/10'
                       : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50'
                }`}>
                {dark ? <Sun size={14} /> : <Moon size={14} />}
              </button>
              {/* Language switcher */}
              <div className="relative">
                <button onClick={() => setShowLang(!showLang)}
                  className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all text-[10px] font-bold ${
                    dark ? 'text-slate-400 hover:text-cyan-400 hover:bg-cyan-400/10'
                         : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50'
                  }`}>
                  <Globe size={14} />
                </button>
                {showLang && (
                  <div className={`absolute top-8 right-0 rounded-lg border shadow-lg z-50 overflow-hidden w-20 ${
                    dark ? 'bg-slate-900 border-white/10' : 'bg-white border-slate-200'
                  }`}>
                    {langs.map(l => (
                      <button key={l} onClick={() => { setLang(l); setShowLang(false); localStorage.setItem('lang', l) }}
                        className={`block w-full px-3 py-2 text-xs text-left transition-all ${
                          lang === l
                            ? 'bg-indigo-600 text-white'
                            : dark ? 'text-slate-300 hover:bg-white/5' : 'text-slate-700 hover:bg-slate-50'
                        }`}>
                        {langLabels[l]}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          {filename ? (
            <div className="px-2.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-1.5">
              <span className="text-emerald-400 text-[11px]">📄</span>
              <p className="text-[10px] text-emerald-400 font-medium truncate">{filename}</p>
            </div>
          ) : (
            <div className="px-2.5 py-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center gap-1.5">
              <span className="text-slate-500 text-[11px]">📂</span>
              <p className="text-[10px] text-slate-500">No dataset loaded</p>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
          {nav.map(({ to, icon: Icon, label, color }, i) => (
            <motion.div key={to} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04, duration: 0.3 }}>
              {isPageAvailable(to) ? (
                <NavLink to={to} end={to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group relative ${
                      isActive
                        ? 'bg-indigo-600/20 text-white border border-indigo-500/30 shadow-glow-sm'
                        : dark
                          ? 'text-slate-400 hover:text-white hover:bg-white/5'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`
                  }>
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <motion.div layoutId="activeNav"
                          className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-indigo-400 rounded-full"
                          transition={{ duration: 0.2 }} />
                      )}
                      <Icon size={16} className={isActive ? 'text-indigo-400' : color + ' opacity-60 group-hover:opacity-100'} />
                      <span className="font-medium">{label}</span>
                    </>
                  )}
                </NavLink>
              ) : (
                <div className="relative group cursor-not-allowed">
                  <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm opacity-35">
                    <Icon size={16} className={color} />
                    <span className="font-medium text-slate-400">{label}</span>
                    <span className="ml-auto text-[9px] bg-slate-700 text-slate-400 px-1.5 py-0.5 rounded-full">N/A</span>
                  </div>
                  <div className="absolute left-0 top-full mt-1 hidden group-hover:flex flex-col gap-0.5 bg-slate-900 border border-amber-500/40 text-[11px] px-3 py-2 rounded-lg z-50 shadow-xl" style={{minWidth:'220px'}}>
                    <span className="text-amber-400 font-semibold">⚠️ Not available</span>
                    <span className="text-slate-300">{getDisabledReason(to)}</span>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </nav>

        {/* Bottom */}
        <div className={`px-3 py-4 border-t ${dark ? 'border-white/5' : 'border-slate-200'} space-y-1`}>
          <div className="px-3 py-2 rounded-lg">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">{t('signed_in_as')}</p>
            <p className={`text-xs font-medium truncate ${dark ? 'text-slate-300' : 'text-slate-700'}`}>
              {localStorage.getItem('username') || 'User'}
            </p>
          </div>
          <button onClick={logout}
            className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200">
            <LogOut size={16} />
            <span>{t('logout')}</span>
          </button>
        </div>
      </motion.aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto relative z-10">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.2 }} className="min-h-full">
          <Outlet />
        </motion.div>
      </main>
    </div>
    </TContext.Provider></LangContext.Provider>
  )
}