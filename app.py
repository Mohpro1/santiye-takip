import streamlit as st
import pandas as pd
import json
import os

# Set up page layout
st.set_page_config(page_title="Şantiye Takip Paneli", layout="wide", page_icon="🏗️")

st.title("🏗️ Şantiye Hakediş ve İlerleme Gösterge Paneli")

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

# Initialize session state from file data if it exists
if "saved_state" not in st.session_state:
    st.session_state.saved_state = load_data()

# Helper function to track state changes dynamically
def get_state_val(key, default):
    return st.session_state.saved_state.get(key, default)

def update_state_val(key, val):
    st.session_state.saved_state[key] = val
    save_data(st.session_state.saved_state)

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

# ==========================================
# SEPARATED TABS (MONEY IS NOW SEPARATE)
# ==========================================
tab_money, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FİNANSAL ÖZET (MONEY)", 
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
    st.header("Arka Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(arka_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            
            # Load previous selection or default to true for completed items from original data
            ast_val = st.checkbox("Astar (%5)", value=get_state_val(f"arka_ast_{idx}", True), key=f"arka_ast_cb_{idx}")
            siv_val = st.checkbox("Anove Sıva (%15)", value=get_state_val(f"arka_siv_{idx}", True), key=f"arka_siv_cb_{idx}")
            man_val = st.checkbox("Mantolama (%25)", value=get_state_val(f"arka_man_{idx}", True), key=f"arka_man_cb_{idx}")
            fil_val = st.checkbox("File ve Astar (%20)", value=get_state_val(f"arka_fil_{idx}", True), key=f"arka_fil_cb_{idx}")
            dek_val = st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"arka_dek_{idx}", False), key=f"arka_dek_cb_{idx}")
            boy_val = st.checkbox("Boya (%15)", value=get_state_val(f"arka_boy_{idx}", False), key=f"arka_boy_cb_{idx}")
            
            # Save updates instantly
            update_state_val(f"arka_ast_{idx}", ast_val)
            update_state_val(f"arka_siv_{idx}", siv_val)
            update_state_val(f"arka_man_{idx}", man_val)
            update_state_val(f"arka_fil_{idx}", fil_val)
            update_state_val(f"arka_dek_{idx}", dek_val)
            update_state_val(f"arka_boy_{idx}", boy_val)
            
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
    st.header("Ön Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(on_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            ast_val = st.checkbox("Astar (%5)", value=get_state_val(f"on_ast_{idx}", False), key=f"on_ast_cb_{idx}")
            siv_val = st.checkbox("Anove Sıva (%15)", value=get_state_val(f"on_siv_{idx}", False), key=f"on_siv_cb_{idx}")
            man_val = st.checkbox("Mantolama (%25)", value=get_state_val(f"on_man_{idx}", False), key=f"on_man_cb_{idx}")
            fil_val = st.checkbox("File ve Astar (%20)", value=get_state_val(f"on_fil_{idx}", False), key=f"on_fil_cb_{idx}")
            dek_val = st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"on_dek_{idx}", False), key=f"on_dek_cb_{idx}")
            boy_val = st.checkbox("Boya (%15)", value=get_state_val(f"on_boy_{idx}", False), key=f"on_boy_cb_{idx}")
            
            update_state_val(f"on_ast_{idx}", ast_val)
            update_state_val(f"on_siv_{idx}", siv_val)
            update_state_val(f"on_man_{idx}", man_val)
            update_state_val(f"on_fil_{idx}", fil_val)
            update_state_val(f"on_dek_{idx}", dek_val)
            update_state_val(f"on_boy_{idx}", boy_val)
            
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
    st.header("Banyolar Suwmatik Su Yalıtımı")
    status_options = ["Bekliyor", "Tamamlandı", "Muaf"]
    
    for idx, f in enumerate(floors_data):
        st.subheader(f["floor"])
        c1, c2 = st.columns(2)
        
        with c1:
            if f["b1_area"] > 0:
                saved_status = get_state_val(f"b1_stat_{idx}", f["b1_status"])
                status_1 = st.selectbox(f"Banyo 1 ({f['b1_area']} m²)", status_options, index=status_options.index(saved_status), key=f"b1_sb_{idx}")
                update_state_val(f"b1_stat_{idx}", status_1)
                
                banyo_total_area += f["b1_area"] if status_1 != "Muaf" else 0
                banyo_completed_area += f["b1_area"] if status_1 == "Tamamlandı" else 0
        with c2:
            if f["b2_area"] > 0:
                saved_status2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
                status_2 = st.selectbox(f"Banyo 2 ({f['b2_area']} m²)", status_options, index=status_options.index(saved_status2), key=f"b2_sb_{idx}")
                update_state_val(f"b2_stat_{idx}", status_2)
                
                banyo_total_area += f["b2_area"] if status_2 != "Muaf" else 0
                banyo_completed_area += f["b2_area"] if status_2 == "Tamamlandı" else 0
        st.markdown("---")

banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# ==========================================
# TAB 1 - SEPARATED MONEY DASHBOARD
# ==========================================
with tab_money:
    st.header("💵 Güncel Finansal Hakediş Dağılımı")
    st.markdown("Üretim kademelerine göre güncellenmiş finansal rapor:")

    # Calculations
    arka_rev = arka_completed_area * pm_cephe_price
    on_rev = on_completed_area * pm_cephe_price
    banyo_rev = banyo_completed_area * pm_banyo_price
    total_rev = arka_rev + on_rev + banyo_rev

    arka_cst = arka_completed_area * tech_cephe_price
    on_cst = on_completed_area * tech_cephe_price
    banyo_cst = banyo_completed_area * tech_banyo_price
    total_cst = arka_cst + on_cst + banyo_cst
    total_prf = total_rev - total_cst

    # Key Metrics Display (Perfect for phone layout)
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

    # Simple Visual Indicators
    st.markdown("### 📊 Genel İlerleme Durumları")
    st.write(f"**Arka Cephe Toplam İlerleme ({arka_net_percentage*100:.1f}%)**")
    st.progress(arka_net_percentage)
    st.write(f"**Ön Cephe Toplam İlerleme ({on_net_percentage*100:.1f}%)**")
    st.progress(on_net_percentage)
    st.write(f"**Banyolar Toplam İlerleme ({banyo_net_percentage*100:.1f}%)**")
    st.progress(banyo_net_percentage)
