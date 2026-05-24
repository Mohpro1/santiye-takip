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
pm_cephe_price = st.sidebar.number_input("Mülk Sahibi Fiyatı (Cephe)", value=get_state_val("pm_cephe_price",
