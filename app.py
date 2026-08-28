import socket
import gradio as gr

from src.ui import theme
from src.ui import handlers
from src.config import SERVER_PORT


# ---------------------------------------------------------------------------
# Small UI helpers
# ---------------------------------------------------------------------------

def status_bar_html(agent_id=None):
    """Dynamic bottom status bar instead of hard-coded values."""
    try:
        stats = handlers.memory.stats()
        agent = handlers.STORE.get_agent(agent_id) if agent_id else None
        active_name = agent["name"] if agent else "Default Memory (Shared)"
        return f"""
        <div class="app-global-status-bar">
          <div class="status-left-metrics">
            <span class="status-metric-item"><span class="status-dot">●</span>
              Learning: <b>{'Active' if handlers.LEARNING['active'] else 'Idle'}</b>
            </span>
            <span class="status-metric-item">Skills: <b>{stats.get('skills', 0)}</b></span>
            <span class="status-metric-item">Episodes: <b>{stats.get('episodes', 0)}</b></span>
            <span class="status-metric-item">Facts: <b>{stats.get('facts', 0)}</b></span>
            <span class="status-metric-item">Active Agent: <b>{active_name}</b></span>
          </div>
          <div class="status-right-links">
            <span>PRIMUS AI Studio</span>
            <span>v1.0.0</span>
          </div>
        </div>
        """
    except Exception as exc:
        return f"""
        <div class="app-global-status-bar">
          <span class="status-metric-item">Runtime status unavailable</span>
          <span class="status-metric-item">{str(exc)[:100]}</span>
        </div>
        """


def refresh_camera():
    return handlers.camera_html()



def start_camera_ui():
    handlers.start_camera()
    return handlers.camera_html()

def pause_camera_ui():
    handlers.pause_camera()
    return handlers.camera_html()


def flip_camera_ui():
    handlers.flip_camera()
    return handlers.camera_html()


def snapshot_camera_ui():
    handlers.snapshot_camera()
    return handlers.camera_html()


def refresh_all(agent_id=None):
    """One consistent refresh path for UI state."""
    tick = handlers.timer_tick(agent_id)
    return (*tick, status_bar_html(agent_id))


def boot_all():
    try:
        handlers.boot()
    except Exception:
        pass
    return refresh_all("")


def clear_chat_ui(agent_id=None):
    return handlers.clear_session(agent_id)


def create_agent_and_refresh(name, domain, instructions):
    result = handlers.create_agent(name, domain, instructions)
    # Existing handler returns:
    # notice, agent_select, existing_select, overview, knowledge,
    # task_library, task_select, manager, doc_select, sidebar
    return result


def activate_agent(agent_id):
    """Activate the selected custom agent in Workspace."""
    return handlers.choose_existing_agent(agent_id)


def _switch_mode_with_hint(mode):
    file_box, msg_box = handlers.toggle_chat_mode(mode)
    if "Learn" in (mode or ""):
        hint = (
            '<span class="composer-hint">'
            'Attach a document or teach: '
            '<code>Learn &lt;task&gt;: step 1; step 2</code>'
            '</span>'
        )
    else:
        hint = (
            '<span class="composer-hint">'
            'Ask only about knowledge already taught to this active agent.'
            '</span>'
        )
    return file_box, msg_box, hint


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="PRIMUS AI Studio",
    theme=gr.themes.Base(),
    css=theme.CSS,
    fill_width=True,
) as demo:

    # =======================================================================
    # GLOBAL HEADER
    # =======================================================================

    gr.HTML("""
    <header class="app-global-header">
      <div class="app-brand-lockup">
        <span class="app-brand-icon">🧠</span>
        <div>
          <div class="app-brand-name">PRIMUS AI Studio</div>
          <div class="app-brand-sub">Zero-prior interactive learning environment</div>
        </div>
      </div>
      <div class="app-header-right">
        <span class="status-connected">Connected</span>
        <span class="header-action-link">⚙ Settings</span>
        <span class="user-avatar-badge">SP</span>
      </div>
    </header>
    """)

    # =======================================================================
    # PAGES
    # =======================================================================

    with gr.Tabs(elem_classes=["app-tabs"]) as main_tabs:

        # -------------------------------------------------------------------
        # WORKSPACE
        # -------------------------------------------------------------------
        with gr.Tab("Workspace", id="workspace-tab"):

            with gr.Row(elem_classes=["workspace-layout"]):

                # LEFT: agent directory
                with gr.Column(
                    scale=3,
                    min_width=240,
                    elem_classes=["workspace-left", "sidebar-col", "resizable-sidebar"],
                ):
                    with gr.Row(elem_classes=["sidebar-header-row"]):
                        gr.HTML("""
                        <div>
                          <div class="sidebar-header-title">Agents</div>
                          <div class="sidebar-header-sub">
                            Choose the memory space for this session
                          </div>
                        </div>
                        """)
                        new_agent_quick_btn = gr.Button(
                            "➕ New Agent",
                            variant="secondary",
                            scale=0,
                            min_width=105,
                        )

                    agent_select = gr.Dropdown(
                        label="Switch Active Agent",
                        choices=handlers.agent_choices(),
                        value="",
                        interactive=True,
                        show_label=False,
                        allow_custom_value=False,
                        elem_classes=["sidebar-search-box"],
                    )
                    sidebar_hidden_btn = gr.Button("hidden", elem_id="sidebar_hidden_btn", elem_classes=["hidden-trigger"])

                    sidebar_view = gr.HTML(
                        handlers.sidebar_agents_html(),
                        elem_classes=["sidebar-html"],
                    )

                    gr.HTML("""
                    <div class="sidebar-tip">
                      <b>Tip</b>
                      <span>Agents have isolated procedural memory and documents.</span>
                    </div>
                    """)

                # CENTER: chat
                with gr.Column(
                    scale=6,
                    min_width=420,
                    elem_classes=["workspace-center", "chat-col"],
                ):
                    gr.HTML("""
                    <div class="conversation-header">
                      <div>
                        <div class="panel-title">Conversation &amp; Interactive Teaching</div>
                        <div class="panel-sub">
                          Teach procedures, inspect memory, and query only acquired knowledge.
                        </div>
                      </div>
                      <div class="live-pill">● LIVE</div>
                    </div>
                    """)

                    chatbot = gr.Chatbot(
                        height=520,
                        label="Conversation",
                        elem_id="primus-chat",
                        show_label=False,
                        elem_classes=["conversation-area"],
                    )

                    with gr.Group(
                        elem_classes=["composer", "chat-bottom-bar"]
                    ):
                        with gr.Row(elem_classes=["composer-top-row"]):
                            chat_mode = gr.Radio(
                                choices=["💬 Ask Mode", "🎓 Learn Mode"],
                                value="💬 Ask Mode",
                                show_label=False,
                                interactive=True,
                                elem_classes=["mode-toggle-radio"],
                            )
                            use_camera_context = gr.Checkbox(
                                label="Use camera context",
                                value=False,
                                interactive=True,
                            )

                            use_audio_output = gr.Checkbox(
                                label="Enable Voice Reply",
                                value=True,
                                interactive=True,
                            )

                            composer_hint = gr.HTML(
                                '<span class="composer-hint">'
                                'Ask about something PRIMUS already knows...'
                                '</span>',
                                elem_classes=["composer-hint-wrapper"]
                            )

                        with gr.Row(
                            equal_height=True,
                            elem_classes=["input-action-row"],
                        ):
                            doc_upload_box = gr.UploadButton(
                                "+",
                                file_count="single",
                                type="filepath",
                                elem_classes=["compact-upload-btn"],
                                scale=0,
                                min_width=46,
                            )

                            msg = gr.Textbox(
                                show_label=False,
                                scale=6,
                                placeholder=(
                                    "Ask anything based on what you have taught "
                                    "this active agent..."
                                ),
                                elem_classes=["chatgpt-textbox"],
                                max_lines=1,
                                autofocus=True,
                            )


                            audio_in = gr.Audio(visible=False,
                                sources=["microphone"],
                                type="filepath",
                                show_label=False,
                                elem_classes=["compact-audio-input"],
                                scale=0,
                                min_width=50,
                            )
                            send_btn = gr.Button(
                                "\u2191",
                                variant="primary",
                                elem_classes=["chatgpt-send-btn"],
                                scale=0,
                                min_width=40,
                            )

                        with gr.Row(elem_classes=["voice-reply-row"]):
                            voice_out_chat = gr.Audio(
                                show_label=False,
                                interactive=False,
                                autoplay=True,
                                elem_classes=["voice-reply-player"],
                            )

                        with gr.Row(elem_classes=["composer-bottom-row"]):
                            clear_chat_btn = gr.Button(
                                "Clear conversation",
                                variant="secondary",
                                size="sm",
                            )
                            gr.HTML(
                                '<span class="composer-bottom-helper">'
                                'Enter sends · Shift+Enter creates a new line'
                                '</span>'
                            )

                # RIGHT: inspector
                with gr.Column(
                    scale=4,
                    min_width=300,
                    elem_classes=["workspace-right", "inspector-col", "resizable-inspector"],
                ):

                    with gr.Group(elem_classes=["inspector-card"]):
                        with gr.Row(elem_classes=["inspector-card-header"]):
                            gr.HTML(
                                '<div class="inspector-card-title">'
                                '<span>🗄 Active Knowledge</span>'
                                '</div>'
                            )
                            clear_knowledge_btn = gr.Button(
                                "🗑 Clear",
                                elem_classes=["btn-clear-red"],
                                scale=0,
                                min_width=75,
                            )

                        agent_knowledge = gr.HTML(
                            handlers.agent_knowledge_html()
                        )
                        clear_knowledge_notice = gr.HTML()

                    with gr.Group(elem_classes=["inspector-card"]):
                        with gr.Row(elem_classes=["inspector-card-header"]):
                            gr.HTML(
                                '<div class="inspector-card-title">'
                                '<span>⚡ Live Execution</span>'
                                '</div>'
                            )
                            live_badge = gr.HTML(
                                '<span class="badge-idle">● Idle</span>'
                            )

                        plan_html = gr.HTML(handlers.executor.plan_html())
                        learning_html = gr.HTML(handlers.learning_html())

                    with gr.Group(elem_classes=["inspector-card"]):
                        with gr.Row(elem_classes=["inspector-card-header"]):
                            gr.HTML(
                                '<div class="inspector-card-title">'
                                '<span>💬 Activity Log</span>'
                                '</div>'
                            )
                            clear_activity_btn = gr.Button(
                                "Clear",
                                variant="secondary",
                                scale=0,
                                min_width=65,
                            )

                        with gr.Tabs(elem_classes=["activity-tabs"]):
                            with gr.Tab("Messages"):
                                msg_df = gr.HTML(handlers.message_table_html([]), elem_classes=["read-only-table"])
                            with gr.Tab("Actions"):
                                act_df = gr.HTML(handlers.executor_table_html([]), elem_classes=["read-only-table"])

            status_bar = gr.HTML(status_bar_html())

        # -------------------------------------------------------------------
        # BUILD AGENT
        # -------------------------------------------------------------------
        with gr.Tab("Build Your Agent", id="build-agent-tab"):

            gr.HTML("""
            <div class="page-top-banner">
              <div class="page-title-box">
                <div class="eyebrow">AGENT STUDIO</div>
                <h2 class="page-main-title">Build Your Agent</h2>
                <p class="page-main-sub">
                  Create isolated agents, define their response rules, and manage
                  their private procedures and knowledge documents.
                </p>
              </div>
            </div>
            """)

            with gr.Row(elem_classes=["agent-studio-layout"]):

                with gr.Column(
                    scale=5,
                    min_width=360,
                    elem_classes=["agent-studio-left"],
                ):
                    with gr.Group(elem_classes=["studio-card"]):
                        gr.HTML("""
                        <div class="studio-section-title">
                          <span class="step-number">1</span>
                          Create New Custom Agent
                        </div>
                        <div class="panel-sub">
                          Define the identity and behavior before adding knowledge.
                        </div>
                        """)

                        with gr.Row():
                            agent_name = gr.Textbox(
                                label="Agent name",
                                placeholder="e.g. Compliance Assistant",
                            )
                            agent_domain = gr.Textbox(
                                label="Domain",
                                placeholder="e.g. Internal compliance policies",
                            )

                        agent_instructions = gr.Textbox(
                            label="Response rules",
                            lines=4,
                            placeholder=(
                                "Answer only from what I teach you or upload. "
                                "If unknown, say so."
                            ),
                        )

                        create_agent_btn = gr.Button(
                            "➕ Create New Agent",
                            variant="primary",
                        )
                        agent_notice = gr.HTML()

                    with gr.Group(elem_classes=["studio-card"]):
                        gr.HTML("""
                        <div class="studio-section-title">
                          <span class="step-number">2</span>
                          Select &amp; Activate
                        </div>
                        <div class="panel-sub">
                          The active agent controls Workspace memory isolation.
                        </div>
                        """)

                        existing_agent_select = gr.Dropdown(
                            label="Built agents",
                            choices=handlers.custom_agent_choices(),
                            interactive=True,
                        )

                        activate_workspace_btn = gr.Button(
                            "🚀 Set as Active Workspace Agent",
                            variant="secondary",
                        )

                    with gr.Group(elem_classes=["studio-card"]):
                        gr.HTML(
                            '<div class="sidebar-section-header">'
                            '<span>ALL BUILT AGENTS</span></div>'
                        )
                        agent_overview = gr.HTML(
                            handlers.agent_overview_html()
                        )

                with gr.Column(
                    scale=6,
                    min_width=420,
                    elem_classes=["agent-studio-right"],
                ):
                    gr.HTML("""
                    <div class="studio-section-title">
                      <span class="step-number">3</span>
                      Selected Agent Workspace
                    </div>
                    <div class="panel-sub studio-subtitle">
                      Profile, procedures, documents, and destructive controls.
                    </div>
                    """)

                    agent_manager_view = gr.HTML(
                        handlers.agent_manager_html()
                    )

                    with gr.Group(elem_classes=["studio-card"]):
                        gr.HTML(
                            '<div class="sidebar-section-header">'
                            '<span>📚 KNOWLEDGE DOCUMENTS</span></div>'
                        )

                        agent_doc_upload = gr.File(
                            label="Upload document",
                            file_count="single",
                            type="filepath",
                            interactive=True,
                            elem_classes=["agent-doc-upload"],
                        )

                        doc_select = gr.Dropdown(
                            label="Select document to remove",
                            choices=[],
                            interactive=True,
                        )

                        with gr.Row():
                            upload_agent_doc_btn = gr.Button(
                                "📥 Ingest Document",
                                variant="primary",
                            )
                            delete_doc_btn = gr.Button(
                                "🗑 Delete Document",
                                variant="secondary",
                            )

                        agent_doc_notice = gr.HTML()

                    with gr.Group(elem_classes=["danger-card"]):
                        gr.HTML("""
                        <div class="danger-title">⚠ DANGER ZONE</div>
                        <div class="panel-sub">
                          Deleting a custom agent permanently removes its
                          procedures and documents from this UI's store.
                        </div>
                        """)
                        delete_agent_btn = gr.Button(
                            "Delete Entire Custom Agent",
                            variant="stop",
                        )

        # -------------------------------------------------------------------
        # LEARNING / MEMORY
        # -------------------------------------------------------------------
        with gr.Tab("Learning", id="learning-tab"):

            gr.HTML("""
            <div class="page-top-banner compact">
              <div class="eyebrow">MEMORY INSPECTOR</div>
              <h2 class="page-main-title">Learning &amp; Memory</h2>
              <p class="page-main-sub">
                Inspect retained tasks, episodic events, semantic facts,
                feedback, and version history.
              </p>
            </div>
            """)

            with gr.Tabs(elem_classes=["inner-tabs"]):

                with gr.Tab("Activity"):
                    learn_df = gr.HTML(handlers.learning_table_html([]), elem_classes=["read-only-table", "memory-table"])
                    progress_html = gr.HTML(
                        handlers.learning_progress_html()
                    )

                with gr.Tab("Memory"):
                    gr.HTML("""
                    <div class="memory-section-intro">
                      <div>
                        <div class="section-heading">Persistent Memory</div>
                        <div class="panel-sub">
                          Procedural, episodic, semantic, and sensory memory
                          are shown separately.
                        </div>
                      </div>
                      <div class="memory-live-badge">● LIVE</div>
                    </div>
                    """)

                    mem_df = gr.HTML(handlers.memory_table_html([]), elem_classes=["read-only-table", "memory-table"])

                    mem_html = gr.HTML(
                        handlers.memory_html(),
                        elem_classes=["memory-overview"],
                    )

                    gr.HTML("""
                    <div class="danger-divider">
                      <span>DANGER ZONE</span>
                    </div>
                    <div class="panel-sub">
                      Reset removes learned tasks, facts, feedback, and versions.
                    </div>
                    """)

                    reset_memory_btn = gr.Button(
                        "🗑 Reset Learning Data",
                        variant="stop",
                    )
                    reset_confirm = gr.Checkbox(
                        label="I understand this clears all learning data",
                        visible=False,
                    )
                    reset_confirm_btn = gr.Button(
                        "Confirm clear",
                        variant="stop",
                        visible=False,
                    )
                    reset_notice = gr.HTML()

                with gr.Tab("Task Library"):
                    task_search = gr.Textbox(
                        label="Search tasks",
                        placeholder="Filter by task name...",
                        elem_classes=["task-search"],
                    )

                    task_select = gr.Dropdown(
                        label="Task",
                        choices=handlers.task_choices(),
                        interactive=True,
                    )

                    task_library = gr.HTML(
                        handlers.task_library_html()
                    )

                    with gr.Row():
                        task_name = gr.Textbox(
                            label="Task name",
                            scale=2,
                        )
                        task_steps = gr.Textbox(
                            label="Steps",
                            lines=6,
                            scale=3,
                            placeholder=(
                                "One step per line, or separate with ;"
                            ),
                        )

                    version_html = gr.HTML()

                    with gr.Row():
                        task_add = gr.Button(
                            "➕ Add Task",
                            variant="primary",
                        )
                        task_save = gr.Button(
                            "💾 Save Version",
                        )
                        task_delete = gr.Button(
                            "🗑 Delete Task",
                            variant="stop",
                        )

                    task_delete_confirm = gr.Checkbox(
                        label="Confirm task deletion"
                    )
                    task_notice = gr.HTML()

        # -------------------------------------------------------------------
        # PERCEPTION
        # -------------------------------------------------------------------
        with gr.Tab("Perception", id="perception-tab"):

            gr.HTML("""
            <div class="page-top-banner compact">
              <div class="eyebrow">MULTIMODAL INPUT</div>
              <h2 class="page-main-title">Perception Studio</h2>
              <p class="page-main-sub">
                Camera status, snapshots, speech input, and voice responses.
              </p>
            </div>
            """)

            with gr.Row(elem_classes=["perception-layout"]):
                with gr.Column(scale=3):
                    cam_html = gr.HTML(handlers.camera_html())

                    with gr.Row():
                        start_cam_btn = gr.Button("Start Camera")
                        flip_btn = gr.Button("↔ Flip")
                        pause_btn = gr.Button("⏯ Pause / Resume")
                        snap_btn = gr.Button("📸 Snapshot")

                    camera_notice = gr.HTML()

                with gr.Column(scale=2):
                    
                    voice_out = gr.Audio(
                        label="Latest voice reply",
                        interactive=False,
                        autoplay=True,
                    )

        # -------------------------------------------------------------------
        # SYSTEM
        # -------------------------------------------------------------------
        with gr.Tab("System", id="system-tab"):

            gr.HTML("""
            <div class="page-top-banner compact">
              <div class="eyebrow">RUNTIME</div>
              <h2 class="page-main-title">System Health</h2>
              <p class="page-main-sub">
                Compute, memory, model, executor, and perception telemetry.
              </p>
            </div>
            """)

            stats_html = gr.HTML()
            panels_html = gr.HTML()

    # =======================================================================
    # STATE
    # =======================================================================

    chat_state = gr.State([])
    msg_state = gr.State([])

    OUTPUTS = [
        chatbot,
        chat_state,
        msg_df,
        msg_state,
        act_df,
        learn_df,
        mem_df,
        plan_html,
        learning_html,
        mem_html,
        task_library,
        agent_knowledge,
        voice_out,
        voice_out_chat,
        msg,
        doc_upload_box,
        sidebar_view,
    ]

    # =======================================================================
    # EVENT WIRING
    # =======================================================================

    # Mode switch
    chat_mode.change(
        _switch_mode_with_hint,
        inputs=[chat_mode],
        outputs=[doc_upload_box, msg, composer_hint],
    )

    # Quick New Agent -> open Build Your Agent tab
    new_agent_quick_btn.click(
        lambda: gr.update(selected="build-agent-tab"),
        outputs=[main_tabs],
    )

    # Create agent
    create_agent_btn.click(
        create_agent_and_refresh,
        inputs=[agent_name, agent_domain, agent_instructions],
        outputs=[
            agent_notice,
            agent_select,
            existing_agent_select,
            agent_overview,
            agent_knowledge,
            task_library,
            task_select,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
    )
    # Sidebar click event trigger
    def _handle_sidebar_click(js_val):
        updates = handlers.select_agent(js_val)
        return (js_val,) + updates

    sidebar_hidden_btn.click(
        _handle_sidebar_click,
        inputs=[agent_select],
        outputs=[
            agent_select,
            agent_overview,
            agent_knowledge,
            task_library,
            task_select,
            existing_agent_select,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
        js="(x) => [window.__selected_sidebar_agent]"
    )



    # Select built agent
    existing_agent_select.change(
        handlers.choose_existing_agent,
        inputs=[existing_agent_select],
        outputs=[
            agent_select,
            agent_overview,
            agent_knowledge,
            task_library,
            task_select,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
    )

    # Activate selected agent
    activate_workspace_btn.click(
        activate_agent,
        inputs=[existing_agent_select],
        outputs=[
            agent_select,
            agent_overview,
            agent_knowledge,
            task_library,
            task_select,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
    )

    # Workspace agent switch
    agent_select.change(
        handlers.select_agent,
        inputs=[agent_select],
        outputs=[
            agent_overview,
            agent_knowledge,
            task_library,
            task_select,
            existing_agent_select,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
    )

    # Upload custom-agent document
    upload_agent_doc_btn.click(
        handlers.upload_agent_document,
        inputs=[existing_agent_select, agent_doc_upload],
        outputs=[
            agent_doc_notice,
            agent_doc_upload,
            agent_manager_view,
            agent_knowledge,
            agent_overview,
            doc_select,
            sidebar_view,
        ],
    )

    # Delete custom-agent document
    delete_doc_btn.click(
        handlers.delete_agent_doc,
        inputs=[existing_agent_select, doc_select],
        outputs=[
            agent_doc_notice,
            agent_manager_view,
            agent_knowledge,
            agent_overview,
            doc_select,
            sidebar_view,
        ],
    )

    # Delete custom agent
    delete_agent_btn.click(
        handlers.delete_agent_custom,
        inputs=[existing_agent_select],
        outputs=[
            agent_notice,
            agent_overview,
            agent_knowledge,
            agent_manager_view,
            agent_select,
            existing_agent_select,
            task_select,
            doc_select,
            sidebar_view,
        ],
    )

    # Clear active-agent knowledge
    clear_knowledge_btn.click(
        handlers.clear_active_agent_knowledge,
        inputs=[agent_select],
        outputs=[
            clear_knowledge_notice,
            agent_knowledge,
            agent_overview,
            task_library,
            agent_manager_view,
            sidebar_view,
            task_select,
            doc_select,
            plan_html,
            mem_df,
            mem_html,
        ],
    )

    # Clear visible activity session
    clear_activity_btn.click(
        lambda: (handlers.message_table_html([]), handlers.executor_table_html([])),
        outputs=[msg_df, act_df],
    )


    # Clear chat session
    clear_chat_btn.click(
        clear_chat_ui,
        inputs=[agent_select],
        outputs=OUTPUTS,
    )

    # Send message / Enter
    send_btn.click(
        handlers.process_input,
        inputs=[
            msg,
            audio_in,
            chat_state,
            msg_state,
            agent_select,
            use_camera_context,
            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],
        outputs=OUTPUTS,
    )

    msg.submit(
        handlers.process_input,
        inputs=[
            msg,
            audio_in,
            chat_state,
            msg_state,
            agent_select,
            use_camera_context,
            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],
        outputs=OUTPUTS,
    )


    doc_upload_box.upload(
        handlers.process_input,
        inputs=[
            msg,
            audio_in,
            chat_state,
            msg_state,
            agent_select,
            use_camera_context,
            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],
        outputs=OUTPUTS,
    )

    audio_in.stop_recording(
        handlers.process_input,
        inputs=[
            msg,
            audio_in,
            chat_state,
            msg_state,
            agent_select,
            use_camera_context,
            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],
        outputs=OUTPUTS,
    )
    
    audio_in.upload(
        handlers.process_input,
        inputs=[
            msg,
            audio_in,
            chat_state,
            msg_state,
            agent_select,
            use_camera_context,
            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],
        outputs=OUTPUTS,
    )

    chatbot.clear(
        handlers.clear_session,
        inputs=[agent_select],
        outputs=OUTPUTS
    )

    # Task search/editor
    task_search.input(
        handlers.task_choices,
        inputs=[task_search, agent_select],
        outputs=task_select,
    )

    task_select.change(
        handlers.task_editor,
        inputs=[task_select, agent_select],
        outputs=[task_name, task_steps, version_html],
    )

    task_save.click(
        handlers.save_task,
        inputs=[task_select, task_name, task_steps, agent_select],
        outputs=[
            task_notice,
            task_select,
            task_library,
            agent_knowledge,
            task_name,
            task_steps,
            version_html,
        ],
    )

    task_add.click(
        handlers.add_task,
        inputs=[task_name, task_steps, agent_select],
        outputs=[
            task_notice,
            task_select,
            task_library,
            agent_knowledge,
            task_name,
            task_steps,
            version_html,
        ],
    )

    task_delete.click(
        handlers.delete_task,
        inputs=[task_select, task_delete_confirm, agent_select],
        outputs=[
            task_notice,
            task_select,
            task_library,
            agent_knowledge,
            task_name,
            task_steps,
            version_html,
            task_delete_confirm,
        ],
    )

    # Perception
    start_cam_btn.click(
        start_camera_ui,
        outputs=[cam_html],
    )

    use_camera_context.change(
        start_camera_ui,
        outputs=[cam_html]
    )

    flip_btn.click(
        flip_camera_ui,
        outputs=[cam_html],
    )

    pause_btn.click(
        pause_camera_ui,
        outputs=[cam_html],
    )

    snap_btn.click(
        snapshot_camera_ui,
        outputs=[cam_html],
    )

    # Memory reset
    reset_memory_btn.click(
        handlers.show_reset_confirmation,
        inputs=None,
        outputs=[reset_notice, reset_confirm, reset_confirm_btn],
    )

    reset_confirm_btn.click(
        handlers.reset_learning_data,
        inputs=[reset_confirm],
        outputs=[
            reset_notice,
            mem_df,
            mem_html,
            task_library,
            agent_overview,
            agent_knowledge,
            agent_select,
            existing_agent_select,
            task_select,
            progress_html,
            learning_html,
            plan_html,
            agent_manager_view,
            doc_select,
            sidebar_view,
        ],
    )

    # -----------------------------------------------------------------------
    # Runtime refresh
    # -----------------------------------------------------------------------

    TICK_OUTPUTS = [
        stats_html,
        panels_html,
        plan_html,
        learning_html,
        act_df,
        learn_df,
        mem_df,
        mem_html,
        task_library,
        agent_knowledge,
        progress_html,
        status_bar,
    ]

    def _tick(agent_id):
        values = handlers.timer_tick(agent_id)
        return (*values, status_bar_html(agent_id))

    if hasattr(gr, "Timer"):
        timer = gr.Timer(1.5)
        timer.tick(
            _tick,
            inputs=[agent_select],
            outputs=TICK_OUTPUTS,
        )

    demo.load(
        boot_all,
        outputs=TICK_OUTPUTS,
    )


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

def _get_free_port(preferred_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("127.0.0.1", preferred_port)) != 0:
            return preferred_port

    for port in range(preferred_port + 1, preferred_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port

    return preferred_port


if __name__ == "__main__":
    launch_port = _get_free_port(SERVER_PORT)
    print(f"Starting PRIMUS on port {launch_port}...")

    demo.launch(
        server_name="0.0.0.0",
        server_port=launch_port,
        share=False,
        inbrowser=True,
    )
    # Inject sidebar JS on load
    demo.load(None, None, None, js="""
    function() {
        document.addEventListener("click", function(e) {
            let target = e.target.closest(".sidebar-agent-item");
            if (target) {
                let agentId = target.getAttribute("data-agent-id");
                if(agentId === "default") agentId = "";
                window.__selected_sidebar_agent = agentId;
                let btn = document.querySelector("#sidebar_hidden_btn button") || document.querySelector("#sidebar_hidden_btn");
                if (btn) btn.click();
            }
        });
    }
    """)

