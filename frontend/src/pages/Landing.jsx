import { useNavigate } from "react-router-dom"

export default function Landing() {
  const navigate = useNavigate()

  const stats = [
    { value: "96",   label: "Quality Score", color: "#818cf8" },
    { value: "4",    label: "Segments",      color: "#22d3ee" },
    { value: "+34%", label: "Forecast",      color: "#10b981" },
    { value: "2K",   label: "Anomalies",     color: "#f472b6" },
  ]
  const bars = [40,65,50,80,60,90,95,88]

  const features = [
    { icon: "📊", title: "6 ML Models", desc: "KMeans clustering, ARIMA forecasting, Linear Regression, Apriori rules, Isolation Forest anomaly detection, and SHAP explainability — all in one platform." },
    { icon: "🤖", title: "AI Copilot", desc: "Get strategic recommendations, action plans, and natural language queries powered by a large language model. Ask anything about your data." },
    { icon: "📄", title: "One-click Export", desc: "Download a professional PDF report, PowerPoint presentation, or Excel spreadsheet with all your analysis results instantly." },
    { icon: "🔒", title: "Secure Auth", desc: "JWT-based authentication with encrypted passwords. Your data stays private and protected at all times." },
  ]

  const analytics = [
    { icon: "👥", title: "Customer Segmentation", desc: "Automatically group your customers into meaningful segments using KMeans + RFM analysis. Understand who your best customers are." },
    { icon: "📈", title: "Sales Forecasting", desc: "Predict future revenue with ARIMA time series models. Get confidence intervals and trend indicators for the next 7-90 days." },
    { icon: "🔍", title: "Anomaly Detection", desc: "Isolation Forest automatically flags suspicious transactions. Every anomaly comes with a plain English explanation of why it was flagged." },
    { icon: "🛒", title: "Market Basket Analysis", desc: "Discover which products are frequently bought together using the Apriori algorithm. Get rules in plain English like 87% of customers who buy X also buy Y." },
  ]

  return (
    <div style={{ minHeight:"100vh", background:"#050508", fontFamily:"Inter,system-ui,sans-serif", position:"relative" }}>
      <style>{`
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap");
        @keyframes orbFloat { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-20px)} }
        @keyframes beam { 0%{left:-80%;opacity:0} 20%{opacity:1} 80%{opacity:1} 100%{left:100%;opacity:0} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes barGrow { from{transform:scaleY(0.6)} to{transform:scaleY(1)} }
        @keyframes floatCard { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
        .beam { position:absolute; height:1px; background:linear-gradient(90deg,transparent,rgba(99,102,241,0.5),rgba(6,182,212,0.3),transparent); animation:beam linear infinite; opacity:0; }
        .nav-link:hover { color:#94a3b8 !important; }
        .btn-primary:hover { transform:translateY(-2px); box-shadow:0 12px 32px rgba(99,102,241,0.4) !important; }
        .btn-secondary:hover { border-color:rgba(255,255,255,0.2) !important; color:#94a3b8 !important; }
        .feature-card:hover { border-color:rgba(99,102,241,0.3) !important; background:rgba(99,102,241,0.05) !important; transform:translateY(-4px); }
        .feature-card { transition: all 0.2s; }
        html { scroll-behavior: smooth; }
      `}</style>

      <div style={{ position:"fixed", inset:0, backgroundImage:"linear-gradient(rgba(99,102,241,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03) 1px,transparent 1px)", backgroundSize:"40px 40px", pointerEvents:"none" }} />
      <div style={{ position:"fixed", width:600, height:600, borderRadius:"50%", background:"radial-gradient(circle,rgba(99,102,241,0.1) 0%,transparent 65%)", top:-200, left:-100, animation:"orbFloat 12s ease-in-out infinite", pointerEvents:"none" }} />
      <div style={{ position:"fixed", width:400, height:400, borderRadius:"50%", background:"radial-gradient(circle,rgba(6,182,212,0.07) 0%,transparent 65%)", bottom:-100, right:-50, animation:"orbFloat 15s ease-in-out infinite reverse", pointerEvents:"none" }} />

      <nav style={{ position:"sticky", top:0, zIndex:100, display:"flex", alignItems:"center", justifyContent:"space-between", padding:"22px 56px", borderBottom:"1px solid rgba(255,255,255,0.05)", background:"rgba(5,5,8,0.9)", backdropFilter:"blur(20px)" }}>
        <div style={{ display:"flex", alignItems:"center", gap:12 }}>
          <svg width="40" height="40" viewBox="0 0 36 36" fill="none">
            <rect x="3" y="5" width="30" height="20" rx="3" stroke="url(#l1)" strokeWidth="1.8" fill="rgba(99,102,241,0.08)"/>
            <line x1="3" y1="10" x2="33" y2="10" stroke="url(#l1)" strokeWidth="1.2" opacity="0.4"/>
            <line x1="18" y1="25" x2="18" y2="30" stroke="url(#l1)" strokeWidth="1.8" strokeLinecap="round"/>
            <line x1="11" y1="30" x2="25" y2="30" stroke="url(#l1)" strokeWidth="1.8" strokeLinecap="round"/>
            <rect x="7" y="17" width="4" height="6" rx="1" fill="#6366f1" opacity="0.7"/>
            <rect x="13" y="14" width="4" height="9" rx="1" fill="#818cf8"/>
            <rect x="19" y="16" width="4" height="7" rx="1" fill="#22d3ee" opacity="0.8"/>
            <polyline points="9,16 15,13 21,15 25,12" stroke="#f472b6" strokeWidth="1.2" strokeLinecap="round" fill="none"/>
            <circle cx="9" cy="16" r="1.2" fill="#f472b6"/>
            <circle cx="15" cy="13" r="1.2" fill="#f472b6"/>
            <circle cx="21" cy="15" r="1.2" fill="#f472b6"/>
            <circle cx="25" cy="12" r="1.2" fill="#f472b6"/>
            <defs><linearGradient id="l1" x1="0" y1="0" x2="36" y2="36"><stop stopColor="#6366f1"/><stop offset="1" stopColor="#22d3ee"/></linearGradient></defs>
          </svg>
          <div>
            <div style={{ fontSize:20, fontWeight:900, letterSpacing:-0.5, lineHeight:1, color:"#f8fafc" }}>Insight<span style={{ background:"linear-gradient(135deg,#a5b4fc,#22d3ee)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>Advisor</span></div>
            <div style={{ fontSize:9, color:"#334155", textTransform:"uppercase", letterSpacing:"0.15em", marginTop:2 }}>AI Business Analytics</div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:32 }}>
          {[["Features","#features"],["Analytics","#analytics"],["About","#about"]].map(([l,href]) => (
            <a key={l} href={href} className="nav-link" style={{ fontSize:14, color:"#475569", cursor:"pointer", transition:"color 0.2s", fontWeight:500, textDecoration:"none" }}>{l}</a>
          ))}
        </div>
        <button onClick={() => navigate("/login")} className="btn-primary" style={{ padding:"11px 28px", background:"linear-gradient(135deg,#6366f1,#4f46e5)", border:"none", borderRadius:10, fontSize:14, fontWeight:700, color:"white", cursor:"pointer", fontFamily:"inherit", transition:"all 0.2s" }}>Sign In →</button>
      </nav>

      <div style={{ position:"relative", zIndex:10, display:"flex", alignItems:"center", padding:"80px 56px", gap:56, minHeight:"calc(100vh - 81px)" }}>
        <div style={{ flex:1, animation:"fadeUp 0.7s ease-out both" }}>
          <div style={{ display:"inline-flex", alignItems:"center", gap:8, background:"rgba(99,102,241,0.08)", border:"1px solid rgba(99,102,241,0.2)", borderRadius:100, padding:"5px 16px", fontSize:12, marginBottom:32, width:"fit-content" }}>
            <div style={{ width:6, height:6, borderRadius:"50%", background:"#6366f1", animation:"pulse 2s ease-in-out infinite" }} />
            <span style={{ color:"#818cf8", fontWeight:600 }}>New</span>
            <div style={{ width:1, height:10, background:"rgba(99,102,241,0.3)" }} />
            <span style={{ color:"#22d3ee", fontWeight:600 }}>AI Copilot v2.0 is live</span>
          </div>
          <h1 style={{ fontSize:58, fontWeight:900, lineHeight:1.1, letterSpacing:-2, margin:0 }}>
            <span style={{ color:"#f8fafc" }}>Modern</span><br/>
            <span style={{ background:"linear-gradient(135deg,#818cf8,#22d3ee)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>Analytics</span><br/>
            <span style={{ color:"#f8fafc" }}>for Retail</span><br/>
            <span style={{ color:"#f8fafc" }}>Businesses</span>
          </h1>
          <p style={{ fontSize:16, color:"#475569", lineHeight:1.85, maxWidth:480, margin:"24px 0 36px" }}>Upload your data and get AI-powered customer segmentation, sales forecasting, anomaly detection, and actionable recommendations — all in one platform.</p>
          <div style={{ display:"flex", gap:14, marginBottom:44 }}>
            <button className="btn-primary" onClick={() => navigate("/login")} style={{ display:"flex", alignItems:"center", gap:8, padding:"14px 32px", background:"linear-gradient(135deg,#6366f1,#4f46e5)", border:"none", borderRadius:12, fontSize:14, fontWeight:700, color:"white", cursor:"pointer", fontFamily:"inherit", transition:"all 0.2s" }}>Start Analyzing →</button>
            <a href="#features" className="btn-secondary" style={{ display:"flex", alignItems:"center", gap:8, padding:"14px 28px", background:"transparent", border:"1px solid rgba(255,255,255,0.1)", borderRadius:12, fontSize:14, color:"#64748b", cursor:"pointer", fontFamily:"inherit", transition:"all 0.2s", textDecoration:"none" }}>Learn More ↓</a>
          </div>
          <div style={{ display:"flex", gap:36 }}>
            {[["6","ML Models"],["200K+","Rows Analyzed"],["3","Languages"],["5min","Time to Insight"]].map(([n,l]) => (
              <div key={l}>
                <div style={{ fontSize:22, fontWeight:900, background:"linear-gradient(135deg,#818cf8,#22d3ee)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>{n}</div>
                <div style={{ fontSize:11, color:"#334155", marginTop:3 }}>{l}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ width:520, animation:"floatCard 5s ease-in-out infinite", flexShrink:0 }}>
          <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:20, padding:24, position:"relative", overflow:"hidden" }}>
            <div style={{ position:"absolute", top:0, left:0, right:0, height:1, background:"linear-gradient(90deg,transparent,rgba(99,102,241,0.5),rgba(6,182,212,0.3),transparent)" }} />
            <div style={{ display:"flex", gap:6, marginBottom:20 }}>
              <div style={{ width:12, height:12, borderRadius:"50%", background:"#ef4444" }} />
              <div style={{ width:12, height:12, borderRadius:"50%", background:"#f59e0b" }} />
              <div style={{ width:12, height:12, borderRadius:"50%", background:"#10b981" }} />
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:12 }}>
              {stats.map(({ value, label, color }) => (
                <div key={label} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:12, padding:"16px" }}>
                  <div style={{ fontSize:30, fontWeight:800, color, fontFamily:"monospace", lineHeight:1 }}>{value}</div>
                  <div style={{ fontSize:12, color:"#475569", marginTop:6 }}>{label}</div>
                </div>
              ))}
            </div>
            <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.05)", borderRadius:12, padding:"16px" }}>
              <div style={{ fontSize:12, color:"#475569", marginBottom:12 }}>Revenue forecast</div>
              <div style={{ display:"flex", alignItems:"flex-end", gap:6, height:64 }}>
                {bars.map((h, i) => (
                  <div key={i} style={{ flex:1, height:`${h}%`, borderRadius:"3px 3px 0 0", background: i >= 5 ? "linear-gradient(to top,#22d3ee,#06b6d4)" : "linear-gradient(to top,#6366f1,#818cf8)", animation:`barGrow 1s ease-out ${i*0.1}s both`, transformOrigin:"bottom" }} />
                ))}
              </div>
              <div style={{ display:"flex", justifyContent:"space-between", marginTop:8 }}>
                <span style={{ fontSize:10, color:"#334155" }}>Historical</span>
                <span style={{ fontSize:10, color:"#22d3ee" }}>Forecast →</span>
              </div>
            </div>
            <div style={{ display:"flex", gap:8, marginTop:12, flexWrap:"wrap" }}>
              {[["AI Copilot","#6366f1"],["ARIMA","#22d3ee"],["KMeans","#f472b6"],["Isolation Forest","#10b981"]].map(([t,c]) => (
                <div key={t} style={{ padding:"4px 10px", background:`${c}15`, border:`1px solid ${c}30`, borderRadius:100, fontSize:10, color:c, fontWeight:500 }}>{t}</div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div id="features" style={{ position:"relative", zIndex:10, padding:"100px 56px", borderTop:"1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ textAlign:"center", marginBottom:60 }}>
          <div style={{ display:"inline-block", padding:"4px 16px", background:"rgba(99,102,241,0.1)", border:"1px solid rgba(99,102,241,0.2)", borderRadius:100, fontSize:12, color:"#818cf8", fontWeight:600, marginBottom:16 }}>FEATURES</div>
          <h2 style={{ fontSize:40, fontWeight:900, color:"#f8fafc", letterSpacing:-1, margin:"0 0 16px" }}>Everything you need in one platform</h2>
          <p style={{ fontSize:16, color:"#475569", maxWidth:500, margin:"0 auto" }}>Built for SMEs who cannot afford Tableau or Power BI — get enterprise-level analytics for free.</p>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:20, maxWidth:1200, margin:"0 auto" }}>
          {features.map(({ icon, title, desc }) => (
            <div key={title} className="feature-card" style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:16, padding:24 }}>
              <div style={{ fontSize:32, marginBottom:16 }}>{icon}</div>
              <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:10 }}>{title}</div>
              <div style={{ fontSize:13, color:"#475569", lineHeight:1.7 }}>{desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div id="analytics" style={{ position:"relative", zIndex:10, padding:"100px 56px", borderTop:"1px solid rgba(255,255,255,0.05)", background:"rgba(99,102,241,0.02)" }}>
        <div style={{ textAlign:"center", marginBottom:60 }}>
          <div style={{ display:"inline-block", padding:"4px 16px", background:"rgba(6,182,212,0.1)", border:"1px solid rgba(6,182,212,0.2)", borderRadius:100, fontSize:12, color:"#22d3ee", fontWeight:600, marginBottom:16 }}>ANALYTICS</div>
          <h2 style={{ fontSize:40, fontWeight:900, color:"#f8fafc", letterSpacing:-1, margin:"0 0 16px" }}>Powerful analysis, zero complexity</h2>
          <p style={{ fontSize:16, color:"#475569", maxWidth:500, margin:"0 auto" }}>From raw CSV to actionable insights in under 5 minutes — no data science degree required.</p>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:20, maxWidth:1200, margin:"0 auto" }}>
          {analytics.map(({ icon, title, desc }) => (
            <div key={title} className="feature-card" style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:16, padding:24 }}>
              <div style={{ fontSize:32, marginBottom:16 }}>{icon}</div>
              <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:10 }}>{title}</div>
              <div style={{ fontSize:13, color:"#475569", lineHeight:1.7 }}>{desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div id="about" style={{ position:"relative", zIndex:10, padding:"100px 56px", borderTop:"1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ maxWidth:800, margin:"0 auto", textAlign:"center" }}>
          <div style={{ display:"inline-block", padding:"4px 16px", background:"rgba(244,114,182,0.1)", border:"1px solid rgba(244,114,182,0.2)", borderRadius:100, fontSize:12, color:"#f472b6", fontWeight:600, marginBottom:16 }}>ABOUT</div>
          <h2 style={{ fontSize:40, fontWeight:900, color:"#f8fafc", letterSpacing:-1, margin:"0 0 16px" }}>Built for the 99%</h2>
          <p style={{ fontSize:16, color:"#475569", lineHeight:1.85, marginBottom:48 }}>InsightAdvisor was designed and developed by <span style={{ color:"#818cf8", fontWeight:600 }}>Anass Elmanaa</span>, a Software Engineering graduate from Sichuan University (2026). Our mission is to democratize data analytics — every business owner deserves powerful insights without a $70,000/year price tag.</p>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:20, marginBottom:48 }}>
            {[
              { icon:"🎯", title:"Our Mission", desc:"Make enterprise-level analytics accessible to every SME — in their language, in under 5 minutes." },
              { icon:"🌍", title:"Our Vision", desc:"Every business owner in Morocco, Canada, or China should make data-driven decisions without needing a data scientist." },
              { icon:"📧", title:"Contact", desc:"Questions or partnerships? Reach out at anasselmanaa7@gmail.com — we respond within 24 hours." },
            ].map(({ icon, title, desc }) => (
              <div key={title} className="feature-card" style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:16, padding:24, textAlign:"left" }}>
                <div style={{ fontSize:28, marginBottom:12 }}>{icon}</div>
                <div style={{ fontSize:14, fontWeight:700, color:"#e2e8f0", marginBottom:8 }}>{title}</div>
                <div style={{ fontSize:13, color:"#475569", lineHeight:1.7 }}>{desc}</div>
              </div>
            ))}
          </div>
          <button onClick={() => navigate("/login")} className="btn-primary" style={{ padding:"16px 48px", background:"linear-gradient(135deg,#6366f1,#4f46e5)", border:"none", borderRadius:12, fontSize:15, fontWeight:700, color:"white", cursor:"pointer", fontFamily:"inherit", transition:"all 0.2s" }}>Get Started Free →</button>
        </div>
      </div>

      <div style={{ borderTop:"1px solid rgba(255,255,255,0.05)", padding:"24px 56px", display:"flex", alignItems:"center", justifyContent:"center", position:"relative", zIndex:10 }}>
        <div style={{ fontSize:11, color:"#1e293b" }}>Built by Anass Elmanaa · Sichuan University · anasselmanaa7@gmail.com</div>
      </div>
    </div>
  )
}
