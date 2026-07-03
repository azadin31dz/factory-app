import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(
    page_title="إدارة مصنع الحقائب",
    page_icon="💼",
    layout="centered"
)

# --- كود سحري لحذف ومنع التداخل والشريط العمودي المزعج في الهواتف ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* ضبط الخطوط والاتجاه من اليمين لليسار */
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    
    /* إخفاء الأزرار الجانبية الشفافة التي تسبب تداخل الحروف */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* تنسيق كروت الإحصائيات لتبدو ممتازة على الهاتف */
    [data-testid="stMetric"] {
        background-color: #1E1E1E !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #4E7055 !important;
        margin-bottom: 15px !important;
    }
    [data-testid="stMetricValue"] {
        color: #E6CBA8 !important;
        font-size: 1.8rem !important;
        text-align: center !important;
    }
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
        font-size: 1rem !important;
        text-align: center !important;
    }
    
    /* ضبط أزرار اختيار الصفحات لتكون كبيرة ومناسبة لليد */
    .stRadio > div {
        flex-direction: column !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_NAME = "factory_web.db"
PRICE_PER_PIECE = 550

# إعداد قاعدة البيانات
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
        cursor.executemany("INSERT INTO workers (name) VALUES (?)", [(f"عامل {i}",) for i in range(1, 6)])
    cursor.execute("SELECT COUNT(*) FROM colors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colors (color_name) VALUES (?)", [("أسود",), ("رمادي",), ("بيج",), ("أخضر",)])
    conn.commit()
    conn.close()

init_db()

st.title("💼 نظام إدارة مصنع الحقائب")

# أزرار تنقل واضحة في منتصف الشاشة بدلاً من القائمة الجانبية المعطلة
page = st.radio("🚦 اختر الصفحة التي تريدها:", ["📊 لوحة التحكم", "📝 تسجيل إنتاج جديد", "⚙️ إضافة عمال وألوان", "💾 نسخة احتياطية"], horizontal=True)

st.write("---")

# --- 1. صفحة لوحة التحكم ---
if page == "📊 لوحة التحكم":
    st.subheader("📊 إحصائيات إنتاج اليوم")
    
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    df_prod = pd.read_sql_query(f"""
        SELECT p.id, w.name as worker_name, c.color_name, p.quantity, (p.quantity * p.price_per_piece) as wages
        FROM daily_production p 
        JOIN workers w ON p.worker_id = w.id 
        JOIN colors c ON p.color_id = c.id
        WHERE p.production_date = '{current_date}'
    """, conn)
    
    if not df_prod.empty:
        total_bags = df_prod['quantity'].sum()
        total_wages = df_prod['wages'].sum()
        
        st.metric("📦 إجمالي حقائب اليوم", f"{total_bags} حقيبة")
        st.metric("💰 إجمالي أجور العمال", f"{total_wages:,.0f} دج")
        
        st.write("---")
        st.subheader("📋 جدول تفاصيل الإنتاج:")
        st.dataframe(df_prod[["worker_name", "color_name", "quantity", "wages"]], use_container_width=True, hide_index=True)
    else:
        st.metric("📦 إجمالي حقائب اليوم", "0 حقيبة")
        st.metric("💰 إجمالي أجور العمال", "0 دج")
        st.info("لا توجد بيانات مسجلة لليوم. اذهب لصفحة التسجيل لإدخال الإنتاج.")
    conn.close()

# --- 2. صفحة تسجيل الإنتاج ---
elif page == "📝 تسجيل إنتاج جديد":
    st.subheader("📝 إدخال حركة إنتاج")
    
    conn = sqlite3.connect(DB_NAME)
    workers = pd.read_sql_query("SELECT id, name FROM workers WHERE is_active=1", conn)
    colors = pd.read_sql_query("SELECT id, color_name FROM colors", conn)
    
    worker_opt = st.selectbox("👤 اسم العامل:", workers['name'].tolist())
    color_opt = st.selectbox("🎨 لون الحقيبة:", colors['color_name'].tolist())
    qty = st.number_input("🔢 الكمية (عدد الحقائب):", min_value=1, value=10, step=1)
    
    if st.button("✅ حفظ في قاعدة البيانات", type="primary", use_container_width=True):
        w_id = workers[workers['name'] == worker_opt]['id'].values[0]
        c_id = colors[colors['color_name'] == color_opt]['id'].values[0]
        current_date = datetime.now().date().strftime("%Y-%m-%d")
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO daily_production (production_date, worker_id, color_id, quantity, price_per_piece) VALUES (?, ?, ?, ?, ?)",
                       (current_date, int(w_id), int(c_id), int(qty), PRICE_PER_PIECE))
        conn.commit()
        st.success(f"تم تسجيل {qty} حقائب للعامل {worker_opt} بنجاح!")
    conn.close()

# --- 3. صفحة الإعدادات ---
elif page == "⚙️ إضافة عمال وألوان":
    st.subheader("👤 إضافة عامل جديد للمصنع")
    new_worker = st.text_input("اكتب اسم العامل:")
    conn = sqlite3.connect(DB_NAME)
    if st.button("إضافة العامل الآن"):
        if new_worker:
            try:
                conn.execute("INSERT INTO workers (name) VALUES (?)", (new_worker,))
                conn.commit()
                st.success(f"تمت إضافة {new_worker} بنجاح!")
            except: st.error("الاسم مسجل بالفعل")
            
    st.write("---")
    st.subheader("🎨 إضافة لون جديد")
    new_color = st.text_input("اكتب اسم اللون الجديد:")
    if st.button("إضافة اللون الآن"):
        if new_color:
            try:
                conn.execute("INSERT INTO colors (color_name) VALUES (?)", (new_color,))
                conn.commit()
                st.success(f"تمت إضافة اللون {new_color}!")
            except: st.error("اللون مسجل بالفعل")
    conn.close()

# --- 4. صفحة النسخ الاحتياطي ---
elif page == "💾 نسخة احتياطية":
    st.subheader("💾 تحميل قاعدة البيانات")
    st.write("يمكنك تحميل الملف لحفظه على هاتفك كنسخة احتياطية في أي وقت:")
    try:
        with open(DB_NAME, "rb") as f:
            st.download_button("📥 تحميل ملف قاعدة البيانات (.db)", f, file_name="factory_data.db", use_container_width=True)
    except:
        st.info("لا توجد بيانات للنسخ الاحتياطي حالياً.")
    
