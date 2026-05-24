import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Page configuration
st.set_page_config(page_title="Construction Tracking Dashboard", layout="wide", page_icon="🏗️")

st.title("🏗️ Site Progress, Payment & Live Timeline Dashboard")

# ==========================================
# DATA PERSISTENCE SYSTEM (SAVE / LOAD)
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
# SIDEBAR - UNIT PRICE SETTINGS
# ==========================================
st.sidebar.header("💵 Unit Price Settings")
pm_cephe_price = st.sidebar.number_input("PM Facade Unit Price (₺/m²)", value=get_state_val("pm_cephe_price", 500.0), step=10.0, key="pm_cephe_input")
update_state_val("pm_cephe_price", pm_cephe_price)

tech_cephe_price = st.sidebar.number_input("Technician Facade Unit Price (₺/m²)", value=get_state_val("tech_cephe_price", 350.0), step=10.0, key="tech_cephe_input")
update_state_val("tech_cephe_price", tech_cephe_price)

pm_banyo_price = st.sidebar.number_input("PM Bathroom Unit Price (₺/m²)", value=get_state_val("pm_banyo_price", 190.0), step=5.0, key="pm_banyo_input")
update_state_val("pm_banyo_price", pm_banyo_price)

tech_banyo_price = st.sidebar.number_input("Technician Bathroom Unit Price (₺/m²)", value=get_state_val("tech_banyo_price", 130.0), step=5.0, key="tech_banyo_input")
update_state_val("tech_banyo_price", tech_banyo_price)

weights = {"Primer": 0.05, "Plaster": 0.15, "Insulation": 0.25, "Mesh & Basecoat": 0.20, "Decorative Finish": 0.20, "Painting": 0.15}

# ==========================================
# PRE-COMPUTE ALL METRICS
# ==========================================
today_str = date.today().strftime('%d.%m.%Y')

# --- Rear Facade ---
arka_sections = {"Main Surface (Front)": 104.4, "Side Facade 1": 136.5, "Side Facade 2": 83.0, "Side Facade 3": 33.0}
arka_progresses = {}
for idx, (section, area) in enumerate(arka_sections.items()):
    ast = get_state_val(f"arka_ast_{idx}", False)
    siv = get_state_val(f"arka_siv_{idx}", False)
    man = get_state_val(f"arka_man_{idx}", False)
    fil = get_state_val(f"arka_fil_{idx}", False)
    dek = get_state_val(f"arka_dek_{idx}", False)
    boy = get_state_val(f"arka_boy_{idx}", False)
    arka_progresses[section] = ((weights["Primer"] if ast else 0) + (weights["Plaster"] if siv else 0) + (weights["Insulation"] if man else 0) + (weights["Mesh & Basecoat"] if fil else 0) + (weights["Decorative Finish"] if dek else 0) + (weights["Painting"] if boy else 0))

arka_total_area = sum(arka_sections.values())
arka_completed_area = sum(arka_sections[sec] * arka_progresses[sec] for sec in arka_sections)
arka_net_percentage = arka_completed_area / arka_total_area if arka_total_area > 0 else 0

# --- Front Facade ---
on_sections = {"Main Surface (Front)": 80.0, "Side Facade 1": 68.25, "Side Facade 2": 41.5}
on_progresses = {}
for idx, (section, area) in enumerate(on_sections.items()):
    ast = get_state_val(f"on_ast_{idx}", False)
    siv = get_state_val(f"on_siv_{idx}", False)
    man = get_state_val(f"on_man_{idx}", False)
    fil = get_state_val(f"on_fil_{idx}", False)
    dek = get_state_val(f"on_dek_{idx}", False)
    boy = get_state_val(f"on_boy_{idx}", False)
    on_progresses[section] = ((weights["Primer"] if ast else 0) + (weights["Plaster"] if siv else 0) + (weights["Insulation"] if man else 0) + (weights["Mesh & Basecoat"] if fil else 0) + (weights["Decorative Finish"] if dek else 0) + (weights["Painting"] if boy else 0))

on_total_area = sum(on_sections.values())
on_completed_area = sum(on_sections[sec] * on_progresses[sec] for sec in on_sections)
on_net_percentage = on_completed_area / on_total_area if on_total_area > 0 else 0

# --- Bathrooms ---
floors_data = [
    {"floor": "Basement (-1)", "b1_area": 34.35, "b1_status": "Pending", "b2_area": 0.0, "b2_status": "Exempt"},
    {"floor": "Entrance Hall (0)", "b1_area": 34.35, "b1_status": "Pending", "b2_area": 15.68, "b2_status": "Completed"},
    {"floor": "1st Floor", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "2nd Floor", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "3rd Floor", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.87, "b2_status": "Completed"},
    {"floor": "Attic Floor", "b1_area": 34.35, "b1_status": "Completed", "b2_area": 20.0, "b2_status": "Pending"},
]
banyo_total_area = 0
banyo_completed_area = 0
for idx, f in enumerate(floors_data):
    b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
    b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
    if f["b1_area"] > 0 and b1_s != "Exempt":
        banyo_total_area += f["b1_area"]
        if b1_s == "Completed": banyo_completed_area += f["b1_area"]
    if f["b2_area"] > 0 and b2_s != "Exempt":
        banyo_total_area += f["b2_area"]
        if b2_s == "Completed": banyo_completed_area += f["b2_area"]
banyo_net_percentage = banyo_completed_area / banyo_total_area if banyo_total_area > 0 else 0

# --- Financials ---
arka_rev = arka_completed_area * pm_cephe_price
on_rev = on_completed_area * pm_cephe_price
banyo_rev = banyo_completed_area * pm_banyo_price
total_rev = arka_rev + on_rev + banyo_rev

arka_cst = arka_completed_area * tech_cephe_price
on_cst = on_completed_area * tech_cephe_price
banyo_cst = banyo_completed_area * tech_banyo_price
total_cst = arka_cst + on_cst + banyo_cst
total_prf = total_rev - total_cst

# --- Timeline Assembly ---
timeline_events = []
for idx, (section, _) in enumerate(arka_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_arka_{phase}_{idx}", "")
        if d: timeline_events.append({"Date": d, "Work Item": "Rear Facade", "Location/Floor": section, "Stage": {"ast":"Primer","siv":"Plaster","man":"Insulation","fil":"Mesh+Basecoat","dek":"Decorative Finish","boy":"Painting"}[phase]})
for idx, (section, _) in enumerate(on_sections.items()):
    for phase in ["ast", "siv", "man", "fil", "dek", "boy"]:
        d = get_state_val(f"date_on_{phase}_{idx}", "")
        if d: timeline_events.append({"Date": d, "Work Item": "Front Facade", "Location/Floor": section, "Stage": {"ast":"Primer","siv":"Plaster","man":"Insulation","fil":"Mesh+Basecoat","dek":"Decorative Finish","boy":"Painting"}[phase]})
for idx, f in enumerate(floors_data):
    d1 = get_state_val(f"date_b1_{idx}", "")
    if d1: timeline_events.append({"Date": d1, "Work Item": "Bathroom Insulation", "Location/Floor": f["floor"], "Stage": "Bathroom 1 Completed"})
    d2 = get_state_val(f"date_b2_{idx}", "")
    if d2: timeline_events.append({"Date": d2, "Work Item": "Bathroom Insulation", "Location/Floor": f["floor"], "Stage": "Bathroom 2 Completed"})

# ==========================================
# REPORT HTML ENGINE
# ==========================================
def make_report_wrapper(title, content_html):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
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
            <button class="btn" onclick="window.print()">🖨️ SAVE THIS PAGE AS PDF / PRINT</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">Report Date: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# Application Tabs
tab_money, tab_timeline, tab_schedule, tab_arka, tab_on, tab_banyo = st.tabs([
    "💰 FINANCIAL SUMMARY", "⏱️ LIVE SITE TIMELINE", "📅 TARGET SCHEDULE",
    "🧱 Rear Facade Tracking", "🏢 Front Facade Tracking", "💧 Bathroom Insulation"
])

# --- 1. MONEY TAB ---
with tab_money:
    st.header("💵 Current Financial Payment Breakdowns")
    
    money_html = f"""
    <div class="grid">
        <div class="card"><div class="card-lbl">Project Manager Progress Payment</div><div class="card-val">₺ {total_rev:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Technician Total Payments</div><div class="card-val">₺ {total_cst:,.2f}</div></div>
        <div class="card"><div class="card-lbl">Company Net Profit</div><div class="card-val">₺ {total_prf:,.2f}</div></div>
    </div>
    <table>
        <thead><tr><th>Work Item Description</th><th>Progress %</th><th>PM Valuation</th><th>Technician Cost</th><th>Net Profit</th></tr></thead>
        <tbody>
            <tr><td>Rear Facade Works</td><td>{arka_net_percentage*100:.1f}%</td><td>₺ {arka_rev:,.2f}</td><td>₺ {arka_cst:,.2f}</td><td>₺ {(arka_rev-arka_cst):,.2f}</td></tr>
            <tr><td>Front Facade Works</td><td>{on_net_percentage*100:.1f}%</td><td>₺ {on_rev:,.2f}</td><td>₺ {on_cst:,.2f}</td><td>₺ {(on_rev-on_cst):,.2f}</td></tr>
            <tr><td>Bathrooms Suwmatik Waterproofing</td><td>{banyo_net_percentage*100:.1f}%</td><td>₺ {banyo_rev:,.2f}</td><td>₺ {banyo_cst:,.2f}</td><td>₺ {(banyo_rev-banyo_cst):,.2f}</td></tr>
            <tr class="total"><td>TOTAL</td><td>-</td><td>₺ {total_rev:,.2f}</td><td>₺ {total_cst:,.2f}</td><td>₺ {total_prf:,.2f}</td></tr>
        </tbody>
    </table>
    """
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("FINANCIAL PROGRESS SUMMARY REPORT", money_html), file_name="financial_summary_report.html", mime="text/html", key="dl_money")

    m1, m2, m3 = st.columns(3)
    m1.metric("Receivable from PM", f"₺ {total_rev:,.2f}")
    m2.metric("Payable to Technicians", f"₺ {total_cst:,.2f}")
    m3.metric("Net Profit", f"₺ {total_prf:,.2f}")
    
    summary_data = {
        "Work Item Description": ["Rear Facade", "Front Facade", "Bathroom Insulation", "TOTAL"],
        "Progress %": [f"{arka_net_percentage*100:.1f}%", f"{on_net_percentage*100:.1f}%", f"{banyo_net_percentage*100:.1f}%", "-"],
        "PM Milestone Pay": [f"₺ {arka_rev:,.2f}", f"₺ {on_rev:,.2f}", f"₺ {banyo_rev:,.2f}", f"₺ {total_rev:,.2f}"],
        "Technician Cost": [f"₺ {arka_cst:,.2f}", f"₺ {on_cst:,.2f}", f"₺ {banyo_cst:,.2f}", f"₺ {total_cst:,.2f}"],
        "Net Profit": [f"₺ {(arka_rev - arka_cst):,.2f}", f"₺ {(on_rev - on_cst):,.2f}", f"₺ {(banyo_rev - banyo_cst):,.2f}", f"₺ {total_prf:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

# --- 2. TIMELINE TAB ---
with tab_timeline:
    st.header("⏱️ Live Site Construction Log")
    
    t_rows = ""
    if timeline_events:
        df_t = pd.DataFrame(timeline_events)
        df_t['dt_obj'] = pd.to_datetime(df_t['Date'], format='%d.%m.%Y')
        df_t = df_t.sort_values(by='dt_obj', ascending=False)
        for _, r in df_t.iterrows():
            t_rows += f"<tr><td>{r['Date']}</td><td>{r['Work Item']}</td><td>{r['Location/Floor']}</td><td>{r['Stage']}</td></tr>"
    else:
        t_rows = "<tr><td colspan='4' style='text-align:center;'>No tracked milestones logged yet.</td></tr>"
        
    timeline_html = f"<table><thead><tr><th>Date</th><th>Work Item</th><th>Location / Floor</th><th>Completed Stage</th></tr></thead><tbody>{t_rows}</tbody></table>"
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("LIVE TRACKED SITE TIMELINE REPORT", timeline_html), file_name="live_timeline_report.html", mime="text/html", key="dl_time")

    if timeline_events:
        st.dataframe(df_t.drop(columns=['dt_obj']), use_container_width=True)
    else:
        st.info("No completed steps recorded yet.")

# --- 3. SCHEDULE TAB ---
with tab_schedule:
    st.header("📅 Project Targeted Milestone Schedule")
    today = date.today()
    def parse_saved_date(key, default_date):
        saved = get_state_val(key, None)
        if saved:
            try: return datetime.fromisoformat(saved).date()
            except: return saved
        return default_date

    col_item, col_start, col_end = st.columns(3)
    with col_item:
        st.write("##### Work Item")
        st.write("<br><p style='padding:11px 0;'><b>Rear Facade Construction</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Front Facade Construction</b></p>", unsafe_allow_html=True)
        st.write("<br><p style='padding:11px 0;'><b>Bathrooms Waterproofing</b></p>", unsafe_allow_html=True)
    with col_start:
        st.write("##### Planned Start Date")
        arka_start = st.date_input("Rear Start", value=parse_saved_date("arka_start_dt", today), key="arka_s_in", label_visibility="collapsed")
        on_start = st.date_input("Front Start", value=parse_saved_date("on_start_dt", today), key="on_s_in", label_visibility="collapsed")
        banyo_start = st.date_input("Banyo Start", value=parse_saved_date("banyo_start_dt", today), key="banyo_s_in", label_visibility="collapsed")
    with col_end:
        st.write("##### Target End Date")
        arka_end = st.date_input("Rear End", value=parse_saved_date("arka_end_dt", today), key="arka_e_in", label_visibility="collapsed")
        on_end = st.date_input("Front End", value=parse_saved_date("on_end_dt", today), key="on_e_in", label_visibility="collapsed")
        banyo_end = st.date_input("Banyo End", value=parse_saved_date("banyo_end_dt", today), key="banyo_e_in", label_visibility="collapsed")

    update_state_val("arka_start_dt", arka_start)
    update_state_val("on_start_dt", on_start)
    update_state_val("banyo_start_dt", banyo_start)
    update_state_val("arka_end_dt", arka_end)
    update_state_val("on_end_dt", on_end)
    update_state_val("banyo_end_dt", banyo_end)

    def calc_p(s, e):
        if today < s: return 0.0
        if today >= e: return 1.0
        tot = (e - s).days
        return ((today - s).days) / tot if tot > 0 else 1.0

    p_arka, p_on, p_banyo = calc_p(arka_start, arka_end), calc_p(on_start, on_end), calc_p(banyo_start, banyo_end)

    def get_badge(p, a):
        diff = a - p
        if diff < -0.05: return "Delayed", "#d32f2f"
        elif diff > 0.05: return "Ahead of Schedule", "#388e3c"
        return "On Schedule", "#1976d2"

    b_arka, c_arka = get_badge(p_arka, arka_net_percentage)
    b_on, c_on = get_badge(p_on, on_net_percentage)
    b_banyo, c_banyo = get_badge(p_banyo, banyo_net_percentage)

    sched_html = f"""
    <table>
        <thead><tr><th>Work Item</th><th>Planned Progress</th><th>Actual Progress</th><th>Status</th></tr></thead>
        <tbody>
            <tr><td>Rear Facade</td><td>{p_arka*100:.1f}%</td><td>{arka_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_arka}">{b_arka}</span></td></tr>
            <tr><td>Front Facade</td><td>{p_on*100:.1f}%</td><td>{on_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_on}">{b_on}</span></td></tr>
            <tr><td>Bathroom Insulation</td><td>{p_banyo*100:.1f}%</td><td>{banyo_net_percentage*100:.1f}%</td><td><span class="status-badge" style="background:{c_banyo}">{b_banyo}</span></td></tr>
        </tbody>
    </table>
    """
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("TARGET VS ACTUAL SCHEDULE METRICS", sched_html), file_name="target_schedule_report.html", mime="text/html", key="dl_sched")

    st.markdown("### 📊 Target Timeline vs. Actual On-Site Performance")
    def display_schedule_row(title, planned, actual):
        diff = actual - planned
        if diff < -0.05: status, color = "🔴 DELAYED COMPARED TO TARGET", "red"
        elif diff > 0.05: status, color = "🚀 AHEAD OF SCHEDULE PROGRESS", "green"
        else: status, color = "🟢 METICULOUSLY ON SCHEDULE", "blue"
        st.write(f"#### {title}")
        c_p, c_a, c_s = st.columns(3)
        c_p.metric("Target Planned Progress", f"{planned*100:.1f}%")
        c_a.metric("Actual Site Progress", f"{actual*100:.1f}%", delta=f"{diff*100:+.1f}%")
        c_s.markdown(f"<h5 style='color:{color}; padding-top:10px;'>{status}</h5>", unsafe_allow_html=True)
        st.markdown("---")

    display_schedule_row("Rear Facade", p_arka, arka_net_percentage)
    display_schedule_row("Front Facade", p_on, on_net_percentage)
    display_schedule_row("Bathroom Insulation", p_banyo, banyo_net_percentage)

# --- 4. REAR FACADE ---
with tab_arka:
    st.header("🧱 Rear Facade Segment Progression")
    
    arka_html = "<table><thead><tr><th>Section / Elevation</th><th>Sizing Matrix (m²)</th><th>Net Progress</th></tr></thead><tbody>"
    for sec, area in arka_sections.items():
        arka_html += f"<tr><td>{sec}</td><td>{area} m²</td><td><b>{arka_progresses[sec]*100:.1f}%</b></td></tr>"
    arka_html += f"<tr class='total'><td>TOTAL NET WEIGHTED AVERAGE</td><td>{arka_total_area} m²</td><td>{arka_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("REAR FACADE WORK STEPS REPORT", arka_html), file_name="rear_facade_report.html", mime="text/html", key="dl_arka")

    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(arka_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            ast_val = st.checkbox("Primer (%5)", value=get_state_val(f"arka_ast_{idx}", False), key=f"arka_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_ast_cb_{idx}", f"arka_ast_{idx}", f"date_arka_ast_{idx}"))
            siv_val = st.checkbox("Plaster (%15)", value=get_state_val(f"arka_siv_{idx}", False), key=f"arka_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_siv_cb_{idx}", f"arka_siv_{idx}", f"date_arka_siv_{idx}"))
            man_val = st.checkbox("Insulation (%25)", value=get_state_val(f"arka_man_{idx}", False), key=f"arka_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_man_cb_{idx}", f"arka_man_{idx}", f"date_arka_man_{idx}"))
            fil_val = st.checkbox("Mesh & Basecoat (%20)", value=get_state_val(f"arka_fil_{idx}", False), key=f"arka_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_fil_cb_{idx}", f"arka_fil_{idx}", f"date_arka_fil_{idx}"))
            dek_val = st.checkbox("Decorative Finish (%20)", value=get_state_val(f"arka_dek_{idx}", False), key=f"arka_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_dek_cb_{idx}", f"arka_dek_{idx}", f"date_arka_dek_{idx}"))
            boy_val = st.checkbox("Painting (%15)", value=get_state_val(f"arka_boy_{idx}", False), key=f"arka_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"arka_boy_cb_{idx}", f"arka_boy_{idx}", f"date_arka_boy_{idx}"))
            st.metric("Section Progress Status", f"{arka_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 5. FRONT FACADE ---
with tab_on:
    st.header("🏢 Front Facade Segment Progression")
    
    on_html = "<table><thead><tr><th>Section / Elevation</th><th>Sizing Matrix (m²)</th><th>Net Progress</th></tr></thead><tbody>"
    for sec, area in on_sections.items():
        on_html += f"<tr><td>{sec}</td><td>{area} m²</td><td><b>{on_progresses[sec]*100:.1f}%</b></td></tr>"
    on_html += f"<tr class='total'><td>TOTAL NET WEIGHTED AVERAGE</td><td>{on_total_area} m²</td><td>{on_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("FRONT FACADE WORK STEPS REPORT", on_html), file_name="front_facade_report.html", mime="text/html", key="dl_on")

    col1, col2 = st.columns(2)
    for idx, (section, area) in enumerate(on_sections.items()):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.write(f"### {section} ({area} m²)")
            ast_val = st.checkbox("Primer (%5)", value=get_state_val(f"on_ast_{idx}", False), key=f"on_ast_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_ast_cb_{idx}", f"on_ast_{idx}", f"date_on_ast_{idx}"))
            siv_val = st.checkbox("Plaster (%15)", value=get_state_val(f"on_siv_{idx}", False), key=f"on_siv_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_siv_cb_{idx}", f"on_siv_{idx}", f"date_on_siv_{idx}"))
            man_val = st.checkbox("Insulation (%25)", value=get_state_val(f"on_man_{idx}", False), key=f"on_man_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_man_cb_{idx}", f"on_man_{idx}", f"date_on_man_{idx}"))
            fil_val = st.checkbox("Mesh & Basecoat (%20)", value=get_state_val(f"on_fil_{idx}", False), key=f"on_fil_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_fil_cb_{idx}", f"on_fil_{idx}", f"date_on_fil_{idx}"))
            dek_val = st.checkbox("Decorative Finish (%20)", value=get_state_val(f"on_dek_{idx}", False), key=f"on_dek_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_dek_cb_{idx}", f"on_dek_{idx}", f"date_on_dek_{idx}"))
            boy_val = st.checkbox("Painting (%15)", value=get_state_val(f"on_boy_{idx}", False), key=f"on_boy_cb_{idx}", on_change=handle_checkbox_change, args=(f"on_boy_cb_{idx}", f"on_boy_{idx}", f"date_on_boy_{idx}"))
            st.metric("Section Progress Status", f"{on_progresses[section]*100:.1f}%")
            st.markdown("---")

# --- 6. BATHROOM INSULATION ---
with tab_banyo:
    st.header("💧 Bathroom Suwmatik Waterproofing Status")
    
    banyo_html = "<table><thead><tr><th>Floor Level</th><th>Bathroom 1 Status</th><th>Bathroom 2 Status</th></tr></thead><tbody>"
    for idx, f in enumerate(floors_data):
        b1_s = get_state_val(f"b1_stat_{idx}", f["b1_status"])
        b2_s = get_state_val(f"b2_stat_{idx}", f["b2_status"])
        banyo_html += f"<tr><td>{f['floor']}</td><td>{b1_s} ({f['b1_area']} m²)</td><td>{b2_s} ({f['b2_area']} m²)</td></tr>"
    banyo_html += f"<tr class='total'><td>TOTAL COMPLETED METRAGE RATIO</td><td colspan='2' style='text-align:center;'>{banyo_net_percentage*100:.1f}%</td></tr></tbody></table>"
    st.download_button("📱 DOWNLOAD PDF / SCREENSHOT REPORT FOR THIS PAGE", make_report_wrapper("BATHROOM WATERPROOFING SYSTEM REPORT", banyo_html), file_name="bathroom_insulation_report.html", mime="text/html", key="dl_banyo")

    status_options = ["Pending", "Completed", "Exempt"]
    for idx, f in enumerate(floors_data):
        st.subheader(f["floor"])
        c1, c2 = st.columns(2)
        with c1:
            if f["b1_area"] > 0:
                saved_status = get_state_val(f"b1_stat_{idx}", f["b1_status"])
                status_1 = st.selectbox(f"Bathroom 1 ({f['b1_area']} m²)", status_options, index=status_options.index(saved_status), key=f"b1_sb_{idx}")
                if status_1 != saved_status:
                    update_state_val(f"b1_stat_{idx}", status_1)
                    update_state_val(f"date_b1_{idx}", date.today().strftime("%d.%m.%Y") if status_1 == "Completed" else "")
        with c2:
            if f["b2_area"] > 0:
                saved_status2 = get_state_val(f"b2_stat_{idx}", f["b2_status"])
                status_2 = st.selectbox(f"Bathroom 2 ({f['b2_area']} m²)", status_options, index=status_options.index(saved_status2), key=f"b2_sb_{idx}")
                if status_2 != saved_status2:
                    update_state_val(f"b2_stat_{idx}", status_2)
                    update_state_val(f"date_b2_{idx}", date.today().strftime("%d.%m.%Y") if status_2 == "Completed" else "")
        st.markdown("---")
