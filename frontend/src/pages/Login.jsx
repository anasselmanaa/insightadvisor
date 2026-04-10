import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api"
import toast from "react-hot-toast"

export default function Login() {
  const navigate  = useNavigate()
  const [form, setForm]           = useState({ email: localStorage.getItem('email') || '', password: '' })
  const [loading, setLoading]     = useState(false)
  const [showForgot, setShowForgot] = useState(false)
  const [rememberMe, setRememberMe] = useState(!!localStorage.getItem('email'))
  const [forgotEmail, setForgotEmail] = useState("")
  const [forgotSent, setForgotSent]   = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post("/auth/login", new URLSearchParams({username: form.email, password: form.password}), {headers: {"Content-Type": "application/x-www-form-urlencoded"}})
      if (rememberMe) localStorage.setItem("token", res.data.access_token)
      else sessionStorage.setItem("token", res.data.access_token)
      localStorage.setItem("email", form.email)
      const me = await api.get("/auth/me")
      localStorage.setItem("username", me.data.username)
      toast.success("Welcome back!")
      navigate("/dashboard")
    } catch (err) {
      toast.error(err.response?.data?.detail || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  function handleForgot(e) {
    e.preventDefault()
    if (!forgotEmail) { toast.error("Enter your email"); return }
    setForgotSent(true)
    toast.success("Reset link sent! Check your email.")
    setTimeout(() => { setShowForgot(false); setForgotSent(false); setForgotEmail("") }, 3000)
  }

  function handleGoogle() {
    toast("Google login coming soon!", { icon: "🚀" })
  }

  return (
    <div style={{ minHeight:"100vh", background:"#050508", fontFamily:"Inter,system-ui,sans-serif", display:"flex", flexDirection:"column", position:"relative", overflow:"hidden" }}>

      <style>{`
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap");
        @keyframes orbFloat { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-20px)} }
        @keyframes beam { 0%{left:-80%;opacity:0} 20%{opacity:1} 80%{opacity:1} 100%{left:100%;opacity:0} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes modalIn { from{opacity:0;transform:translate(-50%,-48%)} to{opacity:1;transform:translate(-50%,-50%)} }
        .beam { position:absolute; height:1px; background:linear-gradient(90deg,transparent,rgba(99,102,241,0.5),rgba(6,182,212,0.3),transparent); animation:beam linear infinite; opacity:0; }
        .form-input:focus { border-color:rgba(99,102,241,0.5) !important; background:rgba(99,102,241,0.05) !important; outline:none; }
        .submit-btn:hover { transform:translateY(-1px); box-shadow:0 8px 24px rgba(99,102,241,0.4); }
        .google-btn:hover { border-color:rgba(255,255,255,0.15) !important; background:rgba(255,255,255,0.04) !important; }
        .forgot-link:hover { color:#818cf8 !important; }
      `}</style>

      {/* Background */}
      <div style={{ position:"absolute", inset:0, backgroundImage:"linear-gradient(rgba(99,102,241,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03) 1px,transparent 1px)", backgroundSize:"40px 40px" }} />
      <div style={{ position:"absolute", width:600, height:600, borderRadius:"50%", background:"radial-gradient(circle,rgba(99,102,241,0.1) 0%,transparent 65%)", top:-200, left:-100, animation:"orbFloat 12s ease-in-out infinite" }} />
      <div style={{ position:"absolute", width:400, height:400, borderRadius:"50%", background:"radial-gradient(circle,rgba(6,182,212,0.07) 0%,transparent 65%)", bottom:-100, right:-50, animation:"orbFloat 15s ease-in-out infinite reverse" }} />
      <div className="beam" style={{ width:"60%", top:"25%", animationDuration:"5s" }} />
      <div className="beam" style={{ width:"45%", top:"55%", animationDuration:"7s", animationDelay:"2s" }} />
      <div className="beam" style={{ width:"55%", top:"75%", animationDuration:"6s", animationDelay:"4s" }} />

      {/* Forgot Password Modal */}
      {showForgot && (
        <div style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.7)", zIndex:100, backdropFilter:"blur(4px)" }} onClick={() => setShowForgot(false)}>
          <div style={{ position:"absolute", top:"50%", left:"50%", transform:"translate(-50%,-50%)", background:"#0d0d1a", border:"1px solid rgba(99,102,241,0.2)", borderRadius:20, padding:32, width:380, animation:"modalIn 0.3s ease-out" }} onClick={e => e.stopPropagation()}>
            <div style={{ fontSize:18, fontWeight:800, color:"#f8fafc", marginBottom:6 }}>Reset your password</div>
            <div style={{ fontSize:12, color:"#334155", marginBottom:24 }}>Enter your email and we will send you a reset link</div>
            {!forgotSent ? (
              <form onSubmit={handleForgot}>
                <input
                  className="form-input"
                  type="email"
                  placeholder="you@company.com"
                  value={forgotEmail}
                  onChange={e => setForgotEmail(e.target.value)}
                  style={{ width:"100%", background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"11px 14px", color:"#e2e8f0", fontSize:13, fontFamily:"inherit", marginBottom:14, boxSizing:"border-box", transition:"all 0.2s" }}
                />
                <button type="submit" style={{ width:"100%", padding:12, background:"linear-gradient(135deg,#6366f1,#4f46e5)", border:"none", borderRadius:10, color:"white", fontSize:13, fontWeight:700, cursor:"pointer", fontFamily:"inherit" }}>
                  Send Reset Link
                </button>
                <button type="button" onClick={() => setShowForgot(false)} style={{ width:"100%", padding:10, background:"transparent", border:"none", color:"#475569", fontSize:12, cursor:"pointer", marginTop:8, fontFamily:"inherit" }}>
                  Cancel
                </button>
              </form>
            ) : (
              <div style={{ textAlign:"center", padding:"20px 0" }}>
                <div style={{ fontSize:32, marginBottom:12 }}>✅</div>
                <div style={{ fontSize:14, color:"#10b981", fontWeight:600 }}>Reset link sent!</div>
                <div style={{ fontSize:12, color:"#334155", marginTop:4 }}>Check your email inbox</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Navbar */}
      <nav style={{ position:"relative", zIndex:10, display:"flex", alignItems:"center", justifyContent:"space-between", padding:"20px 56px", borderBottom:"1px solid rgba(255,255,255,0.05)" }}>
        <Link to="/landing" style={{ display:"flex", alignItems:"center", gap:10, textDecoration:"none" }}>
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect x="3" y="5" width="30" height="20" rx="3" stroke="url(#l2)" strokeWidth="1.8" fill="rgba(99,102,241,0.08)"/>
            <line x1="3" y1="10" x2="33" y2="10" stroke="url(#l2)" strokeWidth="1.2" opacity="0.4"/>
            <line x1="18" y1="25" x2="18" y2="30" stroke="url(#l2)" strokeWidth="1.8" strokeLinecap="round"/>
            <line x1="11" y1="30" x2="25" y2="30" stroke="url(#l2)" strokeWidth="1.8" strokeLinecap="round"/>
            <rect x="7" y="17" width="4" height="6" rx="1" fill="#6366f1" opacity="0.7"/>
            <rect x="13" y="14" width="4" height="9" rx="1" fill="#818cf8"/>
            <rect x="19" y="16" width="4" height="7" rx="1" fill="#22d3ee" opacity="0.8"/>
            <polyline points="9,16 15,13 21,15 25,12" stroke="#f472b6" strokeWidth="1.2" strokeLinecap="round" fill="none"/>
            <circle cx="9" cy="16" r="1.2" fill="#f472b6"/>
            <circle cx="15" cy="13" r="1.2" fill="#f472b6"/>
            <circle cx="21" cy="15" r="1.2" fill="#f472b6"/>
            <circle cx="25" cy="12" r="1.2" fill="#f472b6"/>
            <defs>
              <linearGradient id="l2" x1="0" y1="0" x2="36" y2="36"><stop stopColor="#6366f1"/><stop offset="1" stopColor="#22d3ee"/></linearGradient>
            </defs>
          </svg>
          <div>
            <div style={{ fontSize:18, fontWeight:800, letterSpacing:-0.3, lineHeight:1, color:"#f8fafc" }}>Insight<span style={{ background:"linear-gradient(135deg,#a5b4fc,#22d3ee)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>Advisor</span></div>
            <div style={{ fontSize:8, color:"#334155", textTransform:"uppercase", letterSpacing:"0.12em", marginTop:2 }}>AI Business Analytics</div>
          </div>
        </Link>
        <div style={{ fontSize:13, color:"#334155" }}>
          No account? <Link to="/register" style={{ color:"#6366f1", textDecoration:"none", fontWeight:600 }}>Sign up free</Link>
        </div>
      </nav>

      {/* Main */}
      <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center", padding:"40px 24px", position:"relative", zIndex:10 }}>
        <div style={{ width:"100%", maxWidth:420, animation:"fadeUp 0.6s ease-out both" }}>

          <div style={{ textAlign:"center", marginBottom:32 }}>
            <div style={{ fontSize:28, fontWeight:900, color:"#f8fafc", letterSpacing:-0.5, marginBottom:6 }}>Welcome back</div>
            <div style={{ fontSize:13, color:"#334155" }}>Sign in to your analytics dashboard</div>
          </div>

          <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.07)", borderRadius:20, padding:32, position:"relative", overflow:"hidden" }}>
            <div style={{ position:"absolute", top:0, left:0, right:0, height:1, background:"linear-gradient(90deg,transparent,rgba(99,102,241,0.5),rgba(6,182,212,0.3),transparent)" }} />

            {/* Google */}
            <button className="google-btn" onClick={handleGoogle} style={{ width:"100%", padding:"11px 16px", background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, color:"#94a3b8", fontSize:13, cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", gap:10, fontFamily:"inherit", marginBottom:20, transition:"all 0.2s" }}>
              <svg width="18" height="18" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Continue with Google
            </button>

            <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:20 }}>
              <div style={{ flex:1, height:1, background:"rgba(255,255,255,0.05)" }} />
              <span style={{ fontSize:11, color:"#1e293b" }}>or sign in with email</span>
              <div style={{ flex:1, height:1, background:"rgba(255,255,255,0.05)" }} />
            </div>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom:14 }}>
                <label style={{ fontSize:10, color:"#475569", textTransform:"uppercase", letterSpacing:"0.1em", fontWeight:500, display:"block", marginBottom:6 }}>Email address</label>
                <div style={{ position:"relative" }}>
                  <svg style={{ position:"absolute", left:12, top:"50%", transform:"translateY(-50%)", opacity:0.3 }} width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="white" strokeWidth="1.5"/><polyline points="22,6 12,13 2,6" stroke="white" strokeWidth="1.5"/></svg>
                  <input className="form-input" type="email" placeholder="you@company.com" value={form.email} onChange={e => setForm({...form, email:e.target.value})} required
                    style={{ width:"100%", background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"11px 14px 11px 36px", color:"#e2e8f0", fontSize:13, fontFamily:"inherit", boxSizing:"border-box", transition:"all 0.2s" }} />
                </div>
              </div>

              <div style={{ marginBottom:14 }}>
                <label style={{ fontSize:10, color:"#475569", textTransform:"uppercase", letterSpacing:"0.1em", fontWeight:500, display:"block", marginBottom:6 }}>Password</label>
                <div style={{ position:"relative" }}>
                  <svg style={{ position:"absolute", left:12, top:"50%", transform:"translateY(-50%)", opacity:0.3 }} width="14" height="14" viewBox="0 0 24 24" fill="none"><rect x="3" y="11" width="18" height="11" rx="2" stroke="white" strokeWidth="1.5"/><path d="M7 11V7a5 5 0 0110 0v4" stroke="white" strokeWidth="1.5" strokeLinecap="round"/></svg>
                  <input className="form-input" type="password" placeholder="••••••••••" value={form.password} onChange={e => setForm({...form, password:e.target.value})} required
                    style={{ width:"100%", background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"11px 14px 11px 36px", color:"#e2e8f0", fontSize:13, fontFamily:"inherit", boxSizing:"border-box", transition:"all 0.2s" }} />
                </div>
              </div>

              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:20 }}>
                <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12, color:"#334155", cursor:"pointer" }}>
                  <input type="checkbox" checked={rememberMe} onChange={e => setRememberMe(e.target.checked)} style={{ accentColor:"#6366f1", width:12, height:12 }} />
                  Remember me
                </label>
                <span className="forgot-link" onClick={() => setShowForgot(true)} style={{ fontSize:12, color:"#4338ca", cursor:"pointer", transition:"color 0.2s" }}>
                  Forgot password?
                </span>
              </div>

              <button className="submit-btn" type="submit" disabled={loading} style={{ width:"100%", padding:13, background:"linear-gradient(135deg,#6366f1,#4f46e5)", border:"none", borderRadius:10, color:"white", fontSize:13, fontWeight:700, cursor:"pointer", fontFamily:"inherit", transition:"all 0.2s", display:"flex", alignItems:"center", justifyContent:"center", gap:8, position:"relative", overflow:"hidden" }}>
                {loading ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style={{ animation:"spin 1s linear infinite" }}><circle cx="12" cy="12" r="10" stroke="white" strokeWidth="3" strokeDasharray="31.4" strokeDashoffset="10"/></svg>
                ) : (
                  <>Sign in to InsightAdvisor <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></>
                )}
              </button>
            </form>

            <div style={{ textAlign:"center", marginTop:20, fontSize:12, color:"#1e293b" }}>
              Don&apos;t have an account?{" "}
              <Link to="/register" style={{ color:"#6366f1", textDecoration:"none", fontWeight:600 }}>Create one free</Link>
            </div>
          </div>

          <div style={{ textAlign:"center", marginTop:24, fontSize:10, color:"#1e293b" }}>
            Built by Anass Elmanaa · Sichuan University · insightadvisor.co
          </div>
        </div>
      </div>
    </div>
  )
}