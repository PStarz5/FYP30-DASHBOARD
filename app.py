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
# DATA LOADING & FEATURE ENGINEERING ENGINE
# ============================================================
@st.cache_data
def process_data(file_buffer):
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
    df_all["prediksi point"] = pd.to_numeric(df_all.get("prediksi point", 0), errors="coerce").fillna(0).astype(int)
    df_all["point apps"] = pd.to_numeric(df_all.get("point apps", 0), errors="coerce").fillna(0).astype(int)
    
    # Calculate Selisih as absolute positive gap
    df_all["selisih"] = (df_all["prediksi point"] - df_all["point apps"]).abs().astype(int)

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
            return "🟡 Beda Tipis (1-2 Point)"
        elif diff <= 5:
            return "🟠 Beda Sedang (3-5 Point)"
        else:
            return "🔴 Beda Banyak (>5 Point)"

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
st.markdown(f"""
<div style="text-align: center; padding: 10px 0 20px 0;">
<h1 style="font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #60a5fa, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px;">
📊 FYP B30 - Freshman Progress & Analytics
</h1>
<p style="color: #94a3b8; font-size: 1rem; font-weight: 500; margin-bottom: 24px;">
Platform Analytics Point Logbook, Anomaly Detection & Progress Dashboard
</p>

<div style="max-width: 850px; margin: 0 auto; padding: 20px 24px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(59, 130, 246, 0.3); border-top: 4px solid #3b82f6; border-radius: 14px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
<h4 style="color: #60a5fa; font-size: 1.1rem; margin-top: 0; margin-bottom: 8px; font-weight: 700;">📌 Petunjuk Monitoring & Crosscheck Logbook FYP</h4>
<p style="margin-bottom: 6px; font-size: 0.93rem; color: #cbd5e1;">
Status <b>"Belum Sesuai"</b> menandakan adanya selisih antara data <b>File Monitoring FL</b> dengan <b>Logbook Aplikasi</b> real-time.
</p>
<p style="margin-bottom: 14px; font-size: 0.88rem; color: #94a3b8;">
FYPL & PIC dimohon melakukan audit silang dengan bukti fisik/digital pada Google Drive Logbook.
</p>
<a href="{GDRIVE_LOGBOOK_LINK}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 8px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem; box-shadow: 0 4px 14px rgba(59,130,246,0.35);">
📁 Buka Google Drive Logbook All Drive
</a>
</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🎛️ Data Source & Filters")

uploaded_file = st.sidebar.file_uploader("Upload File Excel Monitoring", type=["xlsx", "xls"], key="sidebar_uploader")

if uploaded_file is not None:
    df_raw = process_data(uploaded_file)
elif os.path.exists("logbook_mismatch_per_kelas.xlsx"):
    df_raw = process_data("logbook_mismatch_per_kelas.xlsx")
else:
    # Centered Hero Section for Upload
    hero_col1, hero_col2, hero_col3 = st.columns([1, 2.8, 1])
    with hero_col2:
        st.markdown("""
<div style="text-align: center; padding: 28px 24px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 16px; margin-top: 10px; margin-bottom: 20px;">
<h3 style="color: #60a5fa; margin-top: 0; font-weight: 700;">📥 Upload File Excel Monitoring FYP</h3>
<p style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 16px;">
Silakan upload file Excel terbaru kamu di bawah ini (format: <b>1 sheet = 1 kelas</b>) untuk mulai menganalisis data kepatuhan point logbook.
</p>
</div>
""", unsafe_allow_html=True)

        center_file = st.file_uploader("Drop file Excel di sini atau klik untuk memilih file", type=["xlsx", "xls"], key="center_uploader")
        
        if center_file is not None:
            uploaded_file = center_file
            df_raw = process_data(uploaded_file)
        else:
            st.stop()

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

severity_list = ["🟢 Sesuai", "🟡 Beda Tipis (1-2 Point)", "🟠 Beda Sedang (3-5 Point)", "🔴 Beda Banyak (>5 Point)"]
selected_severity = st.sidebar.multiselect("Filter Tingkat Selisih Point", severity_list, default=severity_list)

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
tab_overview, tab_rootcause, tab_diagnostics, tab_details, tab_action = st.tabs([
    "📊 Ringkasan",
    "🌳 Peta Pemetaan",
    "👤 Ranking FL & PIC",
    "📋 Data Detail",
    "💬 Pesan WA"
])

# ------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------
with tab_overview:
    total_fm = len(df_filtered)
    sesuai_count = len(df_filtered[df_filtered["Status"] == "Sesuai"])
    belum_count = len(df_filtered[df_filtered["Status"] == "Belum Sesuai"])
    high_risk_count = len(df_filtered[df_filtered["Severity Level"] == "🔴 Beda Banyak (>5 Point)"])
    
    compliance_rate = (sesuai_count / total_fm * 100) if total_fm > 0 else 0
    mismatch_rate = (belum_count / total_fm * 100) if total_fm > 0 else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Freshman</div>
            <div class="metric-value">{total_fm:,}</div>
            <div class="metric-subtitle">Mahasiswa Terfilter</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Persentase Sesuai</div>
            <div class="metric-value">{compliance_rate:.1f}%</div>
            <div class="metric-subtitle">{sesuai_count} Student Sesuai</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Belum Sesuai</div>
            <div class="metric-value" style="color: #f87171;">{belum_count:,}</div>
            <div class="metric-subtitle negative">{mismatch_rate:.1f}% Perlu Cek</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Beda > 5 Point</div>
            <div class="metric-value" style="color: #ef4444;">{high_risk_count:,}</div>
            <div class="metric-subtitle negative">Selisih Banyak</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        active_pics = df_filtered["PIC"].nunique()
        active_classes = df_filtered["Kelas"].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Jumlah Kelas & PIC</div>
            <div class="metric-value">{active_classes} <span style="font-size: 1rem; color: #888;">Kelas</span></div>
            <div class="metric-subtitle">{active_pics} PIC Aktif</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Automated Data Insights Callout Box
    st.subheader("💡 Ringkasan Penting Hari Ini")
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
            📌 **Kelas Paling Banyak Belum Sesuai:** **{top_disc_class}** ({top_disc_class_count} freshman belum sesuai)  
            🚨 **Freshmen Leader (FL) Perlu Cek Ulang:** **{top_fl_name}** (Kelas {top_fl_class} - {top_fl_count} freshman bermasalah)
            """)
        with insight_col2:
            st.warning(f"""
            📚 **Top Sesi Incomplete Terbanyak:** **{top_sess_name}** ({top_sess_count} kejadian)  
            ⚡ Terdapat **{high_risk_count}** freshman dengan **Selisih > 5 Point** yang membutuhkan pengecekan ulang logbook secepatnya.
            """)

    st.divider()

    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.subheader("🍩 Perbandingan Status Point")
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
        st.subheader("📊 Grafik Tingkat Selisih Point")
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
                "🟡 Beda Tipis (1-2 Point)": "#eab308",
                "🟠 Beda Sedang (3-5 Point)": "#f97316",
                "🔴 Beda Banyak (>5 Point)": "#ef4444"
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
    st.subheader("🌳 Peta Pemetaan Freshman Belum Sesuai")
    st.caption("Lihat daftar freshman yang belum sesuai point-nya, dikelompokkan berdasarkan PIC, Kelas, dan Freshmen Leader (FL).")

    chart_type = st.radio("Pilih Mode Grafik:", ["🌳 Kotak Hirarki (Treemap)", "☀️ Lingkaran Bertingkat (Sunburst)"], horizontal=True)

    df_belum = df_filtered[df_filtered["Status"] == "Belum Sesuai"].copy()
    
    if not df_belum.empty:
        df_belum["Gap Sizing"] = df_belum["selisih"].apply(lambda v: max(1, v))
        
        # Smart compact label formatting for real Excel data like logbook_mismatch_per_kelas.xlsx
        def make_leaf_label(r):
            lbl = f"<b>{r['NAMA FRESHMEN']}</b><br>Selisih: -{r['selisih']} pt ({r['prediksi point']} ➔ {r['point apps']})"
            notes = []
            
            # Format Sesi 0
            v0 = str(r.get('Sesi yang 0', '-')).strip()
            if v0 not in ['-', 'nan', 'None', '']:
                s_list = [s.strip() for s in v0.split(',') if s.strip()]
                if len(s_list) == 1:
                    notes.append(f"0: {s_list[0]}")
                elif len(s_list) == 2:
                    notes.append(f"0: {s_list[0]}, {s_list[1]}")
                elif len(s_list) > 2:
                    notes.append(f"0: {len(s_list)} Sesi ({s_list[0]}...)")
                    
            # Format Sesi Kosong
            vk = str(r.get('Sesi yang Kosong', '-')).strip()
            if vk not in ['-', 'nan', 'None', '']:
                s_list = [s.strip() for s in vk.split(',') if s.strip()]
                if len(s_list) == 1:
                    notes.append(f"Kosong: {s_list[0]}")
                elif len(s_list) == 2:
                    notes.append(f"Kosong: {s_list[0]}, {s_list[1]}")
                elif len(s_list) > 2:
                    notes.append(f"Kosong: {len(s_list)} Sesi ({s_list[0]}...)")

            if notes:
                lbl += f"<br>📚 " + " | ".join(notes)
            return lbl

        df_belum["Leaf Label"] = df_belum.apply(make_leaf_label, axis=1)

        if chart_type == "🌳 Kotak Hirarki (Treemap)":
            fig_hierarchy = px.treemap(
                df_belum,
                path=["PIC", "Kelas", "NAMA FRESHMEN LEADER", "Leaf Label"],
                values="Gap Sizing",
                color="Severity Level",
                color_discrete_map={
                    "🟡 Beda Tipis (1-2 Point)": "#eab308",
                    "🟠 Beda Sedang (3-5 Point)": "#f97316",
                    "🔴 Beda Banyak (>5 Point)": "#ef4444"
                },
                custom_data=["NAMA FRESHMEN", "prediksi point", "point apps", "selisih", "NIM FRESHMEN", "Sesi yang 0", "Sesi yang Kosong"]
            )
            fig_hierarchy.update_traces(
                textfont=dict(size=14),
                hovertemplate="<b>%{customdata[0]}</b> (NIM: %{customdata[4]})<br>Point Prediksi: %{customdata[1]} pt<br>Point Apps: %{customdata[2]} pt<br><b>Selisih Gap: -%{customdata[3]} pt</b><br>Sesi 0: %{customdata[5]}<br>Sesi Kosong: %{customdata[6]}<extra></extra>"
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
                    "🟡 Beda Tipis (1-2 Point)": "#eab308",
                    "🟠 Beda Sedang (3-5 Point)": "#f97316",
                    "🔴 Beda Banyak (>5 Point)": "#ef4444"
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
# TAB 3: PIC & FL DIAGNOSTICS
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