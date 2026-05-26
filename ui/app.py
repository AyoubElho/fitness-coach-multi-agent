import logging
import html
import re
import sys
import warnings
from pathlib import Path
from uuid import uuid4

import streamlit as st
from langgraph.types import Command

warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

sys.path.insert(0, str(Path(__file__).parent.parent))

from graph import graph

AGENTS = [
    (
        "goal_analyzer",
        "Goal Analyzer",
        "Structures your goal, timeframe, level, and constraints.",
    ),
    (
        "workout_designer",
        "Workout Designer",
        "Builds a weekly training plan around your schedule.",
    ),
    (
        "nutrition_planner",
        "Nutrition Planner",
        "Creates calories, macros, hydration, and meal ideas.",
    ),
    (
        "progress_tracker",
        "Progress Tracker",
        "Adds measurable checkpoints before final approval.",
    ),
]

AGENT_LABELS = {
    "supervisor": "Supervisor",
    **{agent_id: label for agent_id, label, _ in AGENTS},
}

STAGE_PROGRESS = {
    "input": 8,
    "running": 48,
    "awaiting_approval": 78,
    "done": 100,
}

st.set_page_config(page_title="Fitness Coach Studio", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --app-bg: #f6f7fb;
    --surface: #ffffff;
    --surface-soft: #eef3f8;
    --ink: #17202a;
    --muted: #697386;
    --line: #dde4ee;
    --green: #00a878;
    --blue: #2563eb;
    --coral: #ff6b5f;
    --amber: #f4b942;
}

html, body, [class*="css"], [class*="st-"], [data-testid], [data-baseweb] {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.material-icons,
.material-symbols-rounded,
.material-symbols-outlined,
span[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: inherit;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: "liga";
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "liga";
}

code, pre {
    font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
}

.stApp {
    background:
        linear-gradient(180deg, rgba(37, 99, 235, 0.07), rgba(246, 247, 251, 0) 260px),
        var(--app-bg);
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: #101827;
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: rgba(248, 250, 252, 0.82);
}

[data-testid="stSidebar"] .stProgress > div > div > div > div {
    background: var(--green);
}

section[data-testid="stMain"] label,
section[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stMain"] [role="radiogroup"] label,
section[data-testid="stMain"] [role="radiogroup"] span,
section[data-testid="stMain"] .stSlider label,
section[data-testid="stMain"] .stSlider span {
    color: var(--ink) !important;
}

section[data-testid="stMain"] [data-testid="stWidgetLabel"] {
    color: var(--ink) !important;
}

section[data-testid="stMain"] [role="radiogroup"] {
    gap: 0.65rem;
}

section[data-testid="stMain"] [role="radiogroup"] label {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 8px 10px;
    min-width: 118px;
}

section[data-testid="stMain"] [role="radiogroup"] label:has(input:checked) {
    border-color: rgba(37, 99, 235, 0.42);
    background: rgba(37, 99, 235, 0.08);
}

section[data-testid="stMain"] [data-testid="stMainBlockContainer"],
.main .block-container {
    max-width: 1320px;
    padding: 4.25rem clamp(1rem, 2.4vw, 2rem) 3rem;
}

h1, h2, h3 {
    color: var(--ink);
    letter-spacing: 0;
}

.top-band {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 0.85rem;
    box-shadow: 0 12px 34px rgba(16, 24, 39, 0.07);
}

.top-band h1 {
    margin: 0 0 6px 0;
    font-size: clamp(2rem, 3.6vw, 3.2rem);
    line-height: 1.02;
}

.top-band p {
    margin: 0;
    color: var(--muted);
    max-width: 760px;
    font-size: 1.02rem;
}

.section-title {
    margin: 0.9rem 0 0.6rem;
    color: var(--ink);
    font-size: 1.05rem;
    font-weight: 800;
}

.coach-grid {
    display: grid;
    gap: 10px;
}

.coach-card,
.metric-tile,
.plan-shell,
.approval-shell {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 10px 24px rgba(16, 24, 39, 0.06);
}

.coach-card {
    padding: 14px 15px;
}

.coach-card strong {
    display: block;
    color: var(--ink);
    font-size: 0.96rem;
}

.coach-card span {
    color: var(--muted);
    display: block;
    font-size: 0.86rem;
    line-height: 1.45;
    margin-top: 4px;
}

.agent-step {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 16px;
    background: var(--surface);
    margin-bottom: 10px;
}

.agent-step strong {
    display: block;
    color: var(--ink);
    font-size: 0.98rem;
}

.agent-step span {
    color: var(--muted);
    display: block;
    font-size: 0.86rem;
    margin-top: 3px;
}

.agent-step.active {
    border-color: rgba(37, 99, 235, 0.5);
    box-shadow: inset 4px 0 0 var(--blue), 0 10px 24px rgba(37, 99, 235, 0.10);
}

.agent-step.done {
    border-color: rgba(0, 168, 120, 0.36);
    box-shadow: inset 4px 0 0 var(--green);
}

.agent-badge {
    float: right;
    border-radius: 999px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--ink);
    background: var(--surface-soft);
}

.agent-step.active .agent-badge {
    background: rgba(37, 99, 235, 0.12);
    color: var(--blue);
}

.agent-step.done .agent-badge {
    background: rgba(0, 168, 120, 0.12);
    color: #047857;
}

.metric-tile {
    padding: 16px;
    min-height: 104px;
}

.metric-tile span {
    color: var(--muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    font-weight: 800;
}

.metric-tile strong {
    display: block;
    color: var(--ink);
    font-size: 1.35rem;
    margin-top: 8px;
    line-height: 1.15;
}

.metric-tile em {
    color: var(--muted);
    display: block;
    font-size: 0.85rem;
    font-style: normal;
    margin-top: 5px;
}

.plan-shell,
.approval-shell,
.result-shell {
    padding: 18px 20px;
    margin-top: 0.85rem;
}

.plan-shell h3,
.approval-shell h3,
.result-shell h3 {
    margin-top: 0;
}

.result-shell {
    margin-top: 0.35rem;
    margin-bottom: 0.75rem;
}

.markdown-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 10px 24px rgba(16, 24, 39, 0.06);
    margin-top: 0.85rem;
    padding: 24px 26px;
    overflow-x: auto;
}

.markdown-card h3 {
    margin: 0 0 1rem;
}

.markdown-card h4 {
    margin: 1rem 0 0.45rem;
    font-size: 1.02rem;
}

.markdown-card p {
    margin: 0.55rem 0;
    line-height: 1.6;
}

.markdown-card ul {
    margin: 0.45rem 0 0.75rem 1.25rem;
    padding-left: 1rem;
}

.markdown-card li {
    margin: 0.32rem 0;
    line-height: 1.55;
}

.markdown-card strong {
    font-weight: 800;
}

.approval-actions-spacer {
    height: 0.85rem;
}

@media (max-width: 900px) {
    section[data-testid="stMain"] [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding: 3.75rem 1rem 2.5rem;
    }

    .top-band {
        padding: 18px;
    }
}

.callout {
    border-left: 5px solid var(--amber);
    background: #fff8e6;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 0.9rem;
    color: #5d4610;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div,
div[data-testid="stMultiSelect"] div {
    border-radius: 8px;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    border-radius: 8px;
    font-weight: 800;
    min-height: 2.8rem;
}

button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: var(--green);
    border-color: var(--green);
}

section[data-testid="stMain"] .stButton > button[kind="primary"],
section[data-testid="stMain"] [data-testid="stFormSubmitButton"] button[kind="primary"],
section[data-testid="stMain"] button[data-testid^="stBaseButton-primary"] {
    background: var(--green) !important;
    border-color: var(--green) !important;
    color: #ffffff !important;
}

section[data-testid="stMain"] .stButton > button[kind="primary"] *,
section[data-testid="stMain"] [data-testid="stFormSubmitButton"] button[kind="primary"] *,
section[data-testid="stMain"] button[data-testid^="stBaseButton-primary"] * {
    color: #ffffff !important;
}

section[data-testid="stMain"] .stButton > button[kind="secondary"],
section[data-testid="stMain"] .stDownloadButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
}

section[data-testid="stMain"] .stDownloadButton > button,
section[data-testid="stMain"] .stDownloadButton > button[kind="secondary"],
section[data-testid="stMain"] button[data-testid^="stBaseButton-secondary"]:has([data-testid="stDownloadButton"]) {
    background: var(--green) !important;
    border-color: var(--green) !important;
    color: #ffffff !important;
}

section[data-testid="stMain"] .stDownloadButton > button *,
section[data-testid="stMain"] .stDownloadButton > button[kind="secondary"] * {
    color: #ffffff !important;
}

section[data-testid="stMain"] .stButton > button[kind="secondary"]:hover,
section[data-testid="stMain"] .stDownloadButton > button[kind="secondary"]:hover {
    background: #fff5f4 !important;
    border-color: var(--coral) !important;
    color: #9f2f28 !important;
}

section[data-testid="stMain"] .stDownloadButton > button:hover,
section[data-testid="stMain"] .stDownloadButton > button[kind="secondary"]:hover {
    background: #07966d !important;
    border-color: #07966d !important;
    color: #ffffff !important;
}

section[data-testid="stMain"] .stDownloadButton > button:hover * {
    color: #ffffff !important;
}

section[data-testid="stMain"] [data-testid="stAlert"] {
    margin-top: 0.9rem;
}

section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 24px rgba(16, 24, 39, 0.06) !important;
    padding: 18px 20px !important;
    margin-top: 0.85rem !important;
}

section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] {
    max-width: 100%;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    border-color: var(--blue);
    color: var(--blue);
}

.small-muted {
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.5;
}
</style>
""",
    unsafe_allow_html=True,
)

def reset_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.thread_id = f"session-{uuid4().hex[:10]}"
    st.session_state.stage = "input"
    st.session_state.interrupt_data = None
    st.session_state.completed_agents = []

def init_session() -> None:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"session-{uuid4().hex[:10]}"
    if "stage" not in st.session_state:
        st.session_state.stage = "input"
    if "interrupt_data" not in st.session_state:
        st.session_state.interrupt_data = None
    if "completed_agents" not in st.session_state:
        st.session_state.completed_agents = []

def get_config() -> dict:
    return {"configurable": {"thread_id": st.session_state.thread_id}}

def build_user_request(
    goal_brief: str,
    primary_focus: str,
    target: str,
    timeframe: str,
    fitness_level: str,
    minutes_per_session: int,
    training_days: int,
    equipment: list[str],
    nutrition_preference: str,
    constraints: str,
) -> str:
    context = [
        f"Primary focus: {primary_focus}",
        f"Specific target: {target.strip() or 'Not specified'}",
        f"Timeframe: {timeframe.strip() or 'Not specified'}",
        f"Current fitness level: {fitness_level}",
        f"Time available: {minutes_per_session} minutes per session, {training_days} days per week",
        f"Available equipment: {', '.join(equipment) if equipment else 'Not specified'}",
        f"Nutrition preference: {nutrition_preference}",
        f"Constraints: {constraints.strip() or 'None mentioned'}",
    ]

    brief = goal_brief.strip()
    if not brief:
        brief = "Create a personalized fitness plan using the structured context below."

    return f"{brief}\n\nStructured context:\n- " + "\n- ".join(context)

def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="top-band">
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )

def render_sidebar() -> None:
    with st.sidebar:
        st.title("Fitness Coach")
        st.caption("LangGraph multi-agent planning")

        progress = STAGE_PROGRESS.get(st.session_state.stage, 0)
        st.progress(progress)
        st.caption(f"Session progress: {progress}%")

        if st.session_state.get("user_request"):
            st.markdown("**Current request**")
            preview = st.session_state.user_request.split("\n", 1)[0]
            st.caption(preview[:190] + ("..." if len(preview) > 190 else ""))

        st.markdown("---")
        st.markdown("**Coach team**")
        for _, label, description in AGENTS:
            st.caption(f"{label}: {description}")

        st.markdown("---")
        if st.button("New plan", use_container_width=True):
            reset_session()
            st.rerun()

        st.caption("Educational guidance only. Consult a qualified professional for medical concerns.")

def render_agent_rail(active_agent: str | None = None, completed_agents: set[str] | None = None) -> None:
    completed_agents = completed_agents or set()
    cards = []
    for agent_id, label, description in AGENTS:
        if active_agent == agent_id:
            state_class = "active"
            badge = "Active"
        elif agent_id in completed_agents:
            state_class = "done"
            badge = "Done"
        else:
            state_class = ""
            badge = "Queued"

        cards.append(
            f"""
<div class="agent-step {state_class}">
    <span class="agent-badge">{badge}</span>
    <strong>{label}</strong>
    <span>{description}</span>
</div>
"""
        )
    st.markdown("".join(cards), unsafe_allow_html=True)

def render_coach_cards() -> None:
    cards = []
    for _, label, description in AGENTS:
        cards.append(
            f"""
<div class="coach-card">
    <strong>{label}</strong>
    <span>{description}</span>
</div>
"""
        )
    st.markdown(f"<div class='coach-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)

def render_metric(label: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
<div class="metric-tile">
    <span>{label}</span>
    <strong>{value}</strong>
    <em>{helper}</em>
</div>
""",
        unsafe_allow_html=True,
    )

def markdown_to_card_html(markdown_text: str) -> str:
    def inline_format(text: str) -> str:
        escaped = html.escape(text)
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)

    parts = []
    list_depth = 0

    def set_list_depth(depth: int) -> None:
        nonlocal list_depth
        while list_depth < depth:
            parts.append("<ul>")
            list_depth += 1
        while list_depth > depth:
            parts.append("</ul>")
            list_depth -= 1

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            set_list_depth(0)
            continue

        leading_spaces = len(raw_line) - len(raw_line.lstrip(" "))
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")

        if is_bullet:
            depth = max(1, min(3, leading_spaces // 2 + 1))
            set_list_depth(depth)
            parts.append(f"<li>{inline_format(stripped[2:].strip())}</li>")
            continue

        set_list_depth(0)
        if stripped.startswith("### "):
            parts.append(f"<h4>{inline_format(stripped[4:].strip())}</h4>")
        elif stripped.startswith("## "):
            parts.append(f"<h4>{inline_format(stripped[3:].strip())}</h4>")
        elif stripped.startswith("# "):
            parts.append(f"<h4>{inline_format(stripped[2:].strip())}</h4>")
        else:
            parts.append(f"<p>{inline_format(stripped)}</p>")

    set_list_depth(0)
    return "\n".join(parts)

def remove_duplicate_card_heading(title: str, content: str | None) -> str | None:
    if not content:
        return content

    def normalize(value: str) -> str:
        value = re.sub(r"^[#\s]+", "", value.strip())
        value = re.sub(r"\*\*", "", value)
        value = value.rstrip(":")
        value = re.sub(r"\b(daily|weekly)\b", "", value, flags=re.IGNORECASE)
        value = re.sub(r"[^a-z0-9]+", " ", value.lower())
        return " ".join(value.split())

    lines = content.splitlines()
    first_content_index = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first_content_index is None:
        return content

    first_line = lines[first_content_index]
    if normalize(first_line) == normalize(title):
        del lines[first_content_index]
        while lines and not lines[0].strip():
            del lines[0]
        return "\n".join(lines)

    return content

def render_markdown_panel(title: str, content: str | None, empty_message: str) -> None:
    content = remove_duplicate_card_heading(title, content)
    body = markdown_to_card_html(content) if content else f"<p>{html.escape(empty_message)}</p>"
    st.markdown(
        f"""
<div class="markdown-card">
    <h3>{html.escape(title)}</h3>
    {body}
</div>
""",
        unsafe_allow_html=True,
    )

def compose_plan_markdown(state: dict) -> str:
    sections = [
        ("Goal & Profile", state.get("user_profile")),
        ("Weekly Workout Plan", state.get("workout_plan")),
        ("Nutrition Plan", state.get("nutrition_plan")),
        ("Progress Milestones", state.get("progress_milestones")),
    ]
    lines = ["# Fitness Plan"]
    for title, content in sections:
        if content:
            lines.extend([f"\n## {title}\n", content.strip()])
    return "\n".join(lines).strip() + "\n"

def run_intake_screen() -> None:
    render_header(
        "Fitness Coach Studio",
        "Build a personalized plan with a goal analyzer, workout designer, nutrition planner, and progress tracker.",
    )

    left, right = st.columns([1.45, 0.9], gap="large")

    with left:
        st.markdown('<div class="section-title">Plan intake</div>', unsafe_allow_html=True)
        with st.form("fitness_intake"):
            goal_brief = st.text_area(
                "Goal brief",
                placeholder=(
                    "Example: I want to lose 5 kg in 3 months. I am a beginner, "
                    "can train 4 days per week, and prefer home workouts."
                ),
                height=124,
            )

            col1, col2 = st.columns(2)
            with col1:
                primary_focus = st.selectbox(
                    "Primary focus",
                    [
                        "Weight loss",
                        "Muscle gain",
                        "Strength",
                        "Endurance",
                        "General fitness",
                        "Mobility",
                    ],
                )
                target = st.text_input("Specific target", placeholder="Lose 5 kg, run 5K, gain muscle")
            with col2:
                timeframe = st.text_input("Timeframe", placeholder="8 weeks, 3 months, this semester")
                fitness_level = st.radio(
                    "Fitness level",
                    ["Beginner", "Intermediate", "Advanced"],
                    horizontal=True,
                )

            col3, col4 = st.columns(2)
            with col3:
                training_days = st.slider("Training days per week", 1, 7, 4)
            with col4:
                minutes_per_session = st.slider("Minutes per session", 10, 120, 35, step=5)

            equipment = st.multiselect(
                "Available equipment",
                [
                    "Bodyweight",
                    "Dumbbells",
                    "Resistance bands",
                    "Barbell",
                    "Machines",
                    "Cardio machine",
                    "Outdoor space",
                    "Pull-up bar",
                ],
                default=["Bodyweight"],
            )
            nutrition_preference = st.selectbox(
                "Nutrition preference",
                [
                    "No preference",
                    "High protein",
                    "Vegetarian",
                    "Vegan",
                    "Low carb",
                    "Mediterranean style",
                    "Budget friendly",
                ],
            )
            constraints = st.text_area(
                "Constraints or notes",
                placeholder="Injuries, foods to avoid, no gym, fasting schedule, sleep issues, etc.",
                height=86,
            )

            submitted = st.form_submit_button("Build my fitness plan", type="primary", use_container_width=True)

        if submitted:
            if not goal_brief.strip() and not target.strip():
                st.warning("Add a short goal brief or a specific target first.")
            else:
                st.session_state.user_request = build_user_request(
                    goal_brief=goal_brief,
                    primary_focus=primary_focus,
                    target=target,
                    timeframe=timeframe,
                    fitness_level=fitness_level,
                    minutes_per_session=minutes_per_session,
                    training_days=training_days,
                    equipment=equipment,
                    nutrition_preference=nutrition_preference,
                    constraints=constraints,
                )
                st.session_state.intake_summary = {
                    "focus": primary_focus,
                    "level": fitness_level,
                    "days": str(training_days),
                    "minutes": str(minutes_per_session),
                }
                st.session_state.completed_agents = []
                st.session_state.stage = "running"
                st.rerun()

    with right:
        st.markdown('<div class="section-title">Coach workflow</div>', unsafe_allow_html=True)
        render_coach_cards()
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            render_metric("Output", "4 sections", "Profile, training, food, progress")
        with col_b:
            render_metric("Review", "Approval", "Commit only after review")
        st.markdown(
            """
<div class="callout small-muted">
The more specific your intake is, the better the agents can respect your schedule, equipment, and constraints.
</div>
""",
            unsafe_allow_html=True,
        )

def run_graph_screen() -> None:
    render_header(
        "Your coaching team is working",
        "The supervisor is routing the request through each specialist. This can take a little while because the agents may search the local fitness knowledge base.",
    )

    progress_bar = st.progress(0)
    status = st.empty()
    rail = st.empty()
    completed_agents = set(st.session_state.get("completed_agents", []))

    initial_state = {
        "user_request": st.session_state.user_request,
        "messages": [],
    }

    interrupt_caught = False
    step_count = 0

    with st.spinner("Building your plan..."):
        with rail.container():
            render_agent_rail(completed_agents=completed_agents)
        for event in graph.stream(initial_state, config=get_config()):
            for node_name, node_output in event.items():
                if node_name == "__interrupt__":
                    st.session_state.interrupt_data = node_output[0].value
                    st.session_state.completed_agents = list({*completed_agents, "progress_tracker"})
                    st.session_state.stage = "awaiting_approval"
                    interrupt_caught = True
                    break

                label = AGENT_LABELS.get(node_name, node_name)
                if node_name in {agent_id for agent_id, _, _ in AGENTS}:
                    completed_agents.add(node_name)
                    st.session_state.completed_agents = list(completed_agents)

                step_count += 1
                progress_bar.progress(min(90, 12 + step_count * 13))
                status.info(f"Active step: {label}")
                with rail.container():
                    render_agent_rail(active_agent=node_name, completed_agents=completed_agents)

            if interrupt_caught:
                break

    if interrupt_caught:
        st.rerun()
    else:
        st.session_state.stage = "done"
        st.rerun()

def run_approval_screen() -> None:
    render_header(
        "Review your plan",
        "Read the generated profile, training plan, nutrition plan, and milestones before committing.",
    )

    data = st.session_state.interrupt_data or {}
    full_plan = data.get("full_plan", "")

    st.markdown(
        """
<div class="approval-shell">
    <h3>Approval checkpoint</h3>
    <p class="small-muted">Approve the plan if it fits your real schedule and constraints. Reject it to finish without committing, then start a new plan with adjusted intake details.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="approval-actions-spacer"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Approve plan", type="primary", use_container_width=True):
            with st.spinner("Finalizing your commitment..."):
                for _ in graph.stream(Command(resume="yes"), config=get_config()):
                    pass
            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("Reject plan", use_container_width=True):
            with st.spinner("Closing this draft..."):
                for _ in graph.stream(Command(resume="no"), config=get_config()):
                    pass
            st.session_state.stage = "done"
            st.rerun()

    render_markdown_panel(
        "Generated plan",
        full_plan,
        "No plan content was returned.",
    )

def run_done_screen() -> None:
    state = graph.get_state(config=get_config()).values
    approved = bool(state.get("plan_approved"))

    render_header(
        "Your fitness plan",
        "A complete draft from the multi-agent coach, organized for review and weekly use.",
    )

    metric_cols = st.columns(4)
    intake_summary = st.session_state.get("intake_summary", {})
    with metric_cols[0]:
        render_metric("Focus", intake_summary.get("focus", "Custom"), "Primary goal")
    with metric_cols[1]:
        render_metric("Level", intake_summary.get("level", "Profiled"), "Starting point")
    with metric_cols[2]:
        render_metric("Schedule", f"{intake_summary.get('days', '-')}/wk", "Training days")
    with metric_cols[3]:
        render_metric("Status", "Approved" if approved else "Draft", "Commitment checkpoint")

    if approved:
        st.success("Plan approved. Stay consistent and update your progress weekly.")
    else:
        st.warning("Plan was not approved. You can start a new plan with adjusted inputs.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Download plan",
            data=compose_plan_markdown(state),
            file_name="fitness_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        if st.button("Build a new plan", use_container_width=True):
            reset_session()
            st.rerun()

    tabs = st.tabs(["Profile", "Workout", "Nutrition", "Milestones"])
    with tabs[0]:
        render_markdown_panel(
            "Goal & Profile",
            state.get("user_profile"),
            "No profile was generated for this session.",
        )
    with tabs[1]:
        render_markdown_panel(
            "Weekly Workout Plan",
            state.get("workout_plan"),
            "No workout plan was generated for this session.",
        )
    with tabs[2]:
        render_markdown_panel(
            "Nutrition Plan",
            state.get("nutrition_plan"),
            "No nutrition plan was generated for this session.",
        )
    with tabs[3]:
        render_markdown_panel(
            "Progress Milestones",
            state.get("progress_milestones"),
            "No progress milestones were generated for this session.",
        )

init_session()
render_sidebar()

if st.session_state.stage == "input":
    run_intake_screen()
elif st.session_state.stage == "running":
    run_graph_screen()
elif st.session_state.stage == "awaiting_approval":
    run_approval_screen()
elif st.session_state.stage == "done":
    run_done_screen()
