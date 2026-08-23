CSS = """
body, .gradio-container {
    background:
        radial-gradient(1100px 600px at 8% 0%, rgba(255,255,255,0.10), transparent 60%),
        radial-gradient(900px 500px at 92% 15%, rgba(255,255,255,0.07), transparent 60%),
        radial-gradient(800px 500px at 50% 100%, rgba(255,255,255,0.06), transparent 60%),
        #050505 !important;
    color: #f5f5f5 !important;
}
.gradio-container { max-width: 1700px !important; }

.gr-box, .gr-block, div.block.padded, .padded, .block {
    background: rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(16px) saturate(140%);
    -webkit-backdrop-filter: blur(16px) saturate(140%);
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
    color: #f5f5f5 !important;
}

label span, .label-wrap, div.label, span.label { color: #a3a3a3 !important; }

input[type="text"], textarea, select {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}
input::placeholder, textarea::placeholder { color: #8a8a8a !important; }

button {
    background: rgba(255,255,255,0.10) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}
button:hover { background: rgba(255,255,255,0.18) !important; }
button.primary, button.variant-primary {
    background: rgba(255,255,255,0.92) !important;
    color: #000 !important;
    border-color: rgba(255,255,255,0.9) !important;
    font-weight: 700;
}

#primus-chat { background: transparent !important; border: none !important; }
#primus-chat .message, #primus-chat .bot, #primus-chat .user {
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(12px);
    color: #f5f5f5 !important;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px !important;
    text-align: left !important;
}
#primus-chat .message-row { justify-content: flex-start !important; }

.tab-nav, .tabs { background: transparent !important; }
.tab-nav button {
    background: rgba(255,255,255,0.05) !important;
    color: #a3a3a3 !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
}
.tab-nav button.selected {
    background: rgba(255,255,255,0.14) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

table, th, td {
    background: transparent !important;
    color: #e5e5e5 !important;
    border-color: rgba(255,255,255,0.10) !important;
}

.component-wrapper, .wrap { background: transparent !important; }

.panel-title { color: #ffffff !important; }
.panel-sub { color: #a3a3a3 !important; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 8px; }
"""