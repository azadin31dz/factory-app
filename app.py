import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="إدارة مصنع الحقائب",
    page_icon="💼",
    layout="centered"
)

# --- التنسيق الجمالي الخارق والعصري (CSS المطور) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    /* ضبط الخطوط والاتجاه العام */
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    
    /* خلفية التطبيق الفاخرة باللون الأسود الملكي */
    .stApp {
        background: radial-gradient(circle at top, #1a1c1e 0%, #0f1011 100%) !important;
    }
    
    /* إخفاء القوائم الجانبية المزعجة تماماً */
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* العنوان الرئيسي ثلاثي الأبعاد وعصري جداً */
    .main-title-container {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(27, 94, 32, 0.3);
        margin-bottom: 30px !important;
        text-align: center !important;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-title {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        text-align: center !important;
        margin: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* أزرار اختيار الصفحات العلوية (تنسيق يشبه تطبيقات الهاتف الاحترافية) */
    .stRadio > div {
        background-color: #16181a !important;
        padding: 10px !important;
        border-radius: 14px !important;
        border: 1px solid #2d3135 !important;
        gap: 10px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }
    .stRadio [data-testid="stMarkdownContainer"] p {
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* الكروت الذكية الفاخرة (Glassmorphism + Neon Border) */
    .premium-card {
        background: rgba(30, 34, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 6px solid #4caf50;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    .premium-card:hover {
        transform: translateY(-2px);
    }
    .card-label {
        color: #9aa0a6 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-value {
        color: #4caf50 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.2);
    }
    .card-value-wages {
        color: #ffca28 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(255, 202, 40, 0.2);
    }
    
    /* تجميل الجداول لتصبح عصرية متناسقة مع الوضع الداكن */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #16181a !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #2d3135 !important;
    }
    
    /* العناوين الفرعية الجانبية */
    h3 {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        border-right: 4px solid #4caf50;
        padding-right: 10px !important;
    }
    h4 {
        color: #e8eaed !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    /* الأزرار الرئيسية الملونة ذات الملمس الناعم اللامع */
    div.stButton > button {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* زر الحذف ذو اللون الأحمر الناري */
    .delete-btn div.stButton > button {
        background: linear-gradient(135deg, #b71c1c 0%, #e53935 100%) !important;
        box-shadow: 0 4px 15px rgba(229, 57, 53, 0.3) !important;
    }
    .delete-btn div.stButton > button:hover {
        background: linear-gradient(135deg, #c62828 0%, #ef5350 100%) !important;
        box-shadow: 0 6px 20px rgba(229, 57, 53, 0.5) !important;
    }
    
    /* تحسين الحقول والمدخلات الفردية */
    .stSelectbox div, .stNumberInput div, .stTextInput div, .stDateInput div {
        background-color: #1e2226 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# مسار قاعدة البيانات الآمن لضمان عدم الحذف
DB_DIR = os.path.expanduser("~")
DB_NAME = os.path.join(DB_DIR, "factory_secure_web.db")
PRICE_PER_PIECE = 550

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS workers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, is_active INTEGER DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS colors (id INTEGER PRIMARY KEY AUTOINCREMENT, color_name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_production (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        production_date DATE, worker_id INTEGER, color_id INTEGER, quantity INTEGER, price_per_piece REAL,
                        FOREIGN KEY(worker_id) REFERENCES workers(id), FOREIGN KEY(color_id) REFERENCES colors(id))''')
    
    cursor.execute("SELECT COUNT(*) FROM workers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO workers (name) VALUES (?)", [("عامل 1",), ("عامل 2",), ("عامل 3",)])
    cursor.execute("SELECT COUNT(*) FROM colors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colors (color_name) VALUES (?)", [("أسود",), ("رمادي",), ("بيج",), ("أخضر",)])
    conn.commit()
    conn.close()

init_db()

# تصميم العنوان الجديد كلياً
st.markdown('<div class="main-title-container"><h1 class="main-title">🏭 مصنع الحقائب الذكي • Smart Factory</h1></div>', unsafe_allow_html=True)

# أزرار تنقل عصرية بأيقونات جميلة ومحسنة جداً للهاتف
page = st.radio("📌 لوحة التحكم السريعة:", ["📊 التقارير والأيام", "📝 تسجيل الإنتاج", "⚙️ إدارة العمال والألوان", "💾 الأمان والنسخ"], horizontal=True)

st.write(" ")

# --- 1. صفحة لوحة التحكم والتقارير بأثر رجعي ---
if page == "📊 التقارير والأيام":
    st.markdown("### 🔍 مراجعة التقارير والإنتاج السابق")
    
    selected_date = st.date_input("📅 اختر اليوم الذي تريد العودة إليه لتفقد سجلاته:", datetime.now().date())
    formatted_date = selected_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    df_prod = pd.read_sql_query(f"""
        SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as
    
