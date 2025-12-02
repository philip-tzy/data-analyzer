# survey_app_final.py
# Full Streamlit app — Rainbow UI with full-page background (A)
# Run: python -m streamlit run survey_app_final.py
# Dependencies: streamlit, pandas, numpy, matplotlib, scipy, openpyxl (for xlsx)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats
import io, base64, os
from typing import List

# ---------- Config ----------
st.set_page_config(page_title="Survey Analyzer", layout="wide")

# Path to background image (change if you saved a different filename)
BG_IMAGE_PATH = "/mnt/data/a4df5aa-7a52-414a-9c33-e96e5d9d443d.png"

# ---------- Session defaults ----------
if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = False
if "lang" not in st.session_state:
    st.session_state.lang = "en"  # default English
if "missing_method" not in st.session_state:
    st.session_state.missing_method = "Drop rows (default)"

# ---------- Utilities ----------
def read_image_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BG_BASE64 = read_image_base64(BG_IMAGE_PATH)

# ---------- Multilanguage dictionary ----------
LANGUAGES = {
    "en": "English",
    "id": "Indonesia",
    "cn": "中文",
    "jp": "日本語",
    "kr": "한국어",
    "ru": "Русский",
    "de": "Deutsch",
    "nl": "Nederlands",
}

TEXT = {
    "title": {
        "en": "Survey Analyzer — Rainbow Theme",
        "id": "Aplikasi Analisis Survei — Tema Pelangi",
        "cn": "调查分析器 — 彩虹主题",
        "jp": "アンケート解析 — レインボーテーマ",
        "kr": "설문 분석기 — 무지개 테마",
        "ru": "Анализатор опросов — Радужная тема",
        "de": "Umfrage-Analysetool — Regenbogenthema",
        "nl": "Enquête-Analyzer — Regenboogthema",
    },
    "subtitle": {
        "en": "Upload Excel/CSV, compute descriptive stats, associations, and export PDF.",
        "id": "Unggah Excel/CSV, hitung statistik deskriptif, asosiasi, dan ekspor PDF.",
        "cn": "上传 Excel/CSV，计算描述统计、关联，并导出 PDF。",
        "jp": "Excel/CSV をアップロードして、記述統計・関連性を計算し、PDF を出力します。",
        "kr": "Excel/CSV 업로드, 기술 통계 및 연관성 계산, PDF 내보내기.",
        "ru": "Загрузите Excel/CSV, вычислите описательную статистику и ассоциации, экспортируйте в PDF.",
        "de": "Excel/CSV hochladen, deskriptive Statistik und Assoziationen berechnen, PDF exportieren.",
        "nl": "Upload Excel/CSV, bereken beschrijvende statistiek en associaties, exporteer PDF.",
    },
    "upload": {
        "en": "Upload dataset (.xlsx or .csv)",
        "id": "Unggah dataset (.xlsx atau .csv)",
        "cn": "上传数据集 (.xlsx 或 .csv)",
        "jp": "データセットをアップロード (.xlsx または .csv)",
        "kr": "데이터셋 업로드 (.xlsx 또는 .csv)",
        "ru": "Загрузить набор данных (.xlsx или .csv)",
        "de": "Datensatz hochladen (.xlsx oder .csv)",
        "nl": "Dataset uploaden (.xlsx of .csv)",
    },
    "group_members": {
        "en": "Group members",
        "id": "Anggota kelompok",
        "cn": "小组成员",
        "jp": "グループメンバー",
        "kr": "그룹 구성원",
        "ru": "Члены группы",
        "de": "Gruppenmitglieder",
        "nl": "Groepsleden",
    },
    "missing_label": {
        "en": "Missing value handling",
        "id": "Penanganan nilai kosong",
        "cn": "缺失值处理",
        "jp": "欠損値の処理",
        "kr": "결측치 처리",
        "ru": "Обработка пропущенных значений",
        "de": "Umgang mit fehlenden Werten",
        "nl": "Omgaan met ontbrekende waarden",
    },
    "missing_options": {
        "en": ["Drop rows (default)", "Fill with 0", "Fill with mean", "Fill with median"],
        "id": ["Hapus baris (default)", "Isi dengan 0", "Isi dengan mean", "Isi dengan median"],
        "cn": ["删除含缺失的行 (默认)", "用 0 填充", "用均值填充", "用中位数填充"],
        "jp": ["行を削除（デフォルト）", "0で埋める", "平均で埋める", "中央値で埋める"],
        "kr": ["행 삭제 (기본)", "0으로 채우기", "평균으로 채우기", "중앙값으로 채우기"],
        "ru": ["Удалить строки (по умолч.)", "Заполнить 0", "Заполнить средним", "Заполнить медианой"],
        "de": ["Zeilen löschen (Standard)", "Mit 0 füllen", "Mit Mittelwert füllen", "Mit Median füllen"],
        "nl": ["Rijen verwijderen (standaard)", "Vullen met 0", "Vullen met gemiddelde", "Vullen met mediaan"],
    },
    "compute_composites": {
        "en": "Compute composite scores X_total & Y_total (sum)",
        "id": "Hitung skor komposit X_total & Y_total (jumlah)",
        "cn": "计算合成分数 X_total & Y_total（求和）",
        "jp": "合成スコア X_total と Y_total を計算 (合計)",
        "kr": "합성 점수 X_total & Y_total 계산 (합)",
        "ru": "Вычислить составные показатели X_total и Y_total (сумма)",
        "de": "Kompositwerte X_total & Y_total berechnen (Summe)",
        "nl": "Bereken samengestelde scores X_total & Y_total (som)",
    },
    "enable_chi2": {
        "en": "Enable Chi-square (if you want categorical totals)",
        "id": "Aktifkan Chi-square (jika mau total kategori)",
        "cn": "启用卡方检验（如果要类别化总分）",
        "jp": "Chi-square を有効にする（カテゴリ化された合計時）",
        "kr": "카이제곱 활성화 (카테고리화된 합계 사용 시)",
        "ru": "Включить Chi-square (если нужны категориальные суммы)",
        "de": "Chi-Quadrat aktivieren (bei kategorischen Summen)",
        "nl": "Chi-kwadraat inschakelen (voor categorische totals)",
    },
    "auto_method": {
        "en": "Automatically chosen method based on normality:",
        "id": "Metode yang dipilih otomatis berdasarkan normalitas:",
        "cn": "基于正态性自动选择的方法：",
        "jp": "正規性に基づき自動選択された方法：",
        "kr": "정규성 기반 자동 선택 방법:",
        "ru": "Автоматически выбранный метод по нормальности:",
        "de": "Automatisch gewählte Methode basierend auf Normalität:",
        "nl": "Automatisch gekozen methode op basis van normaliteit:",
    },
}

def T(key):
    lang = st.session_state.lang
    return TEXT.get(key, {}).get(lang, "")

# ---------- CSS for full-screen background (A) + UI styles ----------
_bg_css = ""
if BG_BASE64:
    # IMPORTANT: inside f-string we MUST escape any literal '{' or '}' by doubling them '{{' '}}'
    _bg_css = f"""
    <style>
    /* Times New Roman globally */
    html, body, [class*="css"] {{ font-family: "Times New Roman", Times, serif !important; }}

    /* Full-page background image */
    .stApp {{
        background-image: url("data:image/png;base64,{BG_BASE64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        transition: background 0.6s ease;
    }}

    /* dark mode toggling via .dark on html will be managed by JS helper */
    html.dark .stApp {{
        filter: brightness(0.68);
    }}

    /* Rainbow bar */
    .rainbow-bar {{
        height:14px;
        border-radius:12px;
        background: linear-gradient(90deg, #ff3b3b 0%, #ff8a3d 16%, #ffd93d 33%, #8cff3d 50%, #20ffd0 66%, #2dbcff 82%, #b66aff 100%);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        margin: 6px 0 18px 0;
        animation: glow 3.5s infinite alternate;
    }}
    @keyframes glow {{ from {{ filter: brightness(0.95); transform: translateY(0px); }} to {{ filter: brightness(1.12); transform: translateY(-2px); }} }}

    /* Glass cards (no white large top box) */
    .glass-card {{
        background: rgba(255,255,255,0.70);
        backdrop-filter: blur(8px);
        border-radius:14px;
        padding:14px;
        box-shadow: 0 8px 30px rgba(10,20,40,0.08);
        border: 1px solid rgba(31,45,107,0.06);
        margin-bottom:14px;
        transition: transform 0.28s ease, box-shadow 0.28s ease;
    }}
    html.dark .glass-card {{
        background: linear-gradient(135deg,#071022 0%, #071028 50%, #04110b 100%);
        border: 1px solid rgba(255,255,255,0.03);
        box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    }}

    /* small accent inside */
    .card-accent {{
        height:6px;
        border-radius:8px;
        background: linear-gradient(90deg, rgba(255,59,59,0.95), rgba(255,138,61,0.95), rgba(255,217,61,0.95), rgba(140,255,61,0.95), rgba(32,255,208,0.95), rgba(45,188,255,0.95), rgba(182,106,255,0.95));
        margin-bottom:10px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    }}

    /* metrics */
    .metric {{
        background: rgba(255,255,255,0.92);
        border-radius: 8px;
        padding: 8px 10px;
        text-align:center;
    }}
    html.dark .metric {{ background: rgba(255,255,255,0.04); }}
    .metric-label {{ font-size:12px; color:#5b6390; }}
    .metric-value {{ font-size:18px; font-weight:700; color:#16224a; }}
    html.dark .metric-value {{ color:#cfe8ff; }}

    /* small fade-in */
    .fade-in {{ animation: fadeIn 0.6s ease both; }}
    # --- Corrected keyframes (use inside your f-string CSS) ---
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}


    /* buttons rounded */
    .stButton>button {{ border-radius:10px; padding:8px 14px; }}

    /* override header background box */
    header[role="banner"] {{ background: transparent !important; box-shadow: none !important; }}
    </style>
    """
else:
    _bg_css = "<style>html, body { font-family: 'Times New Roman', Times, serif !important; }</style>"

st.markdown(_bg_css, unsafe_allow_html=True)

# ---------- JS helper to toggle dark class ----------
def set_dark_class_js(enable: bool):
    if enable:
        js = "document.documentElement.classList.add('dark')"
    else:
        js = "document.documentElement.classList.remove('dark')"
    st.components.v1.html(f"<script>{js}</script>", height=0)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("Preferences / Preferensi")
    # language selector
    lang_choice = st.selectbox("🌐 Language / Pilih Bahasa", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.lang) if st.session_state.lang in list(LANGUAGES.keys()) else 0)
    st.session_state.lang = lang_choice

    # dark mode toggle
    dark_toggle = st.checkbox("🌙 Dark Mode", value=st.session_state.theme_dark)
    st.session_state.theme_dark = dark_toggle
    set_dark_class_js(dark_toggle)

    st.markdown("---")
    st.subheader(TEXT["missing_label"][st.session_state.lang])
    missing_opts = TEXT["missing_options"][st.session_state.lang]
    missing_choice = st.radio("", options=missing_opts, index=0)
    # normalize to English internal keys
    mapping_missing = dict(zip(missing_opts, ["Drop rows (default)", "Fill with 0", "Fill with mean", "Fill with median"]))
    st.session_state.missing_method = mapping_missing.get(missing_choice, "Drop rows (default)")

    st.markdown("---")
    st.subheader("Column tagging / Kategorisasi Kolom")
    st.caption("Select Likert X/Y items and demographic columns (optional)")

# ---------- Header: rainbow bar and title ----------
st.markdown('<div class="rainbow-bar"></div>', unsafe_allow_html=True)
st.markdown(f"<div class='glass-card fade-in'><h1 style='margin:6px 0 2px 0'>{TEXT['title'][st.session_state.lang]}</h1><div style='color:rgba(0,0,0,0.6);'>{TEXT['subtitle'][st.session_state.lang]}</div></div>", unsafe_allow_html=True)

# ---------- Group members ----------
GROUP_INFO = [
    "Aldy Candra Winata — 004202400130 — Industrial Engineering — President University",
    "Mitza Cetta Cadudasa — 004202200059 — Industrial Engineering — President University",
    "Fauziah Fithriyani Pamuji — 004202400007 — Industrial Engineering — President University",
    "Miftahul Khaerunnisa — 004202400057 — Industrial Engineering — President University"
]

with st.expander(TEXT["group_members"][st.session_state.lang], expanded=False):
    for m in GROUP_INFO:
        st.write(m)

# ---------- File upload ----------
uploaded = st.file_uploader(TEXT["upload"][st.session_state.lang], type=["xlsx", "csv"])
if not uploaded:
    st.info(TEXT["upload"][st.session_state.lang])
    st.stop()

# read file safely
try:
    if str(uploaded.name).lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded, engine="openpyxl")
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

st.success("File loaded successfully.")
st.dataframe(df.head(8))

# ---------- Sidebar: column tagging (continued) ----------
all_cols = df.columns.tolist()
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
default_x = numeric_cols[:4]
default_y = numeric_cols[4:8]

with st.sidebar:
    x_items = st.multiselect('Select X items (min 4) / Pilih item X (min 4)', all_cols, default=default_x)
    y_items = st.multiselect('Select Y items (min 4) / Pilih item Y (min 4)', all_cols, default=default_y)
    suggest_demo = [c for c in all_cols if any(k in c.lower() for k in ['age','gender','major','department','education','phone','usage'])]
    demo_cols = st.multiselect('Demographic columns (optional) / Kolom demografi (opsional)', all_cols, default=suggest_demo)

    compute_composites = st.checkbox(TEXT["compute_composites"][st.session_state.lang], value=True if (len(x_items)>=1 and len(y_items)>=1) else False)
    allow_chi2 = st.checkbox(TEXT["enable_chi2"][st.session_state.lang], value=False)
    if allow_chi2:
        bins = st.slider('Number of bins (for chi-square) / Jumlah bin', 2, 6, 3)

# ---------- Data cleaning & missing handling ----------
df_work = df.copy()
for c in x_items + y_items:
    df_work[c] = pd.to_numeric(df_work[c], errors="coerce")

if compute_composites:
    if len(x_items) >= 1:
        df_work["X_total"] = df_work[x_items].sum(axis=1, skipna=False)
    if len(y_items) >= 1:
        df_work["Y_total"] = df_work[y_items].sum(axis=1, skipna=False)

# apply missing value handling chosen
mm = st.session_state.missing_method
if mm == "Fill with 0":
    df_work = df_work.fillna(0)
elif mm == "Fill with mean":
    numeric_means = df_work.mean(numeric_only=True)
    df_work = df_work.fillna(numeric_means)
elif mm == "Fill with median":
    numeric_meds = df_work.median(numeric_only=True)
    df_work = df_work.fillna(numeric_meds)
# else "Drop rows (default)" -> do not globally fill, we'll drop pairwise in association step if default

# ---------- Descriptive helper ----------
def descriptive_series(s: pd.Series):
    s_num = pd.to_numeric(s, errors='coerce')
    out = {}
    out['count'] = int(s_num.count())
    if out['count'] == 0:
        return out
    out['mean'] = s_num.mean()
    out['median'] = s_num.median()
    out['mode'] = s_num.mode().tolist()
    out['min'] = s_num.min()
    out['max'] = s_num.max()
    out['std'] = s_num.std(ddof=1)
    freq = s.value_counts(dropna=False).sort_index()
    pct = (freq / freq.sum() * 100).round(2)
    out['freq_table'] = pd.DataFrame({'count': freq, 'percent': pct})
    return out

items_to_describe = x_items + y_items if (len(x_items)+len(y_items) > 0) else numeric_cols

# ---------- Descriptive display (cards) ----------
st.header("A. " + ("Descriptive Statistics" if st.session_state.lang == "en" else "Statistik Deskriptif"))
st.markdown('<div style="display:flex;flex-wrap:wrap;gap:14px;">', unsafe_allow_html=True)

for col in items_to_describe:
    out = descriptive_series(df_work[col])
    st.markdown('<div class="glass-card fade-in" style="width:48%;">', unsafe_allow_html=True)
    st.markdown('<div class="card-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:700;margin-bottom:6px;'>{col}</div>", unsafe_allow_html=True)
    if out.get('count', 0) == 0:
        st.write("No numeric data for this item." if st.session_state.lang == "en" else "Tidak ada data numerik untuk item ini.")
        st.markdown('</div>', unsafe_allow_html=True)
        continue
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Count' if st.session_state.lang == 'en' else 'Jumlah'}</div><div class='metric-value'>{out['count']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Mean' if st.session_state.lang == 'en' else 'Rata-rata'}</div><div class='metric-value'>{out['mean']:.3f}</div></div>", unsafe_allow_html=True)
    with c2:
        med = out.get('median','')
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Median' if st.session_state.lang == 'en' else 'Median'}</div><div class='metric-value'>{med}</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        mode_display = out['mode'][0] if isinstance(out.get('mode'), list) and len(out['mode'])>0 else ''
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Mode' if st.session_state.lang == 'en' else 'Modus'}</div><div class='metric-value'>{mode_display}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Min' if st.session_state.lang == 'en' else 'Min'}</div><div class='metric-value'>{out['min']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric'><div class='metric-label'>{'Max' if st.session_state.lang == 'en' else 'Max'}</div><div class='metric-value'>{out['max']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    t1, t2 = st.columns([1,1])
    with t1:
        st.markdown(f"<div style='font-weight:700;margin-bottom:6px;'>{'Frequency & Percentage' if st.session_state.lang == 'en' else 'Frekuensi & Persentase'}</div>", unsafe_allow_html=True)
        st.dataframe(out['freq_table'].reset_index().rename(columns={'index':col}))
    with t2:
        fig, axes = plt.subplots(1,2, figsize=(6,2.2))
        data = pd.to_numeric(df_work[col], errors='coerce').dropna()
        axes[0].hist(data, bins=min(8, max(3, int(len(data)/4))))
        axes[0].set_title('Histogram')
        axes[0].tick_params(axis='both', which='major', labelsize=8)
        axes[1].boxplot(data, vert=True)
        axes[1].set_title('Boxplot')
        axes[1].tick_params(axis='both', which='major', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Composite totals ----------
if compute_composites:
    st.header("Composite scores (X_total, Y_total)" if st.session_state.lang == "en" else "Statistik skor komposit (X_total, Y_total)")
    for comp in ["X_total", "Y_total"]:
        if comp in df_work.columns:
            out = descriptive_series(df_work[comp])
            st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;margin-bottom:6px;'>{comp}</div>", unsafe_allow_html=True)
            if out.get('count',0) == 0:
                st.write("No data" if st.session_state.lang == "en" else "Tidak ada data")
                st.markdown('</div>', unsafe_allow_html=True)
                continue
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Count' if st.session_state.lang == 'en' else 'Jumlah'}</div><div class='metric-value'>{out['count']}</div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Mean' if st.session_state.lang == 'en' else 'Rata-rata'}</div><div class='metric-value'>{out['mean']:.3f}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Median' if st.session_state.lang == 'en' else 'Median'}</div><div class='metric-value'>{out['median']}</div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                mode_display = out['mode'][0] if isinstance(out.get('mode'), list) and len(out['mode'])>0 else ''
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Mode' if st.session_state.lang == 'en' else 'Modus'}</div><div class='metric-value'>{mode_display}</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Min' if st.session_state.lang == 'en' else 'Min'}</div><div class='metric-value'>{out['min']}</div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric'><div class='metric-label'>{'Std Dev' if st.session_state.lang == 'en' else 'Std Dev'}</div><div class='metric-value'>{out['std']:.3f}</div></div>", unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            t1, t2 = st.columns([1,1])
            with t1:
                st.markdown(f"<div style='font-weight:700;margin-bottom:6px;'>{'Frequency & Percentage' if st.session_state.lang == 'en' else 'Frekuensi & Persentase'}</div>", unsafe_allow_html=True)
                st.dataframe(out['freq_table'].reset_index().rename(columns={'index':comp}))
            with t2:
                fig, axes = plt.subplots(1,2, figsize=(6,2.2))
                data = pd.to_numeric(df_work[comp], errors='coerce').dropna()
                axes[0].hist(data, bins=min(10, max(4, int(len(data)/3))))
                axes[0].set_title('Histogram')
                axes[0].tick_params(axis='both', which='major', labelsize=8)
                axes[1].boxplot(data, vert=True)
                axes[1].set_title('Boxplot')
                axes[1].tick_params(axis='both', which='major', labelsize=8)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

# ---------- Association Analysis ----------
st.header("B. Association Analysis (X and Y)" if st.session_state.lang == "en" else "B. Analisis Asosiasi (X dan Y)")
has_X_total = "X_total" in df_work.columns
has_Y_total = "Y_total" in df_work.columns
if not (has_X_total and has_Y_total):
    st.warning("Composite totals X_total and Y_total missing. Select X and Y items and enable composite computation in sidebar." if st.session_state.lang == "en" else "Skor komposit X_total dan Y_total belum tersedia. Pilih item X dan Y lalu aktifkan penghitungan komposit di sidebar.")
else:
    # pair handling depends on missing method
    if st.session_state.missing_method == "Drop rows (default)":
        pair = df_work[["X_total", "Y_total"]].dropna()
    else:
        pair = df_work[["X_total", "Y_total"]]

    n_pairs = len(pair)
    st.write(("Number of valid pairs:" if st.session_state.lang == "en" else "Jumlah pasangan valid:"), n_pairs)
    if n_pairs < 3:
        st.warning("Not enough pairs to perform correlation (need at least 3)." if st.session_state.lang == "en" else "Pasangan tidak cukup untuk korelasi (butuh minimal 3).")
    else:
        # normality
        try:
            stat_x, p_x = stats.shapiro(pair["X_total"]) if n_pairs >= 3 else (None, None)
            stat_y, p_y = stats.shapiro(pair["Y_total"]) if n_pairs >= 3 else (None, None)
        except Exception:
            p_x, p_y = None, None

        st.write(("Shapiro p-values (X_total, Y_total):" if st.session_state.lang == "en" else "p-value Shapiro (X_total, Y_total):"),
                 round(p_x,4) if p_x is not None else None,
                 round(p_y,4) if p_y is not None else None)

        auto_method = "pearson" if (p_x is not None and p_y is not None and p_x > 0.05 and p_y > 0.05) else "spearman"
        st.write((TEXT["auto_method"][st.session_state.lang] if st.session_state.lang in TEXT["auto_method"] else TEXT["auto_method"]["en"]), auto_method.capitalize())

        # allow manual override (power users) - keep feature
        method_choice = st.radio("Choose method (Auto / Pearson / Spearman / Chi-square)" if st.session_state.lang == "en" else "Pilih metode (Otomatis / Pearson / Spearman / Chi-square)",
                                 options=["Auto", "Pearson", "Spearman", "Chi-square"], index=0)
        if method_choice == "Auto":
            method_used = auto_method
        elif method_choice == "Chi-square":
            method_used = "chi2"
        else:
            method_used = method_choice.lower()

        if method_used == "chi2":
            st.info("Chi-square requires categorical variables. We'll bin X_total and Y_total." if st.session_state.lang == "en" else "Chi-square memerlukan variabel kategorikal. Kita akan melakukan bin pada X_total dan Y_total.")
            bins_choice = st.selectbox("Binning method / Metode binning", options=["Quantiles", "Equal width"])
            nbins = st.slider("Number of bins / Jumlah bin", 2, 6, value=3)
            if bins_choice == "Quantiles":
                pair["X_cat"] = pd.qcut(pair["X_total"], q=nbins, duplicates="drop").astype(str)
                pair["Y_cat"] = pd.qcut(pair["Y_total"], q=nbins, duplicates="drop").astype(str)
            else:
                pair["X_cat"] = pd.cut(pair["X_total"], bins=nbins, duplicates="drop").astype(str)
                pair["Y_cat"] = pd.cut(pair["Y_total"], bins=nbins, duplicates="drop").astype(str)
            ct = pd.crosstab(pair["X_cat"], pair["Y_cat"])
            st.subheader("Contingency table" if st.session_state.lang == "en" else "Tabel Kontingensi")
            st.dataframe(ct)
            try:
                chi2, p_val, dof, exp = stats.chi2_contingency(ct)
                st.write(("Chi-square:", "p-value:"))
                st.write(round(chi2,4), round(p_val,4))
                interp = ("Dependent (reject H0)" if p_val < 0.05 else "Independent (fail to reject H0)")
                st.write(("Interpretation:", interp))
            except Exception as e:
                st.error(f"Chi-square error: {e}")
        else:
            try:
                if method_used == "pearson":
                    r, pval = stats.pearsonr(pair["X_total"], pair["Y_total"])
                    label = "Pearson r"
                else:
                    r, pval = stats.spearmanr(pair["X_total"], pair["Y_total"])
                    label = "Spearman rho"
            except Exception as e:
                st.error(f"Correlation error: {e}")
                r, pval, label = np.nan, np.nan, "Error"

            # Show result card
            st.markdown('<div class="glass-card" style="width:48%;">', unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;margin-bottom:6px;'>{label}</div>", unsafe_allow_html=True)
            try:
                st.markdown(f"<div style='font-size:18px;font-weight:700;color:#16224a;'>{r:.4f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:6px'>p-value: {pval:.4f}</div>", unsafe_allow_html=True)
            except Exception:
                st.write("Result: ", r, pval)
            abs_r = abs(r) if not np.isnan(r) else 0
            if abs_r < 0.1:
                strength = ("negligible" if st.session_state.lang == "en" else "sangat lemah")
            elif abs_r < 0.3:
                strength = ("weak" if st.session_state.lang == "en" else "lemah")
            elif abs_r < 0.5:
                strength = ("moderate" if st.session_state.lang == "en" else "sedang")
            elif abs_r < 0.7:
                strength = ("strong" if st.session_state.lang == "en" else "kuat")
            else:
                strength = ("very strong" if st.session_state.lang == "en" else "sangat kuat")
            direction = ("positive" if r > 0 else "negative") if not np.isnan(r) else ""
            st.markdown(f"<div style='margin-top:8px'><b>{'Interpretation' if st.session_state.lang == 'en' else 'Interpretasi'}:</b> {direction}, {strength}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # scatter with regression line (visual)
            fig, ax = plt.subplots(figsize=(6,4))
            ax.scatter(pair["X_total"], pair["Y_total"], alpha=0.75)
            try:
                slope, intercept, _, _, _ = stats.linregress(pair["X_total"], pair["Y_total"])
                xs = np.array([pair["X_total"].min(), pair["X_total"].max()])
                ax.plot(xs, slope * xs + intercept, color="red", linestyle="--")
            except Exception:
                pass
            ax.set_xlabel("X_total", fontname="Times New Roman")
            ax.set_ylabel("Y_total", fontname="Times New Roman")
            ax.set_title("Scatter X_total vs Y_total", fontname="Times New Roman")
            st.pyplot(fig)
            plt.close(fig)

# ---------- PDF export ----------
st.header("Export report / Ekspor laporan")
if st.button("Generate PDF report / Buat laporan PDF"):
    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        # Title page
        fig = plt.figure(figsize=(8.27, 11.69)); plt.axis("off")
        plt.text(0.5, 0.85, TEXT["title"][st.session_state.lang], ha="center", va="center", fontsize=18, fontname="Times New Roman", weight="bold")
        plt.text(0.5, 0.80, TEXT["subtitle"][st.session_state.lang], ha="center", va="center", fontsize=10, fontname="Times New Roman")
        plt.text(0.1, 0.75, f"{TEXT['group_members'][st.session_state.lang]}: " + ", ".join([m.split(" — ")[0] for m in GROUP_INFO]), fontsize=9, fontname="Times New Roman")
        pdf.savefig(fig); plt.close(fig)

        # Descriptive summary
        fig = plt.figure(figsize=(8.27, 11.69)); plt.axis("off")
        y_pos = 0.95
        plt.text(0.01, y_pos, ("Descriptive statistics summary:" if st.session_state.lang == "en" else "Ringkasan statistik deskriptif:"), fontsize=12, fontname="Times New Roman", weight="bold")
        y_pos -= 0.03
        items = items_to_describe.copy()
        if compute_composites:
            items += [c for c in ["X_total", "Y_total"] if c in df_work.columns]
        for col in items:
            if y_pos < 0.05:
                pdf.savefig(fig); plt.close(fig); fig = plt.figure(figsize=(8.27, 11.69)); plt.axis("off"); y_pos = 0.95
            try:
                s = pd.to_numeric(df_work[col], errors="coerce")
                txt = f"{col} — mean: {s.mean():.3f}, median: {s.median():.3f}, std: {s.std():.3f}, n: {int(s.count())}"
            except Exception:
                txt = f"{col} — (could not compute numeric summary)"
            plt.text(0.01, y_pos, txt, fontsize=10, fontname="Times New Roman")
            y_pos -= 0.03
        pdf.savefig(fig); plt.close(fig)

        # Association summary + scatter image
        if has_X_total and has_Y_total and len(df_work[["X_total","Y_total"]].dropna()) >= 3:
            pair2 = df_work[["X_total","Y_total"]].dropna()
            fig = plt.figure(figsize=(8.27, 11.69)); plt.axis("off")
            plt.text(0.01, 0.95, ("Association Analysis" if st.session_state.lang == "en" else "Analisis Asosiasi"), fontsize=12, fontname="Times New Roman", weight="bold")
            y_pos = 0.9
            try:
                if method_used == "chi2":
                    txt = ("Chi-square test performed on categorized totals." if st.session_state.lang == "en" else "Uji Chi-square dilakukan pada total yang dikategorikan.")
                    plt.text(0.01, y_pos, txt, fontsize=10, fontname="Times New Roman"); y_pos -= 0.03
                    try:
                        plt.text(0.01, y_pos, f"Chi2 = {chi2:.4f}, p = {p_val:.4f}", fontsize=10, fontname="Times New Roman"); y_pos -= 0.03
                    except:
                        pass
                    pdf.savefig(fig); plt.close(fig)
                else:
                    try:
                        txt = f"{label} = {r:.4f}, p = {pval:.4f}"
                    except:
                        txt = f"Correlation: could not compute"
                    plt.text(0.01, y_pos, txt, fontsize=10, fontname="Times New Roman"); y_pos -= 0.03
                    plt.text(0.01, y_pos, ("Interpretation:" if st.session_state.lang == "en" else "Interpretasi:") + f" {direction}, {strength}", fontsize=10, fontname="Times New Roman"); y_pos -= 0.03
                    pdf.savefig(fig); plt.close(fig)
                    # scatter page
                    fig2, ax2 = plt.subplots(figsize=(8,6))
                    ax2.scatter(pair2["X_total"], pair2["Y_total"], alpha=0.7)
                    try:
                        ax2.plot(xs, slope*xs + intercept, color='red', linestyle='--')
                    except:
                        pass
                    ax2.set_xlabel("X_total", fontname="Times New Roman")
                    ax2.set_ylabel("Y_total", fontname="Times New Roman")
                    ax2.set_title("X_total vs Y_total", fontname="Times New Roman")
                    pdf.savefig(fig2); plt.close(fig2)
            except Exception:
                pass

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="survey_report.pdf">Download PDF report</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.success("PDF ready. Click the link above to download." if st.session_state.lang == "en" else "PDF siap. Klik link di atas untuk mengunduh.")

# ---------- End ----------