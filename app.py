import streamlit as st

st.set_page_config(
    page_title="DataMind AI — BI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --neon: #00F5C4;
    --neon2: #7C3AED;
    --bg: #0A0E1A;
    --card: #111827;
    --card2: #1a2235;
    --border: rgba(0,245,196,0.15);
    --text: #E2E8F0;
    --muted: #64748b;
    --danger: #F87171;
    --warn: #FBBF24;
}

* { font-family: 'DM Sans', sans-serif; }
code, pre, .mono { font-family: 'Space Mono', monospace !important; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem 2rem !important; max-width: 1400px !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #0A0E1A 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--neon) !important;
    box-shadow: 0 0 30px rgba(0,245,196,0.1) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00F5C4 0%, #7C3AED 100%) !important;
    color: #0A0E1A !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(0,245,196,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 40px rgba(0,245,196,0.5) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: var(--neon) !important; font-weight: 700 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; }

/* Expander */
[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--neon) !important;
    box-shadow: 0 0 20px rgba(0,245,196,0.2) !important;
}

/* Download button */
.stDownloadButton > button {
    background: var(--card2) !important;
    color: var(--neon) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,245,196,0.1) !important;
    border-color: var(--neon) !important;
    box-shadow: 0 0 20px rgba(0,245,196,0.2) !important;
}

/* Code blocks */
.stCode, .stCodeBlock { border-radius: 10px !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,245,196,0.2), rgba(124,58,237,0.2)) !important;
    color: var(--neon) !important;
}

/* Progress bar */
.stProgress > div > div { background: var(--neon) !important; border-radius: 99px !important; }

/* Alerts */
.stAlert { border-radius: 12px !important; border-left-width: 4px !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--neon) !important; }

/* Select box */
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* Notification badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-neon { background: rgba(0,245,196,0.15); color: #00F5C4; border: 1px solid rgba(0,245,196,0.3); }
.badge-purple { background: rgba(124,58,237,0.15); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }
.badge-warn { background: rgba(251,191,36,0.15); color: #FBBF24; border: 1px solid rgba(251,191,36,0.3); }
.badge-danger { background: rgba(248,113,113,0.15); color: #F87171; border: 1px solid rgba(248,113,113,0.3); }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding: 1.5rem 0 1rem 0; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">⚡</div>
        <div style="font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700;
                    background: linear-gradient(90deg, #00F5C4, #7C3AED);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            DataMind AI
        </div>
        <div style="font-size: 0.75rem; color: #64748b; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px;">
            BI Agent v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(0,245,196,0.15); margin: 0 0 1.5rem 0;'>", unsafe_allow_html=True)

    # API Key input
    st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;'>Claude API Key</div>", unsafe_allow_html=True)

    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        label_visibility="collapsed",
        key="api_key_input"
    )

    if api_key and len(api_key) > 20 and "PASTE" not in api_key:
        st.markdown('<div style="color:#00F5C4; font-size:0.85rem; margin-top:6px;">✓ API key entered</div>', unsafe_allow_html=True)
        st.session_state['api_key'] = api_key
    elif api_key:
        st.markdown('<div style="color:#F87171; font-size:0.85rem; margin-top:6px;">✗ Key looks invalid</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:0.8rem; color:#64748b; margin-top:6px; line-height:1.6;">
            Get free credits at<br>
            <a href="https://console.anthropic.com" target="_blank"
               style="color:#00F5C4; text-decoration:none;">console.anthropic.com →</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(0,245,196,0.15); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Pipeline steps
    st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-bottom:12px;'>Pipeline</div>", unsafe_allow_html=True)

    steps = [
        ("01", "Upload Excel / CSV"),
        ("02", "AI Analyzes Data"),
        ("03", "Auto-Clean"),
        ("04", "Generate DAX"),
        ("05", "Power Query Code"),
        ("06", "Build Dashboard"),
        ("07", "Export All"),
    ]
    for num, label in steps:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <span style="font-family:'Space Mono',monospace; font-size:0.7rem;
                         color:#00F5C4; opacity:0.6; min-width:24px;">{num}</span>
            <span style="font-size:0.85rem; color:#94a3b8;">{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(0,245,196,0.15); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Supported formats
    st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>Supported Formats</div>", unsafe_allow_html=True)
    for fmt in [".xlsx", ".xls", ".csv"]:
        st.markdown(f'<span class="badge badge-neon" style="margin-right:4px;">{fmt}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem; color:#334155; text-align:center;'>Built with Claude AI · Anthropic</div>", unsafe_allow_html=True)

# ── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <div style="font-family: 'Space Mono', monospace; font-size: 0.8rem;
                color: #00F5C4; letter-spacing: 3px; text-transform: uppercase;
                margin-bottom: 1rem; opacity: 0.8;">
        ⚡ Powered by Claude AI
    </div>
    <h1 style="font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 700;
               background: linear-gradient(135deg, #E2E8F0 0%, #00F5C4 50%, #7C3AED 100%);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               margin: 0 0 1rem 0; line-height: 1.1;">
        Your Excel Data,<br>Transformed in Seconds
    </h1>
    <p style="font-size: 1.15rem; color: #64748b; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.7;">
        Upload any Excel file. Get clean data, DAX formulas,
        Power Query code, interactive charts and a PDF report — instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Capability Pills ─────────────────────────────────────────────────────────
cols = st.columns(4)
caps = [
    ("🧹", "Auto Clean", "Removes duplicates, fixes types, fills gaps"),
    ("📐", "DAX Formulas", "10+ measures ready for Power BI"),
    ("🔄", "Power Query", "M code to replicate cleaning in PBI"),
    ("📊", "Dashboard", "5 interactive charts + PDF report"),
]
for col, (icon, title, desc) in zip(cols, caps):
    with col:
        st.markdown(f"""
        <div style="background: #111827; border: 1px solid rgba(0,245,196,0.12);
                    border-radius: 14px; padding: 1.2rem; text-align: center;
                    transition: all 0.3s ease; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-weight: 700; font-size: 0.95rem; color: #E2E8F0; margin-bottom: 0.3rem;">{title}</div>
            <div style="font-size: 0.8rem; color: #475569; line-height: 1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gate: require API key ────────────────────────────────────────────────────
if not api_key or len(api_key) < 20 or "PASTE" in api_key:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0,245,196,0.05), rgba(124,58,237,0.05));
                border: 1px solid rgba(0,245,196,0.2); border-radius: 16px;
                padding: 2rem; text-align: center; margin: 1rem 0;">
        <div style="font-size: 2rem; margin-bottom: 0.8rem;">🔑</div>
        <div style="font-size: 1.1rem; font-weight: 600; color: #E2E8F0; margin-bottom: 0.5rem;">
            Enter your Claude API Key to begin
        </div>
        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">
            Free account at <a href="https://console.anthropic.com" target="_blank"
            style="color:#00F5C4;">console.anthropic.com</a> — includes $5 free credits (~500 reports)
        </div>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
            <div style="font-size:0.85rem; color:#475569;">✓ No subscription needed</div>
            <div style="font-size:0.85rem; color:#475569;">✓ Your key stays private</div>
            <div style="font-size:0.85rem; color:#475569;">✓ ~$0.02 per report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── File Upload Section ──────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#00F5C4;
            letter-spacing:2px; text-transform:uppercase; margin-bottom:0.8rem; opacity:0.8;">
    Step 01 — Upload Your Data
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drop your Excel or CSV files here",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if not uploaded_files:
    st.markdown("""
    <div style="text-align:center; padding: 2rem; color: #334155; font-size:0.9rem;">
        ↑ Upload one or more files to begin your analysis
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Route to analysis page ───────────────────────────────────────────────────
# Store files in session state
import io, pandas as pd
st.session_state['uploaded_files_data'] = {}

all_dfs = {}
for uf in uploaded_files:
    try:
        raw_bytes = uf.read()
        if uf.name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(raw_bytes))
        else:
            sheets = pd.read_excel(io.BytesIO(raw_bytes), sheet_name=None)
            df = list(sheets.values())[0]
        all_dfs[uf.name] = df
    except Exception as e:
        st.error(f"Could not read **{uf.name}**: {e}")

if not all_dfs:
    st.stop()

st.session_state['all_dfs'] = all_dfs
st.session_state['api_key'] = api_key

# ── File preview cards ───────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#00F5C4;
            letter-spacing:2px; text-transform:uppercase; margin-bottom:0.8rem; opacity:0.8;">
    Step 02 — Preview
</div>
""", unsafe_allow_html=True)

for fname, df in all_dfs.items():
    with st.expander(f"📄 {fname}  —  {df.shape[0]:,} rows × {df.shape[1]} cols", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{df.shape[0]:,}")
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing", f"{df.isnull().sum().sum():,}")
        c4.metric("Duplicates", f"{df.duplicated().sum():,}")
        st.dataframe(df.head(8), use_container_width=True)

# ── Analyse Button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    run = st.button("⚡  Run Full AI Analysis", use_container_width=True)

if run:
    st.switch_page("pages/1_Analysis.py")
