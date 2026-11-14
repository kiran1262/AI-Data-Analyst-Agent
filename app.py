from __future__ import annotations

import io
import json
import os
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from groq import Groq

# ---------------------------- Page and visual theme ----------------------------
st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { color-scheme: dark; }
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .stApp {
      background:
        radial-gradient(ellipse at 50% 0%, rgba(0,190,255,.14), transparent 34%),
        radial-gradient(ellipse at 100% 35%, rgba(89,78,255,.12), transparent 32%),
        linear-gradient(145deg,#050b16 0%,#081526 52%,#070d1b 100%);
      color: #e8f5ff;
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .block-container { max-width: 1500px; padding-top: 1.1rem; padding-bottom: 3rem; }
    section[data-testid="stSidebar"] {
      background: linear-gradient(180deg,#0b1a2d,#081221);
      border-right: 1px solid rgba(65,199,255,.22);
    }
    .hero {
      position:relative; overflow:hidden; padding:30px 34px; border-radius:22px;
      background: linear-gradient(112deg,rgba(9,37,62,.98),rgba(13,54,83,.94) 55%,rgba(34,37,96,.96));
      border:1px solid rgba(65,205,255,.45);
      box-shadow:0 0 32px rgba(0,174,255,.12), inset 0 0 35px rgba(0,183,255,.06);
      margin-bottom:20px;
    }
    .hero:after { content:""; position:absolute; width:300px;height:300px;right:-75px;top:-150px;border-radius:50%;background:rgba(0,211,255,.12);filter:blur(3px); }
    .hero h1 { margin:0; font-size:clamp(28px,3vw,42px); font-weight:800; letter-spacing:-1.2px; color:#f2fbff; }
    .hero p { margin:9px 0 0; color:#9ec9df; font-size:14px; }
    .eyebrow { color:#45d9ff; font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; margin-bottom:9px; }
    .kpi {
      padding:17px 18px; min-height:112px; border-radius:17px;
      background:linear-gradient(145deg,rgba(13,36,58,.96),rgba(9,24,42,.96));
      border:1px solid rgba(58,193,239,.28); box-shadow:0 7px 28px rgba(0,0,0,.2);
    }
    .kpi-label { color:#8db7cb; font-size:10px; font-weight:800; letter-spacing:1.2px; }
    .kpi-value { color:#e9fbff; font-size:26px; font-weight:800; margin-top:9px; }
    .kpi-help { color:#6e9bb3; font-size:11px; margin-top:3px; }
    .panel-title { font-size:19px; font-weight:800; color:#e7f7ff; margin:15px 0 10px; }
    .hint { padding:12px 15px; border-radius:12px; background:rgba(0,168,220,.08); border:1px solid rgba(0,195,255,.2); color:#9bc5d9; font-size:12px; }
    div[data-testid="stMetric"] { background:rgba(10,31,51,.9); border:1px solid rgba(65,205,255,.23); border-radius:14px; padding:13px; }
    div[data-testid="stMetricLabel"] { color:#9bc5d9; }
    div[data-testid="stMetricValue"] { color:#e8fbff; }
    .stButton>button, .stDownloadButton>button {
      border:1px solid rgba(53,207,255,.55); border-radius:10px;
      background:linear-gradient(90deg,#087fa9,#3155b8); color:white; font-weight:700;
    }
    .stButton>button:hover, .stDownloadButton>button:hover { border-color:#5ce7ff; color:white; box-shadow:0 0 18px #00bce944; }
    .stTabs [data-baseweb="tab-list"] { gap:7px; border-bottom:1px solid rgba(61,192,231,.2); }
    .stTabs [data-baseweb="tab"] { background:rgba(12,35,56,.75); border-radius:9px 9px 0 0; color:#9dc8dc; padding:9px 14px; }
    .stTabs [aria-selected="true"] { color:#55e0ff !important; border-bottom:2px solid #31d5ff; }
    [data-testid="stFileUploader"] { background:rgba(9,31,50,.65); border:1px dashed rgba(67,205,255,.42); border-radius:13px; padding:8px; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { background:#0b1c30; }
    div[data-testid="stDataFrame"] { border:1px solid rgba(65,205,255,.22); border-radius:12px; }
    hr { border-color:rgba(68,180,220,.18); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Autonomous analytics workspace · powered by Groq</div>
      <h1>🤖 AI Data Analyst Agent</h1>
      <p>Upload your data. Ask questions in plain English. Discover patterns, generate charts and turn raw files into clear business insights.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------- Helpers ----------------------------
def read_upload(uploaded_file: Any) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    if name.endswith(".csv"):
        # Try common encodings; pandas infers delimiter by default only when python engine is selected.
        try:
            return pd.read_csv(io.BytesIO(raw))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(raw), encoding="latin-1")
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(raw))
    raise ValueError("Unsupported file type. Upload CSV, XLSX or XLS.")


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # Remove fully empty rows/columns; retain original data values otherwise.
    df = df.dropna(how="all").dropna(axis=1, how="all")
    for col in df.columns:
        if df[col].dtype == "object":
            series = df[col].astype(str).str.strip()
            numeric = pd.to_numeric(series.str.replace(",", "", regex=False), errors="coerce")
            if len(series) and numeric.notna().mean() >= 0.88:
                df[col] = numeric
    return df


def column_profile(df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {}
    for col in df.columns:
        s = df[col]
        item: dict[str, Any] = {
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_pct": round(float(s.isna().mean() * 100), 2),
            "unique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            item["min"] = _safe_num(s.min())
            item["max"] = _safe_num(s.max())
            item["mean"] = _safe_num(s.mean())
            item["sum"] = _safe_num(s.sum())
        else:
            item["top_values"] = s.astype(str).value_counts().head(5).to_dict()
        profile[str(col)] = item
    return profile


def _safe_num(value: Any) -> Any:
    if pd.isna(value):
        return None
    return round(float(value), 4)


def overview_stats(df: pd.DataFrame) -> dict[str, Any]:
    numeric = df.select_dtypes(include=np.number)
    categorical = df.select_dtypes(exclude=np.number)
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "numeric_columns": list(numeric.columns[:30]),
        "categorical_columns": list(categorical.columns[:30]),
        "profile": column_profile(df),
        "sample_rows": df.head(6).replace({np.nan: None}).to_dict(orient="records"),
    }


def make_chart(df: pd.DataFrame, x_col: str, y_col: str | None, chart_type: str, color_col: str | None):
    palette = ["#22d3ee", "#a78bfa", "#34d399", "#f472b6", "#fbbf24", "#60a5fa"]
    if chart_type == "Histogram":
        fig = px.histogram(df, x=x_col, color=color_col, color_discrete_sequence=palette, nbins=30)
    elif chart_type == "Box plot":
        fig = px.box(df, x=x_col if y_col else None, y=y_col, color=color_col, color_discrete_sequence=palette)
    elif chart_type == "Scatter":
        if not y_col:
            raise ValueError("Choose a Y-axis column for a scatter chart.")
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=palette, opacity=.78)
    elif chart_type == "Line":
        if not y_col:
            raise ValueError("Choose a Y-axis column for a line chart.")
        grouped = df.groupby(x_col, dropna=False)[y_col].mean().reset_index()
        fig = px.line(grouped, x=x_col, y=y_col, markers=True, color_discrete_sequence=palette)
    elif chart_type == "Pie":
        grouped = df[x_col].fillna("Missing").astype(str).value_counts().head(15).reset_index()
        grouped.columns = [x_col, "Count"]
        fig = px.pie(grouped, names=x_col, values="Count", hole=.48, color_discrete_sequence=palette)
    elif chart_type == "Bar":
        if y_col and pd.api.types.is_numeric_dtype(df[y_col]):
            grouped = df.groupby(x_col, dropna=False)[y_col].sum().reset_index().sort_values(y_col, ascending=False).head(25)
            fig = px.bar(grouped, x=x_col, y=y_col, color=y_col, color_continuous_scale=["#164e63", "#22d3ee", "#a78bfa"])
        else:
            grouped = df[x_col].fillna("Missing").astype(str).value_counts().head(25).reset_index()
            grouped.columns = [x_col, "Count"]
            fig = px.bar(grouped, x=x_col, y="Count", color="Count", color_continuous_scale=["#164e63", "#22d3ee", "#a78bfa"])
    else:
        raise ValueError("Unsupported chart type.")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,18,32,.55)", font_color="#d7f2ff",
        margin=dict(l=20, r=20, t=45, b=25), title_font_size=16,
        coloraxis_colorbar=dict(tickfont=dict(color="#b8d8e8")),
    )
    fig.update_xaxes(gridcolor="rgba(110,170,200,.12)")
    fig.update_yaxes(gridcolor="rgba(110,170,200,.12)")
    return fig


def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def ask_groq(api_key: str, model: str, question: str, stats: dict[str, Any], history: list[dict[str, str]]) -> str:
    client = get_groq_client(api_key)
    system_prompt = (
        "You are an expert data analyst. Answer using only the supplied dataset profile, "
        "summary and sample rows. Never invent results or claim a calculation was performed if it was not. "
        "If the user asks for a calculation not present in the supplied summary, explain what is missing "
        "and recommend a calculation. Clearly distinguish observations from hypotheses. "
        "Use concise headings, bullet points and business-friendly language. "
        "Warn when sample rows or column profiles are insufficient to support a conclusion. "
        "Do not expose private chain-of-thought; provide concise reasoning and verifiable findings."
    )
    context = json.dumps(stats, ensure_ascii=False, default=str)
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dataset context (JSON):\n{context}\n\nQuestion: {question}"}]
    # Keep the latest few turns for conversational continuity; dataset context is always refreshed.
    if history:
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "system", "content": f"Current dataset context (JSON):\n{context}"}] + history[-6:] + [{"role": "user", "content": question}]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=1300,
    )
    return completion.choices[0].message.content or "The model returned an empty response."


# ---------------------------- Sidebar / data upload ----------------------------
with st.sidebar:
    st.markdown("## 🗂️ Data source")
    uploaded = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "xls"], help="No sample dataset is bundled with this project.")
    st.caption("Your uploaded file is held in the current app session. Use anonymised data.")
    st.divider()
    st.markdown("## 🔐 Groq API")
    saved_key = ""
    try:
        saved_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    api_key = st.text_input("Groq API key", value=saved_key, type="password", help="Or configure GROQ_API_KEY in Streamlit secrets.")
    model = st.selectbox(
        "Groq model",
        options=["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"],
        index=0,
        help="Model availability and free-tier limits can change. Check Groq's current model list.",
    )
    st.caption("Never commit your API key to GitHub.")
    st.divider()
    st.markdown("## 🧩 Workspace")
    st.caption("Python · Pandas · Plotly · LangChain-ready · Groq LLM")

if not uploaded:
    st.markdown(
        """
        <div class="hint">
        <b>Start here:</b> Upload a CSV or Excel file from the left panel. This project intentionally includes
        <b>no sample dataset</b>. Once a file is loaded, the agent profiles the data and unlocks the analytics workspace.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### What you can do")
    a, b, c = st.columns(3)
    a.info("📈 **Explore automatically**\n\nReview dataset quality, key metrics and suggested visualisations.")
    b.info("💬 **Ask in natural language**\n\nAsk questions such as “Which category has the highest revenue?”")
    c.info("📊 **Build charts**\n\nChoose fields and create interactive Plotly charts.")
    st.stop()

try:
    df = normalize_frame(read_upload(uploaded))
except Exception as exc:
    st.error(f"Unable to read this file: {exc}")
    st.stop()

if df.empty:
    st.warning("The uploaded file has no usable rows or columns.")
    st.stop()

st.session_state["active_file_name"] = uploaded.name
st.session_state["active_df"] = df
stats = overview_stats(df)

# ---------------------------- KPI row ----------------------------
numeric_cols = list(df.select_dtypes(include=np.number).columns)
date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
if not date_cols:
    for c in df.columns:
        if any(word in str(c).lower() for word in ["date", "time", "timestamp"]):
            parsed = pd.to_datetime(df[c], errors="coerce")
            if parsed.notna().mean() > .65:
                df[c] = parsed
                date_cols.append(c)
                break

kpis = [
    ("ROWS", f"{len(df):,}", "Records loaded"),
    ("COLUMNS", f"{len(df.columns):,}", "Fields detected"),
    ("DUPLICATES", f"{df.duplicated().sum():,}", "Exact duplicate rows"),
    ("MISSING CELLS", f"{df.isna().sum().sum():,}", "Values requiring review"),
]
cards = st.columns(4)
for col, (label, value, note) in zip(cards, kpis):
    col.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-help">{note}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(f'<div class="panel-title">📁 {uploaded.name}</div>', unsafe_allow_html=True)
st.caption(f"{len(df):,} rows · {len(df.columns)} columns · {len(numeric_cols)} numeric fields")

# ---------------------------- Main tabs ----------------------------
tab_overview, tab_chat, tab_charts, tab_data = st.tabs(
    ["⚡ Overview", "💬 Ask the AI Analyst", "📊 Chart Studio", "🧾 Data & Quality"]
)

with tab_overview:
    left, right = st.columns([1.45, 1])
    with left:
        st.markdown("### Numeric field distributions")
        if numeric_cols:
            selected_num = st.selectbox("Choose a numeric field", numeric_cols, key="overview_num")
            fig = px.histogram(df, x=selected_num, nbins=32, marginal="box",
                               color_discrete_sequence=["#22d3ee"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(5,18,32,.55)", font_color="#d7f2ff",
                              margin=dict(l=15,r=15,t=35,b=15))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns were detected. Check the uploaded file.")
    with right:
        st.markdown("### Dataset composition")
        categorical = [c for c in df.columns if df[c].nunique(dropna=True) <= 30 and c not in numeric_cols]
        if categorical:
            selected_cat = st.selectbox("Choose a category", categorical, key="overview_cat")
            counts = df[selected_cat].fillna("Missing").astype(str).value_counts().head(12).reset_index()
            counts.columns = [selected_cat, "Records"]
            fig = px.pie(counts, names=selected_cat, values="Records", hole=.55,
                         color_discrete_sequence=["#22d3ee","#a78bfa","#34d399","#f472b6","#fbbf24","#60a5fa"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              font_color="#d7f2ff", margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No low-cardinality category columns detected.")
    st.markdown("### Quick data profile")
    profile_rows = []
    for col in df.columns:
        s = df[col]
        profile_rows.append({
            "Column": str(col), "Type": str(s.dtype), "Non-null": int(s.notna().sum()),
            "Missing": int(s.isna().sum()), "Unique": int(s.nunique(dropna=True)),
        })
    st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)

with tab_chat:
    st.markdown("### Ask questions about your uploaded data")
    st.markdown('<div class="hint">Examples: “Summarise this dataset”, “Which 5 categories have the highest average sales?”, “Are there missing values?”, “What trends should I investigate?”</div>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("Ask a question about your data...")
    if question:
        if not api_key:
            st.warning("Add your Groq API key in the sidebar to use AI chat.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Analysing your dataset with Groq..."):
                    try:
                        answer = ask_groq(api_key, model, question, stats, st.session_state.chat_history[:-1])
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as exc:
                        st.error(f"Groq request failed: {exc}")
                        st.caption("Check your API key, selected model, internet connection and Groq rate limits.")
            st.rerun()
    if st.button("Clear conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

with tab_charts:
    st.markdown("### Build an interactive chart")
    all_cols = list(df.columns)
    c1, c2, c3 = st.columns(3)
    x_col = c1.selectbox("X-axis / category", all_cols)
    y_options = ["(Count only)"] + numeric_cols
    y_choice = c2.selectbox("Y-axis / measure", y_options)
    chart_type = c3.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Pie", "Box plot"])
    color_options = ["(No colour grouping)"] + [c for c in all_cols if c != x_col]
    color_choice = st.selectbox("Colour grouping (optional)", color_options)
    y_col = None if y_choice == "(Count only)" else y_choice
    color_col = None if color_choice == "(No colour grouping)" else color_choice
    if st.button("✨ Generate chart", key="generate_chart"):
        try:
            st.plotly_chart(make_chart(df, x_col, y_col, chart_type, color_col), use_container_width=True)
        except Exception as exc:
            st.error(f"Could not build this chart: {exc}")

with tab_data:
    st.markdown("### Preview uploaded data")
    st.dataframe(df.head(500), use_container_width=True, height=360)
    st.markdown("### Data quality checks")
    quality = pd.DataFrame({
        "Column": df.columns,
        "Data type": [str(df[c].dtype) for c in df.columns],
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing (%)": [round(float(df[c].isna().mean()*100), 2) for c in df.columns],
        "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Download uploaded data as CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="analysed_data.csv", mime="text/csv")
    c2.download_button("⬇️ Download data quality report", quality.to_csv(index=False).encode("utf-8"),
                       file_name="data_quality_report.csv", mime="text/csv")

st.divider()
st.caption("AI Data Analyst Agent · Groq-powered natural-language analysis · Validate AI-generated interpretations before making business decisions. Do not upload confidential, personal, financial or regulated data unless you have appropriate authorisation.")
