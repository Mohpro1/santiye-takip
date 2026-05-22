import streamlit as st
import pandas as pd

# Set up page layout
st.set_page_config(page_title="Şantiye İlerleme ve Hakediş Paneli", layout="wide", page_icon="🏗️")

st.title("🏗️ Şantiye Hakediş ve İlerleme Gösterge Paneli")
st.markdown("Bu panel, şantiye imalat ilerlemelerini güncelleyerek hakedişleri ve teknisyen kâr paylarını anlık hesaplar.")

# ==========================================
# SIDEBAR - FINANCIAL PRICE SETTINGS
# ==========================================
st.sidebar.header("💵 Birim Fiyat Ayarları")
st.sidebar.markdown("Proje Müdürü ve Teknisyen birim fiyatlarını buradan güncelleyebilirsiniz:")

st.sidebar.subheader("1. Arka & Ön Cephe İmalatları")
pm_cephe_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=500.0, step=10.0, key="pm_cephe")
tech_cephe_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=350.0, step=10.0, key="tech_cephe")

st.sidebar.subheader("2. Banyolar Suwmatik Yalıtımı")
pm_banyo_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=190.0, step=5.0, key="pm_banyo")
tech_banyo_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=130.0, step=5.0, key="tech_banyo")

# Task Weights for Facade works
weights = {
    "Astar": 0.05,
    "Anove Sıva (Kaba)": 0.15,
    "Mantolama": 0.25,
    "File ve Astar": 0.20,
    "Dekoratif Sıva": 0.20,
    "Boya": 0.15
}

# ==========================================
# MAIN TABS FOR WORK ITEMS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🧱 Arka Cephe Takibi", "🏢 Ön Cephe Takibi", "💧 Banyo Yalıtım Takibi"])

# --- TAB 1: ARKA CEPHE ---
with tab1:
    st.header("Arka Cephe Detaylı İmalat Takibi")
    
    # Sections data from your excel
    arka_sections = {
        "Ana Yüzey (Yüz)": 104.4,
        "Yan Cephe 1 (Cenip 1)": 136.5,
        "Yan Cephe 2 (Cenip 2)": 83.0,
        "Yan Cephe 3 (Cenip 3)": 33.0
    }
    
    arka_progresses = {}
    col1, col2 = st.columns(2)
    
    for idx, (section, area) in enumerate(arka_sections.items()):
        # Split into two columns for beautiful layout
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            # Pre-populate based on Excel values (65% completed tasks)
            astar = st.checkbox("Astar (%5)", value=True, key=f"arka_astar_{idx}")
            siva = st.checkbox("Anove Sıva (%15)", value=True, key=f"arka_siva_{idx}")
            manto = st.checkbox("Mantolama (%25)", value=True, key=f"arka_manto_{idx}")
            file_ast = st.checkbox("File ve Astar (%20)", value=True, key=f"arka_file_{idx}")
            dekor = st.checkbox("Dekoratif Sıva (%20)", value=False, key=f"arka_dekor_{idx}")
            boya = st.checkbox("Boya (%15)", value=False, key=f"arka_boya_{idx}")
            
            # Compute section net progress percentage
            sec_progress = (
                (weights["Astar"] if astar else 0) +
                (weights["Anove Sıva (Kaba)"] if siva else 0) +
                (weights["Mantolama"] if manto else 0) +
                (weights["File ve Astar"] if file_ast else 0) +
                (weights["Dekoratif Sıva"] if dekor else 0) +
                (weights["Boya"] if boya else 0)
            )
            arka_progresses[section] = sec_progress
            st.metric(label="Bölüm Net İlerlemesi", value=f"{sec_progress*100:.1f}%")
            st.markdown("---")

    # Overall calculation for Arka Cephe
    arka_total_area = sum(arka_sections.values())
    arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
    arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- TAB 2: ÖN CEPHE ---
with tab2:
    st.header("Ön Cephe Detaylı İmalat Takibi")
    
    on_sections = {
        "Ana Yüzey (Yüz)": 80.0,
        "Yan Cephe 1": 68.25,
        "Yan Cephe 2": 41.5
    }
    
    on_progresses = {}
    col1, col2 = st.columns(2)
    
    for idx, (section, area) in enumerate(on_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            # Pre-populate based on Excel values (0% default)
            astar = st.checkbox("Astar (%5)", value=False, key=f"on_astar_{idx}")
            siva = st.checkbox("Anove Sıva (%15)", value=False, key=f"on_siva_{idx}")
            manto = st.checkbox("Mantolama (%25)", value=False, key=f"on_manto_{idx}")
            file_ast = st.checkbox("File ve Astar (%20)", value=False, key=f"on_file_{idx}")
            dekor = st.checkbox("Dekoratif Sıva (%20)", value=False, key=f"on_dekor_{idx}")
            boya = st.checkbox("Boya (%15)", value=False, key=f"on_boya_{idx}")
            
            sec_progress = (
                (weights["Astar"] if astar else 0) +
                (weights["Anove Sıva (Kaba)"] if siva else 0) +
                (weights["Mantolama"] if manto else 0) +
                (weights["File ve Astar"] if file_ast else 0) +
                (weights["Dekoratif Sıva"] if dekor else 0) +
                (weights["Boya"] if boya else 0)
            )
            on_progresses[section] = sec_progress
            st.metric(label="Bölüm Net İlerlemesi", value=f"{sec_progress*100:.1f}%")
            st.markdown("---")
            
    on_total_area = sum(on_sections.values())
    on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
    on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- TAB 3: BANYOLAR WATERPROOFING ---
with tab3:
    st.header("Banyolar Suwmatik Yalıtım Takibi")
    
    # Floor layout data from Excel
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
    
    st.markdown("Her katın banyo imalat durumunu seçerek ilerlemeyi güncelleyin:")
    
    for idx, f in enumerate(floors_data):
        st.subheader(f["floor"])
        c1, c2 = st.columns(2)
        
        with c1:
            if f["b1_area"] > 0:
                status_1 = st.selectbox(f"Banyo 1 ({f['b1_area']} m²) Durumu", ["Bekliyor", "Tamamlandı", "Muaf"], index=["Bekliyor", "Tamamlandı", "Muaf"].index(f["b1_status"]), key=f"b1_{idx}")
                banyo_total_area += f["b1_area"] if status_1 != "Muaf" else 0
                banyo_completed_area += f["b1_area"] if status_1 == "Tamamlandı" else 0
        
        with c2:
            if f["b2_area"] > 0:
                status_2 = st.selectbox(f"Banyo 2 ({f['b2_area']} m²) Durumu", ["Bekliyor", "Tamamlandı", "Muaf"], index=["Bekliyor", "Tamamlandı", "Muaf"].index(f["b2_status"]), key=f"b2_{idx}")
                banyo_total_area += f["b2_area"] if status_2 != "Muaf" else 0
                banyo_completed_area += f["b2_area"] if status_2 == "Tamamlandı" else 0
        st.markdown("---")
        
    banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0


# ==========================================
# FINANCIAL DASHBOARD SUMMARY (GENEL ÖZET)
# ==========================================
st.markdown("## 📈 Genel Finansal Durum Özet Tablosu")

# Revenue calculations (From Project Manager)
arka_revenue = arka_completed_area * pm_cephe_price
on_revenue = on_completed_area * pm_cephe_price
banyo_revenue = banyo_completed_area * pm_banyo_price
total_revenue = arka_revenue + on_revenue + banyo_revenue

# Cost calculations (To Technician)
arka_cost = arka_completed_area * tech_cephe_price
on_cost = on_completed_area * tech_cephe_price
banyo_cost = banyo_completed_area * tech_banyo_price
total_cost = arka_cost + on_cost + banyo_cost

# Net profit
total_profit = total_revenue - total_cost

# High-level summary metrics
m1, m2, m3 = st.columns(3)
m1.metric(label="💰 Proje Müdüründen Alınacak (Hakediş)", value=f"₺ {total_revenue:,.2f}")
m2.metric(label="🧑‍🔧 Teknisyene Ödenecek Tutar", value=f"₺ {total_cost:,.2f}")
m3.metric(label="✨ Net Kârınız (Profit)", value=f"₺ {total_profit:,.2f}", delta=f"{(total_profit/total_revenue*100 if total_revenue > 0 else 0):.1f}% Kâr Oranı")

# Build data summary frame
summary_data = {
    "İş Kalemi Açıklaması": ["Arka Cephe İmalatları", "Ön Cephe İmalatları", "Banyolar Suwmatik Yalıtımı", "GENEL TOPLAM"],
    "Toplam Metraj (m²)": [f"{arka_total_area:.2f}", f"{on_total_area:.2f}", f"{banyo_total_area:.2f}", f"{(arka_total_area + on_total_area + banyo_total_area):.2f}"],
    "Net İlerleme %": [f"{arka_net_percentage*100:.2f}%", f"{on_net_percentage*100:.2f}%", f"{banyo_net_percentage*100:.2f}%", "-"],
    "Müdürden Alınacak Hakediş": [f"₺ {arka_revenue:,.2f}", f"₺ {on_revenue:,.2f}", f"₺ {banyo_revenue:,.2f}", f"₺ {total_revenue:,.2f}"],
    "Teknisyene Ödenecek": [f"₺ {arka_cost:,.2f}", f"₺ {on_cost:,.2f}", f"₺ {banyo_cost:,.2f}", f"₺ {total_cost:,.2f}"],
    "Net Kârınız": [f"₺ {(arka_revenue - arka_cost):,.2f}", f"₺ {(on_revenue - on_cost):,.2f}", f"₺ {(banyo_revenue - banyo_cost):,.2f}", f"₺ {total_profit:,.2f}"]
}

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True)

# Visual Progress Bars
st.markdown("### 📊 İş İlerleme Çubukları")
st.write("**Arka Cephe İlerlemesi**")
st.progress(arka_net_percentage)
st.write("**Ön Cephe İlerlemesi**")
st.progress(on_net_percentage)
st.write("**Banyolar Yalıtım İlerlemesi**")
st.progress(banyo_net_percentage)