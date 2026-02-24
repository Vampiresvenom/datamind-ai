import streamlit as st
import pandas as pd
import numpy as np
import json, re, io, os, textwrap
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="DataMind AI — Analysis", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root { --neon:#00F5C4; --bg:#0A0E1A; --card:#111827; --card2:#1a2235; --border:rgba(0,245,196,0.15); --text:#E2E8F0; --muted:#64748b; }
* { font-family:'DM Sans',sans-serif; }
html,body,.stApp { background:var(--bg) !important; color:var(--text) !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding:2rem !important; max-width:1400px !important; }
[data-testid="stSidebar"] { background:#0d1220 !important; border-right:1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color:var(--text) !important; }
.stButton>button { background:linear-gradient(135deg,#00F5C4,#7C3AED) !important; color:#0A0E1A !important; border:none !important; border-radius:10px !important; font-weight:700 !important; }
.stDownloadButton>button { background:#1a2235 !important; color:#00F5C4 !important; border:1px solid var(--border) !important; border-radius:10px !important; font-weight:600 !important; }
[data-testid="stMetric"] { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:12px !important; padding:1rem !important; }
[data-testid="stMetricValue"] { color:var(--neon) !important; font-weight:700 !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--card) !important; border-radius:12px !important; padding:4px !important; border:1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { border-radius:8px !important; color:var(--muted) !important; font-weight:600 !important; }
.stTabs [aria-selected="true"] { background:rgba(0,245,196,0.15) !important; color:var(--neon) !important; }
[data-testid="stExpander"] { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:12px !important; }
.stProgress>div>div { background:var(--neon) !important; border-radius:99px !important; }
hr { border-color:var(--border) !important; }
.pill { display:inline-block; padding:3px 12px; border-radius:99px; font-size:0.75rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin:2px; }
.pill-g { background:rgba(0,245,196,0.1); color:#00F5C4; border:1px solid rgba(0,245,196,0.25); }
.pill-r { background:rgba(248,113,113,0.1); color:#F87171; border:1px solid rgba(248,113,113,0.25); }
.pill-y { background:rgba(251,191,36,0.1); color:#FBBF24; border:1px solid rgba(251,191,36,0.25); }
.dax-block { background:#0d1220; border:1px solid rgba(0,245,196,0.15); border-radius:10px; padding:1rem; font-family:'Space Mono',monospace; font-size:0.82rem; line-height:1.7; color:#a5f3fc; overflow-x:auto; }
.section-label { font-family:'Space Mono',monospace; font-size:0.72rem; color:#00F5C4; letter-spacing:2px; text-transform:uppercase; opacity:0.8; margin-bottom:0.6rem; }
.insight-card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.6rem; border-left:3px solid #00F5C4; }
.issue-card { background:var(--card); border:1px solid rgba(251,191,36,0.2); border-radius:12px; padding:0.8rem 1.2rem; margin-bottom:0.5rem; border-left:3px solid #FBBF24; font-size:0.9rem; color:#FBBF24; }
.action-card { background:var(--card); border:1px solid rgba(0,245,196,0.15); border-radius:12px; padding:0.8rem 1.2rem; margin-bottom:0.5rem; border-left:3px solid #00F5C4; font-size:0.9rem; color:#94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── Guard: session state check ───────────────────────────────────────────────
if 'all_dfs' not in st.session_state or 'api_key' not in st.session_state:
    st.warning("Please upload files and enter your API key on the home page first.")
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    st.stop()

all_dfs = st.session_state['all_dfs']
api_key = st.session_state['api_key']

# ── Imports from utils ───────────────────────────────────────────────────────
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_engine import analyze_with_claude, generate_dax, generate_power_query
from utils.data_cleaner import clean_dataframe, build_data_summary
from utils.report_builder import build_excel_report, build_pdf_report
from utils.charts import make_charts

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:1rem; margin-bottom:2rem;">
    <div style="font-size:2rem;">⚡</div>
    <div>
        <h1 style="margin:0; font-size:1.8rem; font-weight:700;
                   background:linear-gradient(90deg,#E2E8F0,#00F5C4);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            AI Analysis Pipeline
        </h1>
        <div style="color:#64748b; font-size:0.9rem; margin-top:2px;">
            Running full BI workflow on your data
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Process each file ────────────────────────────────────────────────────────
for filename, df_raw in all_dfs.items():

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,245,196,0.08),rgba(124,58,237,0.08));
                border:1px solid rgba(0,245,196,0.2); border-radius:16px;
                padding:1.2rem 1.5rem; margin:1.5rem 0 1rem 0;
                display:flex; align-items:center; gap:12px;">
        <span style="font-size:1.3rem;">📄</span>
        <div>
            <div style="font-weight:700; font-size:1.05rem;">{filename}</div>
            <div style="color:#64748b; font-size:0.85rem;">
                {df_raw.shape[0]:,} rows · {df_raw.shape[1]} columns
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 AI Analysis",
        "🧹 Cleaned Data",
        "📐 DAX Formulas",
        "🔄 Power Query",
        "📊 Dashboard"
    ])

    # ── TAB 1: AI Analysis ───────────────────────────────────────────────────
    with tab1:
        if f'{filename}_ai' not in st.session_state:
            with st.spinner("🤖 Claude is reading your data..."):
                try:
                    summary = build_data_summary(df_raw)
                    ai = analyze_with_claude(api_key, filename, summary)
                    st.session_state[f'{filename}_ai'] = ai
                except Exception as e:
                    st.error(f"AI Analysis failed: {e}")
                    st.stop()

        ai = st.session_state[f'{filename}_ai']

        # Description + domain
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown('<div class="section-label">What is this data?</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="insight-card">
                <div style="font-size:1rem; line-height:1.7; color:#cbd5e1;">{ai.get('data_description','')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-label">Domain</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:var(--card); border:1px solid var(--border); border-radius:12px;
                        padding:1.2rem; text-align:center;">
                <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Detected as</div>
                <div style="font-size:1.3rem; font-weight:700; color:#00F5C4; margin-top:4px;">{ai.get('domain','General')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Quality issues + KPIs side by side
        q_col, k_col = st.columns(2)
        with q_col:
            st.markdown('<div class="section-label">⚠️ Quality Issues Found</div>', unsafe_allow_html=True)
            issues = ai.get('quality_issues', [])
            if issues:
                for issue in issues:
                    st.markdown(f'<div class="issue-card">⚠️ {issue}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="action-card">✓ No major quality issues found</div>', unsafe_allow_html=True)

        with k_col:
            st.markdown('<div class="section-label">🎯 Recommended KPIs</div>', unsafe_allow_html=True)
            for kpi in ai.get('kpis', []):
                st.markdown(f'<div class="insight-card" style="border-left-color:#7C3AED;">🎯 {kpi}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Insights
        st.markdown('<div class="section-label">💡 Business Insights</div>', unsafe_allow_html=True)
        for insight in ai.get('insights', []):
            st.markdown(f'<div class="insight-card">💡 {insight}</div>', unsafe_allow_html=True)

        # Column summary table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📋 Column Summary</div>', unsafe_allow_html=True)
        col_df = pd.DataFrame({
            'Column': df_raw.columns,
            'Type': df_raw.dtypes.astype(str).values,
            'Non-Null': df_raw.count().values,
            'Missing': df_raw.isnull().sum().values,
            'Unique': df_raw.nunique().values
        })
        st.dataframe(col_df, use_container_width=True, hide_index=True)

    # ── TAB 2: Cleaned Data ──────────────────────────────────────────────────
    with tab2:
        if f'{filename}_clean' not in st.session_state:
            with st.spinner("🧹 Cleaning your data..."):
                df_clean, actions = clean_dataframe(df_raw)
                st.session_state[f'{filename}_clean'] = df_clean
                st.session_state[f'{filename}_actions'] = actions

        df_clean = st.session_state[f'{filename}_clean']
        actions = st.session_state[f'{filename}_actions']

        # Before / after metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows Before", f"{df_raw.shape[0]:,}")
        m2.metric("Rows After", f"{df_clean.shape[0]:,}",
                  delta=f"-{df_raw.shape[0]-df_clean.shape[0]}" if df_raw.shape[0] != df_clean.shape[0] else "No change")
        m3.metric("Missing Before", f"{df_raw.isnull().sum().sum():,}")
        m4.metric("Missing After", f"{df_clean.isnull().sum().sum():,}",
                  delta=f"-{df_raw.isnull().sum().sum()-df_clean.isnull().sum().sum()}" if df_raw.isnull().sum().sum() > 0 else "None")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">✅ Cleaning Actions Taken</div>', unsafe_allow_html=True)
        for action in actions:
            st.markdown(f'<div class="action-card">✓ {action}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📋 Cleaned Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df_clean, use_container_width=True)

    # ── TAB 3: DAX Formulas ──────────────────────────────────────────────────
    with tab3:
        ai = st.session_state.get(f'{filename}_ai', {})
        df_clean = st.session_state.get(f'{filename}_clean', df_raw)

        if f'{filename}_dax' not in st.session_state:
            with st.spinner("📐 Claude is writing DAX formulas..."):
                try:
                    dax, table_name = generate_dax(api_key, filename, df_clean, ai)
                    st.session_state[f'{filename}_dax'] = dax
                    st.session_state[f'{filename}_table'] = table_name
                except Exception as e:
                    st.error(f"DAX generation failed: {e}")
                    dax, table_name = {}, filename

        dax = st.session_state.get(f'{filename}_dax', {})
        table_name = st.session_state.get(f'{filename}_table', filename)

        st.markdown(f"""
        <div style="background:var(--card); border:1px solid var(--border); border-radius:12px;
                    padding:1rem 1.2rem; margin-bottom:1.5rem;">
            <span style="color:#64748b; font-size:0.85rem;">Power BI Table Name: </span>
            <code style="color:#00F5C4; font-family:'Space Mono',monospace;">{table_name}</code>
            <span style="color:#64748b; font-size:0.85rem; margin-left:1.5rem;">
                How to use: </span>
            <span style="color:#94a3b8; font-size:0.85rem;">
                Modeling → New Measure → Paste formula
            </span>
        </div>
        """, unsafe_allow_html=True)

        if dax:
            for name, formula in dax.items():
                with st.expander(f"📐 {name}"):
                    st.markdown(f'<div class="dax-block">{formula}</div>', unsafe_allow_html=True)
                    st.code(formula, language="sql")

    # ── TAB 4: Power Query ───────────────────────────────────────────────────
    with tab4:
        ai = st.session_state.get(f'{filename}_ai', {})
        df_clean = st.session_state.get(f'{filename}_clean', df_raw)
        actions = st.session_state.get(f'{filename}_actions', [])

        if f'{filename}_pq' not in st.session_state:
            with st.spinner("🔄 Claude is writing Power Query M code..."):
                try:
                    pq = generate_power_query(api_key, filename, df_raw, df_clean, actions)
                    st.session_state[f'{filename}_pq'] = pq
                except Exception as e:
                    st.error(f"Power Query generation failed: {e}")
                    pq = "// Error generating Power Query code"

        pq = st.session_state.get(f'{filename}_pq', '')

        st.markdown("""
        <div style="background:var(--card); border:1px solid rgba(251,191,36,0.2);
                    border-radius:12px; padding:1rem 1.2rem; margin-bottom:1.5rem;
                    border-left:3px solid #FBBF24;">
            <div style="color:#FBBF24; font-weight:600; margin-bottom:4px;">How to use in Power BI</div>
            <div style="color:#94a3b8; font-size:0.9rem; line-height:1.8;">
                1. Open Power BI Desktop &nbsp;→&nbsp;
                2. Home → Transform Data &nbsp;→&nbsp;
                3. View → Advanced Editor &nbsp;→&nbsp;
                4. Delete all code → Paste below &nbsp;→&nbsp;
                5. Update file path → Click Done
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.code(pq, language="javascript")

    # ── TAB 5: Dashboard ─────────────────────────────────────────────────────
    with tab5:
        ai = st.session_state.get(f'{filename}_ai', {})
        df_clean = st.session_state.get(f'{filename}_clean', df_raw)

        if f'{filename}_charts' not in st.session_state:
            with st.spinner("📊 Building your dashboard..."):
                charts = make_charts(df_clean, ai)
                st.session_state[f'{filename}_charts'] = charts

        charts = st.session_state.get(f'{filename}_charts', [])
        for fig in charts:
            st.plotly_chart(fig, use_container_width=True)

    # ── Download Section ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:#00F5C4;
                letter-spacing:2px; text-transform:uppercase; opacity:0.8; margin-bottom:1rem;">
        📥 Export Your Outputs
    </div>
    """, unsafe_allow_html=True)

    df_clean = st.session_state.get(f'{filename}_clean', df_raw)
    ai = st.session_state.get(f'{filename}_ai', {})
    dax = st.session_state.get(f'{filename}_dax', {})
    actions = st.session_state.get(f'{filename}_actions', [])
    pq = st.session_state.get(f'{filename}_pq', '')
    charts = st.session_state.get(f'{filename}_charts', [])

    d1, d2, d3, d4 = st.columns(4)
    base = filename.replace('.xlsx','').replace('.xls','').replace('.csv','')
    ts = datetime.now().strftime('%Y%m%d_%H%M')

    # Excel
    with d1:
        with st.spinner("Building Excel..."):
            try:
                xl_bytes = build_excel_report(df_clean, ai, dax, actions, filename)
                st.download_button(
                    "📁 Cleaned Excel",
                    data=xl_bytes,
                    file_name=f"Cleaned_{base}_{ts}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Excel error: {e}")

    # PDF
    with d2:
        with st.spinner("Building PDF..."):
            try:
                pdf_bytes = build_pdf_report(df_clean, ai, dax, cleaning_actions=actions, filename=filename, charts=charts)
                st.download_button(
                    "📄 PDF Report",
                    data=pdf_bytes,
                    file_name=f"Report_{base}_{ts}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF error: {e}")

    # DAX
    with d3:
        if dax:
            dax_txt = f"DAX Formulas for: {filename}\nGenerated: {datetime.now()}\nTable: '{st.session_state.get(f'{filename}_table',base)}'\n\n"
            dax_txt += "="*60 + "\n\n"
            dax_txt += "HOW TO USE:\nPower BI Desktop → Modeling → New Measure → Paste formula\n\n"
            dax_txt += "="*60 + "\n\n"
            for n, f in dax.items():
                dax_txt += f"// {n}\n{f}\n\n{'-'*50}\n\n"
            st.download_button(
                "📐 DAX Formulas",
                data=dax_txt,
                file_name=f"DAX_{base}_{ts}.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Power Query
    with d4:
        if pq:
            pq_txt = f"Power Query M Code for: {filename}\nGenerated: {datetime.now()}\n\n"
            pq_txt += "="*60 + "\nHOW TO USE:\nPower BI → Transform Data → Advanced Editor → Paste\n"
            pq_txt += "="*60 + "\n\n" + pq
            st.download_button(
                "🔄 Power Query",
                data=pq_txt,
                file_name=f"PowerQuery_{base}_{ts}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)

# ── Back button ──────────────────────────────────────────────────────────────
if st.button("← Upload New File"):
    for key in list(st.session_state.keys()):
        if key not in ['api_key']:
            del st.session_state[key]
    st.switch_page("app.py")
