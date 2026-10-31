import os
# ── Kill LangSmith tracing before any langchain import ───────────────────────
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"]    = "false"

import streamlit as st
import operator, re, time
from pathlib import Path
from typing import TypedDict, List, Annotated, Optional, Literal

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Blog Writing Agent",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp { background-color: #05080f; color: #e8ebf0; }

/* Sidebar */
[data-testid="stSidebar"] { background: #080c15 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] * { color: #e8ebf0 !important; }
[data-testid="stSidebar"] .stTextArea textarea {
    background: #c87f3e !important; color: #1a0d00 !important;
    border: none !important; border-radius: 10px !important; font-weight: 500 !important;
}
[data-testid="stSidebar"] .stTextArea textarea::placeholder { color: rgba(26,13,0,0.55) !important; }
[data-testid="stSidebar"] input[type="date"] {
    background: #c87f3e !important; color: #1a0d00 !important;
    border: none !important; border-radius: 10px !important; font-weight: 500 !important;
}

/* Generate button */
[data-testid="stSidebar"] .stButton > button {
    background: #c87f3e !important; color: #1a0d00 !important;
    font-weight: 700 !important; border: none !important;
    border-radius: 10px !important; width: 100% !important;
    padding: 10px 0 !important; font-size: 14px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 4px 20px rgba(200,127,62,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #7a8499 !important;
    border-radius: 7px 7px 0 0 !important; padding: 8px 18px !important;
    font-weight: 500 !important; font-size: 13px !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: rgba(255,255,255,0.08) !important; color: #e8ebf0 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px !important; }

/* Cards */
.plan-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #3ccfff; border-radius: 10px; padding: 16px 18px; margin-bottom: 12px;
}
.plan-title-card {
    background: linear-gradient(135deg, rgba(60,207,255,0.08), rgba(184,255,60,0.06));
    border: 1px solid rgba(60,207,255,0.2); border-radius: 10px; padding: 16px 20px; margin-bottom: 14px;
}
.evidence-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
}

/* Badges */
.badge { display:inline-block; font-size:10px; font-weight:600; padding:2px 8px;
         border-radius:20px; margin-right:4px; text-transform:uppercase; letter-spacing:0.05em; }
.badge-green  { background:rgba(184,255,60,0.12);  color:#b8ff3c; }
.badge-blue   { background:rgba(60,207,255,0.12);  color:#3ccfff; }
.badge-gold   { background:rgba(200,127,62,0.12);  color:#c87f3e; }
.badge-purple { background:rgba(180,100,255,0.12); color:#c47aff; }

/* Meta pill */
.meta-pill { display:inline-block; background:rgba(184,255,60,0.08); color:#b8ff3c;
             font-size:11px; font-weight:600; padding:3px 10px; border-radius:20px;
             margin-right:8px; border:1px solid rgba(184,255,60,0.2); }

/* Log box */
.log-box { background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.08);
           border-radius:10px; padding:16px 18px;
           font-family:'JetBrains Mono','Fira Code',monospace; font-size:12px;
           max-height:450px; overflow-y:auto; }
.log-line { margin:3px 0; }
.log-time  { color:#7a8499; margin-right:10px; }
.log-green { color:#b8ff3c; }
.log-blue  { color:#3ccfff; }
.log-red   { color:#ff6b6b; }

/* Main title */
.main-title { font-size:clamp(24px,4vw,42px); font-weight:700;
              letter-spacing:-0.02em; line-height:1.1; margin-bottom:16px; }
.title-blog    { color:#b8ff3c; }
.title-writing { color:#3ccfff; }
.title-agent   { color:#e8ebf0; }

/* Empty states */
.empty-state { text-align:center; padding:60px 20px; color:#7a8499; }
.empty-icon  { font-size:52px; margin-bottom:16px; opacity:0.4; }
.empty-text  { font-size:14px; max-width:300px; margin:auto; line-height:1.6; }

hr { border-color:rgba(255,255,255,0.08) !important; }

/* Past blog items */
div[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; font-size: 12px !important;
    text-align: left !important; padding: 6px 10px !important;
}

/* Progress steps */
.step-row { display:flex; align-items:center; gap:10px;
            padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05); }
.step-icon { font-size:16px; width:24px; flex-shrink:0; }
.step-text { font-size:13px; color:#e8ebf0; }
.step-done { color:#b8ff3c; }
.step-run  { color:#3ccfff; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def _init():
    defaults = {
        "plan":       None,
        "evidence":   [],
        "final_md":   "",
        "logs":       [],
        "generating": False,
        "steps_done": [],   # list of step label strings shown during run
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Pipeline loader (cached once) ─────────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️  Loading AI pipeline…")
def load_pipeline():
    from dotenv import load_dotenv
    load_dotenv()

    from pydantic import BaseModel, Field as PField
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import Send
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage
    from langchain_community.tools.tavily_search import TavilySearchResults
    import warnings
    warnings.filterwarnings("ignore")

    llm = ChatOllama(model="llama3.2:latest")

    # ── Schemas ───────────────────────────────────────────────────────────────
    class Task(BaseModel):
        id: int
        title: str
        brief: str = PField(..., description="What to cover")
        goal: str
        bullets: List[str] = PField(..., min_length=3, max_length=5)
        target_words: int
        section_type: Literal[
            "Engaging Headlines","intro","core","example",
            "checklist","common_mistakes","Links","conclusion"
        ]
        tags: List[str] = PField(default_factory=list)
        requires_research: bool = False
        requires_citations: bool = False
        requires_code: bool = False

    class Plan(BaseModel):
        blog_title: str
        tasks: List[Task]
        audience: str
        tone: str
        blog_kind: Literal["explainer","tutorial","news_roundup","comparison","system_design"] = "explainer"
        constraints: List[str] = PField(default_factory=list)

    class RouterDecision(BaseModel):
        needs_research: bool
        mode: Literal["closed_book","hybrid","open_book"]
        queries: List[str] = PField(default_factory=list)

    class EvidenceItem(BaseModel):
        title: str
        url: str
        published_at: Optional[str] = None
        snippet:      Optional[str] = None
        source:       Optional[str] = None

    class EvidencePack(BaseModel):
        evidence: List[EvidenceItem] = PField(default_factory=list)

    class State(TypedDict):
        topic: str; mode: str; needs_research: bool; queries: List[str]
        evidence: List[EvidenceItem]; plan: Optional[Plan]
        sections: Annotated[List[tuple], operator.add]
        merged_md: str; md_with_placeholders: str; image_specs: List[dict]; final: str

    # ── Router ────────────────────────────────────────────────────────────────
    ROUTER_SYS = """You are a routing module for a technical blog planner.
Decide whether web research is needed before planning.
Modes: closed_book (needs_research=false) | hybrid (needs_research=true) | open_book (needs_research=true).
If needs_research=true output 3-10 specific queries."""

    def router_node(state):
        d = llm.with_structured_output(RouterDecision).invoke([
            SystemMessage(content=ROUTER_SYS),
            HumanMessage(content=f"Topic: {state['topic']}")
        ])
        return {"needs_research": d.needs_research, "mode": d.mode, "queries": d.queries}

    def route_next(state):
        return "research" if state["needs_research"] else "orchestrator"

    # ── Research ──────────────────────────────────────────────────────────────
    def _tavily(q, max_results=5):
        tool = TavilySearchResults(max_results=max_results)
        results = tool.invoke({"query": q})
        return [{
            "title": r.get("title",""), "url": r.get("url",""),
            "snippet": r.get("content") or r.get("snippet",""),
            "published_at": r.get("published_date") or r.get("published_at"),
            "source": r.get("source"),
        } for r in (results or [])]

    RESEARCH_SYS = """Produce a deduplicated list of EvidenceItem objects from raw search results.
Only include items with non-empty URLs. Keep snippets short. Deduplicate by URL."""

    def research_node(state):
        raw = []
        for q in state.get("queries", []):
            raw.extend(_tavily(q, max_results=6))
        if not raw:
            return {"evidence": []}
        pack = llm.with_structured_output(EvidencePack).invoke([
            SystemMessage(content=RESEARCH_SYS),
            HumanMessage(content=f"Raw results:\n{raw}"),
        ])
        return {"evidence": list({e.url: e for e in pack.evidence if e.url}.values())}

    # ── Orchestrator ──────────────────────────────────────────────────────────
    ORCH_SYS = (
        "You are a senior technical writer. Produce a highly actionable outline "
        "for a technical blog post. Create 5-7 sections (tasks). Each section needs: "
        "goal (1 sentence), 3-5 concrete bullets, target word count (120-450). "
        "Output must strictly match the Plan schema."
    )

    def orchestrator(state):
        evidence = state.get("evidence", [])
        plan = llm.with_structured_output(Plan).invoke([
            SystemMessage(content=ORCH_SYS),
            HumanMessage(content=(
                f"Topic: {state['topic']}\nMode: {state.get('mode','closed_book')}\n\n"
                f"Evidence: {[e.model_dump() for e in evidence][:16]}"
            )),
        ])
        return {"plan": plan}

    def fanout(state):
        return [Send("worker", {
            "task": t.model_dump(), "topic": state["topic"],
            "mode": state["mode"], "plan": state["plan"].model_dump(),
            "evidence": [e.model_dump() for e in state.get("evidence", [])],
        }) for t in state["plan"].tasks]

    # ── Worker ────────────────────────────────────────────────────────────────
    WORKER_SYS = """You are a senior technical writer. Write ONE section of a technical blog in Markdown.
Start with '## <Section Title>'. Cover ALL bullets. Stay within target word count (±15%).
Output ONLY the section markdown. Be precise, avoid fluff."""

    def worker(payload):
        task = Task.model_validate(payload["task"]) if isinstance(payload["task"], dict) else payload["task"]
        plan = Plan.model_validate(payload["plan"]) if isinstance(payload["plan"], dict) else payload["plan"]
        evidence = [EvidenceItem(**e) if isinstance(e, dict) else e for e in payload.get("evidence", [])]
        bullets_text = "\n- " + "\n- ".join(task.bullets)
        ev_text = "\n".join(f"- {e.title} | {e.url}" for e in evidence[:20]) if evidence else ""
        md = llm.invoke([
            SystemMessage(content=WORKER_SYS),
            HumanMessage(content=(
                f"Blog title: {plan.blog_title}\nAudience: {plan.audience}\nTone: {plan.tone}\n"
                f"Blog kind: {plan.blog_kind}\nTopic: {payload['topic']}\n"
                f"Section title: {task.title}\nGoal: {task.goal}\n"
                f"Target words: {task.target_words}\nrequires_code: {task.requires_code}\n"
                f"Bullets:{bullets_text}\n\nEvidence:\n{ev_text}"
            ))
        ]).content.strip()
        return {"sections": [(task.id, md)]}

    # ── Reducer ───────────────────────────────────────────────────────────────
    def reducer(state):
        plan = state["plan"]
        ordered = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
        final_md = f"# {plan.blog_title}\n\n" + "\n\n".join(ordered) + "\n"
        safe = re.sub(r'[\\/:*?"<>|]', '', plan.blog_title).strip()
        out = Path("C:/Users/hp/Desktop/Blog_ChatAI/outputs")
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{safe}.md").write_text(final_md, encoding="utf-8")
        return {"final": final_md}

    # ── Build graph ───────────────────────────────────────────────────────────
    g = StateGraph(State)
    g.add_node("router",       router_node)
    g.add_node("research",     research_node)
    g.add_node("orchestrator", orchestrator)
    g.add_node("worker",       worker)
    g.add_node("reducer",      reducer)
    g.add_edge(START, "router")
    g.add_conditional_edges("router", route_next, {"research":"research","orchestrator":"orchestrator"})
    g.add_edge("research", "orchestrator")
    g.add_conditional_edges("orchestrator", fanout, ["worker"])
    g.add_edge("worker", "reducer")
    g.add_edge("reducer", END)
    return g.compile()


# ── Helpers ───────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("C:/Users/hp/Desktop/Blog_ChatAI/outputs")

def list_past_blogs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(OUTPUT_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

def add_log(msg: str, level: str = "green"):
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.append((ts, msg, level))

def stc(color: str) -> str:
    m = {"intro":"badge-blue","core":"badge-blue","conclusion":"badge-blue",
         "example":"badge-purple","checklist":"badge-green",
         "common_mistakes":"badge-gold","Engaging Headlines":"badge-green","Links":"badge-purple"}
    return m.get(color, "badge-blue")


# ══════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
      <div style="width:8px;height:8px;border-radius:50%;background:#b8ff3c;box-shadow:0 0 8px #b8ff3c"></div>
      <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Generate New Blog</span>
    </div>""", unsafe_allow_html=True)

    topic = st.text_area("topic", placeholder="e.g. Building RAG pipelines with LangGraph…",
                         height=110, label_visibility="collapsed", key="topic_input")

    st.markdown("""
    <div style="display:flex;align-items:center;gap:6px;margin:6px 0 2px">
      <div style="width:6px;height:6px;border-radius:50%;background:#b8ff3c;opacity:.6"></div>
      <span style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#7a8499">As-of-date</span>
    </div>""", unsafe_allow_html=True)

    as_of = st.date_input("as_of", value=None, label_visibility="collapsed", key="date_input")

    generate_clicked = st.button(
        "Generate ⚡",
        disabled=st.session_state.generating,
        use_container_width=True,
        key="gen_btn",
    )

    st.divider()

    st.markdown("""<span style="font-size:10px;font-weight:600;text-transform:uppercase;
                letter-spacing:.06em;color:#7a8499">Past Blogs</span>""", unsafe_allow_html=True)

    past = list_past_blogs()
    if not past:
        st.caption("No past blogs yet.")
    else:
        for p in past[:15]:
            if st.button(f"📄 {p.stem[:26]}", key=f"pb_{p.stem}", use_container_width=True):
                st.session_state.final_md = p.read_text(encoding="utf-8")
                st.session_state.plan     = None   # clear plan so markdown tab shows it
                st.rerun()


# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<h1 class="main-title">
  <span class="title-blog">Blog</span>
  <span class="title-writing"> Writing</span>
  <span class="title-agent"> Agent</span>
</h1>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PIPELINE EXECUTION
# ══════════════════════════════════════════════════════════
if generate_clicked and not st.session_state.generating:
    if not topic.strip():
        st.warning("⚠️  Please enter a blog topic first.")
        st.stop()

    # Reset state for new run
    st.session_state.generating = True
    st.session_state.plan       = None
    st.session_state.evidence   = []
    st.session_state.final_md   = ""
    st.session_state.logs       = []
    st.session_state.steps_done = []

    pipeline = load_pipeline()

    initial = {
        "topic": topic.strip(), "mode": "", "needs_research": False,
        "queries": [], "evidence": [], "plan": None, "sections": [],
        "merged_md": "", "md_with_placeholders": "", "image_specs": [], "final": "",
    }

    add_log(f"🚀  Pipeline started for: {topic.strip()}")

    # Live progress container — rendered right above the tabs
    progress_area = st.empty()

    def refresh_progress():
        steps = st.session_state.steps_done
        rows = "".join(
            f'<div class="step-row"><span class="step-icon">✅</span>'
            f'<span class="step-text step-done">{s}</span></div>'
            for s in steps
        )
        progress_area.markdown(
            f'<div style="background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.07);'
            f'border-radius:10px;padding:12px 16px;margin-bottom:12px">{rows}</div>',
            unsafe_allow_html=True,
        )

    error_occurred = False
    try:
        for step in pipeline.stream(initial, stream_mode="updates"):
            for node_name, node_output in step.items():

                if node_name == "router":
                    mode  = node_output.get("mode", "closed_book")
                    needs = node_output.get("needs_research", False)
                    qs    = node_output.get("queries", [])
                    label = f"🔀 Router → mode={mode}  research={'YES' if needs else 'NO'}"
                    st.session_state.steps_done.append(label)
                    add_log(label)
                    if qs:
                        add_log(f"🔍 Queries: {', '.join(qs[:4])}", "blue")
                    refresh_progress()

                elif node_name == "research":
                    ev_raw = node_output.get("evidence", [])
                    label  = f"📚 Research done — {len(ev_raw)} sources"
                    st.session_state.steps_done.append(label)
                    add_log(label, "blue")
                    st.session_state.evidence = [
                        e.model_dump() if hasattr(e, "model_dump") else e
                        for e in ev_raw
                    ]
                    refresh_progress()

                elif node_name == "orchestrator":
                    p = node_output.get("plan")
                    if p:
                        label = f"📋 Plan ready — '{p.blog_title}'  ({len(p.tasks)} sections)"
                        st.session_state.steps_done.append(label)
                        add_log(label)
                        st.session_state.plan = p.model_dump()
                        refresh_progress()

                elif node_name == "worker":
                    for sid, _ in node_output.get("sections", []):
                        label = f"✍️  Section {sid} written"
                        st.session_state.steps_done.append(label)
                        add_log(label)
                    refresh_progress()

                elif node_name == "reducer":
                    final_md = node_output.get("final", "")
                    st.session_state.final_md = final_md
                    label = "✅ Blog assembled & saved to outputs/"
                    st.session_state.steps_done.append(label)
                    add_log(label, "green")
                    refresh_progress()

    except Exception as e:
        add_log(f"❌ Error: {e}", "red")
        st.error(f"Pipeline error: {e}")
        error_occurred = True

    st.session_state.generating = False
    progress_area.empty()   # clear the progress box

    if not error_occurred:
        st.success("✅ Blog generated successfully!")

    st.rerun()   # re-render page so tabs show new data


# ══════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════
tab_plan, tab_ev, tab_md, tab_logs = st.tabs([
    "🌿  Plan",
    "🔬  Evidence",
    "📝  Markdown Preview",
    "📋  Logs",
])

# ── PLAN ──────────────────────────────────────────────────
with tab_plan:
    plan = st.session_state.plan
    if not plan:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">🌿</div>
          <p class="empty-text">Your blog outline will appear here after generation.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Title card
        st.markdown(f"""<div class="plan-title-card">
          <div style="font-size:20px;font-weight:700;
               background:linear-gradient(90deg,#3ccfff,#b8ff3c);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text">{plan['blog_title']}</div>
        </div>""", unsafe_allow_html=True)

        # Meta pills
        st.markdown(
            f'<div style="margin-bottom:16px">'
            f'<span class="meta-pill">📖 {plan["blog_kind"]}</span>'
            f'<span class="meta-pill">👥 {plan["audience"][:40]}</span>'
            f'<span class="meta-pill">🎨 {plan["tone"]}</span>'
            f'<span class="meta-pill">📌 {len(plan["tasks"])} sections</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Task cards
        for task in plan["tasks"]:
            bullets_html = "".join(
                f'<li style="font-size:12px;margin-bottom:5px;color:rgba(232,235,240,.85)">'
                f'<span style="color:#b8ff3c;font-weight:700;margin-right:6px">→</span>{b}</li>'
                for b in task["bullets"]
            )
            flags = (
                ('<span class="badge badge-green">🔍 Research</span>'  if task.get("requires_research") else "") +
                ('<span class="badge badge-gold">📎 Citations</span>'  if task.get("requires_citations") else "") +
                ('<span class="badge badge-blue">💻 Code</span>'       if task.get("requires_code") else "")
            )
            tags_html = "".join(
                f'<span style="font-size:10px;padding:2px 7px;background:rgba(255,255,255,.06);'
                f'border-radius:20px;color:#7a8499;margin-right:4px">{t}</span>'
                for t in task.get("tags", [])
            )
            st.markdown(f"""<div class="plan-card">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <div style="width:26px;height:26px;border-radius:50%;
                     background:linear-gradient(135deg,#3ccfff,#b8ff3c);
                     display:flex;align-items:center;justify-content:center;
                     font-size:11px;font-weight:700;color:#000;flex-shrink:0">{task['id']}</div>
                <div style="font-size:14px;font-weight:600;flex:1">{task['title']}</div>
                <span class="badge {stc(task['section_type'])}">{task['section_type']}</span>
              </div>
              <div style="font-size:12px;color:#7a8499;margin-bottom:10px;line-height:1.5">{task['goal']}</div>
              <ul style="list-style:none;margin:0;padding:0">{bullets_html}</ul>
              {f'<div style="margin-top:8px">{tags_html}</div>' if tags_html else ''}
              {f'<div style="margin-top:8px">{flags}</div>' if flags else ''}
              <div style="font-size:10px;color:#7a8499;margin-top:8px">🎯 {task['target_words']} words</div>
            </div>""", unsafe_allow_html=True)

# ── EVIDENCE ──────────────────────────────────────────────
with tab_ev:
    evidence = st.session_state.evidence
    if not evidence:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">🔬</div>
          <p class="empty-text">Research evidence will appear here when the agent searches the web.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="margin-bottom:12px"><span class="meta-pill">📚 {len(evidence)} sources</span></div>',
                    unsafe_allow_html=True)
        for item in evidence:
            url     = item.get("url","")
            snippet = item.get("snippet","")
            pub     = item.get("published_at","")
            source  = item.get("source","")
            st.markdown(f"""<div class="evidence-card">
              <div style="font-size:14px;font-weight:600;margin-bottom:4px">{item.get('title','Untitled')}</div>
              <a href="{url}" target="_blank"
                 style="font-size:11px;color:#3ccfff;word-break:break-all;
                        text-decoration:none;display:block;margin-bottom:6px">{url}</a>
              <div style="display:flex;gap:12px;font-size:10px;color:#7a8499;margin-bottom:6px">
                {f'<span>📅 {pub}</span>' if pub else ''}
                {f'<span>🌐 {source}</span>' if source else ''}
              </div>
              {f'<div style="font-size:12px;color:rgba(232,235,240,.7);line-height:1.55">{snippet[:300]}</div>' if snippet else ''}
            </div>""", unsafe_allow_html=True)

# ── MARKDOWN PREVIEW ──────────────────────────────────────
with tab_md:
    final_md = st.session_state.final_md
    if not final_md:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-text">The rendered blog post will appear here once writing is complete.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Toolbar row
        plan_data  = st.session_state.plan or {}
        blog_title = plan_data.get("blog_title", "blog")
        safe_name  = re.sub(r'[\\/:*?"<>|]', '', blog_title).strip() or "blog"

        col1, col2, col3 = st.columns([1.2, 1, 5])
        with col1:
            st.download_button("⬇️  Download .md", data=final_md,
                               file_name=f"{safe_name}.md",
                               mime="text/markdown", use_container_width=True)
        with col2:
            view_raw = st.toggle("Raw MD", value=False)

        st.divider()

        if view_raw:
            st.code(final_md, language="markdown")
        else:
            st.markdown(final_md)

# ── LOGS ──────────────────────────────────────────────────
with tab_logs:
    logs = st.session_state.logs
    if not logs:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">📋</div>
          <p class="empty-text">Pipeline logs will appear here during generation.</p>
        </div>""", unsafe_allow_html=True)
    else:
        css = {"green":"log-green","blue":"log-blue","red":"log-red"}
        lines = "".join(
            f'<div class="log-line"><span class="log-time">{ts}</span>'
            f'<span class="{css.get(lvl,"log-green")}">{msg}</span></div>'
            for ts, msg, lvl in logs
        )
        st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

        if st.button("🗑️  Clear logs", key="clear_logs"):
            st.session_state.logs = []
            st.rerun()
