import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Havence - Interior Progress Dashboard", layout="wide", page_icon="🏗️")
st.title("🏗️ Havence - منظومة حصر ومتابعة التشطيبات الداخلية والمالية")

# ==========================================
# 2. DATA PERSISTENCE ENGINE (JSON DATABASE)
# ==========================================
DB_FILE = "interior_progress_data.json"

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
# 3. GLOBAL HELPER FUNCTIONS & REPORT WRAPPER
# ==========================================
def make_report_wrapper(title, content_html):
    today_str = date.today().strftime('%d.%m.%Y')
    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; text-align: right; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #1E4620; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #1E4620; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #1E4620; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .grid {{ display: flex; gap: 15px; margin-bottom: 25px; flex-direction: row-reverse; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 12px; font-weight: bold; color: #777; }}
            .card-val {{ font-size: 22px; font-weight: bold; color: #111; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; text-align: right; }}
            th, td {{ border: 1px solid #dddddd; padding: 12px; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; color: #111; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ حفظ التقرير كـ PDF / طباعة</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">تاريخ استخراج التقرير: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# ==========================================
# 4. SIDEBAR - FINANCIAL SETTINGS
# ==========================================
st.sidebar.header("💵 إعدادات فئات أسعار المتر المربع")
pm_price = st.sidebar.number_input("سعر البيع للمالك (₺/m²)", value=get_state_val("global_pm_price", 450.0), step=10.0)
update_state_val("global_pm_price", pm_price)

tech_price = st.sidebar.number_input("تكلفة المتر للفني Labor Cost (₺/m²)", value=get_state_val("global_tech_price", 300.0), step=10.0)
update_state_val("global_tech_price", tech_price)

# خطواط التشغيل والوزن النسبي المستحق هندسياً
interior_weights = {"Ano": 0.15, "Alci": 0.40, "Saten": 0.25, "Boya": 0.20}

# ==========================================
# 5. EXACT QUANTITY SURVEYING STRUCTURE (FROM THE EXCEL V6)
# ==========================================
# بناء هيكل المشروع بالكامل بمساحات الحوائط الصافية المستخرجة
project_structure = {
    "الدور -1 (البدروم السكني والخدمي)": {
        "دكان -1 (المساحة الصافية)": 66.71,
        "مخازن البدروم (القطاع الإنشائي)": 30.22,
        "الطرقة العامة للبدروم": 50.72,
        "سلم البدروم الداخلي": 6.96,
        "الشقة الخلفية (الدور السفلي)": 187.47
    },
    "دور المدخل الأرضي": {
        "المدخل الرئيسي والممر الطولي": 24.32,
        "الطرقة العامة والصالة الأرضية": 50.38,
        "سلم الدور الأرضي": 6.96,
        "الدكان الأرضي الصافي": 24.06,
        "الشقة الخلفية الأرضية": 106.56
    },
    "الدور المتكرر الأول": {
        "الشقة الأمامية (1)": 163.17,
        "الشقة الخلفية (1)": 106.56,
        "السلم العام والطرقة (1)": 50.76
    },
    "الدور المتكرر الثاني": {
        "الشقة الأمامية (2)": 163.17,
        "الشقة الخلفية (2)": 106.56,
        "السلم العام والطرقة (2)": 50.76
    },
    "الدور المتكرر الثالث": {
        "الشقة الأمامية (3)": 163.17,
        "الشقة الخلفية (3)": 106.56,
        "السلم العام والطرقة (3)": 50.76
    },
    "الدور الأخير (الدوبلكس / الملحق)": {
        "الشقة الأمامية الأخير": 163.17,
        "الشقة الخلفية الأخير": 106.56,
        "السلم والمسارات للأخير": 50.76
    }
}

# ==========================================
# 6. MATHEMATICAL COMPILATION ENGINE
# ==========================================
flat_sections = []
total_project_area = 0
total_completed_equivalent_area = 0

global_idx = 0
for floor_name, sections in project_structure.items():
    for sec_name, area in sections.items():
        # استرجاع حالات التشيك بوكس لكل مرحلة
        ano = get_state_val(f"cb_ano_{global_idx}", False)
        alc = get_state_val(f"cb_alc_{global_idx}", False)
        sat = get_state_val(f"cb_sat_{global_idx}", False)
        boy = get_state_val(f"cb_boy_{global_idx}", False)
        
        # حساب نسبة إنجاز القطاع بناءً على الأوزان
        sec_progress = ((interior_weights["Ano"] if ano else 0) + 
                        (interior_weights["Alci"] if alc else 0) + 
                        (interior_weights["Saten"] if sat else 0) + 
                        (interior_weights["Boya"] if boy else 0))
        
        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        flat_sections.append({
            "global_idx": global_idx,
            "floor": floor_name,
            "section": sec_name,
            "area": area,
            "progress": sec_progress,
            "comp_area": completed_area,
            "ano": ano, "alc": alc, "sat": sat, "boy": boy
        })
        global_idx += 1

# حسابات المستخلصات المالية الإجمالية
total_billing_owner = total_completed_equivalent_area * pm_price
total_labor_cost = total_completed_equivalent_area * tech_price
net_company_profit = total_billing_owner - total_labor_cost
overall_project_progress_pct = (total_completed_equivalent_area / total_project_area) if total_project_area > 0 else 0

# تجميع خط الزمن لاشتراطات التطبيق المستقرة
timeline_events = []
for item in flat_sections:
    g_id = item["global_idx"]
    for phase_code, phase_name in [("ano", "Ano (البؤج والأوتار)"), ("alc", "Alçı Makinası (المحارة)"), ("sat", "Saten (المعجون)"), ("boy", "Boya (الدهان التجميلي)")]:
        d = get_state_val(f"date_int_{phase_code}_{g_id}", "")
        if d:
            timeline_events.append({
                "التاريخ": d,
                "الدور": item["floor"],
                "القطاع / الشقة": item["section"],
                "المرحلة المكتملة": phase_name
            })

# ==========================================
# 7. UI NAVIGATION & INTERFACE TABS
# ==========================================
st.markdown(f"### 📊 النسبة الإجمالية المكتملة للموقع: `{overall_project_progress_pct*100:.2f}%`")

tab_money, tab_floors, tab_timeline = st.tabs([
    "💰 الحسابات والمستخلصات المالية", 
    "🏢 متابعة غرف وقطاعات الأدوار تفصيلياً", 
    "⏱️ السجل الزمني الحي للموقع"
])

# --- TAB 1: FINANCIAL SUMMARY ---
with tab_money:
    st.header("💰 الخلاصة المالية وحسابات الأرباح")
    
    # بطاقات المؤشرات السريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي مستحق على المالك (الملك)", f"₺ {total_billing_owner:,.2f}")
    c2.metric("إجمالي مستحق للفنيين (Labor Cost)", f"₺ {total_labor_cost:,.2f}")
    c3.metric("صافي أرباح شركة Havence", f"₺ {net_company_profit:,.2f}", delta=f"{overall_project_progress_pct*100:.1f}% إنجاز")
    
    st.markdown("---")
    
    # إعداد جدول التقرير للطباعة المتوافقة مع الجوال
    table_rows_html = ""
    report_data_list = []
    
    for item in flat_sections:
        sec_billing = item["comp_area"] * pm_price
        sec_cost = item["comp_area"] * tech_price
        sec_profit = sec_billing - sec_cost
        
        report_data_list.append({
            "الدور": item["floor"],
            "القطاع / الشقة": item["section"],
            "المساحة الإجمالية (م2)": f"{item['area']:.2f}",
            "نسبة الإنجاز": f"{item['progress']*100:.0f}%",
            "مستخلص المالك": f"₺ {sec_billing:,.2f}",
            "أجرة الفني": f"₺ {sec_cost:,.2f}",
            "صافي الربح": f"₺ {sec_profit:,.2f}"
        })
        
        table_rows_html += f"""
        <tr>
            <td>{item['floor']}</td>
            <td>{item['section']}</td>
            <td>{item['area']:.2f} م²</td>
            <td>{item['progress']*100:.0f}%</td>
            <td>₺ {sec_billing:,.2f}</td>
            <td>₺ {sec_cost:,.2f}</td>
            <td>₺ {sec_profit:,.2f}</td>
        </tr>
        """
        
    money_html_content = f"""
    <div class="grid">
        <div class="card"><div class="card-lbl">إجمالي مستخلص المالك المعتمَد</div><div class="card-val">₺ {total_billing_owner:,.2f}</div></div>
        <div class="card"><div class="card-lbl">إجمالي تكلفة أجرة الفنيين</div><div class="card-val">₺ {total_labor_cost:,.2f}</div></div>
        <div class="card"><div class="card-lbl">صافي الأرباح المحققة لشركة Havence</div><div class="card-val">₺ {net_company_profit:,.2f}</div></div>
    </div>
    <table>
        <thead>
            <tr>
                <th>الدور</th>
                <th>القطاع / الشقة</th>
                <th>المساحة الصافية</th>
                <th>نسبة الإنجاز</th>
                <th>مستخلص المالك</th>
                <th>أجرة الفني</th>
                <th>صافي الأرباح</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
            <tr class="total">
                <td colspan="2">المجموع الإجمالي الموحد</td>
                <td>{total_project_area:,.2f} م²</td>
                <td>{overall_project_progress_pct*100:.2f}%</td>
                <td>₺ {total_billing_owner:,.2f}</td>
                <td>₺ {total_labor_cost:,.2f}</td>
                <td>₺ {net_company_profit:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.download_button("📱 تحميل مستخلص مالي نظيف متوافق مع الجوال (PDF / HTML)", 
                       make_report_wrapper("تقرير مستخلصات الحصر والتشطيبات الداخلية الموحد - شركة Havence", money_html_content), 
                       file_name="Havence_Financial_Report.html", mime="text/html")
    
    st.dataframe(pd.DataFrame(report_data_list), use_container_width=True)

# --- TAB 2: DETAILED PROGRESS TRACKING BY FLOORS ---
with tab_floors:
    st.header("🏢 أدوار وقطاعات المشروع الإنشائية")
    
    for floor_name, sections in project_structure.items():
        with st.expander(f"⬇️ {floor_name}", expanded=True):
            col1, col2 = st.columns(2)
            
            floor_items = [x for x in flat_sections if x["floor"] == floor_name]
            for idx, item in enumerate(floor_items):
                g_id = item["global_idx"]
                target_col = col1 if idx % 2 == 0 else col2
                
                with target_col:
                    st.write(f"##### 📍 {item['section']} ({item['area']:.2f} م²)")
                    
                    # حقول الاختيار والمراحل لكل الغرف والشقق المستخرجة من الحصر
                    ano_val = st.checkbox("البؤج والأوتار (Ano) [15%]", value=item["ano"], key=f"int_ano_cb_{g_id}", 
                                          on_change=handle_checkbox_change, args=(f"int_ano_cb_{g_id}", f"cb_ano_{g_id}", f"date_int_ano_{g_id}"))
                    
                    alc_val = st.checkbox("المحارة ماكينة وجه واحد (Alçı) [40%]", value=item["alc"], key=f"int_alc_cb_{g_id}", 
                                          on_change=handle_checkbox_change, args=(f"int_alc_cb_{g_id}", f"cb_alc_{g_id}", f"date_int_alc_{g_id}"))
                    
                    sat_val = st.checkbox("المعجون الناعم والتحضير (Saten) [25%]", value=item["sat"], key=f"int_sat_cb_{g_id}", 
                                          on_change=handle_checkbox_change, args=(f"int_sat_cb_{g_id}", f"cb_sat_{g_id}", f"date_int_sat_{g_id}"))
                    
                    boy_val = st.checkbox("الدهانات والوجه النهائي (Boya) [20%]", value=item["boy"], key=f"int_boy_cb_{g_id}", 
                                          on_change=handle_checkbox_change, args=(f"int_boy_cb_{g_id}", f"cb_boy_{g_id}", f"date_int_boy_{g_id}"))
                    
                    st.write(f"نسبة إنجاز القطاع الحالية: `{item['progress']*100:.0f}%` | الأمتار المكافئة: `{item['comp_area']:.2f} م²`")
                    st.markdown("---")

# --- TAB 3: LIVE TIMELINE LOG ---
with tab_timeline:
    st.header("⏱️ سجل تنفيذ مراحل العمل")
    
    if timeline_events:
        df_time = pd.DataFrame(timeline_events)
        # ترتيب السجل تلقائياً لعرض الأحدث في الأعلى لراحة المهندس بالموقع
        df_time['dt_parse'] = pd.to_datetime(df_time['التاريخ'], format='%d.%m.%Y')
        df_time = df_time.sort_values(by='dt_parse', ascending=False).drop(columns=['dt_parse'])
        
        st.dataframe(df_time, use_container_width=True)
        
        # كود التقرير المخصص للسجل الزمني لطباعته منفصلاً
        t_rows_html = ""
        for _, r in df_time.iterrows():
            t_rows_html += f"<tr><td>{r['التاريخ']}</td><td>{r['الدور']}</td><td>{r['القطاع / الشقة']}</td><td>{r['المرحلة المكتملة']}</td></tr>"
            
        time_html = f"""
        <table>
            <thead>
                <tr><th>التاريخ</th><th>الدور</th><th>القطاع / الشقة</th><th>المرحلة المكتملة</th></tr>
            </thead>
            <tbody>{t_rows_html}</tbody>
        </table>
        """
        st.download_button("📱 تحميل سجل التنفيذ الزمني كـ PDF", 
                           make_report_wrapper("سجل التنفيذ والجدول الزمني الفعلي للموقع - Havence", time_html), 
                           file_name="Havence_Timeline_Report.html", mime="text/html")
    else:
        st.info("لم يتم تسجيل أو إنجاز أي خطوة تنفيذية في الموقع حتى الآن.")
