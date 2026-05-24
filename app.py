import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Set up page layout
# Sayfa Yapılandırması
st.set_page_config(page_title="Şantiye Takip Paneli", layout="wide", page_icon="🏗️")

st.title("🏗️ Şantiye Hakediş, İlerleme ve Canlı Takvim Paneli")

# ==========================================
# DATA PERSISTENCE (SAVE / LOAD SYSTEM)
# VERİ SAKLAMA SİSTEMİ (KAYDET / YÜKLE)
# ==========================================
DB_FILE = "progress_data.json"

@@ -36,94 +36,72 @@
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
# YAN MENÜ - BİRİM FİYAT AYARLARI
# ==========================================
st.sidebar.header("💵 Birim Fiyat Ayarları")

st.sidebar.subheader("1. Arka & Ön Cephe İmalatları")
pm_cephe_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_input")
pm_cephe_price = st.sidebar.number_input("PM Cephe Birim Fiyatı (₺/m²)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_input")
update_state_val("pm_cephe_price", pm_cephe_price)

tech_cephe_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_input")
tech_cephe_price = st.sidebar.number_input("Teknisyen Cephe Birim Fiyatı (₺/m²)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_input")
update_state_val("tech_cephe_price", tech_cephe_price)

st.sidebar.subheader("2. Banyolar Suwmatik Yalıtımı")
pm_banyo_price = st.sidebar.number_input("PM Birim Fiyatı (₺/m²)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_input")
pm_banyo_price = st.sidebar.number_input("PM Banyo Birim Fiyatı (₺/m²)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_input")
update_state_val("pm_banyo_price", pm_banyo_price)

tech_banyo_price = st.sidebar.number_input("Teknisyen Birim Fiyatı (₺/m²)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_input")
tech_banyo_price = st.sidebar.number_input("Teknisyen Banyo Birim Fiyatı (₺/m²)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_input")
update_state_val("tech_banyo_price", tech_banyo_price)

# Task Weights for Facade
weights = {
    "Astar": 0.05, "Anove Sıva (Kaba)": 0.15, "Mantolama": 0.25,
    "File ve Astar": 0.20, "Dekoratif Sıva": 0.20, "Boya": 0.15
}
weights = {"Astar": 0.05, "Anove Sıva (Kaba)": 0.15, "Mantolama": 0.25, "File ve Astar": 0.20, "Dekoratif Sıva": 0.20, "Boya": 0.15}

# ==========================================
# PRE-COMPUTE ALL PROGRESS AND FINANCES
# TÜM HESAPLAMALARIN ÖNDEN YAPILMASI
# ==========================================
# --- Arka Cephe Calculations ---
arka_sections = {
    "Ana Yüzey (Yüz)": 104.4, "Yan Cephe 1 (Cenip 1)": 136.5,
    "Yan Cephe 2 (Cenip 2)": 83.0, "Yan Cephe 3 (Cenip 3)": 33.0
}
today_str = date.today().strftime('%d.%m.%Y')

# --- Arka Cephe ---
arka_sections = {"Ana Yüzey (Yüz)": 104.4, "Yan Cephe 1 (Cenip 1)": 136.5, "Yan Cephe 2 (Cenip 2)": 83.0, "Yan Cephe 3 (Cenip 3)": 33.0}
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
    ast = get_state_val(f"arka_ast_{idx}", False)
    siv = get_state_val(f"arka_siv_{idx}", False)
    man = get_state_val(f"arka_man_{idx}", False)
    fil = get_state_val(f"arka_fil_{idx}", False)
    dek = get_state_val(f"arka_dek_{idx}", False)
    boy = get_state_val(f"arka_boy_{idx}", False)
    arka_progresses[section] = ((weights["Astar"] if ast else 0) + (weights["Anove Sıva (Kaba)"] if siv else 0) + (weights["Mantolama"] if man else 0) + (weights["File ve Astar"] if fil else 0) + (weights["Dekoratif Sıva"] if dek else 0) + (weights["Boya"] if boy else 0))

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- Ön Cephe Calculations ---
# --- Ön Cephe ---
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
    ast = get_state_val(f"on_ast_{idx}", False)
    siv = get_state_val(f"on_siv_{idx}", False)
    man = get_state_val(f"on_man_{idx}", False)
    fil = get_state_val(f"on_fil_{idx}", False)
    dek = get_state_val(f"on_dek_{idx}", False)
    boy = get_state_val(f"on_boy_{idx}", False)
    on_progresses[section] = ((weights["Astar"] if ast else 0) + (weights["Anove Sıva (Kaba)"] if siv else 0) + (weights["Mantolama"] if man else 0) + (weights["File ve Astar"] if fil else 0) + (weights["Dekoratif Sıva"] if dek else 0) + (weights["Boya"] if boy else 0))

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- Banyolar Calculations ---
# --- Banyolar ---
floors_data = [
    {"floor": "Bodrum Kat (-1)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 0.0, "b2_status": "Muaf"},
    {"floor": "Giriş Holü (0)", "b1_area": 34.35, "b1_status": "Bekliyor", "b2_area": 15.68, "b2_status": "Tamamlandı"},
@@ -135,18 +113,17 @@
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

    b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
    b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
    if f["b1_area"] > 0 and b1_s != "Muaf":
        banyo_total_area += f["b1_area"]
        if b1_s == "Tamamlandı": banyo_completed_area += f["b1_area"]
    if f["b2_area"] > 0 and b2_s != "Muaf":
        banyo_total_area += f["b2_area"]
        if b2_s == "Tamamlandı": banyo_completed_area += f["b2_area"]
banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# --- Financial Totals ---
# --- Finansallar ---
arka_rev = arka_completed_area * pm_cephe_price
on_rev = on_completed_area * pm_cephe_price
banyo_rev = banyo_completed_area * pm_banyo_price
@@ -158,231 +135,131 @@
total_cst = arka_cst + on_cst + banyo_cst
total_prf = total_rev - total_cst

# --- Timeline Events Assembly ---
# --- Zaman Çizelgesi Verisi ---
timeline_events = []
for idx, (section, _) in enumerate(arka_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_arka_{phase}_{idx}", "")
        if d:
            lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölüm / Kat": section, "Aşama": lbl})

        if d: timeline_events.append({"Tarih": d, "İş Kalemi": "Arka Cephe", "Bölüm/Kat": section, "Aşama": {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"File+Astar","dek":"Dekoratif","boy":"Boya"}[phase]})
for idx, (section, _) in enumerate(on_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_on_{phase}_{idx}", "")
        if d:
            lbl = {"ast":"Astar", "siv":"Anove Sıva", "man":"Mantolama", "fil":"File ve Astar", "dek":"Dekoratif Sıva", "boy":"Boya"}[phase]
            timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölüm / Kat": section, "Aşama": lbl})

        if d: timeline_events.append({"Tarih": d, "İş Kalemi": "Ön Cephe", "Bölüm/Kat": section, "Aşama": {"ast":"Astar","siv":"Sıva","man":"Mantolama","fil":"File+Astar","dek":"Dekoratif","boy":"Boya"}[phase]})
for idx, f in enumerate(floors_data):
    d1 = get_state_val(f"date_b1_{idx}", "")
    if d1:
        timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
    if d1: timeline_events.append({"Tarih": d1, "İş Kalemi": "Banyo Yalıtım", "Bölüm/Kat": f["floor"], "Aşama": "Banyo 1 Tamamlandı"})
    d2 = get_state_val(f"date_b2_{idx}", "")
    if d2:
        timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyolar Yalıtım", "Bölüm / Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})
    if d2: timeline_events.append({"Tarih": d2, "İş Kalemi": "Banyo Yalıtım", "Bölüm/Kat": f["floor"], "Aşama": "Banyo 2 Tamamlandı"})

# ==========================================
# SMART HTML/PDF STANDALONE REPORT GENERATOR
# HTML RAPOR ŞABLON MOTORU
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
def make_report_wrapper(title, content_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Şantiye Hakediş ve İlerleme Raporu - {today_str}</title>
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; margin: 30px; line-height: 1.5; }}
            .no-print-zone {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #2E7D32; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #2E7D32; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #2E7D32; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 26px; font-weight: bold; color: #2E7D32; }}
            .title {{ font-size: 24px; font-weight: bold; color: #2E7D32; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .metrics {{ display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }}
            .grid {{ display: flex; gap: 15px; margin-bottom: 25px; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 12px; font-weight: bold; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #111; }}
            h3 {{ color: #2E7D32; border-left: 4px solid #2E7D32; padding-left: 10px; margin-top: 30px; }}
            .card-lbl {{ font-size: 11px; font-weight: bold; color: #777; text-transform: uppercase; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #111; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #dddddd; padding: 10px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total-row {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            @media print {{ .no-print-zone {{ display: none !important; }} body {{ margin: 10px; }} }}
            .total {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print-zone">
            <button class="btn" onclick="window.print()">🖨️ PDF OLARAK KAYDET / YAZDIR</button>
            <p style="color:#555; font-size:13px; margin-top:8px;">Açılan sayfada üstteki yeşil butona basarak resmi PDF olarak telefonunuza kaydedebilirsiniz.</p>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ BU SAYFAYI PDF YAP / YAZDIR</button>
        </div>
        
        <div class="header">
            <div class="title">🏗️ ŞANTİYE İLERLEME VE HAKEDİŞ RAPORU</div>
            <div class="date">Rapor Üretim Tarihi: {today_str}</div>
        </div>

        <div class="metrics">
            <div class="card"><div class="card-lbl">Müdür Hakediş Tutarı</div><div class="card-val">₺ {total_rev:,.2f}</div></div>
            <div class="card"><div class="card-lbl">Teknisyen Toplam Ödeme</div><div class="card-val">₺ {total_cst:,.2f}</div></div>
            <div class="card"><div class="card-lbl">Şirket Net Kârı</div><div class="card-val">₺ {total_prf:,.2f}</div></div>
            <div class="title">{title}</div>
            <div class="date">Rapor Tarihi: {today_str}</div>
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
        {content_html}
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

# Uygulama Sekmeleri
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FİNANSAL ÖZET (MONEY)",
    "⏱️ CANLI ŞANTİYE TAKVİMİ (TIMELINE)",
    "📅 HEDEF İŞ PROGRAMI",
    "🧱 Arka Cephe Takibi", 
    "🏢 Ön Cephe Takibi", 
    "💧 Banyo Yalıtım Takibi"
    "💰 FİNANSAL ÖZET (MONEY)", "⏱️ CANLI ŞANTİYE TAKVİMİ (TIMELINE)", "📅 HEDEF İŞ PROGRAMI",
    "🧱 Arka Cephe Takibi", "🏢 Ön Cephe Takibi", "💧 Banyo Yalıtım Takibi"
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
# --- 1. MONEY TAB ---
with tab_money:
    st.header("💵 Güncel Finansal Hakediş Dağılımı")
    
    # HTML Raporunu Hazırla
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

# --- TAB_BANYO RENDER ---
with tab_banyo:
    st.header("Banyolar Suwmatik Su Yalıtımı")
    status_options = ["Bekliyor", "Tamamlandı", "Muaf"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Proje Müdüründen Alınacak", f"₺ {total_rev:,.2f}")
    m2.metric("Teknisyenlere Ödenecek", f"₺ {total_cst:,.2f}")
    m3.metric("Şirket Net Kârı", f"₺ {total_prf:,.2f}")

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
    summary_data = {
        "İş Kalemi Açıklaması": ["Arka Cephe", "Ön Cephe", "Banyolar Yalıtım", "TOPLAM"],
        "İlerleme %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", "-"],
        "Müdür Hakediş": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Teknisyen Ödeme": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Kâr": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

# --- TAB_TIMELINE RENDER ---
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
        df_timeline = pd.DataFrame(timeline_events)
        df_timeline['dt_obj'] = pd.to_datetime(df_timeline['Tarih'], format='%d.%m.%Y')
        df_timeline = df_timeline.sort_values(by='dt_obj', ascending=False).drop(columns=['dt_obj'])
        st.dataframe(df_timeline, use_container_width=True)
        st.dataframe(df_t.drop(columns=['dt_obj']), use_container_width=True)
    else:
        st.info("Henüz tamamlanan bir iş adımı yok.")

# --- TAB_SCHEDULE RENDER ---
# --- 3. SCHEDULE TAB ---
with tab_schedule:
    st.header("📅 Proje Hedef Zaman Çizelgesi")
    today = date.today()
@@ -417,48 +294,129 @@
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
    def calc_p(s, e):
        if today < s: return 0.0
        if today >= e: return 1.0
        tot = (e - s).days
        return ((today - s).days) / tot if tot > 0 else 1.0

    p_arka, p_on, p_banyo = calc_p(arka_start, arka_end), calc_p(on_start, on_end), calc_p(banyo_start, banyo_end)

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
        if diff < -0.05: status, color = "🔴 PROGRAMIN GERİSİNDE (DELAYED)", "red"
        elif diff > 0.05: status, color = "🚀 PROGRAMIN ÖNÜNDE (AHEAD)", "green"
        else: status, color = "🟢 ZAMANINDA (ON SCHEDULE)", "blue"
            
        if diff < -0.05: status, color = "🔴 PROGRAMIN GERİSİNDE", "red"
        elif diff > 0.05: status, color = "🚀 PROGRAMIN ÖNÜNDE", "green"
        else: status, color = "🟢 ZAMANINDA", "blue"
        st.write(f"#### {title}")
        c_p, c_a, c_s = st.columns(3)
        c_p.metric("Takvime Göre Planlanan", f"{planned*100:.1f}%")
        c_a.metric("Şantiyede Gerçekleşen", f"{actual*100:.1f}%", delta=f"{diff*100:+.1f}%")
        c_s.markdown(f"<h5 style='color:{color}; padding-top:10px;'>{status}</h5>", unsafe_allow_html=True)
        st.markdown("---")

    display_schedule_row("Arka Cephe Planlama", planned_arka, arka_net_percentage)
    display_schedule_row("Ön Cephe Planlama", planned_on, on_net_percentage)
    display_schedule_row("Banyolar Yalıtım Planlama", planned_banyo, banyo_net_percentage)
    display_schedule_row("Arka Cephe", p_arka, arka_net_percentage)
    display_schedule_row("Ön Cephe", p_on, on_net_percentage)
    display_schedule_row("Banyolar Yalıtım", p_banyo, banyo_net_percentage)

# --- TAB_MONEY RENDER ---
with tab_money:
    st.header("💵 Güncel Finansal Hakediş Dağılımı")
    m1, m2, m3 = st.columns(3)
    m1.metric(label="💼 Proje Müdüründen Alınacak (Hakediş)", value=f"₺ {total_rev:,.2f}")
    m2.metric(label="🛠️ Teknisyenlere Ödenecek Toplam", value=f"₺ {total_cst:,.2f}")
    m3.metric(label="📈 Şirket Net Kârı", value=f"₺ {total_prf:,.2f}", delta=f"{(total_prf/total_rev*100 if total_rev > 0 else 0):.1f}% Kâr Oranı")
# --- 4. ARKA CEPHE TAB ---
with tab_arka:
    st.header("🧱 Arka Cephe İmalat Kademeleri")
    
    arka_html = "<table><thead><tr><th>Bölüm Adı</th><th>Metraj (m²)</th><th>Net İlerleme</th></tr></thead><tbody>"
    for sec, area in arka_sections.items():
        arka_html += f"<tr><td>{sec}</td><td>{area} m²</td><td><b>{arka_progresses[sec]*100:.1f}%</b></td></tr>"
    arka_html += f"<tr class='total'><td>TOPLAM GENEL ORTALAMA</td><td>{arka_total_area} m²</td><td>{arka_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("ARKA CEPHE DETAYLI TAKIP RAPORU", arka_html), file_name="arka_cephe_rapor.html", mime="text/html", key="dl_arka")

    st.markdown("### Detaylı Kalem Dağılım Tablosu")
    summary_data = {
        "İş Kalemi Açıklaması": ["Arka Cephe", "Ön Cephe", "Banyolar Yalıtım", "TOPLAM"],
        "İlerleme %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", "-"],
        "Müdür Hakediş": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Teknisyen Ödeme": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Kâr": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
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
            st.metric("Bölüm İlerlemesi", f"{arka_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 5. ÖN CEPHE TAB ---
with tab_on:
    st.header("🏢 Ön Cephe İmalat Kademeleri")
    
    on_html = "<table><thead><tr><th>Bölüm Adı</th><th>Metraj (m²)</th><th>Net İlerleme</th></tr></thead><tbody>"
    for sec, area in on_sections.items():
        on_html += f"<tr><td>{sec}</td><td>{area} m²</td><td><b>{on_progresses[sec]*100:.1f}%</b></td></tr>"
    on_html += f"<tr class='total'><td>TOPLAM GENEL ORTALAMA</td><td>{on_total_area} m²</td><td>{on_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("ON CEPHE DETAYLI TAKIP RAPORU", on_html), file_name="on_cephe_rapor.html", mime="text/html", key="dl_on")

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
            st.metric("Bölüm İlerlemesi", f"{on_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 6. BANYO TAB ---
with tab_banyo:
    st.header("💧 Banyo Yalıtım Takibi")
    
    banyo_html = "<table><thead><tr><th>Kat Bilgisi</th><th>Banyo 1 Durum</th><th>Banyo 2 Durum</th></tr></thead><tbody>"
    for idx, f in enumerate(floors_data):
        b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
        b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
        banyo_html += f"<tr><td>{f['floor']}</td><td>{b1_s} ({f['b1_area']} m²)</td><td>{b2_s} ({f['b2_area']} m²)</td></tr>"
    banyo_html += f"<tr class='total'><td>NET TAMAMLANMA</td><td colspan='2' style='text-align:center;'>{banyo_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 BU SAYFANIN PDF / EKRAN GÖRÜNTÜSÜNÜ AL", make_report_wrapper("BANYO YALITIM TAKIP RAPORU", banyo_html), file_name="banyo_yalitim_rapor.html", mime="text/html", key="dl_banyo")

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
                    update_state_val(f"date_b1_{idx}", date.today().strftime("%d.%m.%Y") if status_1 == "Tamamlandı" else "")
        with c2:
            if f["b2_area"] > 0:
                saved_status2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
                status_2 = st.selectbox(f"Banyo 2 ({f['b2_area']} m²)", status_options, index=status_options.index(saved_status2), key=f"b2_sb_{idx}")
                if status_2 != saved_status2:
                    update_state_val(f"b2_stat_{idx}", status_2)
                    update_state_val(f"date_b2_{idx}", date.today().strftime("%d.%m.%Y") if status_2 == "Tamamlandı" else "")
        st.markdown("---")
