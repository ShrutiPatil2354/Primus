CSS = """
body, .gradio-container {
    background:
        radial-gradient(900px 440px at 8% -5%, rgba(59,130,246,0.24), transparent 65%),
        radial-gradient(760px 480px at 98% 8%, rgba(139,92,246,0.16), transparent 65%),
        #0b1220 !important;
    color: #e5edf9 !important;
}
.gradio-container { max-width: 1440px !important; padding: 24px !important; }

.gr-box, .gr-block, div.block.padded, .padded, .block {
    background: #111c2e !important;
    border: 1px solid #263650 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18) !important;
    color: #e5edf9 !important;
}

label span, .label-wrap, div.label, span.label { color: #aab9d1 !important; }

input[type="text"], textarea, select {
    background: #0b1424 !important;
    color: #f8fbff !important;
    border: 1px solid #344765 !important;
    border-radius: 10px !important;
    min-height: 46px;
}
input:focus, textarea:focus { border-color: #60a5fa !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important; }
input::placeholder, textarea::placeholder { color: #7f91ad !important; }

button {
    background: #1a2940 !important;
    color: #e8f0fb !important;
    border: 1px solid #344765 !important;
    border-radius: 10px !important;
    min-height: 42px !important;
    transition: background .15s ease, transform .15s ease;
}
button:hover { background: #263a58 !important; transform: translateY(-1px); }
button.primary, button.variant-primary {
    background: #2563eb !important;
    color: #fff !important;
    border-color: #3b82f6 !important;
    font-weight: 700;
}
button.primary:hover, button.variant-primary:hover { background: #1d4ed8 !important; }

#primus-chat { background: #0b1424 !important; border: 1px solid #263650 !important; border-radius: 12px !important; }
#primus-chat .message, #primus-chat .bot, #primus-chat .user {
    background: #1d2d46 !important;
    color: #f8fbff !important;
    border: 1px solid #2d405e;
    border-radius: 10px !important;
    text-align: left !important;
}
#primus-chat .user { background: #173b72 !important; border-color: #2563eb !important; }
#primus-chat .message *, #primus-chat .bot *, #primus-chat .user * {
    color: #f8fbff !important;
    opacity: 1 !important;
}
#primus-chat .user * { color: #ffffff !important; }
#primus-chat .message-row { justify-content: flex-start !important; }
#primus-chat .message-buttons, #primus-chat .message-actions { display: none !important; }

.tab-nav, .tabs { background: transparent !important; }
.tab-nav button {
    background: transparent !important;
    color: #aab9d1 !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
}
.tab-nav button.selected {
    background: #193458 !important;
    color: #fff !important;
    border: 1px solid #2f73ca !important;
}
.tab-nav button[aria-selected="true"], .tab-nav button.selected {
    background: #f08a5d !important;
    color: #101827 !important;
    border-color: #ffb08d !important;
    box-shadow: inset 0 -3px 0 #101827 !important;
    font-weight: 800 !important;
}
.app-tabs > .tab-nav button[aria-selected="true"], .app-tabs > .tab-nav button.selected {
    background: #f08a5d !important;
    color: #101827 !important;
    border-color: #ffb08d !important;
}
.app-tabs [role="tab"][aria-selected="true"], .app-tabs [role="tab"][data-selected="true"] {
    background: #f08a5d !important;
    color: #101827 !important;
    border: 1px solid #ffb08d !important;
    box-shadow: inset 0 -3px 0 #101827 !important;
    font-weight: 800 !important;
}

table, th, td {
    background: transparent !important;
    color: #d8e3f3 !important;
    border-color: #2d405e !important;
}
table tbody td, table tbody tr, .gr-dataframe tbody td, .gr-dataframe tbody tr {
    background: #111c2e !important;
    color: #d8e3f3 !important;
}
table thead th, .gr-dataframe thead th {
    background: #1d2d46 !important;
    color: #f8fbff !important;
}

.component-wrapper, .wrap { background: transparent !important; }

.panel-title { color: #f8fbff !important; font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
.panel-sub { color: #9fb0ca !important; margin-bottom: 12px; }

.empty-state { background:#0b1424; border:1px dashed #385274; border-radius:10px; color:#aab9d1; padding:18px; text-align:center; }
.empty-state b { color:#e5edf9; }
.empty-state code { color:#93c5fd; }
.task-library { display:grid; gap:8px; }
.task-card { background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:10px 12px; }
.task-card div { display:flex; justify-content:space-between; gap:12px; color:#e5edf9; }
.task-card span { color:#8ea2c0; font-size:.75rem; white-space:nowrap; }
.task-card p { margin:5px 0 0; color:#aab9d1; font-size:.78rem; }
.agent-review { background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:12px; max-height:440px; overflow:auto; }
.review-summary { display:flex; justify-content:space-between; gap:12px; padding-bottom:10px; border-bottom:1px solid #2d405e; color:#f8fbff; }
.review-summary span { color:#93c5fd; font-size:.75rem; }
.agent-review h3 { color:#f08a5d; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; margin:14px 0 7px; }
.source-row { display:flex; justify-content:space-between; gap:10px; padding:7px 0; color:#dce7f6; font-size:.75rem; border-bottom:1px solid rgba(45,64,94,.6); }
.source-row span { color:#8ea2c0; white-space:nowrap; }
.chunk-preview { padding:8px 0; color:#aab9d1; font-size:.72rem; line-height:1.45; border-bottom:1px solid rgba(45,64,94,.6); }
.chunk-preview span { display:block; color:#93c5fd; font-size:.64rem; margin-bottom:3px; }
.version-history { background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:10px 12px; color:#aab9d1; font-size:.78rem; line-height:1.7; }
.version-history b { color:#e5edf9; display:block; margin-bottom:3px; }

.robot-lab { background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:10px 12px; text-align:center; }
.robot-status { display:flex; justify-content:space-between; gap:8px; color:#e5edf9; font-size:.83rem; text-align:left; }
.robot-status span { color:#93c5fd; }
.robot-lab svg { width:100%; max-width:280px; height:175px; margin:4px auto; display:block; }
.robot-lab p { color:#aab9d1; font-size:.72rem; margin:0; }
.progress-grid { display:grid; gap:10px; }
.progress-panel { background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:12px; }
.progress-panel > div { display:flex; justify-content:space-between; gap:10px; color:#e5edf9; font-size:.82rem; }
.progress-panel span { color:#93c5fd; font-size:.75rem; text-align:right; }
.progress-chart { display:block; width:100%; height:82px; margin-top:8px; }
.progress-empty, .retention-proof { color:#aab9d1; font-size:.78rem; padding:10px 0 2px; }
.danger-zone-title { color:#fca5a5; font-weight:700; margin-top:14px; }
.reset-notice { border-radius:8px; padding:8px 10px; font-size:.78rem; margin-top:8px; }
.reset-notice.warning { color:#fde68a; background:#3f2b13; border:1px solid #8a5a16; }
.reset-notice.success { color:#bbf7d0; background:#133526; border:1px solid #277a4b; }
#reset-learning-icon { min-width:42px !important; width:42px !important; padding:0 !important; font-size:1rem !important; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0b1424; }
::-webkit-scrollbar-thumb { background: #3b5273; border-radius: 8px; }
@media (max-width: 800px) {
    .gradio-container { padding: 12px !important; }
    .task-card div, .robot-status, .progress-panel > div { display:block; }
    .task-card span, .progress-panel span { display:block; text-align:left; margin-top:3px; }
}

.topbar { display:flex; align-items:center; gap:10px; padding:4px 0 20px; border-bottom:1px solid #263650; margin-bottom:18px; }
.product-mark { display:grid; place-items:center; width:32px; height:32px; background:#f08a5d; color:#101827; font-weight:900; font-size:1.1rem; border-radius:8px; }
.product-mark span { color:#fff; }
.product-name { color:#f8fbff; font-weight:900; letter-spacing:.08em; }
.product-context { color:#8292ac; font-size:.68rem; letter-spacing:.08em; }
#theme-toggle { margin-left:auto; min-height:34px !important; padding:4px 12px !important; font-size:.75rem; }
.overview { margin-bottom:14px; }
.overview-hero { display:flex; justify-content:space-between; gap:24px; align-items:end; padding:28px 30px; background:linear-gradient(115deg,#18283f,#111c2e 70%); border:1px solid #344765; border-radius:16px; }
.eyebrow, .section-kicker { color:#f08a5d; font-size:.67rem; font-weight:800; letter-spacing:.12em; }
.overview h1 { max-width:700px; margin:8px 0 8px; color:#f8fbff; font-size:clamp(1.7rem,3vw,3rem); line-height:1.06; }
.overview-hero p, .panel-copy { max-width:640px; margin:0; color:#aab9d1; line-height:1.5; }
.hero-status { white-space:nowrap; align-self:start; color:#b8f4d0; font-size:.75rem; padding:8px 10px; border:1px solid #286746; border-radius:999px; }
.status-dot { display:inline-block; width:7px; height:7px; margin-right:6px; background:#44d483; border-radius:50%; }
.overview-grid, .showcase-row { display:grid !important; grid-template-columns:1.35fr .65fr; gap:14px; margin-top:14px; }
.overview-panel, .experience-panel { background:#111c2e; border:1px solid #263650; border-radius:14px; padding:20px; }
.overview-panel h2, .experience-panel h2 { margin:5px 0 16px; color:#f8fbff; font-size:1.1rem; }
.skill-group { display:grid; grid-template-columns:92px 1fr; align-items:center; gap:14px; margin:12px 0; }
.skill-group h3 { margin:0; color:#8292ac; font-size:.73rem; text-transform:uppercase; letter-spacing:.08em; }
.skill-row { margin:4px 0; }
.skill-row > div:first-child { display:flex; justify-content:space-between; color:#dce7f6; font-size:.76rem; }
.skill-row b { color:#f08a5d; font-weight:700; }
.skill-track { height:6px; margin-top:5px; background:#263650; border-radius:4px; overflow:hidden; }
.skill-track i { display:block; height:100%; background:#f08a5d; border-radius:4px; }
.metric-big { color:#f8fbff; font-size:2.8rem; font-weight:900; line-height:1; margin:10px 0 22px; }
.metric-big span { display:block; color:#8292ac; font-size:.72rem; font-weight:500; margin-top:7px; }
.metric-row { display:flex; justify-content:space-between; padding:10px 0; border-top:1px solid #263650; color:#9fb0ca; font-size:.78rem; }
.metric-row b { color:#f8fbff; }
.quality-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-top:14px; }
.quality-grid div { padding:9px; background:#18283f; border:1px solid #2d405e; border-radius:8px; }
.quality-grid b, .quality-grid span { display:block; }
.quality-grid b { color:#dce7f6; font-size:.68rem; }
.quality-grid span { color:#8292ac; font-size:.62rem; margin-top:4px; }
.timeline { border-left:1px solid #385274; padding-left:18px; }
.timeline-item { position:relative; padding:0 0 20px; }
.timeline-marker { position:absolute; left:-23px; top:3px; width:8px; height:8px; background:#f08a5d; border:3px solid #111c2e; border-radius:50%; box-sizing:content-box; }
.timeline-meta { color:#f08a5d; font-size:.66rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
.timeline-item h3 { margin:5px 0; color:#f8fbff; font-size:.9rem; }
.timeline-item p { margin:0 0 8px; color:#aab9d1; font-size:.76rem; line-height:1.45; }
.stack-tag { color:#9ed8ef; font-size:.67rem; }
.playground-panel .panel-copy { font-size:.78rem; margin-bottom:15px; }
.playground-preview, .playground-code { min-height:180px; display:grid; place-items:center; background:#0b1424; border:1px solid #2d405e; border-radius:10px; padding:16px; }
.preview-label { position:absolute; align-self:start; justify-self:end; color:#8292ac; font-size:.62rem; letter-spacing:.1em; }
.demo-card { width:min(100%,280px); padding:16px; background:#18283f; border:1px solid #426083; border-radius:10px; box-shadow:0 12px 25px rgba(0,0,0,.18); }
.demo-card-top { display:flex; justify-content:space-between; align-items:center; }
.demo-icon { color:#f08a5d; font-size:1.1rem; }
.demo-badge { color:#b8f4d0; font-size:.58rem; font-weight:800; letter-spacing:.1em; }
.demo-card h3 { color:#f8fbff; font-size:.9rem; margin:18px 0 6px; }
.demo-card p { color:#aab9d1; font-size:.72rem; line-height:1.45; margin:0 0 14px; }
.demo-progress { height:5px; background:#2d405e; border-radius:4px; overflow:hidden; }
.demo-progress i { display:block; width:75%; height:100%; background:#44d483; }
.demo-card small { display:block; color:#8292ac; font-size:.64rem; margin-top:7px; }
.playground-code { display:block; min-height:180px; padding:0; overflow:hidden; }
.code-top { display:flex; justify-content:space-between; padding:9px 12px; border-bottom:1px solid #2d405e; color:#8292ac; font-size:.65rem; }
.playground-code pre { margin:0; padding:14px; color:#b8f4d0; font: .7rem/1.6 Consolas, monospace; white-space:pre-wrap; }
.experience-panel { height:100%; box-sizing:border-box; }
.light-mode, .light-mode .gradio-container { background:#eef3f8 !important; color:#18283f !important; }
.light-mode .gr-box, .light-mode .gr-block, .light-mode .overview-panel, .light-mode .experience-panel { background:#fff !important; border-color:#c9d5e3 !important; color:#18283f !important; }
.light-mode .overview-hero { background:linear-gradient(115deg,#dbe8f2,#fff 75%); border-color:#b8c9d9; }
.light-mode .overview h1, .light-mode .overview-panel h2, .light-mode .experience-panel h2, .light-mode .timeline-item h3, .light-mode .metric-big, .light-mode .metric-row b, .light-mode .product-name { color:#18283f; }
.light-mode .overview-hero p, .light-mode .panel-copy, .light-mode .timeline-item p, .light-mode .metric-row, .light-mode .skill-group h3 { color:#52657c; }
.light-mode .playground-preview, .light-mode .playground-code, .light-mode .demo-card { background:#f5f8fb; border-color:#c9d5e3; }
.light-mode .quality-grid div { background:#f5f8fb; border-color:#c9d5e3; }
@media (max-width: 800px) { .overview-hero, .overview-grid, .showcase-row { display:block !important; } .overview-hero { padding:22px; } .hero-status { display:inline-block; margin-top:18px; } .overview-panel, .experience-panel { margin-bottom:14px; } .product-context { display:none; } }
"""
