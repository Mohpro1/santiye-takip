import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Set up page layout
st.set_page_config(page_title="Şantiye Takip Paneli", layout="wide", page_icon="🏗️")

st.title("🏗️ Şantiye Hakediş, İlerleme ve Canlı Takvim Paneli")

# ==========================================
# DATA PERSISTENCE (SAVE / LOAD SYSTEM)
# ==========================================
DB_FILE = "progress_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Veri kaydedilirken hata oluştu: {e}")

if "saved_state" not in st.session_state:
    st.session_state.saved_state = load_data()

def get_state_val(key, default):
    return st.session_state.saved_state.get(key, default)

def update_state_val(key, val):
    st.session_state.saved_state[key] = val
    save_data(st.session_state.saved_state)

# Helper function handles state tracking using the exact checkbox key safely
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
pm_cephe_price = st.sidebar.number_input("PM Cephe Birim Fiyatı (₺/m²)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_input")
update_state_val("pm_cephe_price", pm_cephe_price)

tech_cephe_price = st.sidebar.number_input("Teknisyen Cephe Birim Fiyatı (₺/m²)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_input")
update_state_val("tech_cephe_price", tech_cephe_price)

st.sidebar.subheader("2. Banyolar Suwmatik Yalıtımı")
pm_banyo_price = st.sidebar.number_input("PM Banyo Birim Fiyatı (₺/m²)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_input")
update_state_val("pm_banyo_price", pm_banyo_price)

tech_banyo_price = st.sidebar.number_input("Teknisyen Banyo Birim Fiyatı (₺/m²)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_input")
update_state_val("tech_banyo_price", tech_banyo_price)

# Task Weights for Facade
weights = {
    "Astar": 0.05, 
    "Anove Sıva (Kaba)": 0.15, 
    "Mantolama": 0.25, 
    "File ve Astar": 0.20, 
    "Dekoratif Sıva": 0.20, 
    "Boya": 0.15
}

# ==========================================
# PRE-COMPUTE ALL PROGRESS AND FINANCES
# ==========================================
today_str = date.today().strftime('%d.%m.%Y')

# --- Arka Cephe Calculations ---
arka_sections = {
    "Ana Yüzey (Yüz)": 104.4, 
    "Yan Cephe 1 (Cenip 1)": 136.5, 
    "Yan Cephe 2 (Cenip 2)": 83.0, 
    "Yan Cephe 3 (Cenip 3)": 33.0
}
arka_progresses = {}
for idx, (section, area) in enumerate(arka_sections.items()):
    ast = get_state_val(f"arka_ast_{idx}", False)
    siv = get_state_val(f"arka_siv_{idx}", False)
    man = get_state_val(f"arka_man_{idx}", False)
    fil = get_state_val(f"arka_fil_{idx}", False)
    dek = get_state_val(f"arka_dek_{idx}", False)
    boy = get_state_val(f"arka_boy_{idx}", False)
    
    sec_progress = (
        (weights["Astar"] if ast else 0) + 
        (weights["Anove Sıva (Kaba)"] if siv else 0) + 
        (weights["Mantolama"] if man else 0) + 
        (weights["File ve Astar"] if fil else 0) + 
        (weights["Dekoratif Sıva"] if dek else 0) + 
        (weights["Boya"] if boy else 0)
    )
    arka_progresses[section] = sec_progress

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- Ön Cephe Calculations ---
on_sections = {
    "Ana Yüzey (Yüz)": 80.0, 
    "Yan Cephe 1": 68.25, 
    "Yan Cephe 2": 41.5
}
on_progresses = {}
for idx, (section, area) in enumerate(on_sections.items()):
    ast = get_state_val(f"on_ast_{idx}", False)
    siv = get_state_val(f"on_siv_{idx}", False)
    man = get_state_val(f"on_man_{idx}", False)
    fil = get_state_val(f"on_fil_{idx}", False)
    dek = get_state_val(f"on_dek_{idx}", False)
    boy = get_state_val(f"on_boy_{idx}", False)
    
    sec_progress = (
        (weights["Astar"] if ast else 0) + 
        (weights["Anove Sıva (Kaba)"] if siv else 0) + 
        (weights["Mantolama"] if man else 0) + 
        (weights["File ve Astar"] if fil else 0) + 
        (weights["Dekoratif Sıva"] if dek else 0) + 
        (weights["Boya"] if boy else 0)
    )
    on_progresses[section] = sec_progress

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- Banyolar Calculations ---
floors_data = [
    {"floor": "Bodrum Kat (-1)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 0.0, "b2_status": "Muaf"},
    {"floor": "Giriş Holü (0)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 15.68, "b2_status": "Tamamlandı"},
    {"floor": "1. Kat", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 20.87, "b2_status": "Bekliyor"},
    {"floor": "2. Kat", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 20.87, "b2_status": "Bekliyor"},
    {"floor": "3. Kat", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 20.87, "b2_status": "Bekliyor"},
    {"floor": "Çatı Katı", "b1_area": 25.64, "b1_status": "Bekliyor", "b2_area": 0.0, "b2_status": "Muaf"}
]

banyo_total_area = 0
banyo_completed_area = 0
for idx, f in enumerate(floors_data):
    b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
    b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
    
    if f["b1_area"] > 0 and b1_s != "Muaf":
        banyo_total_area += f["b1_area"]
        if b1_s == "Tamamlandı": 
            banyo_completed_area += f["b1_area"]
            
    if f["b2_area"] > 0 and b2_s != "Muaf":
        banyo_total_area += f["b2_area"]
        if b2_s == "Tamamlandı": 
            banyo_completed_area += f["b2_area"]

banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# --- Financial Totals ---
arka_rev = arka_completed_area * pm_cephe_price
on_rev = on_completed_area * pm_cephe_price
banyo_rev = banyo_completed_area * pm_banyo_price

arka_cst = arka_completed_area * tech_cephe_price
on_cst = on_completed_area * tech_cephe_price
banyo_cst = banyo_completed_area * tech_banyo_price

total_rev = arka_rev + on_rev + banyo_rev
total_cst = arka_cst + on_cst + banyo_cst
total_prf = total_rev - total_cst

# --- Timeline Events Assembly ---
timeline_events = []
for idx, (section, _) in enumerate(arka_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_arka_{phase}_{idx}", "")
        if d: 
            lbl = {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"File+Astar","dek":"Dekoratif","boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölüm/Kat": section, "Aşama": lbl})

for idx, (section, _) in enumerate(on_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_on_{phase}_{idx}", "")
        if d: 
            lbl = {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"File+Astar","dek":"Dekoratif","boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölüm/Kat": section, "Aşama": lbl})

for idx, f in enumerate(floors_data):
    d1 = get_state_val(f"date_b1_{idx}", "")
    if d1: 
        timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyo Yalıtım", "Bölüm/Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
    d2 = get_state_val(f"date_b2_{idx}", "")
    if d2: 
        timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyo Yalıtım", "Bölüm/Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})

# ==========================================
# SMART HTML/PDF STANDALONE REPORT GENERATOR
# ==========================================
def make_report_wrapper(title, content_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title} - {today_str}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #2E7D32; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #2E7D32; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #2E7D32; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .grid {{ display: flex; gap: 15px; margin-bottom: 25px; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 11px; font-weight: bold; color: #777; text-transform: uppercase; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #111; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #dddddd; padding: 10px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ BU SAYFAYI PDF YAP / YAZDIR</button>
        </div>
        <div class="header">
            <div class="title">🏗️ {title}</div>
            <div class="date">Rapor Tarihi: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

def generate_standalone_report():
    timeline_rows = ""
    if timeline_events:
        df_temp = pd.DataFrame(timeline_events)
        df_temp['dt_obj'] = pd.to_datetime(df_temp['Tarih'], format='%d.%m.%Y')
        df_temp = df_temp.sort_values(by='dt_obj', ascending=False)
        for _, r in df_temp.iterrows():
            timeline_rows += f"<tr><td>{r['Tarih']}</td><td>{r['İş Kalemi']}</td><td>{r['Bölüm/Kat']}</td><td>{r['Aşama']}</td></tr>"
    else:
        timeline_rows = "<tr><td colspan='4' style='text-align:center; color:#999;'>Henüz tamamlanan iş adımı yok.</td></tr>"

    main_html = f"""
    <div class="grid">
        <div class="card"><div class="card-lbl">Müdür Hakediş Tutarı</div><div class="card-val">₺ {total_rev:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Teknisyen Toplam Ödeme</div><div class="card-val">₺ {total_cst:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Şirket Net Kârı</div><div class="card-val">₺ {total_prf:,.2f}</div></div>
    </div>
    <h3>📊 Detaylı Finansal Kalem Dağılımı</h3>
    <table>
        <thead>
            <tr>
                <th>İş Kalemi Açıklaması</th>
                <th>İlerleme %</th>
                <th>Müdür Hakediş</th>
                <th>Teknisyen Ödeme</th>
                <th>Net Kâr</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Arka Cephe İmalatları</td><td>{arka_net_percentage*100:.1f}%</td><td>₺ {arka_rev:,.2f}</td><td>₺ {arka_cst:,.2f}</td><td>₺ {(arka_rev-arka_cst):,.2f}</td></tr>
            <tr><td>Ön Cephe İmalatları</td><td>{on_net_percentage*100:.1f}%</td><td>₺ {on_rev:,.2f}</td><td>₺ {on_cst:,.2f}</td><td>₺ {(on_rev-on_cst):,.2f}</td></tr>
            <tr><td>Banyolar Suwmatik Yalıtımı</td><td>{banyo_net_percentage*100:.1f}%</td><td>₺ {banyo_rev:,.2f}</td><td>₺ {banyo_cst:,.2f}</td><td>₺ {(banyo_rev-banyo_cst):,.2f}</td></tr>
            <tr class="total"><td>TOPLAM</td><td>-</td><td>₺ {total_rev:,.2f}</td><td>₺ {total_cst:,.2f}</td><td>₺ {total_prf:,.2f}</td></tr>
        </tbody>
    </table>
    <h3>⏱️ Canlı Kronolojik Şantiye İmalat Takvimi</h3>
    <table>
        <thead>
            <tr>
                <th>Tarih</th>
                <th>İş Kalemi</th>
                <th>Bölüm / Kat</th>
                <th>Tamamlanan Aşama</th>
            </tr>
        </thead>
        <tbody>
            {timeline_rows}
        </tbody>
    </table>
    """
    return make_report_wrapper("ŞANTİYE İLERLEME VE HAKEDİŞ RAPORU", main_html)

# Render Global Action Button at the top
st.markdown("### 📥 Mobil Uyumlu Rapor Çıktısı")
report_html = generate_standalone_report()
st.download_button(
    label="📱 TELEFONA RESMİ PDF / EKRAN GÖRÜNTÜSÜ RAPORU İNDİR",
    data=report_html,
    file_name=f"santiye_resmi_rapor_{date.today().strftime('%d_%m_%Y')}.html",
    mime="text/html",
    use_container_width=True
)

# Uygulama Sekmeleri
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FİNANSAL ÖZET (MONEY)", 
    "⏱️ CANLI ŞANTİYE TAKVİMİ (TIMELINE)", 
    "📅 HEDEF İŞ PROGRAMI",
    "🧱 Arka Cephe Takibi", 
    "🏢 Ön Cephe Takibi", 
    "💧 Banyo Yalıtım Takibi"
])

# --- 1. MONEY TAB ---
with tab_money:
    st.header("💵 Güncel Finansal Hakediş Dağılımı")
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="💼 Proje Müdüründen Alınacak (Hakediş)", value=f"₺ {total_rev:,.2f}")
    m2.metric(label="🛠️ Teknisyenlere Ödenecek Toplam", value=f"₺ {total_cst:,.2f}")
    m3.metric(label="📈 Şirket Net Kârı", value=f"₺ {total_prf:,.2f}", delta=f"{(total_prf/total_rev*100 if total_rev > 0 else 0):.1f}% Kâr Oranı")

    money_html = f"""
    <div class="grid">
        <div class="card"><div class="card-lbl">Müdür Hakediş</div><div class="card-val">₺ {total_rev:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Teknisyen Ödemeleri</div><div class="card-val">₺ {total_cst:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Şirket Net Kârı</div><div class="card-val">₺ {total_prf:,.2f}</div></div>
    </div>
    <table>
        <thead><tr><th>İş Kalemi Açıklaması</th><th>İlerleme %</th><th>Müdür Hakediş</th><th>Teknisyen Ödeme</th><th>Net Kâr</th></tr></thead>
        <tbody>
            <tr><td>Arka Cephe İmalatları</td><td>{arka_net_percentage*100:.1f}%</td><td>₺ {arka_rev:,.2f}</td><td>₺ {arka_cst:,.2f}</td><td>₺ {(arka_rev-arka_cst):,.2f}</td></tr>
            <tr><td>Ön Cephe İmalatları</td><td>{on_net_percentage*100:.1f}%</td><td>₺ {on_rev:,.2f}</td><td>₺ {on_cst:,.2f}</td><td>₺ {(on_rev-on_cst):,.2f}</td></tr>
            <tr><td>Banyolar Suwmatik Yalıtımı</td><td>{banyo_net_percentage*100:.1f}%</td><td>₺ {banyo_rev:,.2f}</td><td>₺ {banyo_cst:,.2f}</td><td>₺ {(banyo_rev-banyo_cst):,.2f}</td></tr>
            <tr class="total"><td>TOPLAM</td><td>-</td><td>₺ {total_rev:,.2f}</td><td>₺ {total_cst:,.2f}</td><td>₺ {total_prf:,.2f}</td></tr>
        </tbody>
    </table>
    """
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("FINANSAL HAKEDIS RAPORU", money_html), file_name="finansal_ozet_rapor.html", mime="text/html", key="dl_money")

    summary_data = {
        "İş Kalemi Açıklaması": ["Arka Cephe", "Ön Cephe", "Banyolar Yalıtım", "TOPLAM"],
        "İlerleme %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", "-"],
        "Müdür Hakediş": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Teknisyen Ödeme": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Kâr": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

# --- 2. TIMELINE TAB ---
with tab_timeline:
    st.header("⏱️ Canlı Şantiye İmalat Takvimi")
    
    t_rows = ""
    if timeline_events:
        df_t = pd.DataFrame(timeline_events)
        df_t['dt_obj'] = pd.to_datetime(df_t['Tarih'], format='%d.%m.%Y')
        df_t = df_t.sort_values(by='dt_obj', ascending=False)
        for _, r in df_t.iterrows():
            t_rows += f"<tr><td>{r['Tarih']}</td><td>{r['İş Kalemi']}</td><td>{r['Bölüm/Kat']}</td><td>{r['Aşama']}</td></tr>"
    else:
        t_rows = "<tr><td colspan='4' style='text-align:center;'>Henüz veri yok.</td></tr>"
        
    timeline_html = f"<table><thead><tr><th>Tarih</th><th>İş Kalemi</th><th>Bölüm / Kat</th><th>Aşama</th></tr></thead><tbody>{t_rows}</tbody></table>"
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("CANLI IMALAT TAKVIMI RAPORU", timeline_html), file_name="canli_takvim_rapor.html", mime="text/html", key="dl_time")

    if timeline_events:
        st.dataframe(df_t.drop(columns=['dt_obj']), use_container_width=True)
    else:
        st.info("Henüz tamamlanan bir iş adımı yok.")

# --- 3. SCHEDULE TAB ---
with tab_schedule:
    st.header("📅 Proje Hedef Zaman Çizelgesi")
    
    col_dt1, col_dt2, col_dt3 = st.columns(3)
    with col_dt1:
        arka_start = st.date_input("Arka Cephe Başlangıç", value=pd.to_datetime(get_state_val("arka_start_dt", "2026-05-01")).date(), key="s_arka_start")
        arka_end = st.date_input("Arka Cephe Bitiş", value=pd.to_datetime(get_state_val("arka_end_dt", "2026-05-20")).date(), key="s_arka_end")
    with col_dt2:
        on_start = st.date_input("Ön Cephe Başlangıç", value=pd.to_datetime(get_state_val("on_start_dt", "2026-05-10")).date(), key="s_on_start")
        on_end = st.date_input("Ön Cephe Bitiş", value=pd.to_datetime(get_state_val("on_end_dt", "2026-05-30")).date(), key="s_on_end")
    with col_dt3:
        banyo_start = st.date_input("Banyolar Başlangıç", value=pd.to_datetime(get_state_val("banyo_start_dt", "2026-05-05")).date(), key="s_banyo_start")
        banyo_end = st.date_input("Banyolar Bitiş", value=pd.to_datetime(get_state_val("banyo_end_dt", "2026-05-25")).date(), key="s_banyo_end")

    update_state_val("arka_start_dt", str(arka_start))
    update_state_val("arka_end_dt", str(arka_end))
    update_state_val("on_start_dt", str(on_start))
    update_state_val("on_end_dt", str(on_end))
    update_state_val("banyo_start_dt", str(banyo_start))
    update_state_val("banyo_end_dt", str(banyo_end))

    today = date.today()
    def calc_p(s, e):
        if today < s: return 0.0
        if today >= e: return 1.0
        tot = (e - s).days
        return ((today - s).days) / tot if tot > 0 else 1.0

    p_arka = calc_p(arka_start, arka_end)
    p_on = calc_p(on_start, on_end)
    p_banyo = calc_p(banyo_start, banyo_end)

    def get_badge(p, a):
        diff = a - p
        if diff < -0.05: return "Geriye Düştü", "#d32f2f"
        elif diff > 0.05: return "Önünde Gidiyor", "#388e3c"
        return "Zamanında", "#1976d2"

    b_arka, c_arka = get_badge(p_arka, arka_net_percentage)
    b_on, c_on = get_badge(p_on, on_net_percentage)
    b_banyo, c_banyo = get_badge(p_banyo, banyo_net_percentage)

    sched_html = f"""
    <table>
        <thead><tr><th>İş Kalemi</th><th>Planlanan İlerleme</th><th>Gerçekleşen İlerleme</th><th>Durum</th></tr></thead>
        <tbody>
            <tr><td>Arka Cephe</td><td>{p_arka*100:.1f}%</td><td>{arka_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_arka}">{b_arka}</span></td></tr>
            <tr><td>Ön Cephe</td><td>{p_on*100:.1f}%</td><td>{on_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_on}">{b_on}</span></td></tr>
            <tr><td>Banyolar Yalıtım</td><td>{p_banyo*100:.1f}%</td><td>{banyo_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_banyo}">{b_banyo}</span></td></tr>
        </tbody>
    </table>
    """
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("HEDEF IS PROGRAMI ANALIZI", sched_html), file_name="hedef_is_programi_rapor.html", mime="text/html", key="dl_sched")

    st.markdown("### 📊 Planlanan Takvim vs. Gerçekleşen İlerleme Analizi")
    def display_schedule_row(title, planned, actual):
        diff = actual - planned
        if diff < -0.05: status, color = "🔴 PROGRAMIN GERİSİNDE", "red"
        elif diff > 0.05: status, color = "🚀 PROGRAMIN ÖNÜNDE", "green"
        else: status, color = "🟢 ZAMANINDA", "blue"
        
        st.write(f"#### {title}")
        c_p, c_a, c_s = st.columns(3)
        c_p.metric("Takvime Göre Planlanan", f"{planned*100:.1f}%")
        c_a.metric("Şantiyede Gerçekleşen", f"{actual*100:.1f}%", delta=f"{diff*100:+.1f}%")
        c_s.markdown(f"<h5 style='color:{color}; padding-top:10px;'>{status}</h5>", unsafe_allow_html=True)
        st.markdown("---")

    display_schedule_row("Arka Cephe", p_arka, arka_net_percentage)
    display_schedule_row("Ön Cephe", p_on, on_net_percentage)
    display_schedule_row("Banyolar Yalıtım", p_banyo, banyo_net_percentage)

# --- 4. ARKA CEPHE TAB ---
with tab_arka:
    st.header("🧱 Arka Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(arka_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            
            st.checkbox("Astar (%5)", value=get_state_val(f"arka_ast_{idx}", False), key=f"arka_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_ast_cb_{idx}", f"arka_ast_{idx}", f"date_arka_ast_{idx}"))
            st.checkbox("Anove Sıva (%15)", value=get_state_val(f"arka_siv_{idx}", False), key=f"arka_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_siv_cb_{idx}", f"arka_siv_{idx}", f"date_arka_siv_{idx}"))
            st.checkbox("Mantolama (%25)", value=get_state_val(f"arka_man_{idx}", False), key=f"arka_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_man_cb_{idx}", f"arka_man_{idx}", f"date_arka_man_{idx}"))
            st.checkbox("File ve Astar (%20)", value=get_state_val(f"arka_fil_{idx}", False), key=f"arka_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_fil_cb_{idx}", f"arka_fil_{idx}", f"date_arka_fil_{idx}"))
            st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"arka_dek_{idx}", False), key=f"arka_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_dek_cb_{idx}", f"arka_dek_{idx}", f"date_arka_dek_{idx}"))
            st.checkbox("Boya (%15)", value=get_state_val(f"arka_boy_{idx}", False), key=f"arka_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_boy_cb_{idx}", f"arka_boy_{idx}", f"date_arka_boy_{idx}"))
            
            st.metric(label="Bölüm Net İlerlemesi", value=f"{arka_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 5. ÖN CEPHE TAB ---
with tab_on:
    st.header("🏢 Ön Cephe İmalat Kademeleri")
    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(on_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            
            st.checkbox("Astar (%5)", value=get_state_val(f"on_ast_{idx}", False), key=f"on_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_ast_cb_{idx}", f"on_ast_{idx}", f"date_on_ast_{idx}"))
            st.checkbox("Anove Sıva (%15)", value=get_state_val(f"on_siv_{idx}", False), key=f"on_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_siv_cb_{idx}", f"on_siv_{idx}", f"date_on_siv_{idx}"))
            st.checkbox("Mantolama (%25)", value=get_state_val(f"on_man_{idx}", False), key=f"on_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_man_cb_{idx}", f"on_man_{idx}", f"date_on_man_{idx}"))
            st.checkbox("File ve Astar (%20)", value=get_state_val(f"on_fil_{idx}", False), key=f"on_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_fil_cb_{idx}", f"on_fil_{idx}", f"date_on_fil_{idx}"))
            st.checkbox("Dekoratif Sıva (%20)", value=get_state_val(f"on_dek_{idx}", False), key=f"on_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_dek_cb_{idx}", f"on_dek_{idx}", f"date_on_dek_{idx}"))
            st.checkbox("Boya (%15)", value=get_state_val(f"on_boy_{idx}", False), key=f"on_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_boy_cb_{idx}", f"on_boy_{idx}", f"date_on_boy_{idx}"))
            
            st.metric(label="Bölüm Net İlerlemesi", value=f"{on_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 6. BANYO YALITIM TAB ---
with tab_banyo:
    st.header("💧 Banyolar Suwmatik Su Yalıtımı")
    status_options_list = ["Bekliyor", "Tamamlandı", "Muaf"]
    
    for idx, f in enumerate(floors_data):
        st.subheader(f["floor"])
        c1, c2 = st.columns(2)
        
        with c1:
            if f["b1_area"] > 0:
                saved_status = get_state_val(f"b1_stat_{idx}", f["b1_status"])
                
                # المعالجة الذكية والآمنة للفهرس لتفادي خطأ الـ ValueError
                safe_index_b1 = status_options_list.index(saved_status) if saved_status in status_options_list else 0
                
                status_1 = st.selectbox(f"Banyo 1 ({f['b1_area']} m²)", status_options_list, index=safe_index_b1, key=f"b1_sb_{idx}")
                
                if status_1 != saved_status:
                    update_state_val(f"b1_stat_{idx}", status_1)
                    if status_1 == "Tamamlandı":
                        update_state_val(f"date_b1_{idx}", date.today().strftime("%d.%m.%Y"))
                    else:
                        update_state_val(f"date_b1_{idx}", "")
                        
        with c2:
            if f["b2_area"] > 0:
                saved_status2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
                
                # المعالجة الذكية والآمنة للفهرس لتفادي خطأ الـ ValueError للحمام الثاني
                safe_index_b2 = status_options_list.index(saved_status2) if saved_status2 in status_options_list else 0
                
                status_2 = st.selectbox(f"Banyo 2 ({f['b2_area']} m²)", status_options_list, index=safe_index_b2, key=f"b2_sb_{idx}")
                
                if status_2 != saved_status2:
                    update_state_val(f"b2_stat_{idx}", status_2)
                    if status_2 == "Tamamlandı":
                        update_state_val(f"date_b2_{idx}", date.today().strftime("%d.%m.%Y"))
                    else:
                        update_state_val(f"date_b2_{idx}", "")
        st.markdown("---")
