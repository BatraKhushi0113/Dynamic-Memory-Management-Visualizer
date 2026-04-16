"""
app.py - Main Streamlit Dashboard
Dynamic Memory Management Visualizer
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import csv
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from visualizer import generate_full_report

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Memory Management Visualizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# THEME CSS
# ──────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2234;
    --accent: #00f5c4;
    --accent2: #7c6bfc;
    --warn: #ff6b6b;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: #1e293b;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
h1 { font-size: 2rem; background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-value { font-size: 2.2rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.fault { color: var(--warn); }
.hit { color: var(--accent); }
.algo { color: var(--accent2); }
.step-row {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 10px; border-radius: 8px; margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    background: var(--surface2); border: 1px solid var(--border);
}
.step-fault { border-left: 3px solid var(--warn); }
.step-hit   { border-left: 3px solid var(--accent); }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.badge-fault { background: #ff6b6b22; color: var(--warn); }
.badge-hit   { background: #00f5c422; color: var(--accent); }
.section-header {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    border-bottom: 1px solid var(--border); padding-bottom: 6px;
    margin-bottom: 1rem;
}
.frame-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.frame-box {
    width: 70px; height: 70px; border-radius: 10px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    border: 1px solid var(--border); font-weight: 700;
}
.frame-free { background: var(--surface2); color: var(--muted); }
.frame-used { background: linear-gradient(135deg, #7c6bfc22, #00f5c422); color: var(--accent); border-color: var(--accent2); }
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg: #f0f4ff;
    --surface: #ffffff;
    --surface2: #f8faff;
    --accent: #059669;
    --accent2: #6d28d9;
    --warn: #dc2626;
    --text: #1e293b;
    --muted: #64748b;
    --border: #e2e8f0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
h1 { font-size: 2rem; background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 8px #0001;
}
.metric-value { font-size: 2.2rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.fault { color: var(--warn); }
.hit { color: var(--accent); }
.algo { color: var(--accent2); }
.step-row {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 10px; border-radius: 8px; margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    background: var(--surface2); border: 1px solid var(--border);
}
.step-fault { border-left: 3px solid var(--warn); }
.step-hit   { border-left: 3px solid var(--accent); }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.badge-fault { background: #dc262622; color: var(--warn); }
.badge-hit   { background: #05966922; color: var(--accent); }
.section-header {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    border-bottom: 1px solid var(--border); padding-bottom: 6px;
    margin-bottom: 1rem;
}
</style>
"""


# ──────────────────────────────────────────────
# PLOTLY THEME
# ──────────────────────────────────────────────
def plotly_layout(dark: bool, title: str = "") -> dict:
    bg = "#0a0e1a" if dark else "#f0f4ff"
    paper = "#111827" if dark else "#ffffff"
    grid = "#1e293b" if dark else "#e2e8f0"
    text = "#e2e8f0" if dark else "#1e293b"
    return dict(
        title=dict(text=title, font=dict(family="Syne", size=15, color=text)),
        plot_bgcolor=bg,
        paper_bgcolor=paper,
        font=dict(family="JetBrains Mono", color=text, size=11),
        xaxis=dict(gridcolor=grid, zerolinecolor=grid),
        yaxis=dict(gridcolor=grid, zerolinecolor=grid),
        margin=dict(l=40, r=20, t=50, b=40),
    )


# ──────────────────────────────────────────────
# HELPER RENDERERS
# ──────────────────────────────────────────────
def render_metric_card(label: str, value, cls: str = ""):
    return f"""
    <div class="metric-card">
        <div class="metric-value {cls}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>"""


def render_step_log(steps: list[dict], limit: int = 20):
    html = ""
    for s in steps[:limit]:
        cls = "step-fault" if s["is_fault"] else "step-hit"
        badge_cls = "badge-fault" if s["is_fault"] else "badge-hit"
        badge_txt = "FAULT" if s["is_fault"] else "HIT"
        evicted = f" ← evict P{s['evicted_page']}" if s["evicted_page"] is not None else ""
        frames_str = " | ".join(
            f"F{fr[0]}:{fr[1] if fr[1] is not None else '—'}"
            for fr in s["frames_snapshot"]
        )
        html += f"""
        <div class="step-row {cls}">
            <span style="color:var(--muted)">#{s['step']+1:02d}</span>
            <span class="badge {badge_cls}">{badge_txt}</span>
            <span>Ref <b>P{s['page_requested']}</b>{evicted}</span>
            <span style="margin-left:auto;color:var(--muted);font-size:0.75rem">[{frames_str}]</span>
        </div>"""
    return html


def render_timeline_heatmap(timeline: dict, algo: str, dark: bool) -> go.Figure:
    matrix = timeline["matrix"]
    ref = timeline["reference_string"]
    faults = timeline["fault_markers"]
    num_frames = len(matrix)
    steps = len(ref)

    # Convert None → -1 for color mapping
    z = [[v if v is not None else -1 for v in row] for row in matrix]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[f"Ref {i+1}<br>P{ref[i]}" for i in range(steps)],
        y=[f"Frame {i}" for i in range(num_frames)],
        colorscale=[
            [0.0, "#1e293b"],
            [0.01, "#1e3a5f"],
            [0.3, "#3b5998"],
            [0.6, "#7c6bfc"],
            [1.0, "#00f5c4"],
        ] if dark else "Blues",
        showscale=True,
        text=[[str(v) if v != -1 else "—" for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(family="JetBrains Mono", size=11),
        hoverongaps=False,
    ))

    # Mark page faults with red X on x-axis
    fault_x = [f"Ref {i+1}<br>P{ref[i]}" for i, f in enumerate(faults) if f]
    if fault_x:
        fig.add_trace(go.Scatter(
            x=fault_x,
            y=[-0.7] * len(fault_x),
            mode="markers",
            marker=dict(symbol="x", size=10, color="#ff6b6b"),
            name="Page Fault",
            showlegend=True,
        ))

    layout = plotly_layout(dark, f"{algo} — Frame State Timeline")
    layout["yaxis"] = dict(autorange="reversed")

    fig.update_layout(
        **layout,
        height=max(220, num_frames * 55 + 80)
    )

    return fig


def render_fault_curve(fifo_curve: dict, lru_curve: dict, dark: bool) -> go.Figure:
    c1 = "#ff6b6b" if dark else "#dc2626"
    c2 = "#7c6bfc" if dark else "#6d28d9"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fifo_curve["x"], y=fifo_curve["faults"],
                             name="FIFO Faults", line=dict(color=c1, width=2.5), mode="lines+markers",
                             marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=lru_curve["x"], y=lru_curve["faults"],
                             name="LRU Faults", line=dict(color=c2, width=2.5, dash="dash"), mode="lines+markers",
                             marker=dict(size=6)))
    fig.update_layout(**plotly_layout(dark, "Cumulative Page Faults — FIFO vs LRU"), height=300)
    return fig


def render_comparison_bar(comp: dict, dark: bool) -> go.Figure:
    c_fault = "#ff6b6b" if dark else "#dc2626"
    c_hit = "#00f5c4" if dark else "#059669"
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Page Faults", x=comp["algorithms"], y=comp["page_faults"],
                         marker_color=c_fault, text=comp["page_faults"], textposition="outside"))
    fig.add_trace(go.Bar(name="Page Hits", x=comp["algorithms"], y=comp["page_hits"],
                         marker_color=c_hit, text=comp["page_hits"], textposition="outside"))
    fig.update_layout(**plotly_layout(dark, "Algorithm Comparison: Faults vs Hits"), barmode="group", height=320)
    return fig


def render_hit_rate_gauge(hit_rate: float, label: str, dark: bool) -> go.Figure:
    color = "#00f5c4" if dark else "#059669"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(hit_rate * 100, 1),
        title=dict(text=label, font=dict(family="Syne", size=13)),
        number=dict(suffix="%", font=dict(family="JetBrains Mono", size=28)),
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=color),
            bgcolor="#1e293b" if dark else "#e2e8f0",
            steps=[
                dict(range=[0, 40], color="#ff6b6b"),
                dict(range=[40, 70], color="#fbbf24"),
                dict(range=[70, 100], color="#00f5c4"),
            ],
        ),
    ))
    fig.update_layout(paper_bgcolor="#111827" if dark else "#ffffff",
                      font=dict(color="#e2e8f0" if dark else "#1e293b", family="JetBrains Mono"),
                      height=200, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def render_segmentation_chart(seg_data: list[dict], dark: bool) -> go.Figure:
    if not seg_data:
        return go.Figure()
    segs = seg_data[0]["segments"]
    colors = ["#7c6bfc", "#00f5c4", "#ff6b6b", "#fbbf24"]
    fig = go.Figure()
    for i, s in enumerate(segs):
        fig.add_trace(go.Bar(
            name=s["name"], x=[s["limit"]], y=["Memory"],
            orientation="h", marker_color=colors[i % len(colors)],
            text=f"{s['name']}<br>Base:{s['base']} Limit:{s['limit']}",
            textposition="inside", hoverinfo="text",
        ))
    fig.update_layout(
        title="Segmentation Layout (Process 0)",
        barmode="stack",
        height=140,
        yaxis=dict(
            showticklabels=False
        ),
        showlegend=True
    )
    return fig


def render_vm_table(vm_data: dict, dark: bool):
    if not vm_data or "mappings" not in vm_data:
        return pd.DataFrame()
    rows = []
    for m in vm_data["mappings"]:
        rows.append({
            "Page": f"P{m['page_id']}",
            "Logical (start)": m["logical_start"],
            "Logical (end)": m["logical_end"],
            "Frame": f"F{m['frame_id']}" if m["frame_id"] is not None else "—",
            "Physical (start)": m["physical_start"] if m["physical_start"] is not None else "—",
            "In Memory": "✅" if m["valid"] else "💾 Disk",
        })
    return pd.DataFrame(rows)


def export_csv(steps: list[dict]) -> str:
    output = io.StringIO()
    fieldnames = ["step", "page_requested", "is_fault", "evicted_page", "evicted_frame",
                  "fault_count", "hit_count", "algorithm"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(steps)
    return output.getvalue()


# ──────────────────────────────────────────────
# SAMPLE INPUTS
# ──────────────────────────────────────────────
SAMPLES = {
    "Classic OS Example": {
        "ref": "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1",
        "frames": 3, "memory": 512, "page_size": 64, "processes": 2,
    },
    "Locality of Reference": {
        "ref": "1 2 3 4 1 2 5 1 2 3 4 5",
        "frames": 3, "memory": 256, "page_size": 32, "processes": 1,
    },
    "Thrashing Scenario": {
        "ref": "1 2 3 4 5 1 2 3 4 5 1 2 3 4 5",
        "frames": 2, "memory": 128, "page_size": 16, "processes": 2,
    },
    "High Reuse": {
        "ref": "1 2 3 1 2 3 1 2 3 1 2 3",
        "frames": 4, "memory": 256, "page_size": 32, "processes": 1,
    },
}


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")

        dark = st.toggle("🌙 Dark Mode", value=True)

        st.markdown("---")
        st.markdown("### 📋 Quick Samples")
        sample_key = st.selectbox("Load sample", ["— Custom —"] + list(SAMPLES.keys()))

        if sample_key != "— Custom —":
            s = SAMPLES[sample_key]
            default_ref = s["ref"]
            default_frames = s["frames"]
            default_memory = s["memory"]
            default_page = s["page_size"]
            default_procs = s["processes"]
        else:
            default_ref = "7 0 1 2 0 3 0 4 2 3 0 3 2"
            default_frames = 3
            default_memory = 256
            default_page = 32
            default_procs = 2

        st.markdown("### 🔢 Parameters")
        ref_input = st.text_input("Page Reference String", value=default_ref,
                                   help="Space-separated page numbers, e.g. '1 2 3 1 4'")
        num_frames = st.slider("Number of Frames (RAM slots)", 1, 8, default_frames)
        total_memory = st.select_slider("Total Memory (KB)", [64, 128, 256, 512, 1024], default_memory)
        page_size = st.select_slider("Page/Frame Size (KB)", [8, 16, 32, 64, 128], default_page)
        num_processes = st.slider("Number of Processes", 1, 4, default_procs)

        st.markdown("### 🧮 Algorithm")
        algo = st.radio("Primary view", ["Both", "FIFO only", "LRU only"])

        st.markdown("---")
        run = st.button("▶ Run Simulation", use_container_width=True, type="primary")

        return dark, ref_input, num_frames, total_memory, page_size, num_processes, algo, run


# ──────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────
def main():
    dark, ref_input, num_frames, total_memory, page_size, num_processes, algo, run = sidebar()

    # Apply CSS
    st.markdown(DARK_CSS if dark else LIGHT_CSS, unsafe_allow_html=True)

    # Header
    st.markdown("# 🧠 Dynamic Memory Management Visualizer")
    st.markdown(
        "<p style='color:var(--muted);font-size:0.9rem;margin-top:-8px'>"
        "Simulate Paging · Segmentation · Virtual Memory · Page Replacement (FIFO &amp; LRU)"
        "</p>",
        unsafe_allow_html=True,
    )

    if not run and "report" not in st.session_state:
        st.info("👈 Configure parameters in the sidebar and click **▶ Run Simulation**")
        st.markdown("""
        ### 📚 About this Visualizer
        This tool simulates core OS memory management concepts:
        - **Paging** — divide memory into fixed-size frames and map logical pages to physical frames
        - **Segmentation** — divide process memory into logical segments (Code, Data, Stack, Heap)
        - **Virtual Memory** — show the mapping from logical → physical addresses
        - **FIFO** — replace the oldest loaded page on a fault
        - **LRU** — replace the least recently used page on a fault

        Select a **Quick Sample** or enter your own reference string and click **▶ Run Simulation**.
        """)
        return

    # Parse input
    try:
        ref_string = list(map(int, ref_input.split()))
        assert len(ref_string) >= 2
    except Exception:
        st.error("❌ Invalid reference string. Enter space-separated integers, e.g. `7 0 1 2 0 3`")
        return

    if run or "report" in st.session_state:
        if run:
            with st.spinner("Running simulation…"):
                report = generate_full_report(ref_string, num_frames, total_memory, page_size, num_processes)
            st.session_state["report"] = report
        else:
            report = st.session_state["report"]

        fifo_m = report["fifo"]["metrics"]
        lru_m = report["lru"]["metrics"]
        fifo_steps = report["fifo"]["steps"]
        lru_steps = report["lru"]["steps"]
        n = len(ref_string)

        # ── TOP METRICS ──
        st.markdown('<p class="section-header">📊 Simulation Metrics</p>', unsafe_allow_html=True)
        cols = st.columns(6)
        metrics = [
            ("Ref. Length", n, ""),
            ("Frames", num_frames, "algo"),
            ("FIFO Faults", fifo_m["page_faults"], "fault"),
            ("LRU Faults", lru_m["page_faults"], "fault"),
            ("FIFO Hit Rate", f"{fifo_m['hit_rate']*100:.1f}%", "hit"),
            ("LRU Hit Rate", f"{lru_m['hit_rate']*100:.1f}%", "hit"),
        ]
        for col, (label, value, cls) in zip(cols, metrics):
            with col:
                st.markdown(render_metric_card(label, value, cls), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── TABS ──
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Comparison", "🔁 FIFO Detail", "🔁 LRU Detail",
            "🗺️ Memory & VM", "📋 Step Log"
        ])

        # ── TAB 1: Comparison ──
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(render_fault_curve(
                    report["fifo"]["fault_curve"],
                    report["lru"]["fault_curve"], dark),
                    use_container_width=True)
            with c2:
                st.plotly_chart(render_comparison_bar(report["comparison"], dark),
                                use_container_width=True)

            # Gauge row
            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(render_hit_rate_gauge(fifo_m["hit_rate"], "FIFO Hit Rate", dark),
                                use_container_width=True)
            with g2:
                better = "LRU" if lru_m["page_faults"] < fifo_m["page_faults"] else (
                    "FIFO" if fifo_m["page_faults"] < lru_m["page_faults"] else "TIE")
                diff = abs(fifo_m["page_faults"] - lru_m["page_faults"])
                st.markdown(
                    f"""<div class="metric-card" style="margin-top:20px">
                    <div class="metric-value algo">{better}</div>
                    <div class="metric-label">Wins by {diff} fault(s)</div></div>""",
                    unsafe_allow_html=True)
            with g3:
                st.plotly_chart(render_hit_rate_gauge(lru_m["hit_rate"], "LRU Hit Rate", dark),
                                use_container_width=True)

            # CSV export
            st.markdown("---")
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                st.download_button("⬇ Export FIFO Results (CSV)",
                                   export_csv(fifo_steps), "fifo_results.csv", "text/csv")
            with ecol2:
                st.download_button("⬇ Export LRU Results (CSV)",
                                   export_csv(lru_steps), "lru_results.csv", "text/csv")

        # ── TAB 2: FIFO ──
        with tab2:
            if algo != "LRU only":
                st.plotly_chart(render_timeline_heatmap(
                    report["fifo"]["timeline"], "FIFO", dark),
                    use_container_width=True)
                st.markdown(
                    f"**Total Faults:** <span class='fault'>{fifo_m['page_faults']}</span> / "
                    f"**Hits:** <span class='hit'>{fifo_m['page_hits']}</span> / "
                    f"**Fault Rate:** {fifo_m['fault_rate']*100:.1f}%",
                    unsafe_allow_html=True)
            else:
                st.info("FIFO is hidden (LRU only mode selected).")

        # ── TAB 3: LRU ──
        with tab3:
            if algo != "FIFO only":
                st.plotly_chart(render_timeline_heatmap(
                    report["lru"]["timeline"], "LRU", dark),
                    use_container_width=True)
                st.markdown(
                    f"**Total Faults:** <span class='fault'>{lru_m['page_faults']}</span> / "
                    f"**Hits:** <span class='hit'>{lru_m['page_hits']}</span> / "
                    f"**Fault Rate:** {lru_m['fault_rate']*100:.1f}%",
                    unsafe_allow_html=True)
            else:
                st.info("LRU is hidden (FIFO only mode selected).")

        # ── TAB 4: Memory & VM ──
        with tab4:
            st.markdown('<p class="section-header">📦 Segmentation Layout</p>', unsafe_allow_html=True)
            st.plotly_chart(render_segmentation_chart(report["segmentation"], dark),
                            use_container_width=True)

            st.markdown('<p class="section-header">🗺️ Virtual Memory Mapping (Process 0)</p>',
                        unsafe_allow_html=True)
            vm_df = render_vm_table(report["virtual_memory"], dark)
            if not vm_df.empty:
                st.dataframe(vm_df, use_container_width=True, hide_index=True)

            st.markdown('<p class="section-header">🏗️ Physical Memory Frames</p>', unsafe_allow_html=True)
            mem_blocks = report["memory_map"]["blocks"]
            cols_per_row = 8
            for row_start in range(0, len(mem_blocks), cols_per_row):
                row = mem_blocks[row_start:row_start + cols_per_row]
                cols = st.columns(len(row))
                for col, block in zip(cols, row):
                    with col:
                        color = "#00f5c4" if not block["is_free"] else "#64748b"
                        bg = "#7c6bfc22" if not block["is_free"] else "#1e293b"
                        st.markdown(
                            f"<div style='background:{bg};border:1px solid {color};"
                            f"border-radius:8px;padding:8px;text-align:center;"
                            f"font-family:JetBrains Mono,monospace;font-size:0.75rem;color:{color}'>"
                            f"<b>F{block['frame_id']}</b><br>{block['label']}</div>",
                            unsafe_allow_html=True)

            st.markdown('<p class="section-header">🌐 RAM vs Disk Analogy</p>', unsafe_allow_html=True)
            st.markdown("""
            | Location | Analogy | Speed | Cost |
            |----------|---------|-------|------|
            | **CPU Registers** | Your hand | Instant | Very expensive |
            | **Cache (L1/L2)** | Your desk | ~ns | Expensive |
            | **RAM (Physical Frames)** | Filing cabinet | ~100ns | Moderate |
            | **Virtual Memory (Disk)** | Storage room | ~ms | Cheap |

            When a page is not in RAM, a **page fault** occurs and the OS swaps it in from disk — this is thousands of times slower than a RAM access!
            """)

        # ── TAB 5: Step Log ──
        with tab5:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### FIFO Step-by-Step")
                st.markdown(render_step_log(fifo_steps, limit=50), unsafe_allow_html=True)
            with c2:
                st.markdown("### LRU Step-by-Step")
                st.markdown(render_step_log(lru_steps, limit=50), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
