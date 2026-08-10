"""
FYP B30 - Freshman Progress & Data Science Analytics Dashboard
Advanced analytics platform for tracking freshman point accuracy, monitoring FL performance,
identifying discrepancy anomalies, diagnosing course/session drops, and generating actionable logbook audit reports.
"""

import io
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================
st.set_page_config(
    page_title="FYP B30 - Freshman Progress Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Modern Custom CSS Aesthetics
st.markdown("""
<style>
    /* Global Typography & Background Adjustments */
    .main {
        padding-top: 1rem;
    }
    
    /* Custom Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #888888;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #00cc88;
        margin-top: 4px;
    }
    .metric-subtitle.negative {
        color: #ff4d4d;
    }

    /* Custom Callout Box */
    .gdrive-callout {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-left: 5px solid #3b82f6;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 24px;
        color: #f8fafc;
    }
    .gdrive-callout h4 {
        margin-top: 0;
        color: #60a5fa;
        font-size: 1.1rem;
    }
    /* Mobile Responsiveness & Fluid Layout Enhancements */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        div[data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 10px !important;
        }
        .metric-card {
            padding: 14px 16px !important;
            margin-bottom: 8px !important;
        }
        .metric-value {
            font-size: 1.4rem !important;
        }
        .metric-title {
            font-size: 0.75rem !important;
        }
        .gdrive-callout {
            padding: 14px 16px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            flex-wrap: nowrap !important;
            padding-bottom: 6px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.82rem !important;
            padding: 6px 12px !important;
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.04) !important;
            margin-right: 4px !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(59, 130, 246, 0.25) !important;
            color: #60a5fa !important;
            font-weight: 700 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

GDRIVE_LOGBOOK_LINK = "https://drive.google.com/drive/folders/1hwEZYgQ_ZiW1GEQuFDDhQxUvwAS-XnrA?usp=sharing"

# ============================================================
# CLASS TO PIC MAPPING
# ============================================================
PIC_MAPPING = {
    "BBN01": "Jess", "BBN02": "Lyla", "BBN03": "Mengko", "BBN04": "Farah",
    "BBN05": "Farah", "BBN06": "Ken", "BBN07": "Jihan", "BBN08": "Kia",
    "BBN09": "Pitri", "BBN10": "Kia", "BBN11": "Nadira", "BBN12": "Juan",
    "BBN13": "Lyla", "BBN14": "Bayu", "BBN15": "Mengko", "BBN16": "Nata",
    "BBN17": "Refa", "BBN18": "Diana", "BBN19": "Diana", "BBN20": "Razka",
    "BBN21": "Nata", "BBN22": "Jihan", "BBN23": "Juan", "BBN24": "Tian",
    "BBN25": "Jess", "BBN26": "Megan", "BBN27": "Nadira", "BBN28": "Ais",
    "BBN29": "Refa", "BBN30": "Ais", "BBN31": "Kasih", "BBN32": "Ken",
    "BBN33": "Razka",
}

# ============================================================
# SAMPLE DATA GENERATOR (DEMO MODE)
# ============================================================
def generate_sample_dataset():
    """Generates synthetic, realistic data for demonstration when no Excel file is uploaded."""
    fl_names = ["Andi Wijaya", "Budi Santoso", "Citra Dewi", "Doni Pratama", "Eka Putri", "Fajar Hidayat", "Gita Gutawa", "Hendra Setiawan"]
    freshmen_first = ["Aditya", "Bagas", "Chintya", "Davin", "Elsa", "Farhan", "Grace", "Hafiz", "Indah", "Joko", "Kevin", "Laras", "Mitha", "Naufal", "Olivia", "Pratama", "Qirani", "Rian", "Salsa", "Taufik"]
    freshmen_last = ["Pradipta", "Kusuma", "Lestari", "Nugraha", "Ramadhan", "Saputra", "Utami", "Wibowo", "Yulia", "Zulkarnain"]
    
    rows = []
    classes = list(PIC_MAPPING.keys())
    
    for cls in classes:
        num_students = random.randint(8, 14)
        for i in range(num_students):
            fl_name = random.choice(fl_names)
            fm_name = f"{random.choice(freshmen_first)} {random.choice(freshmen_last)}"
            nim_fl = str(random.randint(2600000000, 2699999999))
            nim_fm = str(random.randint(2700000000, 2799999999))
            
            prediksi = random.choice([20, 25, 30, 35, 40, 50])
            # 65% match rate, 35% discrepancy
            if random.random() < 0.65:
                apps = prediksi
                sesi_0 = "-"
                sesi_kosong = "-"
            else:
                gap = random.choice([1, 2, 3, 5, 8, 10, 12])
                apps = max(0, prediksi - gap)
                sesi_0 = f"Sesi {random.randint(1, 6)}" if random.random() > 0.5 else "-"
                sesi_kosong = f"Sesi {random.randint(2, 7)}" if random.random() > 0.4 else "-"
                
            rows.append({
                "Kelas": cls,
                "NIM FRESHMEN LEADER": nim_fl,
                "NAMA FRESHMEN LEADER": fl_name,
                "NIM FRESHMEN": nim_fm,
                "NAMA FRESHMEN": fm_name,
                "prediksi point": prediksi,
                "point apps": apps,
                "selisih": abs(prediksi - apps),
                "Sesi yang 0": sesi_0,
                "Sesi yang Kosong": sesi_kosong
            })
            
    return pd.DataFrame(rows)

# ============================================================
# DATA LOADING & FEATURE ENGINEERING ENGINE
# ============================================================
@st.cache_data
def process_data(file_buffer, is_demo=False):
    if is_demo:
        df_all = generate_sample_dataset()
    else:
        xls = pd.ExcelFile(file_buffer)
        all_dfs = []
        for sheet_name in xls.sheet_names:
            df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
            if df_sheet.empty:
                continue
            df_sheet["Kelas"] = sheet_name.strip()
            all_dfs.append(df_sheet)

        if not all_dfs:
            return pd.DataFrame()
            
        df_all = pd.concat(all_dfs, ignore_index=True)
        df_all.columns = [str(c).strip() for c in df_all.columns]

    # Smart Column Alias Mapper
    col_rename_map = {}
    for col in df_all.columns:
        c_upper = col.upper().strip()
        if c_upper in ["NAMA FRESHMEN", "NAMA FRESHMAN", "NAMA FM", "NAMA MAHASISWA", "NAMA"]:
            col_rename_map[col] = "NAMA FRESHMEN"
        elif c_upper in ["NIM FRESHMEN", "NIM FRESHMAN", "NIM FM", "NIM"]:
            col_rename_map[col] = "NIM FRESHMEN"
        elif c_upper in ["NAMA FRESHMEN LEADER", "NAMA FRESHMAN LEADER", "NAMA FL", "FL NAMA"]:
            col_rename_map[col] = "NAMA FRESHMEN LEADER"
        elif c_upper in ["NIM FRESHMEN LEADER", "NIM FRESHMAN LEADER", "NIM FL"]:
            col_rename_map[col] = "NIM FRESHMEN LEADER"
        elif "PREDIKSI" in c_upper:
            col_rename_map[col] = "prediksi point"
        elif "APPS" in c_upper or "APP" in c_upper:
            col_rename_map[col] = "point apps"
        elif "SELISIH" in c_upper:
            col_rename_map[col] = "selisih"
        elif "SESI" in c_upper and "0" in c_upper:
            col_rename_map[col] = "Sesi yang 0"
        elif "SESI" in c_upper and ("KOSONG" in c_upper or "EMPTY" in c_upper):
            col_rename_map[col] = "Sesi yang Kosong"

    df_all = df_all.rename(columns=col_rename_map)

    # Clean & Coerce Required Columns
    df_all["prediksi point"] = pd.to_numeric(df_all.get("prediksi point", 0), errors="coerce").fillna(0)
    df_all["point apps"] = pd.to_numeric(df_all.get("point apps", 0), errors="coerce").fillna(0)
    
    # Calculate Selisih if absent or invalid
    if "selisih" not in df_all.columns or df_all["selisih"].isnull().all():
        df_all["selisih"] = (df_all["prediksi point"] - df_all["point apps"]).abs()
    else:
        df_all["selisih"] = pd.to_numeric(df_all["selisih"], errors="coerce").fillna(
            (df_all["prediksi point"] - df_all["point apps"]).abs()
        )

    # Core Status Logic
    df_all["Status"] = df_all.apply(
        lambda r: "Belum Sesuai" if r["prediksi point"] != r["point apps"] else "Sesuai",
        axis=1
    )

    # Data Science Severity Profiling
    def classify_severity(row):
        if row["Status"] == "Sesuai":
            return "🟢 Sesuai"
        diff = row["selisih"]
        if diff <= 2:
            return "🟡 Low Variance (1-2 pts)"
        elif diff <= 5:
            return "🟠 Medium Variance (3-5 pts)"
        else:
            return "🔴 High Priority Audit (>5 pts)"

    df_all["Severity Level"] = df_all.apply(classify_severity, axis=1)

    # PIC Mapping
    df_all["PIC"] = df_all["Kelas"].map(PIC_MAPPING).fillna("Belum ada PIC")

    # Clean text columns
    for text_col in ["Sesi yang 0", "Sesi yang Kosong", "NAMA FRESHMEN LEADER", "NAMA FRESHMEN"]:
        if text_col in df_all.columns:
            df_all[text_col] = df_all[text_col].astype(str).fillna("-").replace("nan", "-")

    return df_all


# Helper to Unpack Session Records
def extract_unnested_sessions(df):
    records = []
    for idx, row in df.iterrows():
        # Check Sesi yang Kosong
        val_k = str(row.get("Sesi yang Kosong", "-")).strip()
        if val_k not in ["-", "nan", "None", ""]:
            for s in [x.strip() for x in val_k.replace(";", ",").split(",") if x.strip()]:
                records.append({
                    "Sesi": s,
                    "Tipe Kendala": "Sesi Kosong",
                    "Kelas": row["Kelas"],
                    "PIC": row["PIC"],
                    "FL": row["NAMA FRESHMEN LEADER"],
                    "Freshman": row["NAMA FRESHMEN"],
                    "NIM": row["NIM FRESHMEN"],
                    "selisih": row["selisih"],
                    "Severity": row["Severity Level"]
                })
        # Check Sesi yang 0
        val_0 = str(row.get("Sesi yang 0", "-")).strip()
        if val_0 not in ["-", "nan", "None", ""]:
            for s in [x.strip() for x in val_0.replace(";", ",").split(",") if x.strip()]:
                records.append({
                    "Sesi": s,
                    "Tipe Kendala": "Nilai 0",
                    "Kelas": row["Kelas"],
                    "PIC": row["PIC"],
                    "FL": row["NAMA FRESHMEN LEADER"],
                    "Freshman": row["NAMA FRESHMEN"],
                    "NIM": row["NIM FRESHMEN"],
                    "selisih": row["selisih"],
                    "Severity": row["Severity Level"]
                })
    return pd.DataFrame(records)


# ============================================================
# HEADER & SIDEBAR NAVIGATION
# ============================================================
st.title("📊 FYP B30 - Freshman Progress & Data Science Analytics")

# Custom Banner Callout
st.markdown(f"""
<div class="gdrive-callout">
    <h4>📌 Petunjuk Monitoring & Crosscheck Logbook FYP</h4>
    <p>Status <b>"Belum Sesuai"</b> menandakan adanya selisih antara data <b>File Monitoring FL</b> dengan data <b>Logbook Aplikasi</b> real-time.</p>
    <p>FYPL & PIC dimohon melakukan audit silang dengan bukti fisik/digital pada Google Drive Logbook.</p>
    <a href="{GDRIVE_LOGBOOK_LINK}" target="_blank" style="display: inline-block; background: #3b82f6; color: white; padding: 6px 16px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; margin-top: 6px;">
        📁 Buka Google Drive Logbook All Drive
    </a>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🎛️ Data Source & Filters")

# File Upload vs Demo Mode
data_mode = st.sidebar.radio("Pilih Sumber Data:", ["Upload Excel File", "⚡ Gunakan Sample Demo Data"])

uploaded_file = None
if data_mode == "Upload Excel File":
    uploaded_file = st.sidebar.file_uploader("Upload File Excel Monitoring", type=["xlsx", "xls"])
    if uploaded_file is None:
        st.info("💡 **Tips:** Silakan upload file Excel di sidebar, atau pilih **'⚡ Gunakan Sample Demo Data'** untuk mencoba dashboard langsung!")
        st.stop()
    df_raw = process_data(uploaded_file, is_demo=False)
else:
    df_raw = process_data(None, is_demo=True)
    st.sidebar.success("✅ Menggunakan Sample Data Demo!")

if df_raw.empty:
    st.error("Data kosong atau format sheet tidak sesuai!")
    st.stop()

# Filter Controls
st.sidebar.divider()
st.sidebar.subheader("🔎 Filter Dynamic Data")

# Search Bar
search_query = st.sidebar.text_input("🔍 Cari (Nama / NIM / FL)", placeholder="Ketik nama atau NIM...").strip().lower()

# Multiselects
all_pics = sorted(df_raw["PIC"].unique())
selected_pics = st.sidebar.multiselect("PIC", all_pics, default=all_pics)

all_kelas = sorted(df_raw[df_raw["PIC"].isin(selected_pics)]["Kelas"].unique())
selected_kelas = st.sidebar.multiselect("Kelas", all_kelas, default=all_kelas)

status_filter = st.sidebar.radio("Filter Status Point", ["Semua", "Belum Sesuai", "Sesuai"])

severity_list = ["🟢 Sesuai", "🟡 Low Variance (1-2 pts)", "🟠 Medium Variance (3-5 pts)", "🔴 High Priority Audit (>5 pts)"]
selected_severity = st.sidebar.multiselect("Severity Discrepancy", severity_list, default=severity_list)

# Filtering Engine
df_filtered = df_raw[
    df_raw["PIC"].isin(selected_pics) &
    df_raw["Kelas"].isin(selected_kelas) &
    df_raw["Severity Level"].isin(selected_severity)
]

if status_filter != "Semua":
    df_filtered = df_filtered[df_filtered["Status"] == status_filter]

if search_query:
    df_filtered = df_filtered[
        df_filtered["NAMA FRESHMEN"].str.lower().str.contains(search_query, na=False) |
        df_filtered["NAMA FRESHMEN LEADER"].str.lower().str.contains(search_query, na=False) |
        df_filtered["NIM FRESHMEN"].str.lower().str.contains(search_query, na=False) |
        df_filtered["NIM FRESHMEN LEADER"].str.lower().str.contains(search_query, na=False)
    ]

# ============================================================
# MAIN DASHBOARD TABS
# ============================================================
tab_overview, tab_rootcause, tab_course, tab_scatter, tab_diagnostics, tab_details, tab_action = st.tabs([
    "📊 Overview",
    "🌳 Treemap",
    "📚 Courses",
    "📈 Scatter",
    "👤 Diagnostics",
    "📋 Details",
    "💬 WA Report"
])

# ------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------
with tab_overview:
    total_fm = len(df_filtered)
    sesuai_count = len(df_filtered[df_filtered["Status"] == "Sesuai"])
    belum_count = len(df_filtered[df_filtered["Status"] == "Belum Sesuai"])
    high_risk_count = len(df_filtered[df_filtered["Severity Level"] == "🔴 High Priority Audit (>5 pts)"])
    
    compliance_rate = (sesuai_count / total_fm * 100) if total_fm > 0 else 0
    mismatch_rate = (belum_count / total_fm * 100) if total_fm > 0 else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Freshmen</div>
            <div class="metric-value">{total_fm:,}</div>
            <div class="metric-subtitle">Filtered Students</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Compliance Rate</div>
            <div class="metric-value">{compliance_rate:.1f}%</div>
            <div class="metric-subtitle">{sesuai_count} Sesuai</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Belum Sesuai</div>
            <div class="metric-value" style="color: #f87171;">{belum_count:,}</div>
            <div class="metric-subtitle negative">{mismatch_rate:.1f}% Discrepancy</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">High Risk Audit</div>
            <div class="metric-value" style="color: #ef4444;">{high_risk_count:,}</div>
            <div class="metric-subtitle negative">Point Gap > 5</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        active_pics = df_filtered["PIC"].nunique()
        active_classes = df_filtered["Kelas"].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Coverage</div>
            <div class="metric-value">{active_classes} <span style="font-size: 1rem; color: #888;">Kelas</span></div>
            <div class="metric-subtitle">{active_pics} Active PICs</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Automated Data Insights Callout Box
    st.subheader("💡 Automated Data Science Insights")
    if not df_filtered.empty:
        class_discrepancy = df_filtered.groupby("Kelas")["Status"].apply(lambda s: (s == "Belum Sesuai").sum()).sort_values(ascending=False)
        top_disc_class = class_discrepancy.index[0] if len(class_discrepancy) > 0 else "-"
        top_disc_class_count = class_discrepancy.iloc[0] if len(class_discrepancy) > 0 else 0

        fl_discrepancy = df_filtered.groupby(["Kelas", "NAMA FRESHMEN LEADER"])["Status"].apply(lambda s: (s == "Belum Sesuai").sum()).sort_values(ascending=False)
        top_fl_name = fl_discrepancy.index[0][1] if len(fl_discrepancy) > 0 else "-"
        top_fl_class = fl_discrepancy.index[0][0] if len(fl_discrepancy) > 0 else "-"
        top_fl_count = fl_discrepancy.iloc[0] if len(fl_discrepancy) > 0 else 0

        df_sess_unpacked = extract_unnested_sessions(df_filtered)
        top_sess_name = df_sess_unpacked["Sesi"].value_counts().index[0] if not df_sess_unpacked.empty else "-"
        top_sess_count = df_sess_unpacked["Sesi"].value_counts().iloc[0] if not df_sess_unpacked.empty else 0

        insight_col1, insight_col2 = st.columns(2)
        with insight_col1:
            st.info(f"""
            📌 **Kelas Discrepancy Tertinggi:** **{top_disc_class}** ({top_disc_class_count} freshman belum sesuai)  
            🚨 **FL Perlu Perhatian Khusus:** **{top_fl_name}** (Kelas {top_fl_class} - {top_fl_count} freshman bermasalah)
            """)
        with insight_col2:
            st.warning(f"""
            📚 **Top Sesi Incomplete Terbanyak:** **{top_sess_name}** ({top_sess_count} kejadian)  
            ⚡ Terdapat **{high_risk_count}** freshman kategori **High Priority Audit** yang membutuhkan pengecekan ulang logbook secepatnya.
            """)

    st.divider()

    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.subheader("🍩 Proporsi Compliance Status")
        status_counts = df_filtered["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Jumlah"]
        
        fig_donut = px.pie(
            status_counts, 
            values="Jumlah", 
            names="Status",
            hole=0.55,
            color="Status",
            color_discrete_map={"Sesuai": "#22c55e", "Belum Sesuai": "#ef4444"}
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.subheader("📊 Distribution by Discrepancy Severity")
        sev_counts = df_filtered["Severity Level"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Jumlah"]
        
        fig_sev = px.bar(
            sev_counts,
            x="Jumlah",
            y="Severity",
            orientation="h",
            color="Severity",
            color_discrete_map={
                "🟢 Sesuai": "#22c55e",
                "🟡 Low Variance (1-2 pts)": "#eab308",
                "🟠 Medium Variance (3-5 pts)": "#f97316",
                "🔴 High Priority Audit (>5 pts)": "#ef4444"
            },
            text="Jumlah"
        )
        fig_sev.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_sev, use_container_width=True)

    st.subheader("📈 Ranking Jumlah Belum Sesuai Per Kelas")
    summary_kelas = (
        df_filtered.groupby(["Kelas", "PIC"])["Status"]
        .apply(lambda s: (s == "Belum Sesuai").sum())
        .reset_index(name="Jumlah Belum Sesuai")
        .sort_values("Jumlah Belum Sesuai", ascending=False)
    )

    fig_bar_kelas = px.bar(
        summary_kelas,
        x="Kelas",
        y="Jumlah Belum Sesuai",
        color="Jumlah Belum Sesuai",
        color_continuous_scale="Reds",
        hover_data=["PIC"],
        text="Jumlah Belum Sesuai"
    )
    fig_bar_kelas.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar_kelas, use_container_width=True)


# ------------------------------------------------------------
# TAB 2: ROOT-CAUSE HIERARCHICAL ANALYSIS
# ------------------------------------------------------------
with tab_rootcause:
    st.subheader("🌳 Hierarchical Root-Cause Analysis")
    st.caption("Eksplorasi hirarki bertingkat untuk mengisolasi sumber selisih point dari PIC hingga ke mahasiswa.")

    chart_type = st.radio("Pilih Tampilan Visualisasi Hirarki:", ["🌳 Interactive Treemap", "☀️ Sunburst Chart"], horizontal=True)

    df_belum = df_filtered[df_filtered["Status"] == "Belum Sesuai"].copy()
    
    if not df_belum.empty:
        df_belum["Gap Sizing"] = df_belum["selisih"].apply(lambda v: max(1, v))
        
        # Build detailed label string with session info
        def make_leaf_label(r):
            lbl = f"<b>{r['NAMA FRESHMEN']}</b><br>💥 Selisih: -{r['selisih']} pt ({r['prediksi point']} ➔ {r['point apps']})"
            notes = []
            if r['Sesi yang 0'] != "-":
                notes.append(f"Nilai 0: {r['Sesi yang 0']}")
            if r['Sesi yang Kosong'] != "-":
                notes.append(f"Kosong: {r['Sesi yang Kosong']}")
            if notes:
                lbl += f"<br>📚 " + " | ".join(notes)
            return lbl

        df_belum["Leaf Label"] = df_belum.apply(make_leaf_label, axis=1)

        if chart_type == "🌳 Interactive Treemap":
            fig_hierarchy = px.treemap(
                df_belum,
                path=["PIC", "Kelas", "NAMA FRESHMEN LEADER", "Leaf Label"],
                values="Gap Sizing",
                color="Severity Level",
                color_discrete_map={
                    "🟡 Low Variance (1-2 pts)": "#eab308",
                    "🟠 Medium Variance (3-5 pts)": "#f97316",
                    "🔴 High Priority Audit (>5 pts)": "#ef4444"
                },
                custom_data=["NAMA FRESHMEN", "prediksi point", "point apps", "selisih", "NIM FRESHMEN", "Sesi yang 0", "Sesi yang Kosong"]
            )
            fig_hierarchy.update_traces(
                hovertemplate="<b>%{customdata[0]}</b> (NIM: %{customdata[4]})<br>Prediksi: %{customdata[1]} pt<br>Apps: %{customdata[2]} pt<br><b>Selisih: -%{customdata[3]} pt</b><br>Sesi 0: %{customdata[5]}<br>Sesi Kosong: %{customdata[6]}<extra></extra>"
            )
            fig_hierarchy.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=620)
            st.plotly_chart(fig_hierarchy, use_container_width=True)
        else:
            fig_hierarchy = px.sunburst(
                df_belum,
                path=["PIC", "Kelas", "NAMA FRESHMEN LEADER", "NAMA FRESHMEN"],
                values="Gap Sizing",
                color="Severity Level",
                color_discrete_map={
                    "🟡 Low Variance (1-2 pts)": "#eab308",
                    "🟠 Medium Variance (3-5 pts)": "#f97316",
                    "🔴 High Priority Audit (>5 pts)": "#ef4444"
                },
                custom_data=["prediksi point", "point apps", "selisih"]
            )
            fig_hierarchy.update_traces(
                hovertemplate="<b>%{label}</b><br>Prediksi: %{customdata[0]}<br>Apps: %{customdata[1]}<br>Selisih: %{customdata[2]} pt<extra></extra>"
            )
            fig_hierarchy.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=620)
            st.plotly_chart(fig_hierarchy, use_container_width=True)
        
        with st.expander("🔎 Lihat Daftar Detail Freshman & Point Gap Per FL", expanded=True):
            cols_show = ["Kelas", "PIC", "NAMA FRESHMEN LEADER", "NAMA FRESHMEN", "NIM FRESHMEN", "prediksi point", "point apps", "selisih", "Sesi yang 0", "Sesi yang Kosong", "Severity Level"]
            cols_show = [c for c in cols_show if c in df_belum.columns]
            st.dataframe(
                df_belum[cols_show].sort_values(["Kelas", "NAMA FRESHMEN LEADER"]),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.success("🎉 Tidak ada data 'Belum Sesuai' pada filter saat ini. Semua data sudah Sesuai!")


# ------------------------------------------------------------
# TAB 3: COURSE & SESSION DROP DIAGNOSTICS
# ------------------------------------------------------------
with tab_course:
    st.subheader("📚 Course & Session Drop Diagnostics")
    st.caption("Analisis mendalam untuk mengetahui topik/sesi perkuliahan mana yang paling banyak mengalami kendala logbook (Sesi Nilai 0 atau Sesi Kosong).")

    df_sess = extract_unnested_sessions(df_filtered)

    if not df_sess.empty:
        # Session KPI Summary
        top_sess_list = sorted(df_sess["Sesi"].unique())
        
        c_col1, c_col2 = st.columns([1, 2])
        
        with c_col1:
            st.markdown("#### 🎯 Filter & Pilih Sesi Spresifik:")
            selected_sess = st.selectbox("Pilih Sesi Logbook Bermasalah:", ["-- Tampilkan Semua Sesi --"] + top_sess_list)
            
            if selected_sess != "-- Tampilkan Semua Sesi --":
                df_sess_sub = df_sess[df_sess["Sesi"] == selected_sess]
                st.metric(f"Total Student Incomplete di {selected_sess}", len(df_sess_sub))
                st.metric("Total Kelas Terdampak", df_sess_sub["Kelas"].nunique())
            else:
                st.metric("Total Frekuensi Kejadian Incomplete Sesi", len(df_sess))
                st.metric("Total Topik Sesi Bermasalah", len(top_sess_list))

        with c_col2:
            st.markdown("#### 📊 Top Sesi Penyebab Discrepancy Point")
            sess_rank = df_sess.groupby(["Sesi", "Tipe Kendala"]).size().reset_index(name="Jumlah Student")
            fig_sess_rank = px.bar(
                sess_rank,
                x="Jumlah Student",
                y="Sesi",
                color="Tipe Kendala",
                barmode="stack",
                orientation="h",
                color_discrete_map={"Sesi Kosong": "#ef4444", "Nilai 0": "#f97316"},
                text="Jumlah Student"
            )
            fig_sess_rank.update_layout(height=340, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_sess_rank, use_container_width=True)

        st.divider()

        st.subheader("🔥 Heatmap Matrix: Kelas vs Topik Sesi Bermasalah")
        st.caption("Menunjukkan kelas mana saja yang belum melengkapi sesi tertentu.")
        
        pivot_sess_class = pd.crosstab(df_sess["Kelas"], df_sess["Sesi"])
        fig_sess_heat = px.imshow(
            pivot_sess_class,
            labels=dict(x="Topik Sesi", y="Kelas", color="Jumlah Student"),
            color_continuous_scale="Reds",
            text_auto=True,
            aspect="auto",
            title="Matrix Persebaran Sesi Incomplete Per Kelas"
        )
        fig_sess_heat.update_layout(height=480)
        st.plotly_chart(fig_sess_heat, use_container_width=True)

        st.divider()

        # Detailed Breakdown List by Selected Session
        if selected_sess != "-- Tampilkan Semua Sesi --":
            st.subheader(f"📋 Daftar Mahasiswa Lacking Point pada {selected_sess}")
            df_sess_detail = df_sess[df_sess["Sesi"] == selected_sess][["Kelas", "PIC", "FL", "Freshman", "NIM", "Tipe Kendala", "selisih", "Severity"]]
            st.dataframe(df_sess_detail.sort_values("Kelas"), use_container_width=True, hide_index=True)
        else:
            st.subheader("📋 Breakdown Seluruh Sesi per Mahasiswa")
            st.dataframe(df_sess[["Sesi", "Tipe Kendala", "Kelas", "PIC", "FL", "Freshman", "NIM", "selisih"]].sort_values("Sesi"), use_container_width=True, hide_index=True)

    else:
        st.success("🎉 Tidak ada kendala sesi (Sesi 0 atau Sesi Kosong) ditemukan pada filter saat ini!")


# ------------------------------------------------------------
# TAB 4: COMPLIANCE SCATTER & MATRIX ANALYTICS
# ------------------------------------------------------------
with tab_scatter:
    st.subheader("📈 Compliance Scatter Analytics (Garis Diagonal y = x)")
    st.caption("Diagram sebar Data Science untuk mengevaluasi posisi kesesuaian point. Titik di bawah garis diagonal mewakili freshman dengan selisih point terutang.")

    if not df_filtered.empty:
        fig_scatter = px.scatter(
            df_filtered,
            x="prediksi point",
            y="point apps",
            color="Severity Level",
            size="selisih",
            size_max=22,
            hover_name="NAMA FRESHMEN",
            hover_data=["NIM FRESHMEN", "Kelas", "NAMA FRESHMEN LEADER", "PIC", "selisih"],
            color_discrete_map={
                "🟢 Sesuai": "#22c55e",
                "🟡 Low Variance (1-2 pts)": "#eab308",
                "🟠 Medium Variance (3-5 pts)": "#f97316",
                "🔴 High Priority Audit (>5 pts)": "#ef4444"
            },
            title="Point Prediksi vs Point Apps (Titik di bawah garis = Terutang Point)"
        )

        max_val = max(int(df_filtered["prediksi point"].max()), int(df_filtered["point apps"].max()), 50)
        fig_scatter.add_shape(
            type="line",
            x0=0, y0=0, x1=max_val, y1=max_val,
            line=dict(color="#38bdf8", width=2, dash="dash")
        )
        fig_scatter.add_annotation(
            x=max_val * 0.75, y=max_val * 0.75,
            text="Garis Kepatuhan Sempurna (y = x)",
            showarrow=False,
            font=dict(color="#38bdf8", size=13)
        )
        fig_scatter.update_layout(height=520, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        matrix_col1, matrix_col2 = st.columns(2)

        with matrix_col1:
            st.subheader("🔥 Matrix Severity Concentration Per PIC")
            heatmap_data = pd.crosstab(df_filtered["PIC"], df_filtered["Severity Level"])
            fig_heat = px.imshow(
                heatmap_data,
                labels=dict(x="Severity Level", y="PIC", color="Jumlah Freshmen"),
                color_continuous_scale="Reds",
                text_auto=True,
                aspect="auto",
                title="Matrix Konsentrasi Discrepancy"
            )
            fig_heat.update_layout(height=420)
            st.plotly_chart(fig_heat, use_container_width=True)

        with matrix_col2:
            st.subheader("📊 Distirbusi Statistik Selisih Point")
            df_non_zero = df_filtered[df_filtered["selisih"] > 0]
            if not df_non_zero.empty:
                fig_box = px.box(
                    df_non_zero,
                    x="Kelas",
                    y="selisih",
                    color="Kelas",
                    points="all",
                    title="Sebaran Outlier Selisih Point Per Kelas"
                )
                fig_box.update_layout(height=420, showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("Semua selisih point = 0")


# ------------------------------------------------------------
# TAB 5: PIC & FL DIAGNOSTICS
# ------------------------------------------------------------
with tab_diagnostics:
    diag_col1, diag_col2 = st.columns([1, 1])

    with diag_col1:
        st.subheader("👤 Performance & Workload Per PIC")
        pic_summary = (
            df_filtered.groupby("PIC")
            .agg(
                Jumlah_Kelas=("Kelas", "nunique"),
                Total_Freshman=("Status", "count"),
                Jumlah_Sesuai=("Status", lambda s: (s == "Sesuai").sum()),
                Jumlah_Belum_Sesuai=("Status", lambda s: (s == "Belum Sesuai").sum()),
            )
            .reset_index()
        )
        pic_summary["Compliance %"] = (pic_summary["Jumlah_Sesuai"] / pic_summary["Total_Freshman"] * 100).round(1)
        pic_summary = pic_summary.sort_values("Jumlah_Belum_Sesuai", ascending=False)
        
        st.dataframe(
            pic_summary.style.format({"Compliance %": "{:.1f}%"}).background_gradient(subset=["Jumlah_Belum_Sesuai"], cmap="Reds"),
            use_container_width=True,
            hide_index=True
        )

    with diag_col2:
        st.subheader("🏆 Leaderboard FL (Berdasarkan Jumlah Belum Sesuai)")
        fl_summary = (
            df_filtered.groupby(["Kelas", "NAMA FRESHMEN LEADER", "PIC"])
            .agg(
                Total_FM=("Status", "count"),
                Belum_Sesuai=("Status", lambda s: (s == "Belum Sesuai").sum()),
                High_Risk=("Severity Level", lambda s: (s == "🔴 High Priority Audit (>5 pts)").sum())
            )
            .reset_index()
        )
        fl_summary["Discrepancy %"] = (fl_summary["Belum_Sesuai"] / fl_summary["Total_FM"] * 100).round(1)
        fl_summary = fl_summary.sort_values("Belum_Sesuai", ascending=False)

        st.dataframe(
            fl_summary.style.format({"Discrepancy %": "{:.1f}%"}).background_gradient(subset=["Belum_Sesuai"], cmap="YlOrRd"),
            use_container_width=True,
            hide_index=True
        )


# ------------------------------------------------------------
# TAB 6: DETAIL FRESHMAN DATA
# ------------------------------------------------------------
with tab_details:
    st.subheader("📋 Data Detail Freshmen & Export Engine")

    display_cols = [
        "Kelas",
        "PIC",
        "NAMA FRESHMEN LEADER",
        "NIM FRESHMEN",
        "NAMA FRESHMEN",
        "prediksi point",
        "point apps",
        "selisih",
        "Status",
        "Severity Level",
        "Sesi yang 0",
        "Sesi yang Kosong"
    ]
    display_cols = [c for c in display_cols if c in df_filtered.columns]

    dl_col1, dl_col2, _ = st.columns([1, 1, 2])
    
    with dl_col1:
        csv_data = df_filtered[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Data (CSV)",
            data=csv_data,
            file_name="FYP_B30_Filtered_Progress.csv",
            mime="text/csv"
        )
        
    with dl_col2:
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
            df_filtered[display_cols].to_excel(writer, index=False, sheet_name="Audit Data")
        excel_data = output_buffer.getvalue()
        
        st.download_button(
            label="📊 Export Filtered Data (Excel)",
            data=excel_data,
            file_name="FYP_B30_Filtered_Progress.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    def style_rows(row):
        if row["Status"] == "Belum Sesuai":
            return ["background-color: rgba(239, 68, 68, 0.15); color: #ffffff;"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_filtered[display_cols].style.apply(style_rows, axis=1),
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# TAB 7: ACTIONABLE WA REPORT GENERATOR
# ------------------------------------------------------------
with tab_action:
    st.subheader("💬 Generator Pesan Broadcast WhatsApp Audit")
    st.caption("Fitur ini membuat draf pesan WhatsApp yang rapi secara otomatis untuk dikirimkan ke PIC atau FL yang bersangkutan.")

    gen_mode = st.radio("Buat Laporan Berdasarkan:", ["Target per PIC", "Target per FL / Kelas"])

    if gen_mode == "Target per PIC":
        target_pic = st.selectbox("Pilih PIC:", sorted(df_filtered["PIC"].unique()))
        df_target = df_filtered[(df_filtered["PIC"] == target_pic) & (df_filtered["Status"] == "Belum Sesuai")]

        if not df_target.empty:
            wa_text = f"📢 *FOLLOW-UP AUDIT LOGBOOK FYP B30*\n"
            wa_text += f"Halo kak *{target_pic}*, berikut adalah daftar freshman kelas bimbinganmu yang status point-nya *BELUM SESUAI*:\n\n"

            for cls, group in df_target.groupby("Kelas"):
                wa_text += f"🔹 *Kelas {cls}* ({len(group)} student):\n"
                for _, r in group.iterrows():
                    sess_note = ""
                    if r['Sesi yang 0'] != "-":
                        sess_note += f" | Sesi 0: {r['Sesi yang 0']}"
                    if r['Sesi yang Kosong'] != "-":
                        sess_note += f" | Sesi Kosong: {r['Sesi yang Kosong']}"
                    wa_text += f"  • {r['NAMA FRESHMEN']} (FL: {r['NAMA FRESHMEN LEADER']}) - Selisih: {r['selisih']} pt{sess_note}\n"
                wa_text += "\n"

            wa_text += f"📁 Mohon bantu crosscheck bukti di GDrive Logbook:\n{GDRIVE_LOGBOOK_LINK}\n\nTerima kasih! 🙏"
            
            st.text_area("📋 Copas Pesan WhatsApp di bawah ini:", value=wa_text, height=280)
        else:
            st.success(f"🎉 Selamat! Semua freshman under PIC {target_pic} sudah Sesuai!")

    else:
        target_kelas = st.selectbox("Pilih Kelas:", sorted(df_filtered["Kelas"].unique()))
        df_target = df_filtered[(df_filtered["Kelas"] == target_kelas) & (df_filtered["Status"] == "Belum Sesuai")]

        if not df_target.empty:
            fl_name = df_target["NAMA FRESHMEN LEADER"].iloc[0]
            pic_name = df_target["PIC"].iloc[0]
            
            wa_text = f"📢 *REMINDER CHECK LOGBOOK FYP B30*\n"
            wa_text += f"Halo Kak *{fl_name}* (FL Kelas *{target_kelas}* / PIC: {pic_name}),\n\n"
            wa_text += f"Mohon bantuannya untuk mengecek data point freshman berikut yang masih *BELUM SESUAI* di sistem:\n\n"

            for _, r in df_target.iterrows():
                wa_text += f"• *{r['NAMA FRESHMEN']}* ({r['NIM FRESHMEN']})\n"
                wa_text += f"  - Point Prediksi: {r['prediksi point']} | Point Apps: {r['point apps']} (Selisih: {r['selisih']} pt)\n"
                if r['Sesi yang 0'] != "-":
                    wa_text += f"  - Sesi 0: {r['Sesi yang 0']}\n"
                if r['Sesi yang Kosong'] != "-":
                    wa_text += f"  - Sesi Kosong: {r['Sesi yang Kosong']}\n"
                wa_text += "\n"

            wa_text += f"📁 Silakan update/upload ulang bukti logbook di Google Drive:\n{GDRIVE_LOGBOOK_LINK}\n\nTerima kasih atas kerjasamanya! ✨"

            st.text_area("📋 Copas Pesan WhatsApp di bawah ini:", value=wa_text, height=280)
        else:
            st.success(f"🎉 Semua data freshman di kelas {target_kelas} sudah Sesuai!")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("FYP B30 Freshman Progress Dashboard • Designed with Streamlit & Data Science Engine")