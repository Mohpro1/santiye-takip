import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Havence Project Dashboard", layout="wide", page_icon="🏗️")
st.title("🏗️ Havence - Entegre Şantiye İlerleme, Hakediş & Live Timeline Paneli")

# ==========================================
# 2. DATA PERSISTENCE ENGINE (JSON DATABASE)
# ==========================================
DB_FILE = "havence_integrated_data.json"

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
# 3. GLOBAL HELPER FUNCTIONS & REPORT ENGINE
# ==========================================
def calc_schedule_planned_ratio(start_dt, end_dt):
    today = date.today()
    if today < start_dt: return 0.0
    if today >= end_dt: return 1.0
    total_days = (end_dt - start_dt).days
    return ((today - start_dt).days) / total_days if total_days > 0 else 1.0

def get_schedule_badge(planned, actual):
    diff = actual - planned
    if diff < -0.05: return "Gecikme Var (Delayed)", "#d32f2f"
    elif diff > 0.05: return "Programın Önünde (Ahead)", "#388e3c"
    return "Zamanında (On Schedule)", "#1976d2"

def parse_saved_date(key, default_date):
    saved = get_state_val(key, None)
    if saved:
        try: return datetime.fromisoformat(saved).date()
        except: return saved
    return default_date

def display_schedule_metric_row(title, planned, actual):
    diff = actual - planned
    if diff < -0.05: status, color = "🔴 PROGRAMIN GERİSİNDE - DİKKAT!", "red"
    elif diff > 0.05: status, color = "🚀 PROGRAMIN ÖNÜNDE - HARİKA!", "green"
    else: status, color = "🟢 TAM ZAMANINDA İLERLİYOR", "blue"
    
    st.write(f"#### {title}")
    c_p, c_a, c_s = st.columns(3)
    c_p.metric("Planlanan Hedef İlerleme", f"{planned*100:.1f}%")
    c_a.metric("Mevcut Şantiye İlerlemesi", f"{actual*100:.1f}%", delta=f"{diff*100:+.1f}%")
    c_s.markdown(f"<h5 style='color:{color}; padding-top:10px;'>{status}</h5>", unsafe_allow_html=True)
    st.markdown("---")

def make_report_wrapper(title, content_html):
    today_str = date.today().strftime('%d.%m.%Y')
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #0d47a1; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #0d47a1; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #0d47a1; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .grid {{ display: flex; gap: 15px; margin-bottom: 25px; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 11px; font-weight: bold; color: #777; text-transform: uppercase; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #111; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #dddddd; padding: 10px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total {{ font-weight: bold; background-color: #e3f2fd !important; }}
            .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ RAPORU PDF OLARAK KAYDET / YAZDIR</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">Rapor Tarihi: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# ==========================================
# 4. SIDEBAR - FINANCIAL SYSTEM SETTINGS
# ==========================================
st.sidebar.header("💵 Birim Fiyat Ayarları (Birim: ₺/m²)")

st.sidebar.subheader("Dış Cephe İşleri (Facades)")
pm_cephe_price = st.sidebar.number_input("Mülk Sahibi Fiyatı (Cephe)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_in")
update_state_val("pm_cephe_price", pm_cephe_price)
tech_cephe_price = st.sidebar.number_input("Labor Cost Per Meter (Cephe)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_in")
update_state_val("tech_cephe_price", tech_cephe_price)

st.sidebar.subheader("Su Yalıtımı / Islak Hacim (Bathrooms)")
pm_banyo_price = st.sidebar.number_input("Mülk Sahibi Fiyatı (Banyo)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_in")
update_state_val("pm_banyo_price", pm_banyo_price)
tech_banyo_price = st.sidebar.number_input("Labor Cost Per Meter (Banyo)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_in")
update_state_val("tech_banyo_price", tech_banyo_price)

st.sidebar.subheader("İç Cephe İnce İşleri (Interior Finishing)")
pm_interior_price = st.sidebar.number_input("Mülk Sahibi Fiyatı (İç Cephe)", value=get_state_val("pm_interior_price", 450.0), step=10.0, key="pm_int_in")
update_state_val("pm_interior_price", pm_interior_price)
tech_interior_price = st.sidebar.number_input("Labor Cost Per Meter (İç Cephe)", value=get_state_val("tech_interior_price", 300.0), step=10.0, key="tech_int_in")
update_state_val("tech_interior_price", tech_interior_price)

# Doğrusal İlerleme Ağırlıkları (Progress Weights)
weights_cephe = {"Astar": 0.05, "Sıva": 0.15, "Mantolama": 0.25, "Fileli Sıva": 0.20, "Dekoratif": 0.20, "Boya": 0.15}
weights_interior = {"Ano": 0.15, "Alci": 0.40, "Saten": 0.25, "Boya": 0.20}

# ==========================================
# 5. MATHEMATICAL METRIC COMPILATION (INTEGRATED DATA)
# ==========================================

# --- 5.1 Arka Cephe Hesaplamaları ---
arka_sections = {"Ana Cephe (Arka Surface)": 104.4, "Yan Cephe 1": 136.5, "Yan Cephe 2": 83.0, "Yan Cephe 3": 33.0}
arka_progresses = {}
for idx, (section, area) in enumerate(arka_sections.items()):
    ast = get_state_val(f"arka_ast_{idx}", False)
    siv = get_state_val(f"arka_siv_{idx}", False)
    man = get_state_val(f"arka_man_{idx}", False)
    fil = get_state_val(f"arka_fil_{idx}", False)
    dek = get_state_val(f"arka_dek_{idx}", False)
    boy = get_state_val(f"arka_boy_{idx}", False)
    arka_progresses[section] = ((weights_cephe["Astar"] if ast else 0) + (weights_cephe["Sıva"] if siv else 0) + (weights_cephe["Mantolama"] if man else 0) + (weights_cephe["Fileli Sıva"] if fil else 0) + (weights_cephe["Dekoratif"] if dek else 0) + (weights_cephe["Boya"] if boy else 0))

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- 5.2 Ön Cephe Hesaplamaları ---
on_sections = {"Ana Cephe (Ön Surface)": 80.0, "Yan Cephe 1": 68.25, "Yan Cephe 2": 41.5}
on_progresses = {}
for idx, (section, area) in enumerate(on_sections.items()):
    ast = get_state_val(f"on_ast_{idx}", False)
    siv = get_state_val(f"on_siv_{idx}", False)
    man = get_state_val(f"on_man_{idx}", False)
    fil = get_state_val(f"on_fil_{idx}", False)
    dek = get_state_val(f"on_dek_{idx}", False)
    boy = get_state_val(f"on_boy_{idx}", False)
    on_progresses[section] = ((weights_cephe["Astar"] if ast else 0) + (weights_cephe["Sıva"] if siv else 0) + (weights_cephe["Mantolama"] if man else 0) + (weights_cephe["Fileli Sıva"] if fil else 0) + (weights_cephe["Dekoratif"] if dek else 0) + (weights_cephe["Boya"] if boy else 0))

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- 5.3 Banyo İzolasyon Hesaplamaları (Sıvamatik / Su Yalıtımı) ---
floors_banyo_data = [
    {"floor": "-1. Bodrum Katı", "b1_area": 34.35, "b1_status": "Pending", "b2_area": 0.0, "b2_status": "Exempt"},
    {"floor": "Giriş Kat (Zemin)", "b1_area": 34.35, "b1_status": "Pending", "b2_area": 15.68, "b2_status": "Completed"},
    {"floor": "1. Normal Kat", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "2. Normal Kat", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "3. Normal Kat", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "Çatı Katı (Dubleks)", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.0, "b2_status": "Pending"},
]
banyo_total_area = 0
banyo_completed_area = 0
for idx, f in enumerate(floors_banyo_data):
    b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
    b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
    if f["b1_area"] > 0 and b1_s != "Exempt":
        banyo_total_area += f["b1_area"]
        if b1_s == "Completed": banyo_completed_area += f["b1_area"]
    if f["b2_area"] > 0 and b2_s != "Exempt":
        banyo_total_area += f["b2_area"]
        if b2_s == "Completed": banyo_completed_area += f["b2_area"]
banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# --- 5.4 İÇ CEPHE PROJE YAPISI (EXCEL V6 TAM METRAJ) ---
project_interior_structure = {
    "-1. Kat (Bodrum Katı Sektörleri)": {
        "Dükkan -1 (Net Alanı)": 66.71,
        "Bodrum Depoları (İnşai Kısım)": 30.22,
        "Genel Bodrum Koridoru": 50.72,
        "Bodrum İç Merdiveni": 6.96,
        "Arka Daire (-1 Alt Kat Dubleks)": 187.47
    },
    "Giriş Katı (Zemin Evrakları)": {
        "Ana Giriş Holü ve Geçiş Koridoru": 24.32,
        "Ortak Koridor ve Zemin Holü": 50.38,
        "Giriş Kat Merdiveni": 6.96,
        "Zemin Net Dükkan": 24.06,
        "Zemin Arka Daire": 106.56
    },
    "1. Normal Kat": {
        "Ön Daire (1. Kat)": 163.17,
        "Arka Daire (1. Kat)": 106.56,
        "Genel Merdiven ve Koridor (1. Kat)": 50.76
    },
    "2. Normal Kat": {
        "Ön Daire (2. Kat)": 163.17,
        "Arka Daire (2. Kat)": 106.56,
        "Genel Merdiven ve Koridor (2. Kat)": 50.76
    },
    "3. Normal Kat": {
        "Ön Daire (3. Kat)": 163.17,
        "Arka Daire (3. Kat)": 106.56,
        "Genel Merdiven ve Koridor (3. Kat)": 50.76
    },
    "Son Kat (Çatı Katı / Dubleks Üst Ünite)": {
        "Ön Çatı Dairesi": 163.17,
        "Arka Çatı Dairesi": 106.56,
        "Çatı Kat Merdiven ve Holü": 50.76
    }
}

interior_flat_sections = []
interior_total_area = 0
interior_completed_equivalent_area = 0

g_idx = 0
for floor_name, sections in project_interior_structure.items():
    for sec_name, area in sections.items():
        ano = get_state_val(f"int_ano_{g_idx}", False)
        alc = get_state_val(f"int_alc_{g_idx}", False)
        sat = get_state_val(f"int_sat_{g_idx}", False)
        boy = get_state_val(f"int_boy_{g_idx}", False)
        
        sec_progress = ((weights_interior["Ano"] if ano else 0) + 
                        (weights_interior["Alci"] if alc else 0) + 
                        (weights_interior["Saten"] if sat else 0) + 
                        (weights_interior["Boya"] if boy else 0))
        
        comp_area = area * sec_progress
        interior_total_area += area
        interior_completed_equivalent_area += comp_area
        
        interior_flat_sections.append({
            "g_idx": g_idx,
            "floor": floor_name,
            "section": sec_name,
            "area": area,
            "progress": sec_progress,
            "comp_area": comp_area,
            "ano": ano, "alc": alc, "sat": sat, "boy": boy
        })
        g_idx += 1
interior_net_percentage = interior_completed_equivalent_area / interior_total_area if interior_total_area > 0 else 0

# --- 5.5 Kümülatif Finansal Matris Hesaplaması (Cumulative Financial Ledger) ---
arka_rev = arka_completed_area * pm_cephe_price
on_rev = on_completed_area * pm_cephe_price
banyo_rev = banyo_completed_area * pm_banyo_price
interior_rev = interior_completed_equivalent_area * pm_interior_price
total_rev = arka_rev + on_rev + banyo_rev + interior_rev

arka_cst = arka_completed_area * tech_cephe_price
on_cst = on_completed_area * tech_cephe_price
banyo_cst = banyo_completed_area * tech_banyo_price
interior_cst = interior_completed_equivalent_area * tech_interior_price
total_cst = arka_cst + on_cst + banyo_cst + interior_cst
total_prf = total_rev - total_cst

# --- 5.6 Canlı Zaman Çizelgesi Günlüğü (Live Timeline Compilation) ---
timeline_events = []
for idx, (section, _) in enumerate(arka_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_arka_{phase}_{idx}", "")
        if d: timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölge / Kat": section, "Aşama": {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"Fileli Sıva","dek":"Dekoratif Kaplama","boy":"Final Boya"}[phase]})
for idx, (section, _) in enumerate(on_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_on_{phase}_{idx}", "")
        if d: timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölge / Kat": section, "Aşama": {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"Fileli Sıva","dek":"Dekoratif Kaplama","boy":"Final Boya"}[phase]})
for idx, f in enumerate(floors_banyo_data):
    d1 = get_state_val(f"date_b1_{idx}", "")
    if d1: timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyo İzolasyonu", "Bölge / Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
    d2 = get_state_val(f"date_b2_{idx}", "")
    if d2: timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyo İzolasyonu", "Bölge / Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})
for item in interior_flat_sections:
    g_id = item["g_idx"]
    for phase, name in [("ano", "Ano (Böj)"), ("alc", "Alçı Makinası"), ("sat", "Saten Macun"), ("boy", "Son Kat Boya")]:
        d = get_state_val(f"date_int_{phase}_{g_id}", "")
        if d: timeline_events.append({"Tarih": d, "İş Kalemi": "İç Cephe İnce İşler", "Bölge / Kat": f"{item['floor']} - {item['section']}", "Aşama": name})

# ==========================================
# 6. APPLICATION NAVIGATION INTERFACE (TABS)
# ==========================================
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo, tab_interior = st.tabs([
    "💰 FİNANSAL ÖZET & HAKEDİŞ", "⏱️ CANLI ŞANTİYE GÜNLÜĞÜ", "📅 HEDEF ZAMAN ÇİZGELGESİ",
    "🧱 Arka Cephe Takibi", "🏢 Ön Cephe Takibi", "💧 Banyo İzolasyonu", "🏠 İç Cephe İnce İşleri"
])

# --- TAB 1: MONEY SUMMARY ---
with tab_money:
    st.header("💵 Mevcut Proje Mali Durum Raporu")
    
    money_html = f"""
    <div class="grid">
        <div class="card"><div class="card-lbl">Mülk Sahibine Kesilen Toplam Hakediş</div><div class="card-val">₺ {total_rev:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Ustalara / Taşeronlara Ödenen Toplam</div><div class="card-val">₺ {total_cst:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Havence Net Kar</div><div class="card-val">₺ {total_prf:,.2f}</div></div>
    </div>
    <table>
        <thead><tr><th>İş Kalemi Açıklaması</th><th>İlerleme %</th><th>Mülk Sahibi Hakedişi</th><th>Usta İşçilik Maliyeti</th><th>Net Kar</th></tr></thead>
        <tbody>
            <tr><td>Arka Cephe İmalatları</td><td>{arka_net_percentage*100:.1f}%</td><td>₺ {arka_rev:,.2f}</td><td>₺ {arka_cst:,.2f}</td><td>₺ {(arka_rev-arka_cst):,.2f}</td></tr>
            <tr><td>Ön Cephe İmalatları</td><td>{on_net_percentage*100:.1f}%</td><td>₺ {on_rev:,.2f}</td><td>₺ {on_cst:,.2f}</td><td>₺ {(on_rev-on_cst):,.2f}</td></tr>
            <tr><td>Banyolar Sıvamatik İzolasyonu</td><td>{banyo_net_percentage*100:.1f}%</td><td>₺ {banyo_rev:,.2f}</td><td>₺ {banyo_cst:,.2f}</td><td>₺ {(banyo_rev-banyo_cst):,.2f}</td></tr>
            <tr><td>İç Cephe Alçı, Saten, Boya İşleri</td><td>{interior_net_percentage*100:.1f}%</td><td>₺ {interior_rev:,.2f}</td><td>₺ {interior_cst:,.2f}</td><td>₺ {(interior_rev-interior_cst):,.2f}</td></tr>
            <tr class="total"><td>TOPLAM ENTEGRE HAKEDİŞ</td><td>-</td><td>₺ {total_rev:,.2f}</td><td>₺ {total_cst:,.2f}</td><td>₺ {total_prf:,.2f}</td></tr>
        </tbody>
    </table>
    """
    st.download_button("📱 BU SAYFAYI PDF OLARAK İNDİR (MOBİL UYUMLU)", make_report_wrapper("HAVENCE ENTEGRE FİNANSAL İLERLEME RAPORU", money_html), file_name="havence_finansal_ozet_raporu.html", mime="text/html", key="dl_money")

    m1, m2, m3 = st.columns(3)
    m1.metric("Mülk Sahibinden Alınacak", f"₺ {total_rev:,.2f}")
    m2.metric("Ustalara Ödenecek (Labor Cost)", f"₺ {total_cst:,.2f}")
    m3.metric("Şirket Net Kar Marjı", f"₺ {total_prf:,.2f}")
    
    summary_data = {
        "İş Kalemi Açıklaması": ["Arka Cephe", "Ön Cephe", "Banyo İzolasyonu", "İç Cephe İnce İşler", "TOPLAM"],
        "İlerleme Nispî %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", f"{interior_net_percentage*100:.1f}%", "-"],
        "Mülk Sahibi Hakedişi": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {interior_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Usta İşçilik Maliyeti": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {interior_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Kar Marjı": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {(interior_rev - interior_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

# --- TAB 2: LIVE TIMELINE ---
with tab_timeline:
    st.header("⏱️ Canlı Şantiye İmalat Log Kayıtları")
    
    t_rows = ""
    if timeline_events:
        df_t = pd.DataFrame(timeline_events)
        df_t['dt_obj'] = pd.to_datetime(df_t['Tarih'], format='%d.%m.%Y')
        df_t = df_t.sort_values(by='dt_obj', ascending=False)
        for _, r in df_t.iterrows():
            t_rows += f"<tr><td>{r['Tarih']}</td><td>{r['İş Kalemi']}</td><td>{r['Bölge / Kat']}</td><td>{r['Aşama']}</td></tr>"
    else:
        t_rows = "<tr><td colspan='4' style='text-align:center;'>Henüz tamamlanan imalat adımı kaydedilmedi.</td></tr>"
        
    timeline_html = f"<table><thead><tr><th>Tarih</th><th>İş Kalemi</th><th>Bölge / Kat</th><th>Tamamlanan Aşama</th></tr></thead><tbody>{t_rows}</tbody></table>"
    st.download_button("📱 CANLI ZAMAN ÇİZGELGESİ RAPORUNU İNDİR", make_report_wrapper("ŞANTİYE CANLI İMALAT LOG RAPORU", timeline_html), file_name="santiye_canli_log_raporu.html", mime="text/html", key="dl_time")

    if timeline_events:
        st.dataframe(df_t.drop(columns=['dt_obj']), use_container_width=True)
    else:
        st.info("Kayıtlı imalat aşaması bulunmuyor.")

# --- TAB 3: SCHEDULE METRICS ---
with tab_schedule:
    st.header("📅 Proje Hedeflenen Kilometre Taşları Planlaması")
    today = date.today()

    col_item, col_start, col_end = st.columns(3)
    with col_item:
        st.write("##### İş Kalemi Başlığı")
        st.write("<br><p style='padding:11px 0;'><b>Arka Cephe Mantolama & Boya</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Ön Cephe Mantolama & Boya</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Banyolar Su Yalıtım İzolasyon</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>İç Cephe Komple İnce İşleri</b></p>", unsafe_allow_html=True)
    with col_start:
        st.write("##### Planlanan Başlangıç Tarihi")
        arka_start = st.date_input("Arka Başlangıç", value=parse_saved_date("arka_start_dt", today), key="arka_s_in", label_visibility="collapsed")
        on_start = st.date_input("Ön Başlangıç", value=parse_saved_date("on_start_dt", today), key="on_s_in", label_visibility="collapsed")
        banyo_start = st.date_input("Banyo Başlangıç", value=parse_saved_date("banyo_start_dt", today), key="banyo_s_in", label_visibility="collapsed")
        interior_start = st.date_input("İç Cephe Başlangıç", value=parse_saved_date("interior_start_dt", today), key="interior_s_in", label_visibility="collapsed")
    with col_end:
        st.write("##### Planlanan Hedef Bitiş Tarihi")
        arka_end = st.date_input("Arka Bitiş", value=parse_saved_date("arka_end_dt", today), key="arka_e_in", label_visibility="collapsed")
        on_end = st.date_input("Ön Bitiş", value=parse_saved_date("on_end_dt", today), key="on_e_in", label_visibility="collapsed")
        banyo_end = st.date_input("Banyo Bitiş",
