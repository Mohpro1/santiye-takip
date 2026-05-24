import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Şantiye Takip & Metraj Otomasyonu",
    page_icon="🏗️",
    layout="wide"
)

# ==============================================================================
# 2. DATABASE INITIALIZATION & CONNECTIVITY
# ==============================================================================
DB_FILE = "santiye_takip.db"

def init_db():
    """Initializes the database and seeds it with template tracking data if empty."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            company_name TEXT,
            contractor_name TEXT,
            labor_cost REAL,
            total_amount REAL,
            status TEXT,
            record_date TEXT
        )
    ''')
    
    # Check if database has rows; if not, populate with standard starting samples
    cursor.execute("SELECT COUNT(*) FROM payments")
    if cursor.fetchone()[0] == 0:
        sample_rows = [
            ("Şehir Merkezi Kompleksi", "Havence", "Cüneyt Bey", 150.0, 75000.0, "Ödendi", "2026-05-10"),
            ("Kuzey Sahil Villaları", "Havence", "Cüneyt Bey", 180.0, 120000.0, "Beklemede", "2026-05-20"),
            ("Doğu Blokları Restorasyon", "Havence", "Mehmet Usta", 140.0, 45000.0, "Ödendi", "2026-05-15"),
            ("Güney Rezidans", "İnşaat Anonim", "Ali Bey", 160.0, 90000.0, "Beklemede", "2026-05-22")
        ]
        cursor.executemany('''
            INSERT INTO payments (project_name, company_name, contractor_name, labor_cost, total_amount, status, record_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_rows)
        conn.commit()
    conn.close()

# Initialize the db on startup
init_db()

def run_query(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn, params=params)

def execute_cmd(cmd, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(cmd, params)
        conn.commit()

# ==============================================================================
# 3. FIXED SQL QUERY BUILDER (Lines 88 - 97)
# ==============================================================================
def build_contractor_sql():
    # Line 88: Triple-quoted f-string is correctly opened
    return f"""
    SELECT 
        id,
        project_name,
        company_name,
        contractor_name,
        labor_cost AS [Labor Cost Per Meter],
        total_amount,
        status,
        record_date
    FROM payments
    WHERE company_name = 'Havence'
      AND contractor_name = 'Cüneyt Bey'
    ORDER BY id DESC;
    """  # Line 97: The matching closing quotes are correctly placed here.

# ==============================================================================
# 4. SIDEBAR NAVIGATION CONTROLS
# ==============================================================================
st.sidebar.title("🏗️ Şantiye Takip Sistemi")
st.sidebar.markdown("### Havence Yönetim Paneli")
menu = st.sidebar.radio(
    "Menü Seçimi",
    [
        "📊 Genel Özet & Dashboard", 
        "📋 Metraj & Hakediş Raporları", 
        "💼 Müteahhit ve Ödeme Takibi", 
        "➕ Yeni Veri Girişi"
    ]
)

# ==============================================================================
# 5. DYNAMIC PAGE ROUTING
# ==============================================================================

# --- PAGE A: GENERAL DASHBOARD ---
if menu == "📊 Genel Özet & Dashboard":
    st.title("📊 Şantiye Genel Durum Özeti")
    st.markdown("Projelere ait hakediş, ödeme durumları ve genel finansal metriklerin takibi.")
    
    # Financial metrics calculator
    df_all = run_query("SELECT * FROM payments")
    total_payment = df_all['total_amount'].sum() if not df_all.empty else 0
    paid_amount = df_all[df_all['status'] == 'Ödendi']['total_amount'].sum() if not df_all.empty else 0
    pending_amount = df_all[df_all['status'] == 'Beklemede']['total_amount'].sum() if not df_all.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Hakediş Tutarı", f"{total_payment:,.2f} ₺")
    col2.metric("Ödenen Toplam Tutar", f"{paid_amount:,.2f} ₺", delta=f"{int(paid_amount/total_payment*100) if total_payment else 0}% Ödendi")
    col3.metric("Bekleyen Ödeme Toplamı", f"{pending_amount:,.2f} ₺", delta=f"-{int(pending_amount/total_payment*100) if total_payment else 0}% Bekliyor")
    
    st.markdown("---")
    
    # Data visualization layout
    if not df_all.empty:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Ödeme Durum Dağılımı")
            fig_status = px.pie(df_all, names='status', values='total_amount', color='status',
                                color_discrete_map={'Ödendi': '#2ECC71', 'Beklemede': '#E74C3C'})
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col_chart2:
            st.subheader("Müteahhitlere Göre Hakediş Dağılımı")
            fig_contractor = px.bar(df_all, x='contractor_name', y='total_amount', color='status',
                                    barmode='group', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_contractor, use_container_width=True)
    else:
        st.info("Grafikleri oluşturmak için henüz sisteme girilmiş hakediş verisi bulunmuyor.")

# --- PAGE B: METRAJ / QUANTITY SURVEY DATA VIEWER ---
elif menu == "📋 Metraj & Hakediş Raporları":
    st.title("📋 Metraj ve Alan Hesaplama Raporları")
    st.markdown("Projenize ait Excel/CSV metraj dökümleri ve alan hakediş detayları:")
    
    # Scanning directory automatically for spreadsheet tables
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if csv_files:
        selected_file = st.selectbox("İncelemek İstediğiniz Metraj Tablosunu Seçiniz:", csv_files)
        if selected_file:
            st.markdown(f"**Aktif Görüntülenen Dosya:** `{selected_file}`")
            try:
                df_csv = pd.read_csv(selected_file)
                st.dataframe(df_csv, use_container_width=True)
            except Exception as e:
                st.error(f"Dosya okunurken bir beklenmedik hata oluştu: {e}")
    else:
        st.info("Sistem dizininde otomatik okunabilecek metraj CSV dosyası bulunamadı.")

# --- PAGE C: CONTRACTOR SPECIFIC REPORTS ---
elif menu == "💼 Müteahhit ve Ödeme Takibi":
    st.title("💼 Müteahhit ve Özel Hakediş Filtreleri")
    
    st.subheader("🎯 Cüneyt Bey (Havence Projeleri) Filtrelenmiş Sorgusu")
    st.markdown("Aşağıdaki tablo, düzeltilen SQL f-string şablonu kullanılarak doğrudan veritabanından çekilmiştir:")
    
    # Running the secure dynamic query built at line 88
    sql_query = build_contractor_sql()
    df_filtered = run_query(sql_query)
    
    if not df_filtered.empty:
        st.dataframe(df_filtered, use_container_width=True)
        
        # Interactive UI Action to modify statuses
        st.markdown("### ⚙️ Hızlı Durum Güncelleme")
        selected_id = st.selectbox("Durumunu değiştirmek istediğiniz Hakediş ID seçiniz:", df_filtered['id'].tolist())
        new_status = st.radio("Yeni Ödeme Durumu Seçiniz:", ["Ödendi", "Beklemede"])
        
        if st.button("Durumu Güncelle"):
            execute_cmd("UPDATE payments SET status = ? WHERE id = ?", (new_status, selected_id))
            st.success(f"ID {selected_id} için ödeme durumu '{new_status}' olarak başarıyla güncellendi!")
            st.rerun()
    else:
        st.warning("Aranan kriterlere uygun ('Havence' ve 'Cüneyt Bey') kayıt bulunamadı.")

# --- PAGE D: NEW RECORDS REGISTRATION FORM ---
elif menu == "➕ Yeni Veri Girişi":
    st.title("➕ Yeni Hakediş / Ödeme Kaydı Ekle")
    st.markdown("Yeni bir proje hakedişi veya taşeron işçilik maliyet kaydı girmek için aşağıdaki formu doldurun.")
    
    with st.form("yeni_kayit_formu"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Proje / Şantiye Adı:", value="Merkez Rezidans")
            company_name = st.text_input("Şirket / İşveren Adı:", value="Havence")
            contractor_name = st.text_input("Müteahhit / Taşeron Adı:", value="Cüneyt Bey")
        with col2:
            labor_cost = st.number_input("Metrekare İşçilik Maliyeti (₺):", min_value=0.0, value=150.0, step=5.0)
            total_amount = st.number_input("Toplam Hakediş Tutarı (₺):", min_value=0.0, value=50000.0, step=1000.0)
            status = st.selectbox("Ödeme Durumu:", ["Beklemede", "Ödendi"])
            
        submit_button = st.form_submit_button(label="Hakediş Kaydını Veritabanına Ekle")
        
        if submit_button:
            today_str = datetime.today().strftime('%Y-%m-%d')
            execute_cmd('''
                INSERT INTO payments (project_name, company_name, contractor_name, labor_cost, total_amount, status, record_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project_name, company_name, contractor_name, labor_cost, total_amount, status, today_str))
            st.success(f"'{contractor_name}' adına ait yeni hakediş veritabanına başarıyla eklendi!")
