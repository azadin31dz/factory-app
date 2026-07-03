import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# --- إعدادات الصفحة متوافقة تماماً مع الهواتف ---
st.set_page_config(
    page_title="إدارة مصنع حقائب السفر",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"  # إخفاء القائمة الجانبية تلقائياً في الهواتف
)

# --- تنسيق احترافي لمنع تداخل النصوص في الموبايل ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    # * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    html, body, [data-testid="stSidebarNav"] {
        direction: RTL;
        text-align: right;
    }
    
    /* ضبط كروت الإحصائيات للهاتف */
    [data-testid="stMetric"] {
        background-color: #2D2D2D !important;
        padding: 12px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        border-right: 5px solid #4E7055 !important;
        margin-bottom: 10px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #E6CBA8 !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
        font-size: 0.9rem !important;
    }
    
    /* منع تداخل العناوين الكبيرة */
    h1 {
        font-size: 1.8rem !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        text-align: center !important;
    }
    h2, h3 {
        font-size: 1.3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_NAME = "factory_web.db"
PRICE_PER_PIECE = 550

# --- إعداد قاعدة البيانات ---
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
        cursor.executemany("INSERT INTO workers (name) VALUES (?)", [(f"عامل {i}",) for i in range(1, 8)])
    cursor.execute("SELECT COUNT(*) FROM colors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colors (color_name) VALUES (?)", [("أسود",), ("رمادي",), ("بيج",), ("أخضر",), ("وردي",)])
    conn.commit()
    conn.close()

init_db()

# --- القائمة الجانبية ---
st.sidebar.title("🎛️ قائمة التحكم")
page = st.sidebar.radio("انتقل إلى:", ["📊 لوحة التحكم الرئيسية", "📝 تسجيل الإنتاج السريع", "⚙️ إدارة العمال والألوان", "💾 النسخ الاحتياطي"])

# --- 1. صفحة لوحة التحكم الرئيسية ---
if page == "📊 لوحة التحكم الرئيسية":
    st.title("📊 لوحة التحكم ومتابعة الإنتاج")
    
    selected_date = st.date_input("اختر تاريخ العرض:", datetime.now().date())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    df_prod = pd.read_sql_query(f"""
        SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as wages
        FROM daily_production p 
        JOIN workers w ON p.worker_id = w.id 
        JOIN colors c ON p.color_id = c.id
        WHERE p.production_date = '{date_str}'
    """, conn)
    
    if not df_prod.empty:
        total_bags = df_prod['quantity'].sum()
        total_wages = df_prod['wages'].sum()
        active_w = df_prod['worker_name'].nunique()
    else:
        total_bags, total_wages, active_w = 0, 0, 0
        
    # عرض الكروت بشكل عمودي متناسق للهواتف بدلاً من الطول المتداخل
    st.metric("📦 إنتاج اليوم", f"{total_bags} حقيبة")
    st.metric("💰 إجمالي الأجور", f"{total_wages:,.0f} دج")
    st.metric("👥 العمال النشطين", f"{active_w} عمال")
        
    st.write("---")
    
    if not df_prod.empty:
        st.subheader("📋 جدول إنتاج العمال اليوم")
        summary_df = df_prod.groupby('worker_name').agg({'quantity': 'sum', 'wages': 'sum'}).reset_index()
        summary_df.columns = ["اسم العامل", "عدد الحقائب", "الأجر المستحق (دج)"]
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.subheader("📈 التحليلات البيانية")
        fig, ax = plt.subplots(figsize=(6, 3))
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#1E1E1E')
        ax.bar(summary_df["اسم العامل"], summary_df["عدد الحقائب"], color='#4E7055')
        ax.tick_params(colors='white')
        ax.title.set_color('white')
        st.pyplot(fig)
        
        st.write("---")
        st.subheader("⚠️ إدارة سجلات اليوم")
        record_to_delete = st.selectbox("اختر السجل المراد حذفه:", df_prod['id'].tolist(), format_func=lambda x: f"رقم {x} - {df_prod[df_prod['id']==x]['worker_name'].values[0]} ({df_prod[df_prod['id']==x]['quantity'].values[0]} حقيبة)")
        if st.button("🔴 حذف السجل المختار", type="primary", use_container_width=True):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_production WHERE id=?", (int(record_to_delete),))
            conn.commit()
            st.success("تم الحذف، جاري التحديث...")
            st.rerun()
    else:
        st.info("لا توجد أي بيانات مسجلة لهذا اليوم حتى الآن.")
    conn.close()

# --- 2. صفحة تسجيل الإنتاج السريع ---
elif page == "📝 تسجيل الإنتاج السريع":
    st.title("📝 تسجيل الإنتاج اليومي")
    
    conn = sqlite3.connect(DB_NAME)
    workers = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    colors = pd.read_sql_query("SELECT id, color_name FROM colors", conn)
    
    current_date = st.date_input("تاريخ الإنتاج:", datetime.now().date())
    worker_opt = st.selectbox("👤 اختر العامل:", workers['name'].tolist())
    color_opt = st.selectbox("🎨 اختر اللون:", colors['color_name'].tolist())
    qty = st.number_input("🔢 عدد الحقائب المصنوعة:", min_value=1, max_value=200, value=10, step=1)
    
    if st.button("✅ حفظ وإدراج الإنتاج فوراً", use_container_width=True, type="primary"):
        w_id = workers[workers['name'] == worker_opt]['id'].values[0]
        c_id = colors[colors['color_name'] == color_opt]['id'].values[0]
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO daily_production (production_date, worker_id, color_id, quantity, price_per_piece) VALUES (?, ?, ?, ?, ?)",
                       (current_date.strftime("%Y-%m-%d"), int(w_id), int(c_id), int(qty), PRICE_PER_PIECE))
        conn.commit()
        st.success(f"تم تسجيل {qty} حقائب بنجاح للعامل {worker_opt}!")
    conn.close()

# --- 3. صفحة إدارة العمال والألوان ---
elif page == "⚙️ إدارة العمال والألوان":
    st.title("⚙️ الإعدادات العامة")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    st.subheader("👤 إضافة عامل جديد")
    new_worker = st.text_input("اسم العامل:")
    if st.button("إضافة العامل", use_container_width=True):
        if new_worker:
            try:
                cursor.execute("INSERT INTO workers (name) VALUES (?)", (new_worker,))
                conn.commit()
                st.success("تمت إضافة العامل بنجاح!")
            except:
                st.error("الاسم موجود مسبقاً")
                
    st.write("---")
    st.subheader("🎨 إضافة لون جديد")
    new_color = st.text_input("اسم اللون:")
    if st.button("إضافة اللون", use_container_width=True):
        if new_color:
            try:
                cursor.execute("INSERT INTO colors (color_name) VALUES (?)", (new_color,))
                conn.commit()
                st.success("تمت إضافة اللون بنجاح!")
            except:
                st.error("اللون موجود مسبقاً")
    conn.close()

# --- 4. صفحة النسخ الاحتياطي ---
elif page == "💾 النسخ الاحتياطي":
    st.title("💾 النسخ الاحتياطي")
    st.write("حمل نسخة كاملة من قاعدة البيانات للاحتفاظ بها في هاتفك:")
    
    try:
        with open(DB_NAME, "rb") as f:
            st.download_button(
                label="📥 تحميل نسخة احتياطية (.db)",
                data=f,
                file_name=f"factory_backup_{datetime.now().strftime('%Y%m%d')}.db",
                mime="application/octet-stream",
                use_container_width=True
            )
    except:
        st.info("لا توجد بيانات للنسخ الاحتياطي بعد.")
