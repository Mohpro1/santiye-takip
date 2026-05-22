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
# PRE-COMPUTE ALL PROGRESS AND FINANCES
# ==========================================
# --- Arka Cephe Calculations ---
arka_sections = {
    "Ana Yüzey (Yüz)": 104.4, "Yan Cephe 1 (Cenip 1)": 136.5,
    "Yan Cephe 2 (Cenip 2)": 83.0, "Yan Cephe 3 (Cenip 3)": 33.0
}
arka_progresses = {}
for idx, (section, area) in enumerate(arka_sections.items()):
    ast_val = get_state_val(f"arka_ast_{idx}", False)
    siv_val = get_state_val(f"arka_siv_{idx}", False)
    man_val = get_state_val(f"arka_man_{idx}", False)
    fil_val = get_state_val(f"arka_fil_{idx}", False)
    dek_val = get_state_val(f"arka_dek_{idx}", False)
    boy_val = get_state_val(f"arka_boy_{idx}", False)
    
    sec_progress = (
        (weights["Astar"] if ast_val else 0) + (weights["Anove Sıva (Kaba)"] if siv_val else 0) +
        (weights["Mantolama"] if man_val else 0) + (weights["File ve Astar"] if fil_val else 0) +
        (weights["Dekoratif Sıva"] if dek_val else 0) + (weights["Boya"] if boy_val else 0)
    )
    arka_progresses[section] = sec_progress

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- Ön Cephe Calculations ---
on_sections = {"Ana Yüzey (Yüz)": 80.0, "Yan Cephe 1": 68.25, "Yan Cephe 2": 41.5}
on_progresses = {}
for idx, (section, area) in enumerate(on_sections.items()):
    ast_val = get_state_val(f"on_ast_{idx}", False)
    siv_val = get_state_val(f"on_siv_{idx}", False)
    man_val = get_state_val(f"on_man_{idx}", False)
    fil_val = get_state_val(f"on_fil_{idx}", False)
    dek_val = get_state_val(f"on_dek_{idx}", False)
    boy_val = get_state_val(f"on_boy_{idx}", False)
    
    sec_progress = (
        (weights["Astar"] if ast_val else 0) + (weights["Anove Sıva (Kaba)"] if siv_val else 0) +
        (weights["Mantolama"] if man_val else 0) + (weights["File ve Astar"] if fil_val else 0) +
        (weights["Dekoratif Sıva"] if dek_val else 0) + (weights["Boya"] if boy_val else 0)
    )
    on_progresses[section] = sec_progress

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- Banyolar Calculations ---
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
for idx, f in enumerate(floors_data):
    if f["b1_area"] > 0:
        status_1 = get_state_val(f"b1_stat_{idx}", f["b1_status"])
        banyo_total_area += f["b1_area"] if status_1 != "Muaf" else 0
        banyo_completed_area += f["b1_area"] if status_1 == "Tamamlandı" else 0
    if f["b2_area"] > 0:
        status_2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
        banyo_total_area += f["b2_area"] if status_2 != "Muaf" else 0
        banyo_completed_area += f["b2_area"] if status_2 == "Tamamlandı" else 0

banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# --- Financial Totals ---
arka_rev = arka_completed_area * pm_cephe_price
on_rev = on_completed_area * pm_cephe_price
banyo_rev = banyo_completed_area * pm_banyo_price
total_rev = arka_rev + on_rev + banyo_rev

arka_cst = arka_completed_area * tech_cephe_price
on_cst = on_completed_area * tech_cephe_price
banyo_cst = banyo_completed_area * tech_banyo_price
total_cst = arka_cst + on_cst + banyo_cst
total_prf = total_rev - total_cst

# --- Timeline Events Assembly ---
timeline_events = []
for idx, (section, _) in enumerate(arka_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_arka_{phase}_{idx}", "")
        if d:
            lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölüm / Kat": section, "Aşama": lbl})

for idx, (section, _) in enumerate(on_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_on_{phase}_{idx}", "")
        if d:
            lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölüm / Kat": section, "Aşama": lbl})

for idx, f in enumerate(floors_data):
    d1 = get_state_val(f"date_b1_{idx}", "")
    if d1:
        timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
    d2 = get_state_val(f"date_b2_{idx}", "")
    if d2:
        timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})

# ==========================================
# SMART HTML/PDF STANDALONE REPORT GENERATOR
# ==========================================
def generate_standalone_report():
    today_str = date.today().strftime('%d.%m.%Y')
    
    # Generate Timeline Rows for HTML
    timeline_rows = ""
    if timeline_events:
        df_temp = pd.DataFrame(timeline_events)
        df_temp['dt_obj'] = pd.to_datetime(df_temp['Tarih'], format='%d.%m.%Y')
        df_temp = df_temp.sort_values(by='dt_obj', ascending=False)
        for _, r in df_temp.iterrows():
            timeline_rows += f"<tr><td>{r['Tarih']}</td><td>{r['İş Kalemi']}</td><td>{r['Bölüm / Kat']}</td><td>{r['Aşama']}</td></tr>"
    else:
        timeline_rows = "<tr><td colspan='4' style='text-align:center; color:#999;'>Henüz tamamlanan iş adımı yok.</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Şantiye Hakediş ve İlerleme Raporu - {today_str}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; margin: 30px; line-height: 1.5; }}
            .no-print-zone {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #2E7D32; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
            .header {{ text-align: center; border-bottom: 3px solid #2E7D32; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 26px; font-weight: bold; color: #2E7D32; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .metrics {{ display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 12px; font-weight: bold; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #111; }}
            h3 {{ color: #2E7D32; border-left: 4px solid #2E7D32; padding-left: 10px; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #dddddd; padding: 10px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total-row {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            @media print {{ .no-print-zone {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print-zone">
            <button class="btn" onclick="window.print()">🖨️ PDF OLARAK KAYDET / YAZDIR</button>
            <p style="color:#555; font-size:13px; margin-top:8px;">Açılan sayfada üstteki yeşil butona basarak resmi PDF olarak telefonunuza kaydedebilirsiniz.</p>
        </div>
        
        <div class="header">
            <div class="title">🏗️ ŞANTİYE İLERLEME VE HAKEDİŞ RAPORU</div>
            <div class="date">Rapor Üretim Tarihi: {today_str}</div>
        </div>

        <div class="metrics">
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
                <tr class="total-row"><td>TOPLAM</td><td>-</td><td>₺ {total_rev:,.2f}</td><td>₺ {total_cst:,.2f}</td><td>₺ {total_prf:,.2f}</td></tr>
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
    </body>
    </html>
    """
    return html_content

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

# App Tabs
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FİNANSAL ÖZET (MONEY)",
    "⏱️ CANLI ŞANTİYE TAKVİMİ (TIMELINE)",
    "📅 HEDEF İŞ PROGRAMI",
    "🧱 Arka Cephe Takibi", 
    "🏢 Ön Cephe Takibi", 
    "💧 Banyo Yalıtım Takibi"
])

# --- TAB_ARKA RENDER ---
with tab_arka:
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
            
            st.metric(label="Bölüm Net İlerlemesi", value=f"{arka_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- TAB_ON RENDER ---
with tab_on:
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
            
            st.metric(label="Bölüm Net İlerlemesi", value=f"{on_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- TAB_BANYO RENDER ---
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
                
                if status_1 != saved_status:
                    update_state_val(f"b1_stat_{idx}", status_1)
                    if status_1 == "Tamamlandı":
                        update_state_val(f"date_b1_{idx}", date.today().strftime("%d.%m.%Y"))
                    else:
                        update_state_val(f"date_b1_{idx}", "")
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
        st.markdown("---")

# --- TAB_TIMELINE RENDER ---
with tab_timeline:
    st.header("⏱️ Canlı Şantiye İmalat Takvimi")
    if timeline_events:
        df_timeline = pd.DataFrame(timeline_events)
        df_timeline['dt_obj'] = pd.to_datetime(df_timeline['Tarih'], format='%d.%m.%Y')
        df_timeline = df_timeline.sort_values(by='dt_obj', ascending=False).drop(columns=['dt_obj'])
        st.dataframe(df_timeline, use_container_width=True)
    else:
        st.info("Henüz tamamlanan bir iş adımı yok.")

# --- TAB_SCHEDULE RENDER ---
with tab_schedule:
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

# --- TAB_MONEY RENDER ---
with tab_money:
    st.header("💵 Güncel Finansal Hakediş Dağılımı")
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
