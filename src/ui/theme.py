"""
PRIMUS AI Studio
Complete dark UI theme for Gradio.

This file intentionally owns the visual system instead of relying on
Gradio's light defaults. In particular, all Dataframe/table surfaces are
explicitly styled so the Learning -> Memory page cannot become white.
"""

BG_0 = "#05080f"
BG_1 = "#0b1220"
BG_2 = "#0f1826"
BG_3 = "#141f30"

BORDER = "#1c3252"
BORDER_SOFT = "#152238"

TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

ACCENT_BLUE = "#38bdf8"
ACCENT_PURPLE = "#a855f7"
ACCENT_GREEN = "#22c55e"
ACCENT_ORANGE = "#f97316"
ACCENT_RED = "#ef4444"

FONT_SANS = "'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif"
FONT_MONO = "'JetBrains Mono', 'SF Mono', ui-monospace, monospace"

CSS = f"""
/* ==========================================================================
   0. GLOBAL RESET
   ========================================================================== */

:root,
.dark {{
    --body-background-fill: {BG_0} !important;
    --background-fill-primary: {BG_1} !important;
    --background-fill-secondary: {BG_2} !important;

    --block-background-fill: {BG_1} !important;
    --block-border-color: {BORDER} !important;
    --border-color-primary: {BORDER} !important;

    --body-text-color: {TEXT_PRIMARY} !important;
    --body-text-color-subdued: {TEXT_SECONDARY} !important;

    --input-background-fill: {BG_2} !important;
    --input-border-color: {BORDER} !important;

    --button-primary-background-fill: {ACCENT_BLUE} !important;
    --button-primary-text-color: #04121f !important;

    --button-secondary-background-fill: {BG_2} !important;
    --button-secondary-text-color: {TEXT_PRIMARY} !important;
    --button-secondary-border-color: {BORDER} !important;

    color-scheme: dark;
}}

html,
body,
.gradio-container {{
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100% !important;
    background: {BG_0} !important;
    color: {TEXT_PRIMARY} !important;
    font-family: {FONT_SANS} !important;
}}

.gradio-container {{
    max-width: none !important;
    width: 100% !important;
}}

* {{
    box-sizing: border-box !important;
}}

button,
input,
textarea,
select {{
    font-family: inherit !important;
}}

button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {{
    outline: 2px solid {ACCENT_BLUE} !important;
    outline-offset: 2px !important;
}}


/* ==========================================================================
   1. GRADIO SURFACE NORMALIZATION
   ========================================================================== */

.gradio-container .gr-block,
.gradio-container .gr-box,
.gradio-container .gr-panel,
.gradio-container .gr-group,
.gradio-container .gr-form,
.gradio-container .block {{
    background-color: {BG_1} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {BORDER} !important;
}}

.gradio-container .gr-row,
.gradio-container .gr-column {{
    min-width: 0 !important;
}}

.gradio-container .gr-row {{
    background: transparent !important;
}}

.gradio-container label,
.gradio-container label span {{
    color: {TEXT_SECONDARY} !important;
}}

.gradio-container .prose,
.gradio-container .prose *,
.gradio-container p,
.gradio-container span {{
    color: inherit;
}}

.gradio-container input,
.gradio-container textarea,
.gradio-container select {{
    background: {BG_2} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {BORDER} !important;
}}

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {{
    color: {TEXT_MUTED} !important;
}}


/* ==========================================================================
   2. HEADER
   ========================================================================== */

.app-global-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    min-height: 66px;
    padding: 12px 24px;
    background: {BG_1} !important;
    border-bottom: 1px solid {BORDER};
}}

.app-brand-lockup {{
    display: flex;
    align-items: center;
    gap: 11px;
    min-width: 0;
}}

.app-brand-icon {{
    font-size: 1.45rem;
}}

.app-brand-name {{
    color: {TEXT_PRIMARY} !important;
    font-size: 1.05rem;
    font-weight: 850;
    letter-spacing: .01em;
}}

.app-brand-sub {{
    color: {TEXT_MUTED} !important;
    font-size: .68rem;
    margin-top: 2px;
}}

.app-header-right {{
    display: flex;
    align-items: center;
    gap: 18px;
}}

.status-connected {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: {ACCENT_GREEN} !important;
    font-size: .74rem;
    font-weight: 750;
}}

.status-connected::before {{
    content: "●";
    font-size: .55rem;
}}

.header-action-link {{
    color: {TEXT_SECONDARY} !important;
    font-size: .78rem;
}}

.user-avatar-badge {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 31px;
    height: 31px;
    border-radius: 50%;
    background: linear-gradient(135deg, {ACCENT_BLUE}, {ACCENT_PURPLE});
    color: #04121f !important;
    font-size: .7rem;
    font-weight: 850;
}}


/* ==========================================================================
   3. MAIN TABS
   ========================================================================== */

.app-tabs {{
    background: {BG_0} !important;
}}

.app-tabs > .tab-nav {{
    background: {BG_1} !important;
    border-bottom: 1px solid {BORDER} !important;
    padding: 0 18px !important;
    gap: 2px !important;
}}

.app-tabs > .tab-nav button {{
    background: transparent !important;
    color: {TEXT_MUTED} !important;
    border: 0 !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 16px !important;
    font-size: .82rem !important;
    font-weight: 700 !important;
}}

.app-tabs > .tab-nav button:hover {{
    color: {TEXT_PRIMARY} !important;
}}

.app-tabs > .tab-nav button.selected {{
    color: {TEXT_PRIMARY} !important;
    border-bottom-color: {ACCENT_BLUE} !important;
}}

.app-tabs > .tabitem {{
    background: {BG_0} !important;
    padding: 0 !important;
}}


/* ==========================================================================
   4. COMMON TYPOGRAPHY
   ========================================================================== */

.panel-title,
.page-main-title {{
    color: {TEXT_PRIMARY} !important;
    font-weight: 850 !important;
}}

.panel-title {{
    font-size: .98rem;
}}

.panel-sub,
.page-main-sub {{
    color: {TEXT_SECONDARY} !important;
}}

.panel-sub {{
    font-size: .72rem;
    line-height: 1.5;
}}

.page-top-banner {{
    padding: 22px 24px 12px;
}}

.page-top-banner.compact {{
    padding-bottom: 8px;
}}

.page-main-title {{
    margin: 2px 0 0;
    font-size: 1.3rem;
}}

.page-main-sub {{
    margin: 5px 0 0;
    font-size: .82rem;
    max-width: 850px;
}}

.eyebrow {{
    color: {ACCENT_BLUE} !important;
    font-size: .63rem;
    font-weight: 850;
    letter-spacing: .14em;
}}

.section-heading {{
    color: {TEXT_PRIMARY} !important;
    font-size: .9rem;
    font-weight: 800;
}}

.sub-heading {{
    color: {TEXT_SECONDARY} !important;
    font-size: .72rem;
    font-weight: 700;
}}


/* ==========================================================================
   5. WORKSPACE THREE-COLUMN LAYOUT
   ========================================================================== */

.workspace-layout {{
    gap: 14px !important;
    padding: 14px 18px 8px !important;
    align-items: stretch !important;
}}

.sidebar-col,
.inspector-col,
.chat-col {{
    background: {BG_1} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 13px !important;
}}

.sidebar-col,
.inspector-col {{
    padding: 13px !important;
}}

.chat-col {{
    padding: 13px !important;
    min-height: 720px !important;
    display: flex !important;
    flex-direction: column !important;
}}

.workspace-center {{
    min-width: 0 !important;
}}

.workspace-left,
.workspace-right {{
    min-width: 0 !important;
}}

.resizable-sidebar {{
    resize: horizontal !important;
    overflow: auto !important;
    min-width: 240px !important;
    max-width: 430px !important;
}}

.resizable-inspector {{
    resize: horizontal !important;
    overflow: auto !important;
    min-width: 290px !important;
    max-width: 480px !important;
}}


/* ==========================================================================
   6. SIDEBAR
   ========================================================================== */

.sidebar-header-row {{
    align-items: center !important;
}}

.sidebar-header-title {{
    color: {TEXT_PRIMARY} !important;
    font-size: .95rem;
    font-weight: 850;
}}

.sidebar-header-sub {{
    color: {TEXT_MUTED} !important;
    font-size: .7rem;
    margin-top: 2px;
}}

.sidebar-search-box {{
    margin-top: 3px;
}}

.sidebar-tip {{
    display: flex;
    flex-direction: column;
    gap: 3px;
    margin-top: auto;
    padding: 10px;
    border: 1px dashed {BORDER};
    border-radius: 9px;
    background: {BG_2};
    color: {TEXT_MUTED};
    font-size: .67rem;
    line-height: 1.45;
}}

.sidebar-tip b {{
    color: {TEXT_SECONDARY};
}}

.agent-sidebar-list {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    overflow-y: auto;
    max-height: 510px;
    padding-right: 3px;
}}

.agent-nav-item {{
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 9px;
    border: 1px solid transparent;
    border-radius: 9px;
    cursor: pointer;
}}

.agent-nav-item:hover {{
    background: {BG_2};
}}

.agent-nav-item.active {{
    background: rgba(56, 189, 248, .08);
    border-color: rgba(56, 189, 248, .32);
}}

.agent-avatar-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 31px;
    height: 31px;
    min-width: 31px;
    border-radius: 8px;
    background: {BG_3};
    color: {TEXT_PRIMARY};
}}

.agent-nav-info {{
    min-width: 0;
    flex: 1;
}}

.agent-nav-name {{
    overflow: hidden;
    color: {TEXT_PRIMARY};
    font-size: .78rem;
    font-weight: 750;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.agent-nav-meta {{
    overflow: hidden;
    color: {TEXT_MUTED};
    font-size: .64rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}}


/* ==========================================================================
   7. CHAT
   ========================================================================== */

.conversation-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 1px 2px 10px;
}}

.live-pill,
.memory-live-badge {{
    color: {ACCENT_GREEN} !important;
    background: rgba(34, 197, 94, .08);
    border: 1px solid rgba(34, 197, 94, .25);
    border-radius: 999px;
    padding: 4px 8px;
    font-size: .62rem;
    font-weight: 800;
}}

.conversation-area {{
    flex: 1 1 auto !important;
    min-height: 430px !important;
    background: {BG_0} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 11px !important;
    overflow: auto !important;
}}

#primus-chat {{
    background: {BG_0} !important;
}}

#primus-chat .message {{
    color: {TEXT_PRIMARY} !important;
}}

#primus-chat .bubble-wrap {{
    max-width: 85%;
}}

#primus-chat .user {{
    background: rgba(56, 189, 248, .10) !important;
    border-color: rgba(56, 189, 248, .22) !important;
}}

#primus-chat .bot {{
    background: {BG_2} !important;
    border-color: {BORDER} !important;
}}

.composer {{
    margin-top: 9px !important;
    padding: 10px !important;
    background: {BG_1} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 11px !important;
}}

.composer-top-row {{
    align-items: center !important;
    gap: 8px !important;
}}

.mode-toggle-radio {{
    flex: 0 0 auto !important;
}}

.mode-toggle-radio label {{
    background: {BG_2} !important;
    border-color: {BORDER} !important;
    color: {TEXT_SECONDARY} !important;
    border-radius: 999px !important;
}}

.mode-toggle-radio label.selected,
.mode-toggle-radio input:checked + span {{
    background: {ACCENT_BLUE} !important;
    color: #04121f !important;
    border-color: {ACCENT_BLUE} !important;
}}

.camera-context-toggle {{
    flex: 0 0 auto !important;
}}

.camera-context-toggle label span {{
    color: {TEXT_SECONDARY} !important;
    font-size: .68rem !important;
}}

.composer-hint {{
    color: {TEXT_MUTED} !important;
    font-size: .67rem;
    line-height: 1.4;
}}

.composer-hint code {{
    color: {ACCENT_BLUE} !important;
}}

.input-action-row {{
    align-items: flex-end !important;
    gap: 8px !important;
}}

.chatgpt-textbox textarea {{
    min-height: 44px !important;
    background: {BG_2} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 9px !important;
}}

.chatgpt-send-btn {{
    min-height: 44px !important;
    background: {ACCENT_BLUE} !important;
    color: #04121f !important;
    border: 0 !important;
    font-weight: 800 !important;
}}

.compact-file-input {{
    min-width: 110px !important;
}}

.composer-bottom-row {{
    align-items: center !important;
    margin-top: 4px;
}}

.composer-bottom-helper {{
    margin-left: auto;
    color: {TEXT_MUTED} !important;
    font-size: .64rem;
}}


/* ==========================================================================
   8. INSPECTOR / CARDS
   ========================================================================== */

.inspector-card,
.studio-card {{
    background: {BG_1} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 11px !important;
}}

.inspector-card-header {{
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 7px;
}}

.inspector-card-title span {{
    color: {TEXT_PRIMARY} !important;
    font-size: .82rem;
    font-weight: 850;
}}

.badge-idle {{
    color: {TEXT_MUTED} !important;
    font-size: .65rem;
    font-weight: 750;
}}

.btn-clear-red {{
    color: #fca5a5 !important;
}}

.built-agents-list {{
    display: flex;
    flex-direction: column;
    gap: 7px;
}}

.built-agent-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 9px;
    background: {BG_2};
    border: 1px solid {BORDER_SOFT};
    border-radius: 9px;
}}

.built-agent-main {{
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 0;
}}

.built-agent-icon {{
    font-size: 1rem;
}}

.built-agent-name {{
    color: {TEXT_PRIMARY};
    font-size: .78rem;
    font-weight: 750;
}}

.built-agent-domain {{
    color: {TEXT_MUTED};
    font-size: .64rem;
}}

.meta-badge,
.procedure-badge,
.doc-badge {{
    color: {ACCENT_BLUE};
    background: rgba(56, 189, 248, .08);
    border: 1px solid rgba(56, 189, 248, .22);
    border-radius: 999px;
    padding: 2px 7px;
    font-size: .61rem;
    font-weight: 700;
    white-space: nowrap;
}}


/* ==========================================================================
   9. KNOWLEDGE / MEMORY HTML
   ========================================================================== */

.knowledge-panel {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.knowledge-title-box {{
    display: flex;
    align-items: center;
    gap: 9px;
}}

.knowledge-icon {{
    font-size: 1.2rem;
}}

.knowledge-title {{
    color: {TEXT_PRIMARY};
    font-size: .8rem;
    font-weight: 850;
}}

.knowledge-sub {{
    color: {TEXT_SECONDARY};
    font-size: .65rem;
    margin-top: 2px;
}}

.panel-section-title,
.sidebar-section-header {{
    color: {TEXT_SECONDARY};
    font-size: .65rem;
    font-weight: 850;
    letter-spacing: .07em;
}}

.procedure-list,
.doc-list,
.task-library {{
    display: flex;
    flex-direction: column;
    gap: 7px;
    max-height: 330px;
    overflow-y: auto;
    padding-right: 2px;
}}

.procedure-item,
.doc-item {{
    padding: 9px 10px;
    background: {BG_2};
    border: 1px solid {BORDER_SOFT};
    border-radius: 8px;
}}

.procedure-head,
.doc-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}}

.procedure-name,
.doc-name {{
    color: {TEXT_PRIMARY};
    font-size: .72rem;
    font-weight: 750;
}}

.procedure-steps,
.doc-preview {{
    color: {TEXT_SECONDARY};
    font-size: .66rem;
    line-height: 1.45;
    margin-top: 5px;
}}

.empty-state {{
    padding: 18px 12px;
    text-align: center;
    color: {TEXT_SECONDARY};
    background: {BG_2};
    border: 1px dashed {BORDER};
    border-radius: 9px;
    font-size: .73rem;
    line-height: 1.5;
}}

.version-history {{
    padding: 9px 10px;
    background: {BG_2};
    border: 1px solid {BORDER_SOFT};
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: .67rem;
    line-height: 1.5;
}}


/* ==========================================================================
   10. DATAFRAME — CRITICAL MEMORY PAGE FIX
   ========================================================================== */

/*
   Gradio Dataframe is the main reason the Memory tab can appear white.
   Do not rely only on Gradio theme variables. Explicitly paint every layer.
*/

.dark-dataframe,
.memory-table,
.gradio-dataframe,
[data-testid="dataframe"] {{
    background: {BG_1} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

.dark-dataframe *,
.memory-table *,
.gradio-dataframe *,
[data-testid="dataframe"] * {{
    box-sizing: border-box !important;
}}

.dark-dataframe .wrap,
.memory-table .wrap,
.gradio-dataframe .wrap,
[data-testid="dataframe"] .wrap,
.dark-dataframe .table-wrap,
.memory-table .table-wrap,
.gradio-dataframe .table-wrap,
[data-testid="dataframe"] .table-wrap {{
    background: {BG_1} !important;
    color: {TEXT_PRIMARY} !important;
}}

.dark-dataframe table,
.memory-table table,
.gradio-dataframe table,
[data-testid="dataframe"] table {{
    width: 100% !important;
    background: {BG_2} !important;
    color: {TEXT_PRIMARY} !important;
    border-collapse: collapse !important;
}}

.dark-dataframe thead,
.memory-table thead,
.gradio-dataframe thead,
[data-testid="dataframe"] thead {{
    background: {BG_3} !important;
}}

.dark-dataframe th,
.memory-table th,
.gradio-dataframe th,
[data-testid="dataframe"] th {{
    background: {BG_3} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {BORDER} !important;
    font-size: .7rem !important;
    font-weight: 800 !important;
    padding: 10px 9px !important;
}}

.dark-dataframe td,
.memory-table td,
.gradio-dataframe td,
[data-testid="dataframe"] td {{
    background: {BG_2} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {BORDER_SOFT} !important;
    font-size: .72rem !important;
    padding: 9px !important;
}}

.dark-dataframe tbody tr:nth-child(even) td,
.memory-table tbody tr:nth-child(even) td,
.gradio-dataframe tbody tr:nth-child(even) td,
[data-testid="dataframe"] tbody tr:nth-child(even) td {{
    background: {BG_1} !important;
}}

.dark-dataframe tbody tr:hover td,
.memory-table tbody tr:hover td,
.gradio-dataframe tbody tr:hover td,
[data-testid="dataframe"] tbody tr:hover td {{
    background: {BG_3} !important;
}}

.dark-dataframe input,
.memory-table input,
.gradio-dataframe input,
[data-testid="dataframe"] input {{
    background: {BG_2} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {BORDER} !important;
}}

.dark-dataframe button,
.memory-table button,
.gradio-dataframe button,
[data-testid="dataframe"] button {{
    background: {BG_2} !important;
    color: {TEXT_SECONDARY} !important;
    border-color: {BORDER} !important;
}}

.memory-overview {{
    display: block;
    margin-top: 10px;
}}

.memory-section-intro {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 0 0 9px;
}}

.danger-divider {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 15px;
    color: #fca5a5;
    font-size: .67rem;
    font-weight: 850;
    letter-spacing: .08em;
}}

.danger-divider::before,
.danger-divider::after {{
    content: "";
    height: 1px;
    background: rgba(239, 68, 68, .25);
}}

.danger-divider::before {{
    width: 20px;
}}

.danger-divider::after {{
    flex: 1;
}}


/* ==========================================================================
   11. LEARNING TELEMETRY
   ========================================================================== */

.progress-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 12px;
}}

.progress-panel {{
    padding: 13px;
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

.progress-panel b {{
    color: {TEXT_PRIMARY};
    font-size: .78rem;
}}

.progress-panel span {{
    display: block;
    color: {TEXT_SECONDARY};
    font-size: .68rem;
    margin-top: 2px;
}}

.retention-proof {{
    margin-top: 9px;
    padding-top: 9px;
    border-top: 1px solid {BORDER_SOFT};
    color: {TEXT_SECONDARY};
    font-size: .67rem;
    line-height: 1.5;
}}

.learning-telemetry-active,
.learning-telemetry-idle {{
    margin-top: 8px;
    padding: 10px 11px;
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: 9px;
}}

.learning-telemetry-head {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
}}

.learning-telemetry-title {{
    color: {TEXT_SECONDARY};
    font-size: .68rem;
}}

.learning-telemetry-title b {{
    color: {ACCENT_GREEN};
}}

.learning-telemetry-count {{
    color: {ACCENT_BLUE};
    font-size: .64rem;
    font-weight: 750;
}}

.learning-progress-bar {{
    height: 6px;
    margin-top: 8px;
    background: {BG_1};
    border-radius: 999px;
    overflow: hidden;
}}

.learning-progress-bar div {{
    height: 100%;
    background: linear-gradient(90deg, {ACCENT_BLUE}, {ACCENT_PURPLE});
    border-radius: 999px;
    transition: width .25s ease;
}}

.learning-telemetry-badge {{
    color: {TEXT_SECONDARY};
    font-size: .7rem;
    font-weight: 750;
}}

.pulse-dot {{
    color: {ACCENT_GREEN};
}}

.learning-telemetry-stats {{
    margin-top: 3px;
    color: {TEXT_MUTED};
    font-size: .64rem;
}}


/* ==========================================================================
   12. AGENT STUDIO
   ========================================================================== */

.agent-studio-layout {{
    gap: 14px !important;
    padding: 0 24px 20px !important;
    align-items: flex-start !important;
}}

.agent-studio-left,
.agent-studio-right {{
    min-width: 0 !important;
}}

.studio-card {{
    padding: 14px !important;
    margin-bottom: 12px !important;
}}

.studio-section-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: {TEXT_PRIMARY};
    font-size: .86rem;
    font-weight: 850;
    margin-bottom: 3px;
}}

.step-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 23px;
    height: 23px;
    border-radius: 7px;
    background: rgba(56, 189, 248, .1);
    border: 1px solid rgba(56, 189, 248, .25);
    color: {ACCENT_BLUE};
    font-size: .67rem;
}}

.studio-subtitle {{
    margin-bottom: 10px;
}}

.selected-agent-workspace {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.agent-profile-card {{
    padding: 14px;
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

.profile-header {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.profile-icon {{
    font-size: 1.5rem;
}}

.profile-title {{
    margin: 0;
    color: {TEXT_PRIMARY};
    font-size: .95rem;
}}

.profile-domain {{
    margin: 2px 0 0;
    color: {TEXT_SECONDARY};
    font-size: .7rem;
}}

.profile-rules {{
    margin: 10px 0 0;
    padding-top: 10px;
    border-top: 1px solid {BORDER_SOFT};
    color: {TEXT_SECONDARY};
    font-size: .7rem;
    line-height: 1.55;
}}

.agent-stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
}}

.stat-box {{
    padding: 10px;
    text-align: center;
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: 9px;
}}

.stat-label {{
    color: {TEXT_SECONDARY};
    font-size: .62rem;
}}

.stat-val {{
    display: block;
    margin-top: 3px;
    color: {TEXT_PRIMARY};
    font-size: 1rem;
    font-weight: 850;
}}

.stat-val.status-active {{
    color: {ACCENT_GREEN};
    font-size: .72rem;
}}

.danger-card {{
    padding: 13px !important;
    background: rgba(127, 29, 29, .08) !important;
    border: 1px solid rgba(239, 68, 68, .25) !important;
    border-radius: 10px !important;
}}

.danger-title {{
    color: #fca5a5;
    font-size: .75rem;
    font-weight: 850;
    letter-spacing: .06em;
}}


/* ==========================================================================
   13. GLOBAL STATUS BAR
   ========================================================================== */

.app-global-status-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin: 4px 18px 14px;
    padding: 9px 13px;
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: 9px;
}}

.status-left-metrics,
.status-right-links {{
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}}

.status-metric-item {{
    color: {TEXT_SECONDARY};
    font-size: .65rem;
}}

.status-metric-item b {{
    color: {TEXT_PRIMARY};
}}

.status-dot {{
    color: {ACCENT_GREEN};
}}

.status-right-links {{
    color: {TEXT_MUTED};
    font-size: .63rem;
}}


/* ==========================================================================
   14. SYSTEM / PERCEPTION
   ========================================================================== */

.perception-layout {{
    gap: 14px !important;
    padding: 0 24px 20px !important;
}}

.perception-layout > .gr-column {{
    min-width: 0 !important;
}}

#primus-stream {{
    display: block;
    width: 100%;
    min-height: 260px;
    object-fit: contain;
    background: #000;
}}

.gradio-container audio {{
    background: {BG_2} !important;
}}

.reset-notice {{
    margin-top: 7px;
    padding: 8px 10px;
    border-radius: 8px;
    font-size: .7rem;
    line-height: 1.45;
}}

.reset-notice.success {{
    color: #86efac !important;
    background: rgba(34, 197, 94, .08);
    border: 1px solid rgba(34, 197, 94, .22);
}}

.reset-notice.warning {{
    color: #fca5a5 !important;
    background: rgba(239, 68, 68, .08);
    border: 1px solid rgba(239, 68, 68, .22);
}}


/* ==========================================================================
   15. SCROLLBARS
   ========================================================================== */

* {{
    scrollbar-width: thin;
    scrollbar-color: {BORDER} {BG_0};
}}

*::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

*::-webkit-scrollbar-track {{
    background: {BG_0};
}}

*::-webkit-scrollbar-thumb {{
    background: {BORDER};
    border-radius: 999px;
}}

*::-webkit-scrollbar-thumb:hover {{
    background: #29466f;
}}


/* ==========================================================================
   16. RESPONSIVE
   ========================================================================== */

@media (max-width: 1100px) {{
    .workspace-layout {{
        flex-direction: column !important;
    }}

    .resizable-sidebar,
    .resizable-inspector {{
        width: 100% !important;
        max-width: none !important;
        resize: none !important;
    }}

    .chat-col {{
        min-height: 620px !important;
    }}

    .agent-stats-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .progress-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 720px) {{
    .app-global-header {{
        padding: 10px 14px;
    }}

    .app-header-right .header-action-link {{
        display: none;
    }}

    .app-tabs > .tab-nav {{
        overflow-x: auto !important;
    }}

    .app-tabs > .tab-nav button {{
        white-space: nowrap !important;
    }}

    .workspace-layout,
    .agent-studio-layout,
    .perception-layout {{
        padding-left: 10px !important;
        padding-right: 10px !important;
    }}

    .input-action-row {{
        flex-wrap: wrap !important;
    }}

    .compact-file-input,
    .chatgpt-textbox,
    .chatgpt-send-btn {{
        width: 100% !important;
        min-width: 0 !important;
    }}

    .agent-stats-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .status-right-links {{
        display: none;
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    *,
    *::before,
    *::after {{
        animation: none !important;
        transition: none !important;
    }}
}}
"""



CSS += r"""
/* ========================================================================== 
   FINAL READ-ONLY EVENT TABLES
   ========================================================================== */

.read-only-table,
.event-table-card {{
    width: 100% !important;
    background: transparent !important;
    color: #f1f5f9 !important;
}}

.event-table-card {{
    border: 1px solid #1c3252;
    border-radius: 10px;
    background: #0b1220 !important;
    overflow: hidden;
}}

.event-table-title {{
    padding: 10px 12px;
    border-bottom: 1px solid #1c3252;
    color: #f1f5f9;
    background: #0f1826;
    font-size: 0.78rem;
    font-weight: 800;
}}

.event-table-scroll {{
    width: 100%;
    max-height: 300px;
    overflow: auto;
}}

.event-table {{
    width: 100%;
    min-width: 620px;
    border-collapse: collapse;
    border-spacing: 0;
    background: #0f1826 !important;
    color: #f1f5f9 !important;
    font-size: 0.76rem;
}}

.event-table thead th {{
    position: sticky;
    top: 0;
    z-index: 2;
    padding: 10px 11px;
    text-align: left;
    white-space: nowrap;
    background: #141f30 !important;
    color: #cbd5e1 !important;
    border-bottom: 1px solid #1c3252;
    font-weight: 800;
}}

.event-table tbody td {{
    padding: 10px 11px;
    vertical-align: top;
    background: #0f1826 !important;
    color: #e2e8f0 !important;
    border-bottom: 1px solid #152238;
    line-height: 1.4;
}}

.event-table tbody tr:nth-child(even) td {{
    background: #0b1220 !important;
}}

.event-table tbody tr:hover td {{
    background: #141f30 !important;
}}

.event-table-empty {{
    height: 90px;
    text-align: center !important;
    color: #64748b !important;
}}

.memory-tab .read-only-table {{
    margin: 10px 20px 0;
    width: calc(100% - 40px) !important;
}}

.memory-tab .memory-overview {{
    margin: 12px 20px 24px !important;
}}

@media (max-width: 720px) {{
    .event-table {{
        min-width: 520px;
    }}
    .memory-tab .read-only-table {{
        margin-left: 10px;
        margin-right: 10px;
        width: calc(100% - 20px) !important;
    }}
    .memory-tab .memory-overview {{
        margin-left: 10px !important;
        margin-right: 10px !important;
    }}
}}
"""


CSS += r"""
/* ========================================================================== 
   MEMORY OVERVIEW CARDS
   ========================================================================== */

.memory-overview-content {
    width: 100%;
    color: #f1f5f9 !important;
}

.memory-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
}

.memory-stat-card {
    min-height: 74px;
    padding: 11px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: #0b1220 !important;
    border: 1px solid #1c3252;
    border-radius: 10px;
}

.memory-stat-value {
    font-size: 1.25rem;
    line-height: 1;
    font-weight: 850;
}

.memory-stat-value.procedural { color: #38bdf8 !important; }
.memory-stat-value.episodic { color: #a855f7 !important; }
.memory-stat-value.semantic { color: #22c55e !important; }
.memory-stat-value.sensory { color: #f97316 !important; }

.memory-stat-label {
    color: #94a3b8 !important;
    font-size: .68rem;
    font-weight: 700;
}

.memory-detail-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 12px;
}

.memory-detail-card {
    min-width: 0;
    padding: 13px;
    background: #0b1220 !important;
    border: 1px solid #1c3252;
    border-radius: 10px;
}

.memory-detail-title {
    margin-bottom: 8px;
    color: #f1f5f9 !important;
    font-size: .78rem;
    font-weight: 850;
}

.memory-detail-title span {
    color: #94a3b8 !important;
    font-weight: 700;
}

.memory-detail-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.memory-fact-row,
.memory-slot-row {
    display: grid;
    grid-template-columns: auto minmax(80px, max-content) minmax(0, 1fr);
    gap: 7px;
    align-items: start;
    color: #cbd5e1 !important;
    font-size: .69rem;
    line-height: 1.45;
    overflow-wrap: anywhere;
}

.memory-slot-row {
    grid-template-columns: minmax(95px, max-content) minmax(0, 1fr);
}

.memory-fact-row b,
.memory-slot-row b {
    color: #f1f5f9 !important;
}

.memory-bullet {
    color: #38bdf8 !important;
}

.memory-empty-line {
    color: #64748b !important;
    font-size: .69rem;
}

@media (max-width: 850px) {
    .memory-stat-grid,
    .memory-detail-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 560px) {
    .memory-stat-grid,
    .memory-detail-grid {
        grid-template-columns: 1fr;
    }
}
"""


CSS += r"""
/* ========================================================================== 
   FINAL READ-ONLY TABLE OVERRIDE
   ========================================================================== */

.read-only-table,
.read-only-table .event-table-card,
.event-table-card {
    width: 100% !important;
    max-width: 100% !important;
    background: #0b1220 !important;
    color: #f1f5f9 !important;
    border-color: #1c3252 !important;
}

.event-table-card {
    border: 1px solid #1c3252 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

.event-table-scroll {
    max-height: 320px !important;
    overflow: auto !important;
    background: #0b1220 !important;
}

.event-table {
    width: 100% !important;
    min-width: 600px !important;
    border-collapse: collapse !important;
    background: #0f1826 !important;
    color: #f1f5f9 !important;
}

.event-table thead,
.event-table thead tr {
    background: #141f30 !important;
}

.event-table thead th {
    position: sticky !important;
    top: 0 !important;
    z-index: 3 !important;
    background: #141f30 !important;
    color: #f1f5f9 !important;
    border-bottom: 1px solid #1c3252 !important;
    padding: 10px 11px !important;
    text-align: left !important;
    font-size: 0.73rem !important;
    font-weight: 800 !important;
}

.event-table tbody tr,
.event-table tbody td {
    background: #0f1826 !important;
    color: #e2e8f0 !important;
}

.event-table tbody tr:nth-child(even) td {
    background: #0b1220 !important;
}

.event-table tbody tr:hover td {
    background: #141f30 !important;
    color: #ffffff !important;
}

.event-table tbody td {
    border-bottom: 1px solid #152238 !important;
    padding: 10px 11px !important;
    vertical-align: top !important;
    line-height: 1.45 !important;
    font-size: 0.74rem !important;
}

.event-table-empty {
    background: #0b1220 !important;
    color: #64748b !important;
    text-align: center !important;
}

/* Memory page: show table AND the cards below it without clipping. */
.memory-tab {
    overflow: visible !important;
    background: #05080f !important;
}

.memory-tab .read-only-table {
    margin: 10px 24px 0 !important;
    width: calc(100% - 48px) !important;
}

.memory-tab .memory-overview {
    margin: 12px 24px 28px !important;
    overflow: visible !important;
}

@media (max-width: 720px) {
    .memory-tab .read-only-table {
        margin-left: 10px !important;
        margin-right: 10px !important;
        width: calc(100% - 20px) !important;
    }

    .memory-tab .memory-overview {
        margin-left: 10px !important;
        margin-right: 10px !important;
    }
}
"""


CSS += r"""
/* ========================================================================== 
   FINAL PAGE-SCROLL BEHAVIOR
   ========================================================================== */

.app-tabs > .tabitem {
    overflow-x: hidden !important;
    overflow-y: auto !important;
    min-height: 0 !important;
}

/* Workspace is a full-height application workspace; its children own their
   internal scroll areas. */
.workspace-layout {
    overflow: hidden !important;
}

.chat-col,
.sidebar-col,
.inspector-col {
    min-height: 0 !important;
}

/* Minimal Audio Input Button */
.compact-audio-input {
    min-width: 46px !important;
    max-width: 46px !important;
    height: 46px !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}
.compact-audio-input > div, .compact-audio-input .wrap {
    border: none !important;
    background: transparent !important;
}
.compact-audio-input button {
    min-width: 46px !important;
    height: 46px !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 50% !important;
    background: #0f1c30 !important;
    border: 1px solid #182a46 !important;
}
.compact-audio-input button:hover {
    background: #142540 !important;
    border-color: #38bdf8 !important;
}
.compact-audio-input label > span:first-child,
.compact-audio-input [data-testid="waveform"],
.compact-audio-input .audio-container,
.compact-audio-input .clear-button {
    display: none !important;
}


/* ChatGPT-like Pill Input Bar */
.input-action-row {
    background: #0b1424 !important;
    border: 1px solid #344765 !important;
    border-radius: 26px !important;
    padding: 6px 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

.input-action-row > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

.chatgpt-textbox textarea {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    min-height: 40px !important;
    padding: 10px 0 !important;
}

.compact-upload-btn {
    min-width: 40px !important;
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    background: transparent !important;
    border: none !important;
    font-size: 1.2rem !important;
    color: #aab9d1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.compact-upload-btn:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #fff !important;
}

.compact-audio-input button {
    background: transparent !important;
    border: none !important;
    color: #aab9d1 !important;
    font-size: 1.2rem !important;
}
.compact-audio-input button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #fff !important;
}

.chatgpt-send-btn {
    min-width: 40px !important;
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    background: #3b82f6 !important;
    border: none !important;
    color: #fff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.2rem !important;
}
.chatgpt-send-btn:hover {
    background: #2563eb !important;
}


/* Hidden Trigger for Sidebar Clicks */
.hidden-trigger {
    display: none !important;
}

"""
