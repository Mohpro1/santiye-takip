import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Set up page layout
st.set_page_config(page_title="Şantiye Takip Paneli", layout="wide", page_icon="🏗️")

# Clean, Robust PDF Printer Injection
def add_print_button():
    st.markdown(
        """
        <style>
        @media print {
            [data-testid="stSidebar"], 
            header, 
            footer, 
            .stActionButton,
            button {
                display: none !important;
            }
            .main .block-container {
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
            }
        }
        </style>
        <button onclick="window.print()" style="
            background-color: #2E7D32; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 20px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1);">
            🖨️ Sayfayı Temiz PDF Olarak Kaydet / Yazdır
        </button>
        """, 
        unsafe_allow_html=True
    )

st.title("🏗️ Şantiye Hakediş, İlerleme ve Canlı Takvim Paneli")

# ==========================================
# DATA PERSISTENCE (SAVE / LOAD SYSTEM)
# ==========================================
DB_FILE = "progress_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "saved_state" not in st.session_state:
    st.session_state.saved_state = load_data()

def get_state_val(key, default):
    return st.session_state.saved_state.get(key, default)

def update_state_val(key, val):
    if isinstance(val, (date, datetime)):
        val = val.isoformat()
    st.session_state.saved_state[key] = val
    save_data(st.session_state.saved_state)

# FIXED: Helper function handles state tracking using the exact checkbox key safely
def handle_checkbox_change(cb_key, save_key, date_key):
    if cb_key in st.session_state:
        current_val = st.session_state[cb_key]
        update_state_val(save_key, current_val)
        
        if current_val: 
            if not get_state_val(date_key, None):
                update_state_val(date_key, date.today().strftime("%d.%m.%Y"))
        else: 
            update_state_val(date_key, "")

# ==========================================
# SIDEBAR - FINANCIAL PRICE SETTINGS
# ==========================================
st.sidebar.header("💵 Birim Fiyat Ayarları")

st.sidebar.subheader("1. Arka & Ön Cephe İmalatları")
pm_cephe_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_input")
update_state_val("pm_cephe_price", pm_cephe_price)

tech_cephe_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_input")
update_state_val("tech_cephe_price", tech_cephe_price)

st.sidebar.subheader("2. Banyolar Suwmatik Yalıtımı")
pm_banyo_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_input")
update_state_val("pm_banyo_price", pm_banyo_price)

tech_banyo_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_input")
update_state_val("tech_banyo_price", tech_banyo_price)

# Task Weights for Facade
weights = {
    "Astar": 0.05, "Anove Sıva (Kaba)": 0.15, "Mantolama": 0.25,
    "File ve Astar": 0.20, "Dekoratif Sıva": 0.20, "Boya": 0.15
}

# App Tabs
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FİNANSAL ÖZET (MONEY)",
    "⏱️ CANLI ŞANTİYE TAKVİMİ (TIMELINE)",
    "📅 HEDEF İŞ PROGRAMI",
    "🧱 Arka Cephe Takibi", 
    "🏢 Ön Cephe Takibi", 
    "💧 Banyo Yalıtım Takibi"
])

# --- COMPUTE ARKA CEPHE PROGRESS ---
arka_sections = {
    "Ana Yüzey (Yüz)": 104.4, "Yan Cephe 1 (Cenip 1)": 136.5,
    "Yan Cephe 2 (Cenip 2)": 83.0, "Yan Cephe 3 (Cenip 3)": 33.0
}
arka_progresses = {}
with tab_arka:
    add_print_button()
    st.header("Arka Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(arka_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            
            ast_val = st.checkbox("Astar (%5)", value=get_state_val(f"arka_ast_{idx}", False), key=f"arka_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_ast_cb_{idx}", f"arka_ast_{idx}", f"date_arka_ast_{idx}"))
            siv_val = st.checkbox("Anove Sıva (%15)", value=get_state_val(f"arka_siv_{idx}", False), key=f"arka_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_siv_cb_{idx}", f"arka_siv_{idx}", f"date_arka_siv_{idx}"))
            man_val = st.checkbox("Mantolama (%25)", value=get_state_val(f"arka_man_{idx}", False), key=f"arka_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_man_cb_{idx}", f"arka_man_{idx}", f"date_arka_man_{idx}"))
            fil_val = st.checkbox("File ve Astar (%20)", value=get_state_val(f"arka_fil_{idx}", False), key=f"arka_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_fil_cb_{idx}", f"arka_fil_{idx}", f"date_arka_fil_{idx}"))
            dek_val = st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"arka_dek_{idx}", False), key=f"arka_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_dek_cb_{idx}", f"arka_dek_{idx}", f"date_arka_dek_{idx}"))
            boy_val = st.checkbox("Boya (%15)", value=get_state_val(f"arka_boy_{idx}", False), key=f"arka_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_boy_cb_{idx}", f"arka_boy_{idx}", f"date_arka_boy_{idx}"))
            
            sec_progress = (
                (weights["Astar"] if ast_val else 0) + (weights["Anove Sıva (Kaba)"] if siv_val else 0) +
                (weights["Mantolama"] if man_val else 0) + (weights["File ve Astar"] if fil_val else 0) +
                (weights["Dekoratif Sıva"] if dek_val else 0) + (weights["Boya"] if boy_val else 0)
            )
            arka_progresses[section] = sec_progress
            st.metric(label="Bölüm Net İlerlemesi", value=f"{sec_progress*100:.1f}%")
            st.markdown("---")

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- COMPUTE ÖN CEPHE PROGRESS ---
on_sections = {"Ana Yüzey (Yüz)": 80.0, "Yan Cephe 1": 68.25, "Yan Cephe 2": 41.5}
on_progresses = {}
with tab_on:
    add_print_button()
    st.header("Ön Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(on_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            ast_val = st.checkbox("Astar (%5)", value=get_state_val(f"on_ast_{idx}", False), key=f"on_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_ast_cb_{idx}", f"on_ast_{idx}", f"date_on_ast_{idx}"))
            siv_val = st.checkbox("Anove Sıva (%15)", value=get_state_val(f"on_siv_{idx}", False), key=f"on_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_siv_cb_{idx}", f"on_siv_{idx}", f"date_on_siv_{idx}"))
            man_val = st.checkbox("Mantolama (%25)", value=get_state_val(f"on_man_{idx}", False), key=f"on_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_man_cb_{idx}", f"on_man_{idx}", f"date_on_man_{idx}"))
            fil_val = st.checkbox("File ve Astar (%20)", value=get_state_val(f"on_fil_{idx}", False), key=f"on_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_fil_cb_{idx}", f"on_fil_{idx}", f"date_on_fil_{idx}"))
            dek_val = st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"on_dek_{idx}", False), key=f"on_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_dek_cb_{idx}", f"on_dek_{idx}", f"date_on_dek_{idx}"))
            boy_val = st.checkbox("Boya (%15)", value=get_state_val(f"on_boy_{idx}", False), key=f"on_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_boy_cb_{idx}", f"on_boy_{idx}", f"date_on_boy_{idx}"))
            
            sec_progress = (
                (weights["Astar"] if ast_val else 0) + (weights["Anove Sıva (Kaba)"] if siv_val else 0) +
                (weights["Mantolama"] if man_val else 0) + (weights["File ve Astar"] if fil_val else 0) +
                (weights["Dekoratif Sıva"] if dek_val else 0) + (weights["Boya"] if boy_val else 0)
            )
            on_progresses[section] = sec_progress
            st.metric(label="Bölüm Net İlerlemesi", value=f"{sec_progress*100:.1f}%")
            st.markdown("---")

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- COMPUTE BANYOLAR PROGRESS ---
floors_data = [
    {"floor": "Bodrum Kat (-1)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 0.0, "b2_status": "Muaf"},
    {"floor": "Giriş Holü (0)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 15.68, "b2_status": "Tamamlandı"},
    {"floor": "1. Kat", "b1_area": 34.35, "b1_status": "Tamamlandı", "b2_area": 20.87, "b2_status": "Tamamlandı"},
    {"floor": "2. Kat", "b1_area": 34.35, "b1_status": "Tamamlandı", "b2_area": 20.87, "b2_status": "Tamamlandı"},
    {"floor": "3. Kat", "b1_area": 34.35, "b1_status": "Tamamlandı", "b2_area": 20.87, "b2_status": "Tamamlandı"},
    {"floor": "Çatı Katı", "b1_area": 34.35, "b1_status": "Tamamlandı", "b2_area": 20.0, "b2_status": "Bekliyor"},
]
banyo_total_area = 0
banyo_completed_area = 0

with tab_banyo:
    add_print_button()
    st.header("Banyolar Suwmatik Su Yalıtımı")
    status_options = ["Bekliyor", "Tamamlandı", "Muaf"]
    
    for idx, f in enumerate(floors_data):
        st.subheader(f["floor"])
        c1, c2 = st.columns(2)
        
        with c1:
            if f["b1_area"] > 0:
                saved_status = get_state_val(f"b1_stat_{idx}", f["b1_status"])
                status_1 = st.selectbox(f"Banyo 1 ({f['b1_area']} m²)", status_options, index=status_options.index(saved_status), key=f"b1_sb_{idx}")
                
                if status_1 != saved_status:
                    update_state_val(f"b1_stat_{idx}", status_1)
                    if status_1 == "Tamamlandı":
                        update_state_val(f"date_b1_{idx}", date.today().strftime("%d.%m.%Y"))
                    else:
                        update_state_val(f"date_b1_{idx}", "")
                        
                banyo_total_area += f["b1_area"] if status_1 != "Muaf" else 0
                banyo_completed_area += f["b1_area"] if status_1 == "Tamamlandı" else 0
        with c2:
            if f["b2_area"] > 0:
                saved_status2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
                status_2 = st.selectbox(f"Banyo 2 ({f['b2_area']} m²)", status_options, index=status_options.index(saved_status2), key=f"b2_sb_{idx}")
                
                if status_2 != saved_status2:
                    update_state_val(f"b2_stat_{idx}", status_2)
                    if status_2 == "Tamamlandı":
                        update_state_val(f"date_b2_{idx}", date.today().strftime("%d.%m.%Y"))
                    else:
                        update_state_val(f"date_b2_{idx}", "")
                        
                banyo_total_area += f["b2_area"] if status_2 != "Muaf" else 0
                banyo_completed_area += f["b2_area"] if status_2 == "Tamamlandı" else 0
        st.markdown("---")

banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# ==========================================
# TAB: AUTOMATED TIMELINE GENERATION
# ==========================================
with tab_timeline:
    add_print_button()
    st.header("⏱️ Canlı Şantiye İmalat Takvimi")
    st.markdown("Checklist kutuları işaretlendikçe tamamlanma tarihleri burada otomatik olarak kronolojik listelenir:")

    timeline_events = []
    
    # Extract Arka Cephe dates
    for idx, (section, _) in enumerate(arka_sections.items()):
        for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
            d = get_state_val(f"date_arka_{phase}_{idx}", "")
            if d:
                lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
                timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölüm / Kat": section, "Aşama": lbl})

    # Extract Ön Cephe dates
    for idx, (section, _) in enumerate(on_sections.items()):
        for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
            d = get_state_val(f"date_on_{phase}_{idx}", "")
            if d:
                lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
                timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölüm / Kat": section, "Aşama": lbl})

    # Extract Banyo dates
    for idx, f in enumerate(floors_data):
        d1 = get_state_val(f"date_b1_{idx}", "")
        if d1:
            timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
        d2 = get_state_val(f"date_b2_{idx}", "")
        if d2:
            timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})

    if timeline_events:
        df_timeline = pd.DataFrame(timeline_events)
        df_timeline['dt_obj'] = pd.to_datetime(df_timeline['Tarih'], format='%d.%m.%Y')
        df_timeline = df_timeline.sort_values(by='dt_obj', ascending=False).drop(columns=['dt_obj'])
        st.dataframe(df_timeline, use_container_width=True)
    else:
        st.info("Henüz tamamlanan bir iş adımı yok. Checkboxları işaretlediğinizde takvim burada belirecektir.")

# ==========================================
# TAB: TARGET SCHEDULE SETTINGS
# ==========================================
with tab_schedule:
    add_print_button()
    st.header("📅 Proje Hedef Zaman Çizelgesi")
    
    today = date.today()
    def parse_saved_date(key, default_date):
        saved = get_state_val(key, None)
        if saved:
            try: return datetime.fromisoformat(saved).date()
            except: return saved
        return default_date

    col_item, col_start, col_end = st.columns(3)
    with col_item:
        st.write("##### İş Kalemi")
        st.write("<br><p style='padding:11px 0;'><b>Arka Cephe İmalatları</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Ön Cephe İmalatları</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Banyolar Yalıtım</b></p>", unsafe_allow_html=True)
    with col_start:
        st.write("##### Başlangıç Tarihi")
        arka_start = st.date_input("Arka Başlangıç", value=parse_saved_date("arka_start_dt", today), key="arka_s_in", label_visibility="collapsed")
        on_start = st.date_input("Ön Başlangıç", value=parse_saved_date("on_start_dt", today), key="on_s_in", label_visibility="collapsed")
        banyo_start = st.date_input("Banyo Başlangıç", value=parse_saved_date("banyo_start_dt", today), key="banyo_s_in", label_visibility="collapsed")
    with col_end:
        st.write("##### Bitiş Tarihi")
        arka_end = st.date_input("Arka Bitiş", value=parse_saved_date("arka_end_dt", today), key="arka_e_in", label_visibility="collapsed")
        on_end = st.date_input("Ön Bitiş", value=parse_saved_date("on_end_dt", today), key="on_e_in", label_visibility="collapsed")
        banyo_end = st.date_input("Banyo Bitiş", value=parse_saved_date("banyo_end_dt", today), key="banyo_e_in", label_visibility="collapsed")

    update_state_val("arka_start_dt", arka_start)
    update_state_val("on_start_dt", on_start)
    update_state_val("banyo_start_dt", banyo_start)
    update_state_val("arka_end_dt", arka_end)
    update_state_val("on_end_dt", on_end)
    update_state_val("banyo_end_dt", banyo_end)

    def calculate_planned_progress(start, end):
        if today < start: return 0.0
        if today >= end: return 1.0
        total_days = (end - start).days
        return ((today - start).days) / total_days if total_days > 0 else 1.0

    planned_arka = calculate_planned_progress(arka_start, arka_end)
    planned_on = calculate_planned_progress(on_start, on_end)
    planned_banyo = calculate_planned_progress(banyo_start, banyo_end)

    st.markdown("### 📊 Planlanan Takvim vs. Gerçekleşen İlerleme Analizi")
    def display_schedule_row(title, planned, actual):
        diff = actual - planned
        if diff < -0.05: status, color = "🔴 PROGRAMIN GERİSİNDE (DELAYED)", "red"
        elif diff > 0.05: status, color = "🚀 PROGRAMIN ÖNÜNDE (AHEAD)", "green"
        else: status, color = "🟢 ZAMANINDA (ON SCHEDULE)", "blue"
            
        st.write(f"#### {title}")
        c_p, c_a, c_s = st.columns(3)
        c_p.metric("Takvime Göre Planlanan", f"{planned*100:.1f}%")
        c_a.metric("Şantiyede Gerçekleşen", f"{actual*100:.1f}%", delta=f"{diff*100:+.1f}%")
        c_s.markdown(f"<h5 style='color:{color}; padding-top:10px;'>{status}</h5>", unsafe_allow_html=True)
        st.markdown("---")

    display_schedule_row("Arka Cephe Planlama", planned_arka, arka_net_percentage)
    display_schedule_row("Ön Cephe Planlama", planned_on, on_net_percentage)
    display_schedule_row("Banyolar Yalıtım Planlama", planned_banyo, banyo_net_percentage)

# ==========================================
# TAB: SEPARATED MONEY DASHBOARD
# ==========================================
with tab_money:
    add_print_button()
    st.header("💵 Güncel Finansal Hakediş Dağılımı")

    arka_rev = arka_completed_area * pm_cephe_price
    on_rev = on_completed_area * pm_cephe_price
    banyo_rev = banyo_completed_area * pm_banyo_price
    total_rev = arka_rev + on_rev + banyo_rev

    arka_cst = arka_completed_area * tech_cephe_price
    on_cst = on_completed_area * tech_cephe_price
    banyo_cst = banyo_completed_area * tech_banyo_price
    total_cst = arka_cst + on_cst + banyo_cst
    total_prf = total_rev - total_cst

    m1, m2, m3 = st.columns(3)
    m1.metric(label="💼 Proje Müdüründen Alınacak (Hakediş)", value=f"₺ {total_rev:,.2f}")
    m2.metric(label="🛠️ Teknisyenlere Ödenecek Toplam", value=f"₺ {total_cst:,.2f}")
    m3.metric(label="📈 Şirket Net Kârı", value=f"₺ {total_prf:,.2f}", delta=f"{(total_prf/total_rev*100 if total_rev > 0 else 0):.1f}% Kâr Oranı")

    st.markdown("### Detaylı Kalem Dağılım Tablosu")
    summary_data = {
        "İş Kalemi Açıklaması": ["Arka Cephe", "Ön Cephe", "Banyolar Yalıtım", "TOPLAM"],
        "İlerleme %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", "-"],
        "Müdür Hakediş": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Teknisyen Ödeme": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Kâr": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
